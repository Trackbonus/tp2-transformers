
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

# Rutas
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "resultados" / "dataset_auditado.csv"
OUTPUT_DIR = BASE_DIR / "datos"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Cargar dataset
if not DATA_PATH.exists():
    raise FileNotFoundError(f"No se encontró el dataset: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

if "banda" not in df.columns or "puntuacion" not in df.columns:
    raise ValueError("El dataset debe contener las columnas 'banda' y 'puntuacion'.")

if df["banda"].isna().any() or (df["banda"].astype(str).str.strip() == "").any():
    raise ValueError("Existen registros sin banda identificable.")

# Primera separación: 90% desarrollo, 10% prueba
split_1 = GroupShuffleSplit(
    n_splits=1,
    test_size=0.10,
    random_state=42
)

train_val_idx, test_idx = next(
    split_1.split(df, groups=df["banda"])
)

train_val = df.iloc[train_val_idx].copy()
test = df.iloc[test_idx].copy()

# Segunda separación: 80% entrenamiento, 10% validación
split_2 = GroupShuffleSplit(
    n_splits=1,
    test_size=1/9,
    random_state=42
)

train_idx, val_idx = next(
    split_2.split(train_val, groups=train_val["banda"])
)

train = train_val.iloc[train_idx].copy()
val = train_val.iloc[val_idx].copy()

# Verificar que no haya bandas compartidas
train_bands = set(train["banda"])
val_bands = set(val["banda"])
test_bands = set(test["banda"])

assert train_bands.isdisjoint(val_bands)
assert train_bands.isdisjoint(test_bands)
assert val_bands.isdisjoint(test_bands)

# Verificar que no se hayan perdido registros
assert len(train) + len(val) + len(test) == len(df)

# Guardar conjuntos
train.to_csv(OUTPUT_DIR / "train.csv", index=False)
val.to_csv(OUTPUT_DIR / "validation.csv", index=False)
test.to_csv(OUTPUT_DIR / "test.csv", index=False)

# Resumen
print("=" * 60)
print("SEPARACIÓN DEL DATASET")
print("=" * 60)

print(f"\nTotal de reseñas: {len(df)}")

for name, subset in [
    ("Entrenamiento", train),
    ("Validación", val),
    ("Prueba", test)
]:
    print(f"\n{name}:")
    print(f"  Reseñas: {len(subset)} ({len(subset) / len(df) * 100:.2f}%)")
    print(f"  Bandas únicas: {subset['banda'].nunique()}")
    print(f"  Media de puntuación: {subset['puntuacion'].mean():.2f}")

print("\n" + "-" * 60)
print("VERIFICACIONES")
print("-" * 60)
print("Bandas compartidas: ninguna")
print("Registros perdidos: ninguno")
print("Separación reproducible: random_state=42")

print("\nArchivos guardados:")
print(OUTPUT_DIR / "train.csv")
print(OUTPUT_DIR / "validation.csv")
print(OUTPUT_DIR / "test.csv")

print("\nSeparación terminada.")
