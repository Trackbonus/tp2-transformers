
from pathlib import Path
import json
import shutil

import pandas as pd
import torch

from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    set_seed
)
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
# Nueva ejecución aislada; conserva intactos los resultados históricos.
OUTPUT_DIR = (
    BASE_DIR / "resultados" / "distilbert" / "optimizacion_6_experimentos"
)

MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 512
BATCH_SIZE = 8
SEED = 42

# Experimentos de la primera etapa: comparación de learning rate.
STAGE_1_EXPERIMENTS = [
    {"nombre": "E1", "lr": 1e-5, "epochs": 3, "weight_decay": 0.01},
    {"nombre": "E2", "lr": 2e-5, "epochs": 3, "weight_decay": 0.01},
    {"nombre": "E3", "lr": 3e-5, "epochs": 3, "weight_decay": 0.01},
]

# En la segunda etapa, lr se asigna después de conocer el ganador de la etapa 1.
STAGE_2_EXPERIMENTS = [
    {"nombre": "E4", "epochs": 2, "weight_decay": 0.01},
    {"nombre": "E5", "epochs": 4, "weight_decay": 0.01},
    {"nombre": "E6", "epochs": 3, "weight_decay": 0.05},
]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo:", device)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


# Cargar datos
train_df = pd.read_csv(DATA_DIR / "train.csv")
validation_df = pd.read_csv(DATA_DIR / "validation.csv")

print("Registros entrenamiento:", len(train_df))
print("Registros validación:", len(validation_df))


# Dataset
class ReviewDataset(Dataset):
    def __init__(self, dataframe, tokenizer):
        self.texts = dataframe["texto"].fillna("").tolist()
        self.labels = (
            dataframe["puntuacion"].astype(float) / 100.0
        ).tolist()
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt"
        )

        item = {
            key: value.squeeze(0)
            for key, value in encoding.items()
        }

        item["labels"] = torch.tensor(
            self.labels[idx],
            dtype=torch.float
        )

        return item


def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    predictions = predictions.reshape(-1) * 100
    labels = labels.reshape(-1) * 100

    return {
        "mae": mean_absolute_error(labels, predictions),
        "rmse": mean_squared_error(labels, predictions) ** 0.5
    }


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

train_dataset = ReviewDataset(train_df, tokenizer)
validation_dataset = ReviewDataset(validation_df, tokenizer)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results = []
best_mae = float("inf")
best_model_dir = OUTPUT_DIR / "mejor_modelo"
stage_1_results = []

def run_experiment(experiment):
    global best_mae

    name = experiment["nombre"]

    print("\n" + "=" * 55)
    print("EXPERIMENTO:", name)
    print(experiment)
    print("=" * 55)

    set_seed(SEED)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=1,
        problem_type="regression"
    )

    experiment_dir = OUTPUT_DIR / name

    training_args = TrainingArguments(
        output_dir=str(experiment_dir),
        num_train_epochs=experiment["epochs"],
        learning_rate=experiment["lr"],
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        weight_decay=experiment["weight_decay"],
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
        data_seed=SEED
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        compute_metrics=compute_metrics
    )

    trainer.train()

    metrics = trainer.evaluate()

    result = {
        "experimento": name,
        "etapa": 1 if name in {"E1", "E2", "E3"} else 2,
        "learning_rate": experiment["lr"],
        "epocas": experiment["epochs"],
        "max_length": MAX_LENGTH,
        "seed": SEED,
        "batch_size": BATCH_SIZE,
        "weight_decay": experiment["weight_decay"],
        "mae": metrics["eval_mae"],
        "rmse": metrics["eval_rmse"]
    }

    results.append(result)

    print("\nResultado:", result)

    # Conservar el mejor modelo según MAE de validación
    if result["mae"] < best_mae:
        best_mae = result["mae"]

        if best_model_dir.exists():
            shutil.rmtree(best_model_dir)

        trainer.save_model(str(best_model_dir))
        tokenizer.save_pretrained(str(best_model_dir))

        with open(OUTPUT_DIR / "mejor_configuracion.json", "w") as f:
            json.dump(result, f, indent=4)

        print("Nuevo mejor modelo:", name)

    # Liberar memoria GPU
    del trainer
    del model

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return result


# Etapa 1: comparar exclusivamente las tres tasas de aprendizaje.
for experiment in STAGE_1_EXPERIMENTS:
    stage_1_results.append(run_experiment(experiment))

best_stage_1_result = min(stage_1_results, key=lambda result: result["mae"])
best_stage_1_learning_rate = best_stage_1_result["learning_rate"]
print(
    "\nLearning rate ganador de la etapa 1:",
    best_stage_1_learning_rate,
    "(experimento:", best_stage_1_result["experimento"], ")",
)

# Etapa 2: mantener el learning rate ganador y variar una dimensión por experimento.
for experiment in STAGE_2_EXPERIMENTS:
    run_experiment({**experiment, "lr": best_stage_1_learning_rate})


# Ordenar resultados por MAE
results_df = pd.DataFrame(results)
results_df = results_df.sort_values("mae")

results_df.to_csv(
    OUTPUT_DIR / "resultados_optimizacion.csv",
    index=False
)

with open(OUTPUT_DIR / "resultados_optimizacion.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "learning_rate_ganador_etapa_1": best_stage_1_learning_rate,
            "experimento_ganador_etapa_1": best_stage_1_result["experimento"],
            "resultados": results,
        },
        f,
        indent=4,
        ensure_ascii=False,
    )

print("\n" + "=" * 55)
print("RESULTADOS DE OPTIMIZACIÓN")
print("=" * 55)

print(results_df.to_string(index=False))

print("\nMejor configuración:")
print(results_df.iloc[0].to_dict())

print("\nMejor modelo guardado en:", best_model_dir)
