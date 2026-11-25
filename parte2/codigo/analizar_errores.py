
import pandas as pd
import numpy as np

# Cargar predicciones y conjunto de prueba
pred = pd.read_csv("resultados/comparacion_final/predicciones_test.csv")
test = pd.read_csv("datos/test.csv")

# Comprobar que ambos archivos tienen las mismas reseñas y orden
assert len(pred) == len(test), "Los archivos tienen distinta cantidad de filas"
assert (
    pred[["banda", "album", "puntuacion"]].reset_index(drop=True)
    .equals(test[["banda", "album", "puntuacion"]].reset_index(drop=True))
), "El orden o las reseñas no coinciden"

# Incorporar el texto original
pred["texto"] = test["texto"].values

# Calcular diferencias entre modelos
pred["diferencia_error"] = (
    pred["error_ridge"] - pred["error_distilbert"]
)

# Guardar análisis completo
pred.to_csv(
    "resultados/comparacion_final/analisis_errores.csv",
    index=False
)

def mostrar_casos(df, columna_error, titulo, ascendente=False):
    print("\n" + "=" * 90)
    print(titulo)
    print("=" * 90)

    casos = df.sort_values(
        columna_error, ascending=ascendente
    ).head(10)

    for i, (_, fila) in enumerate(casos.iterrows(), 1):
        print(f"\n{i}. {fila['banda']} - {fila['album']}")
        print(f"Real: {fila['puntuacion']}")
        print(
            f"Ridge: {fila['prediccion_ridge']:.2f} "
            f"(error: {fila['error_ridge']:.2f})"
        )
        print(
            f"DistilBERT: {fila['prediccion_distilbert']:.2f} "
            f"(error: {fila['error_distilbert']:.2f})"
        )
        print(f"Reseña: {str(fila['texto'])[:700]}...")
        
# 1. Mayores errores de cada modelo
mostrar_casos(pred, "error_ridge", "10 MAYORES ERRORES - RIDGE")
mostrar_casos(pred, "error_distilbert", "10 MAYORES ERRORES - DISTILBERT")

# 2. Predicciones más exactas de cada modelo
mostrar_casos(pred, "error_ridge", "10 PREDICCIONES MÁS EXACTAS - RIDGE", True)
mostrar_casos(pred, "error_distilbert", "10 PREDICCIONES MÁS EXACTAS - DISTILBERT", True)

# 3. Casos donde DistilBERT supera a Ridge
mostrar_casos(
    pred.sort_values("diferencia_error", ascending=False),
    "diferencia_error",
    "CASOS DONDE DISTILBERT MEJORA MÁS A RIDGE"
)

# 4. Casos donde Ridge supera a DistilBERT
mostrar_casos(
    pred.sort_values("diferencia_error", ascending=True),
    "diferencia_error",
    "CASOS DONDE RIDGE MEJORA MÁS A DISTILBERT"
)

# Resumen
print("\n" + "=" * 90)
print("RESUMEN")
print("=" * 90)
print("DistilBERT gana en:",
      (pred["error_distilbert"] < pred["error_ridge"]).sum(), "reseñas")
print("Ridge gana en:",
      (pred["error_ridge"] < pred["error_distilbert"]).sum(), "reseñas")
print("Empates:",
      (pred["error_ridge"] == pred["error_distilbert"]).sum())
print("\nAnálisis completo guardado en resultados/comparacion_final/")
