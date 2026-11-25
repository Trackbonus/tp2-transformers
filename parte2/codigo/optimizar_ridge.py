
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "datos"
OUTPUT_DIR = BASE_DIR / "resultados" / "ridge"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar conjuntos
train_df = pd.read_csv(DATA_DIR / "train.csv")
validation_df = pd.read_csv(DATA_DIR / "validation.csv")

X_train = train_df["texto"].fillna("")
y_train = train_df["puntuacion"].astype(float)

X_val = validation_df["texto"].fillna("")
y_val = validation_df["puntuacion"].astype(float)

print("Registros de entrenamiento:", len(train_df))
print("Registros de validación:", len(validation_df))

# TF-IDF: ajustar únicamente con train
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=50000,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_val_tfidf = vectorizer.transform(X_val)

# Hiperparámetros a probar
alphas = [0.01, 0.1, 1, 10, 100]

results = []
best_mae = float("inf")
best_model = None
best_alpha = None

for alpha in alphas:
    print(f"\nEvaluando Ridge alpha={alpha}")

    model = Ridge(alpha=alpha)
    model.fit(X_train_tfidf, y_train)

    predictions = model.predict(X_val_tfidf)

    mae = mean_absolute_error(y_val, predictions)
    rmse = mean_squared_error(y_val, predictions) ** 0.5

    result = {
        "alpha": alpha,
        "mae": mae,
        "rmse": rmse
    }

    results.append(result)

    print(f"MAE:  {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")

    if mae < best_mae:
        best_mae = mae
        best_model = model
        best_alpha = alpha

# Guardar resultados
results_df = pd.DataFrame(results).sort_values("mae")

results_df.to_csv(
    OUTPUT_DIR / "optimizacion_ridge.csv",
    index=False
)

# Guardar mejor modelo y vectorizador
import joblib

joblib.dump(
    best_model,
    OUTPUT_DIR / "mejor_modelo.joblib"
)

joblib.dump(
    vectorizer,
    OUTPUT_DIR / "vectorizador.joblib"
)

print("\n" + "=" * 45)
print("RESULTADOS DE OPTIMIZACIÓN RIDGE")
print("=" * 45)
print(results_df.to_string(index=False))

print("\nMejor alpha:", best_alpha)
print("Mejor MAE:", round(best_mae, 4))
print("Mejor modelo guardado en:", OUTPUT_DIR)
