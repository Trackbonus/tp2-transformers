"""Repite E3 y empareja training/validation loss cada 50 steps."""

from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
    set_seed,
)
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "resultados" / "distilbert" / "curvas_e3"

MODEL_NAME = "distilbert-base-uncased"
LEARNING_RATE = 3e-5
NUM_TRAIN_EPOCHS = 3
WEIGHT_DECAY = 0.01
BATCH_SIZE = 8
MAX_LENGTH = 512
SEED = 42


class ReviewDataset(Dataset):
    """Mismo preprocesamiento que en optimizar_distilbert.py."""

    def __init__(self, dataframe, tokenizer):
        self.texts = dataframe["texto"].fillna("").tolist()
        self.labels = (dataframe["puntuacion"].astype(float) / 100.0).tolist()
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt",
        )
        item = {key: value.squeeze(0) for key, value in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.float)
        return item


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    predictions = predictions.reshape(-1) * 100
    labels = labels.reshape(-1) * 100
    return {
        "mae": mean_absolute_error(labels, predictions),
        "rmse": mean_squared_error(labels, predictions) ** 0.5,
    }


class StepLossCallback(TrainerCallback):
    """Evalúa ambos conjuntos tras cada 50.º paso de optimización."""

    def __init__(self, train_dataset, validation_dataset):
        self.train_dataset = train_dataset
        self.validation_dataset = validation_dataset
        self.trainer = None
        self.records = []

    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step == 0 or state.global_step % 50 != 0:
            return control

        # on_step_end ocurre tras actualizar los pesos. Evaluar ambos datasets
        # ahora asegura que ambos valores pertenecen al mismo checkpoint.
        model_was_training = self.trainer.model.training
        try:
            train_metrics = self.trainer.evaluate(
                eval_dataset=self.train_dataset,
                metric_key_prefix="training",
            )
            validation_metrics = self.trainer.evaluate(
                eval_dataset=self.validation_dataset,
                metric_key_prefix="validation",
            )
        finally:
            # Trainer.training_step también activa train(), pero restauramos
            # explícitamente el modo para no cambiar el estado del loop.
            self.trainer.model.train(model_was_training)

        self.records.append(
            {
                "step": int(state.global_step),
                "epoch": float(state.epoch),
                "training_loss": float(train_metrics["training_loss"]),
                "validation_loss": float(validation_metrics["validation_loss"]),
            }
        )
        print(
            f"Step {state.global_step}: "
            f"training_loss={train_metrics['training_loss']:.8f}, "
            f"validation_loss={validation_metrics['validation_loss']:.8f}"
        )
        return control


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    set_seed(SEED)

    train_df = pd.read_csv(DATA_DIR / "train.csv")
    validation_df = pd.read_csv(DATA_DIR / "validation.csv")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_dataset = ReviewDataset(train_df, tokenizer)
    validation_dataset = ReviewDataset(validation_df, tokenizer)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=1,
        problem_type="regression",
    )

    # Mismos argumentos de entrenamiento que E3 en optimizar_distilbert.py.
    training_args = TrainingArguments(
        # Directorio distinto del resultado anterior de curvas por época.
        output_dir=str(OUTPUT_DIR / "checkpoints_cada_50_steps"),
        num_train_epochs=NUM_TRAIN_EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        weight_decay=WEIGHT_DECAY,
        fp16=torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="mae",
        greater_is_better=False,
        save_total_limit=1,
        logging_steps=50,
        logging_strategy="steps",
        report_to="none",
        seed=SEED,
        data_seed=SEED,
    )

    callback = StepLossCallback(train_dataset, validation_dataset)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        compute_metrics=compute_metrics,
        callbacks=[callback],
    )
    callback.trainer = trainer
    trainer.train()

    if not callback.records:
        raise RuntimeError(
            "El Trainer no generó registros de pérdida en los steps esperados."
        )

    results_df = pd.DataFrame(
        callback.records,
        columns=["step", "epoch", "training_loss", "validation_loss"],
    )
    csv_path = OUTPUT_DIR / "perdidas_cada_50_steps.csv"
    results_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    results = {
        "experimento": "E3",
        "configuracion": {
            "modelo": MODEL_NAME,
            "learning_rate": LEARNING_RATE,
            "num_train_epochs": NUM_TRAIN_EPOCHS,
            "weight_decay": WEIGHT_DECAY,
            "batch_size": BATCH_SIZE,
            "max_length": MAX_LENGTH,
            "seed": SEED,
            "train_file": str(DATA_DIR / "train.csv"),
            "validation_file": str(DATA_DIR / "validation.csv"),
        },
        "definicion_loss": (
            "MSELoss de DistilBERT para regresión, con etiquetas "
            "puntuacion/100, igual que en el optimizador original. En cada "
            "step registrado, training_loss y validation_loss son eval_loss "
            "promedios del Trainer sobre cada conjunto completo, evaluados "
            "secuencialmente sin gradientes con el mismo estado de pesos."
        ),
        "resultados_por_step": callback.records,
    }
    json_path = OUTPUT_DIR / "perdidas_cada_50_steps.json"
    with json_path.open("w", encoding="utf-8") as result_file:
        json.dump(results, result_file, indent=2, ensure_ascii=False)

    plot_path = OUTPUT_DIR / "curvas_perdida_e3_cada_50_steps.png"
    plt.figure(figsize=(8, 5))
    plt.plot(
        results_df["step"],
        results_df["training_loss"],
        marker="o",
        label="Training loss",
    )
    plt.plot(
        results_df["step"],
        results_df["validation_loss"],
        marker="o",
        label="Validation loss",
    )
    plt.xlabel("Step de optimización")
    plt.ylabel("MSE loss")
    plt.title("DistilBERT E3: pérdida cada 50 steps")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=160)
    plt.close()

    print("Pérdidas por step:\n", results_df.to_string(index=False))
    print("CSV:", csv_path)
    print("JSON:", json_path)
    print("Gráfico:", plot_path)


if __name__ == "__main__":
    main()
