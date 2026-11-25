
import pandas as pd
import numpy as np

df = pd.read_csv("resultados/comparacion_final/predicciones_test.csv")

# Todos los intervalos desde 0 hasta 100, en grupos de 5 puntos
limites = list(range(0, 101, 5)) + [101]
etiquetas = [
    f"{inicio}-{fin}"
    for inicio, fin in zip(limites[:-1], limites[1:])
]

df["intervalo"] = pd.cut(
    df["puntuacion"],
    bins=limites,
    labels=etiquetas,
    right=False,
    include_lowest=True
)

# Errores con signo: positivo = sobreestimación
df["error_firmado_ridge"] = (
    df["prediccion_ridge"] - df["puntuacion"]
)

df["error_firmado_distilbert"] = (
    df["prediccion_distilbert"] - df["puntuacion"]
)

# Métricas por intervalo
resultados = []

for intervalo in etiquetas:
    grupo = df[df["intervalo"] == intervalo]

    resultados.append({
        "intervalo": intervalo,
        "cantidad": len(grupo),
        "mae_ridge": grupo["error_ridge"].mean() if len(grupo) else np.nan,
        "mae_distilbert": grupo["error_distilbert"].mean() if len(grupo) else np.nan,
        "rmse_ridge": np.sqrt((grupo["error_ridge"] ** 2).mean()) if len(grupo) else np.nan,
        "rmse_distilbert": np.sqrt((grupo["error_distilbert"] ** 2).mean()) if len(grupo) else np.nan,
        "sesgo_ridge": grupo["error_firmado_ridge"].mean() if len(grupo) else np.nan,
        "sesgo_distilbert": grupo["error_firmado_distilbert"].mean() if len(grupo) else np.nan,
        "gana_ridge": (
            grupo["error_ridge"] < grupo["error_distilbert"]
        ).sum(),
        "gana_distilbert": (
            grupo["error_distilbert"] < grupo["error_ridge"]
        ).sum()
    })

resultado = pd.DataFrame(resultados).round(2)

print("\n" + "=" * 110)
print("ANÁLISIS POR INTERVALO DE PUNTUACIÓN REAL (0-100)")
print("=" * 110)
print(resultado.to_string(index=False))

print("\nTotal de reseñas:", len(df))
print("Reseñas clasificadas:", df["intervalo"].notna().sum())

resultado.to_csv(
    "resultados/comparacion_final/analisis_por_intervalo.csv",
    index=False
)

print("\nArchivo guardado: resultados/comparacion_final/analisis_por_intervalo.csv")
