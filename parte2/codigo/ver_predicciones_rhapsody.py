
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTADOS_DIR = BASE_DIR / "resultados" / "comparacion_final"

# Buscar archivos que contengan las predicciones ya generadas
archivos = list(RESULTADOS_DIR.rglob("*.csv"))

print("Archivos CSV encontrados:")
for archivo in archivos:
    print("-", archivo.relative_to(BASE_DIR))

# Identificar el archivo que contiene las predicciones finales
# Revisa los archivos encontrados si no se detecta automáticamente.
candidatos = [
    f for f in archivos
    if "predic" in f.name.lower()
    or "test" in f.name.lower()
]

if not candidatos:
    raise FileNotFoundError(
        "No encontré archivos CSV de predicciones en resultados/comparacion_final."
    )

print("\nCSV candidatos:")
for i, archivo in enumerate(candidatos):
    print(f"{i}: {archivo.name}")

# Intentar localizar el archivo con las predicciones de ambos modelos
df = None
archivo_usado = None

for archivo in candidatos:
    temporal = pd.read_csv(archivo)
    columnas = [c.lower() for c in temporal.columns]

    tiene_banda = any("banda" in c for c in columnas)
    tiene_album = any("album" in c for c in columnas)
    tiene_ridge = any("ridge" in c for c in columnas)
    tiene_distilbert = any("distilbert" in c for c in columnas)

    if tiene_banda and tiene_album and tiene_ridge and tiene_distilbert:
        df = temporal
        archivo_usado = archivo
        break

if df is None:
    raise ValueError(
        "No encontré un CSV que contenga banda, álbum y predicciones "
        "de ambos modelos. Revisa los archivos y sus columnas."
    )

print(f"\nArchivo utilizado: {archivo_usado.name}")
print("Columnas:", df.columns.tolist())

# Identificar columnas
def buscar_columna(fragmentos):
    for columna in df.columns:
        nombre = columna.lower()
        if all(fragmento in nombre for fragmento in fragmentos):
            return columna
    return None

col_banda = buscar_columna(["banda"])
col_album = buscar_columna(["album"])
col_real = "puntuacion"

# Buscar columnas de predicción
col_ridge = next(
    (c for c in df.columns
     if "ridge" in c.lower() and "pred" in c.lower()),
    None
)

col_distilbert = next(
    (c for c in df.columns
     if "distilbert" in c.lower() and "pred" in c.lower()),
    None
)

if not all([col_banda, col_album, col_real, col_ridge, col_distilbert]):
    raise ValueError(
        "No pude identificar todas las columnas necesarias. "
        f"Columnas disponibles: {df.columns.tolist()}"
    )

# Filtrar Rhapsody y Rhapsody of Fire
mascara = df[col_banda].astype(str).str.contains(
    r"rhapsody",
    case=False,
    na=False
)

resultado = df.loc[mascara, [
    col_banda,
    col_album,
    col_real,
    col_ridge,
    col_distilbert
]].copy()

if resultado.empty:
    print("\nNo hay reseñas de Rhapsody en este conjunto de test.")
else:
    resultado.rename(columns={
        col_banda: "banda",
        col_album: "album",
        col_real: "puntuacion_real",
        col_ridge: "prediccion_ridge",
        col_distilbert: "prediccion_distilbert"
    }, inplace=True)

    resultado["error_ridge"] = (
        resultado["puntuacion_real"] -
        resultado["prediccion_ridge"]
    ).abs()

    resultado["error_distilbert"] = (
        resultado["puntuacion_real"] -
        resultado["prediccion_distilbert"]
    ).abs()

    resultado = resultado.sort_values(["banda", "album"])

    print("\n" + "=" * 100)
    print("PREDICCIONES PARA RHAPSODY")
    print("=" * 100)

    print(resultado.round(2).to_string(index=False))

    print("\nMAE en estas reseñas:")
    print(f"Ridge:      {resultado['error_ridge'].mean():.2f}")
    print(f"DistilBERT: {resultado['error_distilbert'].mean():.2f}")

    salida = RESULTADOS_DIR / "predicciones_rhapsody.csv"
    resultado.to_csv(salida, index=False)

    print(f"\nArchivo guardado en: {salida}")
