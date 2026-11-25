"""Grafica la distribucion de puntuaciones del dataset completo del TP2."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "datos" / "resenas_metal_archives_2000_final.csv"
OUTPUT_DIR = BASE_DIR / "resultados" / "distribucion_dataset"
OUTPUT_PATH = OUTPUT_DIR / "distribucion_puntajes.png"


def main():
    dataset = pd.read_csv(DATA_PATH)
    score_column = "puntuacion"
    if score_column not in dataset.columns:
        raise ValueError(
            f"No se encontro la columna requerida {score_column!r} en {DATA_PATH}"
        )

    numeric_scores = pd.to_numeric(dataset[score_column], errors="coerce")
    valid_scores = numeric_scores.dropna()
    invalid_count = int(numeric_scores.isna().sum())
    if valid_scores.empty:
        raise ValueError("El dataset no contiene puntuaciones numericas validas.")

    count = int(valid_scores.count())
    mean_score = float(valid_scores.mean())
    median_score = float(valid_scores.median())
    std_score = float(valid_scores.std())
    minimum = float(valid_scores.min())
    maximum = float(valid_scores.max())
    quartiles = valid_scores.quantile([0.25, 0.50, 0.75])

    print("Dataset fuente:", DATA_PATH.name)
    print("Columna de puntuacion:", score_column)
    print("Valores invalidos descartados:", invalid_count)
    print("\nEstadisticas descriptivas (puntuacion)")
    print(f"Cantidad de resenas: {count}")
    print(f"Media: {mean_score:.2f}")
    print(f"Mediana: {median_score:.2f}")
    print(f"Desviacion estandar: {std_score:.2f}")
    print(f"Minimo: {minimum:.2f}")
    print(f"Maximo: {maximum:.2f}")
    print("Cuartiles:")
    print(f"  Q1 (25%): {quartiles.loc[0.25]:.2f}")
    print(f"  Q2 (50%): {quartiles.loc[0.50]:.2f}")
    print(f"  Q3 (75%): {quartiles.loc[0.75]:.2f}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUT_PATH.exists():
        raise FileExistsError(
            f"El grafico ya existe y no se sobrescribira: {OUTPUT_PATH}"
        )

    bins = np.arange(0, 105, 5)
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=180)
    ax.hist(
        valid_scores,
        bins=bins,
        color="#3977A8",
        edgecolor="white",
        linewidth=0.8,
        alpha=0.9,
        label=f"Puntuaciones (N = {count:,})",
    )
    ax.axvline(
        mean_score,
        color="#D1495B",
        linewidth=2.3,
        linestyle="--",
        label=f"Media: {mean_score:.2f}",
    )
    ax.axvline(
        median_score,
        color="#2A9D8F",
        linewidth=2.3,
        linestyle="-.",
        label=f"Mediana: {median_score:.2f}",
    )
    ax.set_title("Distribucion de puntuaciones del dataset completo", pad=14)
    ax.set_xlabel("Puntuacion de las resenas (escala 0-100)")
    ax.set_ylabel("Cantidad de resenas")
    ax.set_xlim(0, 100)
    ax.set_xticks(np.arange(0, 101, 10))
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    ax.text(
        0.99,
        0.96,
        f"Observaciones utilizadas: {count:,}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "alpha": 0.85},
    )
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, bbox_inches="tight")
    plt.close(fig)
    print("\nGrafico guardado en:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
