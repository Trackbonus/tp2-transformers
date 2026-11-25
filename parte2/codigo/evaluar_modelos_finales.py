
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import torch

from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
RESULTS_DIR = BASE_DIR / "resultados"

# Modelos seleccionados
RIDGE_DIR = RESULTS_DIR / "ridge"
DISTILBERT_DIR = (
    RESULTS_DIR
    / "distilbert"
    / "optimizacion_6_experimentos"
    / "mejor_modelo"
)

OUTPUT_DIR = RESULTS_DIR / "comparacion_final"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 8
MAX_LENGTH = 512

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Dispositivo:", device)
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


# --------------------------------------------------
# 1. Cargar datos de test
# --------------------------------------------------

test_df = pd.read_csv(DATA_DIR / "test.csv")
validation_df = pd.read_csv(DATA_DIR / "validation.csv")

texts = test_df["texto"].fillna("")
real_scores = test_df["puntuacion"].to_numpy(dtype=float)
validation_texts = validation_df["texto"].fillna("")
validation_scores = validation_df["puntuacion"].to_numpy(dtype=float)

print("Registros de test:", len(test_df))
print("Registros de validación:", len(validation_df))


# --------------------------------------------------
# 2. Evaluar TF-IDF + Ridge
# --------------------------------------------------

print("\nEvaluando TF-IDF + Ridge...")

vectorizer = joblib.load(RIDGE_DIR / "vectorizador.joblib")
ridge_model = joblib.load(RIDGE_DIR / "mejor_modelo.joblib")

X_test_tfidf = vectorizer.transform(texts)
ridge_predictions = ridge_model.predict(X_test_tfidf)
ridge_validation_predictions = ridge_model.predict(
    vectorizer.transform(validation_texts)
)


# --------------------------------------------------
# 3. Evaluar DistilBERT
# --------------------------------------------------

print("\nEvaluando DistilBERT...")

tokenizer = AutoTokenizer.from_pretrained(str(DISTILBERT_DIR))
distilbert_model = AutoModelForSequenceClassification.from_pretrained(
    str(DISTILBERT_DIR)
)

distilbert_model.to(device)
distilbert_model.eval()


class ReviewDataset(Dataset):
    def __init__(self, texts, tokenizer):
        self.texts = texts.tolist()
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        return self.tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt"
        )


def predict_distilbert(texts):
    dataset = ReviewDataset(texts, tokenizer)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE)
    predictions_all = []
    with torch.no_grad():
        for batch in loader:
            batch = {
                key: value.squeeze(1).to(device)
                for key, value in batch.items()
            }
            outputs = distilbert_model(**batch)
            predictions_all.extend(outputs.logits.squeeze(-1).cpu().numpy())
    return np.array(predictions_all) * 100


distilbert_predictions = predict_distilbert(texts)
distilbert_validation_predictions = predict_distilbert(validation_texts)


# --------------------------------------------------
# 4. Calcular métricas
# --------------------------------------------------

def calculate_metrics(real, predicted):
    return {
        "mae": float(mean_absolute_error(real, predicted)),
        "rmse": float(mean_squared_error(real, predicted) ** 0.5),
        "r2": float(r2_score(real, predicted))
    }


ridge_metrics = calculate_metrics(
    real_scores,
    ridge_predictions
)

distilbert_metrics = calculate_metrics(
    real_scores,
    distilbert_predictions
)
ridge_validation_metrics = calculate_metrics(
    validation_scores,
    ridge_validation_predictions
)
distilbert_validation_metrics = calculate_metrics(
    validation_scores,
    distilbert_validation_predictions
)


# --------------------------------------------------
# 5. Mostrar comparación
# --------------------------------------------------

comparison = pd.DataFrame([
    {
        "modelo": "TF-IDF + Ridge",
        "mae": ridge_metrics["mae"],
        "rmse": ridge_metrics["rmse"],
        "r2": ridge_metrics["r2"]
    },
    {
        "modelo": "DistilBERT",
        "mae": distilbert_metrics["mae"],
        "rmse": distilbert_metrics["rmse"],
        "r2": distilbert_metrics["r2"]
    }
])

print("\n" + "=" * 55)
print("COMPARACIÓN FINAL EN TEST")
print("=" * 55)
print(comparison.to_string(index=False))
validation_comparison = pd.DataFrame([
    {"modelo": "TF-IDF + Ridge", **ridge_validation_metrics},
    {"modelo": "DistilBERT", **distilbert_validation_metrics}
])
print("\nCOMPARACIÓN EN VALIDACIÓN")
print(validation_comparison.to_string(index=False))


# --------------------------------------------------
# 6. Calcular mejoras porcentuales
# --------------------------------------------------

mae_improvement = (
    (ridge_metrics["mae"] - distilbert_metrics["mae"])
    / ridge_metrics["mae"] * 100
)

rmse_improvement = (
    (ridge_metrics["rmse"] - distilbert_metrics["rmse"])
    / ridge_metrics["rmse"] * 100
)

print(f"\nMejora de MAE de DistilBERT: {mae_improvement:.2f}%")
print(f"Mejora de RMSE de DistilBERT: {rmse_improvement:.2f}%")


# --------------------------------------------------
# 7. Guardar predicciones
# --------------------------------------------------

predictions_df = test_df[
    ["banda", "album", "puntuacion"]
].copy()

predictions_df["prediccion_ridge"] = ridge_predictions
predictions_df["error_ridge"] = np.abs(
    real_scores - ridge_predictions
)

predictions_df["prediccion_distilbert"] = distilbert_predictions
predictions_df["error_distilbert"] = np.abs(
    real_scores - distilbert_predictions
)

predictions_df.to_csv(
    OUTPUT_DIR / "predicciones_test.csv",
    index=False
)

comparison.to_csv(
    OUTPUT_DIR / "metricas_comparacion.csv",
    index=False
)
validation_comparison.to_csv(
    OUTPUT_DIR / "metricas_validacion.csv",
    index=False
)

final_results = {
    "conjunto": "test",
    "registros": len(test_df),
    "ridge": ridge_metrics,
    "distilbert": distilbert_metrics,
    "validacion": {
        "registros": len(validation_df),
        "ridge": ridge_validation_metrics,
        "distilbert": distilbert_validation_metrics
    },
    "mejora_distilbert_mae_porcentaje": mae_improvement,
    "mejora_distilbert_rmse_porcentaje": rmse_improvement
}

with open(
    OUTPUT_DIR / "resultados_finales.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(final_results, f, indent=4, ensure_ascii=False)

print("\nArchivos guardados en:", OUTPUT_DIR)
