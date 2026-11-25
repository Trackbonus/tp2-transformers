
from pathlib import Path

import json
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "resultados"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar conjuntos
train = pd.read_csv(DATA_DIR / "train.csv")
val = pd.read_csv(DATA_DIR / "validation.csv")

# Variables
X_train = train["texto"].fillna("")
y_train = train["puntuacion"]

X_val = val["texto"].fillna("")
y_val = val["puntuacion"]

# Hiperparámetros a comparar
alphas = [0.1, 1.0, 10.0, 100.0]

results = []

for alpha in alphas:
    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                max_features=50000,
                min_df=2,
                sublinear_tf=True
            )
        ),
        ("regressor", Ridge(alpha=alpha))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_val)

    mae = mean_absolute_error(y_val, predictions)
    rmse = mean_squared_error(y_val, predictions) ** 0.5

    results.append({
        "alpha": alpha,
        "MAE": mae,
        "RMSE": rmse
    })

    print(
        f"Alpha: {alpha:6} | "
        f"MAE: {mae:.4f} | "
        f"RMSE: {rmse:.4f}"
    )

# Seleccionar mejor alpha según MAE
results_df = pd.DataFrame(results)
best = results_df.loc[results_df["MAE"].idxmin()]

print("\nMEJOR CONFIGURACIÓN")
print(f"Alpha: {best['alpha']}")
print(f"MAE: {best['MAE']:.4f}")
print(f"RMSE: {best['RMSE']:.4f}")

# Guardar resultados de validación
results_df.to_csv(
    OUTPUT_DIR / "baseline_tfidf_validacion.csv",
    index=False
)

with open(
    OUTPUT_DIR / "baseline_tfidf_mejor.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(best.to_dict(), f, indent=4)

print("\nResultados guardados en:", OUTPUT_DIR)
