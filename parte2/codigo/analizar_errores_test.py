"""Analiza errores individuales del DistilBERT seleccionado, sin volver a entrenar."""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from torch.utils.data import DataLoader, Dataset

from transformers import AutoModelForSequenceClassification, AutoTokenizer


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
MODEL_DIR = (
    BASE_DIR
    / "resultados"
    / "distilbert"
    / "optimizacion_6_experimentos"
    / "mejor_modelo"
)
OUTPUT_DIR = BASE_DIR / "resultados" / "distilbert" / "analisis_errores_test"
SCORE_ERROR_DIR = OUTPUT_DIR / "error_por_puntuacion"
MAX_LENGTH = 512
BATCH_SIZE = 8


class ReviewDataset(Dataset):
    """Mismo tokenizado que evaluar_modelos_finales.py."""

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
            return_tensors="pt",
        )


def calculate_metrics(real, predicted):
    """Reutiliza la definición de métricas del evaluador final."""
    return {
        "mae": float(mean_absolute_error(real, predicted)),
        "rmse": float(mean_squared_error(real, predicted) ** 0.5),
    }


def load_or_predict(test_df, texts, real_scores, device):
    """Reutiliza predicciones existentes solo si coinciden con el test fila a fila."""
    existing_path = OUTPUT_DIR / "predicciones_y_errores_test.csv"
    if existing_path.exists():
        existing = pd.read_csv(existing_path)
        if (
            len(existing) == len(test_df)
            and "puntuacion_real" in existing
            and np.array_equal(
                existing["puntuacion_real"].to_numpy(dtype=float), real_scores
            )
            and "puntuacion_predicha" in existing
        ):
            return existing["puntuacion_predicha"].to_numpy(dtype=float)

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
    model.to(device)
    model.eval()
    loader = DataLoader(ReviewDataset(texts, tokenizer), batch_size=BATCH_SIZE)
    raw_predictions = []
    with torch.no_grad():
        for batch in loader:
            batch = {key: value.squeeze(1).to(device) for key, value in batch.items()}
            outputs = model(**batch)
            raw_predictions.extend(outputs.logits.squeeze(-1).cpu().numpy())
    return np.asarray(raw_predictions, dtype=float) * 100


def save_score_error_analysis(test_df, predictions, real_scores):
    SCORE_ERROR_DIR.mkdir(parents=True, exist_ok=True)
    absolute_errors = np.abs(predictions - real_scores)
    scores = pd.DataFrame({
        "puntuacion_real": real_scores,
        "puntuacion_predicha": predictions,
        "error_absoluto": absolute_errors,
    })
    if "banda" in test_df:
        scores["banda"] = test_df["banda"].to_numpy()
    if "album" in test_df:
        scores["album"] = test_df["album"].to_numpy()
    scores.to_csv(SCORE_ERROR_DIR / "datos_error_por_resena.csv", index=False)

    edges = np.arange(0, 101, 10)
    labels = [f"{start}-<{start + 10}" for start in range(0, 100, 10)]
    scores["intervalo_puntuacion"] = pd.cut(
        scores["puntuacion_real"], bins=edges, labels=labels,
        right=False, include_lowest=True
    )
    # El último intervalo incluye 100 para cubrir toda la escala.
    scores.loc[scores["puntuacion_real"] == 100, "intervalo_puntuacion"] = labels[-1]
    grouped = scores.groupby("intervalo_puntuacion", observed=False)["error_absoluto"]
    interval_summary = grouped.agg(cantidad="count", mae_promedio="mean").reindex(labels)
    interval_summary.index.name = "intervalo_puntuacion"
    interval_summary = interval_summary.reset_index()
    interval_summary.to_csv(SCORE_ERROR_DIR / "mae_por_intervalo.csv", index=False)

    midpoints = np.arange(5, 100, 10)
    fig, ax = plt.subplots(figsize=(12, 7), dpi=180)
    ax.scatter(
        scores["puntuacion_real"], scores["error_absoluto"],
        alpha=0.60, s=28, color="#2364AA", edgecolors="white", linewidths=0.35,
        label="Reseñas de test"
    )
    ax.plot(
        midpoints, interval_summary["mae_promedio"],
        color="#D1495B", marker="o", linewidth=2.5, markersize=6,
        label="MAE promedio por intervalo"
    )
    counts = interval_summary["cantidad"].to_numpy()
    for x, y, count in zip(midpoints, interval_summary["mae_promedio"], counts):
        if count and pd.notna(y):
            ax.annotate(f"n={count}", (x, y), xytext=(0, 8),
                        textcoords="offset points", ha="center", fontsize=8)
    ax.set(
        title="Error absoluto de DistilBERT seg\u00fan la puntuaci\u00f3n real (test)",
        xlabel="Puntuaci\u00f3n real de la rese\u00f1a (puntos, escala 0-100)",
        ylabel="Error absoluto |predicci\u00f3n - puntuaci\u00f3n real| (puntos)",
        xlim=(0, 100),
    )
    ax.set_xticks(np.arange(0, 101, 10))
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(SCORE_ERROR_DIR / "error_absoluto_por_puntuacion.png", bbox_inches="tight")
    plt.close(fig)

    print("\nMAE Y CANTIDAD POR INTERVALO DE PUNTUACIÓN REAL")
    print(interval_summary.to_string(index=False, na_rep="Sin observaciones"))
    print("Reseñas incluidas en el gráfico:", len(scores))
    return interval_summary


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Dispositivo:", device)
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    test_df = pd.read_csv(DATA_DIR / "test.csv")
    texts = test_df["texto"].fillna("")
    real_scores = test_df["puntuacion"].to_numpy(dtype=float)
    print("Registros de test:", len(test_df))

    predictions = load_or_predict(test_df, texts, real_scores, device)
    signed_errors = predictions - real_scores
    absolute_errors = np.abs(signed_errors)

    results = test_df.copy()
    results["puntuacion_real"] = real_scores
    results["puntuacion_predicha"] = predictions
    results["error_con_signo"] = signed_errors
    results["error_absoluto"] = absolute_errors

    # Las selecciones conservan el orden original en empates.
    largest = results.sort_values("error_absoluto", ascending=False, kind="stable").head(5)
    smallest = results.sort_values("error_absoluto", ascending=True, kind="stable").head(5)
    extremes = pd.concat(
        [largest.assign(grupo="mayor_error"), smallest.assign(grupo="menor_error")],
        ignore_index=True,
    )
    metrics = calculate_metrics(real_scores, predictions)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing_outputs = [
        OUTPUT_DIR / "predicciones_y_errores_test.csv",
        OUTPUT_DIR / "cinco_mayores_y_menores_errores.csv",
        OUTPUT_DIR / "resumen_estadistico.json",
    ]
    if not any(path.exists() for path in existing_outputs):
        results.to_csv(existing_outputs[0], index=False)
        extremes.to_csv(existing_outputs[1], index=False)

    min_idx = int(np.argmin(absolute_errors))
    max_idx = int(np.argmax(absolute_errors))
    summary = {
        "modelo": str(MODEL_DIR.relative_to(BASE_DIR)),
        "conjunto": "test",
        "registros": int(len(results)),
        "escala_puntuaciones": [0, 100],
        "mae": metrics["mae"],
        "rmse": metrics["rmse"],
        "error_absoluto_minimo": results.iloc[min_idx].to_dict(),
        "error_absoluto_maximo": results.iloc[max_idx].to_dict(),
        "nota": "MAE y RMSE calculados sobre las predicciones de este análisis; comparar con la evaluación final del mismo checkpoint.",
    }
    if not any(path.exists() for path in existing_outputs):
        with existing_outputs[2].open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    save_score_error_analysis(test_df, predictions, real_scores)

    def print_case(label, row):
        print(f"{label}: {row.get('banda', '')} — {row.get('album', '')}")
        print(
            f"  Real: {row['puntuacion_real']:.2f} | "
            f"Predicción: {row['puntuacion_predicha']:.2f} | "
            f"Error absoluto: {row['error_absoluto']:.2f}"
        )
        print(f"  Reseña: {str(row.get('texto', ''))[:500]}")

    print("\nRESUMEN DEL ANÁLISIS DE ERRORES")
    print(f"MAE:  {metrics['mae']:.6f}")
    print(f"RMSE: {metrics['rmse']:.6f}")
    print_case("Error absoluto mínimo", results.iloc[min_idx])
    print_case("Error absoluto máximo", results.iloc[max_idx])
    print("\nCinco mayores errores absolutos:")
    for _, row in largest.iterrows():
        print_case("-", row)
    print("\nCinco menores errores absolutos:")
    for _, row in smallest.iterrows():
        print_case("-", row)
    print("\nNuevos archivos guardados en:", SCORE_ERROR_DIR)


if __name__ == "__main__":
    main()
