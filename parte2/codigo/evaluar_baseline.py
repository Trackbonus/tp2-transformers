
from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "resultados"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar datos
train = pd.read_csv(DATA_DIR / "train.csv")
val = pd.read_csv(DATA_DIR / "validation.csv")
test = pd.read_csv(DATA_DIR / "test.csv")

# Recuperar mejor hiperparámetro
with open(OUTPUT_DIR / "baseline_tfidf_mejor.json", encoding="utf-8") as f:
    best = json.load(f)

alpha = best["alpha"]

# Unir entrenamiento y validación
train_val = pd.concat([train, val], ignore_index=True)

X_train = train_val["texto"].fillna("")
y_train = train_val["puntuacion"]

X_test = test["texto"].fillna("")
y_test = test["puntuacion"]

# Construir y entrenar modelo
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        ngram_range=(1, 2),
        max_features=50000,
        min_df=2,
        sublinear_tf=True
    )),
    ("regressor", Ridge(alpha=alpha))
])

model.fit(X_train, y_train)

# Evaluación final
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
rmse = mean_squared_error(y_test, predictions) ** 0.5

print("=" * 50)
print("EVALUACIÓN FINAL: TF-IDF + RIDGE")
print("=" * 50)
print(f"Reseñas de entrenamiento: {len(train_val)}")
print(f"Reseñas de prueba: {len(test)}")
print(f"Alpha seleccionado: {alpha}")
print(f"MAE: {mae:.4f}")
print(f"RMSE: {rmse:.4f}")

# Guardar predicciones
predictions_df = pd.DataFrame({
    "banda": test["banda"],
    "puntuacion_real": y_test,
    "puntuacion_predicha": predictions
})

predictions_df.to_csv(
    OUTPUT_DIR / "baseline_tfidf_predicciones.csv",
    index=False
)

# Guardar métricas
metrics = {
    "modelo": "TF-IDF + Ridge",
    "alpha": alpha,
    "MAE": mae,
    "RMSE": rmse,
    "n_entrenamiento": len(train_val),
    "n_prueba": len(test)
}

with open(
    OUTPUT_DIR / "baseline_tfidf_test.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(metrics, f, indent=4)

# Guardar modelo entrenado
joblib.dump(model, OUTPUT_DIR / "baseline_tfidf.joblib")

print("\nResultados guardados en:", OUTPUT_DIR)
