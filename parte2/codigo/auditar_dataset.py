
from pathlib import Path

import pandas as pd

# Rutas
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "datos" / "resenas_metal_archives_2000_final.csv"
OUTPUT_DIR = BASE_DIR / "resultados"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar dataset
df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("AUDITORÍA DEL DATASET")
print("=" * 60)

print(f"\nCantidad de registros: {len(df)}")
print(f"Cantidad de columnas: {len(df.columns)}")
print("\nColumnas:")
print(df.columns.tolist())

# Verificar columnas necesarias
required = ["puntuacion", "banda", "texto"]
missing = [col for col in required if col not in df.columns]

if missing:
    raise ValueError(f"Faltan columnas necesarias: {missing}")

# Convertir puntuación a número
df["puntuacion"] = (
    df["puntuacion"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .str.strip()
)

df["puntuacion"] = pd.to_numeric(df["puntuacion"], errors="coerce")
df["texto"] = df["texto"].fillna("").astype(str).str.strip()
df["banda"] = df["banda"].fillna("").astype(str).str.strip()

# Calidad de datos
print("\n--- Calidad ---")
print(f"Puntuaciones inválidas: {df['puntuacion'].isna().sum()}")
print(f"Textos vacíos: {(df['texto'] == '').sum()}")
print(f"Bandas vacías: {(df['banda'] == '').sum()}")

if "review_url" in df.columns:
    print(f"URLs duplicadas: {df['review_url'].duplicated().sum()}")

print(f"Bandas únicas: {df['banda'].nunique()}")

# Distribución de puntuaciones
print("\n--- Distribución de puntuaciones ---")
print(df["puntuacion"].describe())
print("\nFrecuencia por puntuación:")
print(df["puntuacion"].value_counts().sort_index().to_string())

# Longitud de reseñas
df["longitud_caracteres"] = df["texto"].str.len()
df["longitud_palabras"] = df["texto"].str.split().str.len()

print("\n--- Longitud de reseñas ---")
print(df[["longitud_caracteres", "longitud_palabras"]].describe())

# Guardar auditoría
df.to_csv(OUTPUT_DIR / "dataset_auditado.csv", index=False)

print("\nArchivo guardado en:", OUTPUT_DIR / "dataset_auditado.csv")
print("\nAuditoría terminada.")
