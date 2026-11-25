"""Mide los tiempos de la configuración ganadora de DistilBERT.

Replica un solo experimento de optimizar_distilbert.py y limita la evaluación
al conjunto de validación. Los checkpoints se guardan en la carpeta exclusiva
de esta medición, sin modificar los resultados de la optimización.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import time

import pandas as pd
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainerCallback,
    TrainingArguments,
    set_seed,
)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = (
    BASE_DIR / "resultados" / "distilbert" / "medicion_tiempos"
)

MODEL_NAME = "distilbert-base-uncased"
LEARNING_RATE = 3e-5
NUM_TRAIN_EPOCHS = 3
BATCH_SIZE = 8
WEIGHT_DECAY = 0.01
SEED = 42
MAX_LENGTH = 512


def synchronize_cuda():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


class ReviewDataset(Dataset):
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


class EpochTimingCallback(TrainerCallback):
    """Registra cada época incluyendo evaluación/guardado como el Trainer."""

    def __init__(self):
        self.epoch_start = None
        self.epoch_times = []

    def on_epoch_begin(self, args, state, control, **kwargs):
        synchronize_cuda()
        self.epoch_start = time.perf_counter()

    def on_save(self, args, state, control, **kwargs):
        synchronize_cuda()
        if self.epoch_start is not None:
            self.epoch_times.append(time.perf_counter() - self.epoch_start)
            self.epoch_start = None


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Dispositivo:", device)
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    train_df = pd.read_csv(DATA_DIR / "train.csv")
    validation_df = pd.read_csv(DATA_DIR / "validation.csv")
    print("Registros entrenamiento:", len(train_df))
    print("Registros validación:", len(validation_df))

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_dataset = ReviewDataset(train_df, tokenizer)
    validation_dataset = ReviewDataset(validation_df, tokenizer)

    set_seed(SEED)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=1,
        problem_type="regression",
    )

    # La salida del Trainer está aislada dentro de la carpeta de medición.
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR / "checkpoints"),
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
        report_to="none",
        seed=SEED,
        data_seed=SEED,
    )

    timing_callback = EpochTimingCallback()
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        compute_metrics=compute_metrics,
        callbacks=[timing_callback],
    )

    synchronize_cuda()
    total_start = time.perf_counter()
    trainer.train()
    synchronize_cuda()
    total_seconds = time.perf_counter() - total_start

    # La evaluación final replica la comprobación de validación del original,
    # pero queda fuera del tiempo de trainer.train().
    validation_metrics = trainer.evaluate()
    epoch_seconds = timing_callback.epoch_times
    average_seconds = (
        sum(epoch_seconds) / len(epoch_seconds) if epoch_seconds else 0.0
    )

    result = {
        "modelo": MODEL_NAME,
        "configuracion": {
            "learning_rate": LEARNING_RATE,
            "num_train_epochs": NUM_TRAIN_EPOCHS,
            "batch_size": BATCH_SIZE,
            "weight_decay": WEIGHT_DECAY,
            "seed": SEED,
            "max_length": MAX_LENGTH,
        },
        "dispositivo": device,
        "dataset": {
            "entrenamiento": str(DATA_DIR / "train.csv"),
            "validacion": str(DATA_DIR / "validation.csv"),
            "registros_entrenamiento": len(train_df),
            "registros_validacion": len(validation_df),
        },
        "tiempos_segundos": {
            "por_epoca": epoch_seconds,
            "total_trainer_train": total_seconds,
            "promedio_por_epoca": average_seconds,
        },
        "metricas_validacion": validation_metrics,
        "fecha_medicion_utc": datetime.now(timezone.utc).isoformat(),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result_path = OUTPUT_DIR / "tiempos_entrenamiento.json"
    with result_path.open("w", encoding="utf-8") as result_file:
        json.dump(result, result_file, indent=2, ensure_ascii=False)

    print("\nTiempos de entrenamiento:")
    for index, seconds in enumerate(epoch_seconds, start=1):
        print(f"Época {index}: {seconds:.2f} s ({seconds / 60:.2f} min)")
    print(f"Total trainer.train(): {total_seconds:.2f} s ({total_seconds / 60:.2f} min)")
    print(f"Promedio por época: {average_seconds:.2f} s ({average_seconds / 60:.2f} min)")
    print("JSON guardado en:", result_path)


if __name__ == "__main__":
    main()
