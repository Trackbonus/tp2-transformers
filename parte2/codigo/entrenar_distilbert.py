
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch

from torch.utils.data import Dataset
from parte2.codigo.contar_parametros import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from sklearn.metrics import mean_absolute_error, mean_squared_error

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "resultados" / "distilbert"

MODEL_NAME = "distilbert-base-uncased"
MAX_LENGTH = 512
BATCH_SIZE = 8
EPOCHS = 3
LEARNING_RATE = 2e-5

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

torch.manual_seed(42)
np.random.seed(42)

print("Dispositivo:", "GPU" if torch.cuda.is_available() else "CPU")
print("Modelo:", MODEL_NAME)

# --------------------------------------------------
# CARGAR DATOS
# --------------------------------------------------

train_df = pd.read_csv(DATA_DIR / "train.csv")
val_df = pd.read_csv(DATA_DIR / "validation.csv")

print(f"Entrenamiento: {len(train_df)}")
print(f"Validación: {len(val_df)}")

# --------------------------------------------------
# TOKENIZACIÓN
# --------------------------------------------------

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class ReviewDataset(Dataset):
    def __init__(self, dataframe):
        self.texts = dataframe["texto"].fillna("").tolist()
        self.labels = (
            dataframe["puntuacion"].astype(float) / 100.0
        ).tolist()

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = tokenizer(
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
            dtype=torch.float32
        )

        return item


train_dataset = ReviewDataset(train_df)
val_dataset = ReviewDataset(val_df)

print("Tokenización preparada.")

# --------------------------------------------------
# MODELO
# --------------------------------------------------

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=1,
    problem_type="regression"
)

# --------------------------------------------------
# MÉTRICAS
# --------------------------------------------------

def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    predictions = predictions.reshape(-1) * 100
    labels = labels.reshape(-1) * 100

    mae = mean_absolute_error(labels, predictions)
    rmse = mean_squared_error(labels, predictions) ** 0.5

    return {"mae": mae, "rmse": rmse}

# --------------------------------------------------
# ENTRENAMIENTO
# --------------------------------------------------

training_args = TrainingArguments(
    output_dir=str(OUTPUT_DIR / "checkpoints"),
    num_train_epochs=EPOCHS,
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="mae",
    greater_is_better=False,
    logging_steps=50,
    save_total_limit=2,
    report_to="none",
    fp16=torch.cuda.is_available(),
    dataloader_num_workers=0
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    callbacks=[
        EarlyStoppingCallback(early_stopping_patience=2)
    ]
)

print("\nIniciando entrenamiento...")
trainer.train()

# --------------------------------------------------
# GUARDAR MODELO
# --------------------------------------------------

trainer.save_model(str(OUTPUT_DIR / "modelo_final"))
tokenizer.save_pretrained(str(OUTPUT_DIR / "modelo_final"))

# Guardar métricas de validación
metrics = trainer.evaluate()

with open(
    OUTPUT_DIR / "metricas_validacion.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(metrics, f, indent=4)

print("\nRESULTADOS DE VALIDACIÓN")
print(f"MAE: {metrics['eval_mae']:.4f}")
print(f"RMSE: {metrics['eval_rmse']:.4f}")
print("\nModelo guardado en:", OUTPUT_DIR / "modelo_final")
