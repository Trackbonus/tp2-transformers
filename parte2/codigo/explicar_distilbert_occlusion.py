"""Analisis de sensibilidad por occlusion de oraciones para DistilBERT."""

import argparse
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


BASE_DIR = Path(__file__).resolve().parents[1]
PREDICTIONS_PATH = (
    BASE_DIR
    / "resultados"
    / "distilbert"
    / "analisis_errores_test"
    / "predicciones_y_errores_test.csv"
)
MODEL_DIR = (
    BASE_DIR
    / "resultados"
    / "distilbert"
    / "optimizacion_6_experimentos"
    / "mejor_modelo"
)
OUTPUT_DIR = BASE_DIR / "resultados" / "distilbert" / "explicabilidad"
MAX_LENGTH = 512
BATCH_SIZE = 8


class TextDataset(Dataset):
    def __init__(self, texts, tokenizer):
        self.texts = list(texts)
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, index):
        return self.tokenizer(
            self.texts[index],
            truncation=True,
            max_length=MAX_LENGTH,
            padding="max_length",
            return_tensors="pt",
        )


def split_sentences(text):
    """Segmentacion ligera que conserva la puntuacion final de cada oracion."""
    pieces = re.split(r"(?<=[.!?])\s+", text.strip())
    return [piece.strip() for piece in pieces if piece.strip()]


def predict(texts, model, tokenizer, device):
    loader = DataLoader(TextDataset(texts, tokenizer), batch_size=BATCH_SIZE)
    values = []
    with torch.no_grad():
        for batch in loader:
            batch = {
                key: value.squeeze(1).to(device)
                for key, value in batch.items()
            }
            logits = model(**batch).logits.squeeze(-1)
            values.extend(logits.cpu().numpy())
    # Mismo reescalado usado en evaluar_modelos_finales.py.
    return np.asarray(values, dtype=float) * 100


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review-url",
        required=True,
        help="URL exacta de la reseña en predicciones_y_errores_test.csv",
    )
    args = parser.parse_args()

    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    matches = predictions_df.loc[
        predictions_df["review_url"].astype(str) == args.review_url
    ]
    if len(matches) != 1:
        candidates = predictions_df.loc[
            predictions_df["banda"].fillna("").str.fullmatch("Dream Theater", case=False)
            & predictions_df["album"].fillna("").str.fullmatch("Awake", case=False),
            ["autor", "puntuacion", "puntuacion_predicha", "review_url"],
        ]
        raise ValueError(
            f"La URL debe coincidir con una sola reseña; coincidencias: {len(matches)}.\n"
            f"Candidatas Dream Theater — Awake:\n{candidates.to_string(index=False)}"
        )

    review = matches.iloc[0]
    text = "" if pd.isna(review["texto"]) else str(review["texto"])
    recorded_prediction = float(review["puntuacion_predicha"])
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError("La reseña no contiene oraciones para analizar.")

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    full_token_count = len(tokenizer(text, truncation=False)["input_ids"])
    was_truncated = full_token_count > MAX_LENGTH
    full_prediction = float(predict([text], model, tokenizer, device)[0])
    consistent = bool(np.isclose(full_prediction, recorded_prediction, rtol=0, atol=1e-4))

    occluded_texts = []
    for removed_index in range(len(sentences)):
        remaining = sentences[:removed_index] + sentences[removed_index + 1 :]
        occluded_texts.append(" ".join(remaining))
    occluded_predictions = predict(occluded_texts, model, tokenizer, device)

    changes = occluded_predictions - full_prediction
    results = pd.DataFrame(
        {
            "numero_oracion": np.arange(1, len(sentences) + 1),
            "oracion": sentences,
            "prediccion_original": full_prediction,
            "prediccion_sin_oracion": occluded_predictions,
            "cambio_prediccion": changes,
            "cambio_absoluto": np.abs(changes),
        }
    ).sort_values("cambio_absoluto", ascending=False, kind="stable")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "occlusion_oraciones.csv"
    chart_path = OUTPUT_DIR / "occlusion_top10.png"
    summary_path = OUTPUT_DIR / "resumen_occlusion.txt"
    for output_path in (csv_path, chart_path, summary_path):
        if output_path.exists():
            raise FileExistsError(f"No se sobrescribira el archivo existente: {output_path}")

    results.to_csv(csv_path, index=False, encoding="utf-8-sig")

    top = results.head(10).sort_values("cambio_prediccion", ascending=True)
    colors = ["#2A9D8F" if value > 0 else "#D1495B" for value in top["cambio_prediccion"]]
    fig_height = max(6.5, 0.55 * len(top))
    fig, ax = plt.subplots(figsize=(13, fig_height), dpi=180)
    y_positions = np.arange(len(top))
    ax.barh(y_positions, top["cambio_prediccion"], color=colors, alpha=0.9)
    labels = [
        f"{int(row.numero_oracion)}. {row.oracion[:105]}{'…' if len(row.oracion) > 105 else ''}"
        for row in top.itertuples()
    ]
    ax.set_yticks(y_positions, labels)
    ax.axvline(0, color="#333333", linewidth=1)
    ax.set_xlabel("Cambio en la prediccion al eliminar la oracion (puntos)")
    ax.set_title("Occlusion de oraciones: 10 mayores cambios en DistilBERT")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    from matplotlib.patches import Patch

    ax.legend(
        handles=[
            Patch(color="#2A9D8F", label="Aumento al eliminar la oracion"),
            Patch(color="#D1495B", label="Disminucion al eliminar la oracion"),
        ],
        loc="best",
        frameon=False,
    )
    fig.tight_layout()
    fig.savefig(chart_path, bbox_inches="tight")
    plt.close(fig)

    direction = lambda value: "aumento" if value > 0 else "disminucion" if value < 0 else "sin cambio"
    top_report = results.head(10)
    with summary_path.open("w", encoding="utf-8") as output:
        output.write("ANALISIS DE SENSIBILIDAD POR OCCLUSION DE ORACIONES\n")
        output.write("Este analisis mide cambios ante eliminaciones de texto; no demuestra causalidad ni constituye una explicacion definitiva del modelo.\n\n")
        output.write(f"Resena: {review.get('banda', '')} — {review.get('album', '')}\n")
        output.write(f"Autor: {review.get('autor', '')}\n")
        output.write(f"URL: {args.review_url}\n")
        output.write(f"Puntuacion real: {float(review['puntuacion_real']):.6f}\n")
        output.write(f"Prediccion original registrada: {recorded_prediction:.8f}\n")
        output.write(f"Prediccion original recalculada: {full_prediction:.8f}\n")
        output.write(f"Consistente con CSV (tolerancia 1e-4): {consistent}\n")
        output.write(f"Tokens incluyendo tokens especiales: {full_token_count}\n")
        output.write(f"Limite de entrada: {MAX_LENGTH}; texto truncado: {was_truncated}\n")
        output.write(f"Oraciones analizadas: {len(sentences)}\n\n")
        output.write("Mayores cambios absolutos (prediccion sin oracion menos prediccion original):\n")
        for row in top_report.itertuples():
            output.write(
                f"\n{int(row.numero_oracion)}. Cambio: {row.cambio_prediccion:+.6f} "
                f"({direction(row.cambio_prediccion)}); prediccion sin oracion: "
                f"{row.prediccion_sin_oracion:.6f}\n{row.oracion}\n"
            )

    print("Dispositivo:", device)
    print("Resena seleccionada:", review.get("autor", ""), "—", args.review_url)
    print(f"Prediccion CSV: {recorded_prediction:.8f}")
    print(f"Prediccion completa recalculada: {full_prediction:.8f}")
    print("Coincide dentro de tolerancia 1e-4:", consistent)
    print(f"Longitud tokenizada: {full_token_count}; truncado a {MAX_LENGTH}: {was_truncated}")
    print("Oraciones analizadas:", len(sentences))
    print("Archivos guardados en:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
