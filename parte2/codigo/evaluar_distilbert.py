
from pathlib import Path
import json

import numpy as np
import pandas as pd
import torch

from torch.utils.data import Dataset, DataLoader
from parte2.codigo.contar_parametros import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
MODEL_DIR = BASE_DIR / "resultados" / "distilbert" / "modelo_final"
OUTPUT_DIR = BASE_DIR / "resultados" / "distilbert"

MODEL_NAME = str(MODEL_DIR)
MAX_LENGTH = 512
BATCH_SIZE = 8

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Dispositivo:", device)
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

# Cargar datos de prueba
test_df = pd.read_csv(DATA_DIR / "test.csv")

print("Registros de prueba:", len(test_df))

# Cargar modelo y tokenizador entrenados
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.to(device)
model.eval()


class ReviewDataset(Dataset):
    def __init__(self, dataframe):
        self.texts = dataframe["texto"].fillna("").tolist()

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt"
        )


dataset = ReviewDataset(test_df)
loader = DataLoader(dataset, batch_size=BATCH_SIZE)

# Generar predicciones
predictions = []

with torch.no_grad():
    for batch in loader:
        batch = {
            key: value.squeeze(1).to(device)
            for key, value in batch.items()
        }

        outputs = model(**batch)
        batch_predictions = outputs.logits.squeeze(-1)

        predictions.extend(batch_predictions.cpu().numpy())

# Recuperar escala original 0-100
predictions = np.array(predictions) * 100
real_scores = test_df["puntuacion"].to_numpy(dtype=float)

# Calcular métricas
mae = mean_absolute_error(real_scores, predictions)
rmse = mean_squared_error(real_scores, predictions) ** 0.5

# Guardar predicciones
results_df = test_df[
    ["banda", "album", "puntuacion"]
].copy()

results_df["prediccion"] = predictions
results_df["error_absoluto"] = np.abs(
    real_scores - predictions
)

predictions_path = OUTPUT_DIR / "distilbert_test_predicciones.csv"
results_df.to_csv(predictions_path, index=False)

# Guardar métricas
metrics = {
    "modelo": "DistilBERT",
    "conjunto": "test",
    "n_registros": len(test_df),
    "mae": float(mae),
    "rmse": float(rmse)
}

metrics_path = OUTPUT_DIR / "distilbert_test.json"

with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4, ensure_ascii=False)

print("\nRESULTADOS DE TEST")
print(f"MAE:  {mae:.4f}")
print(f"RMSE: {rmse:.4f}")

print("\nArchivos guardados:")
print(predictions_path)
print(metrics_path)
