
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cargar datos
df = pd.read_csv("resultados/comparacion_final/predicciones_test.csv")
intervalos = pd.read_csv(
    "resultados/comparacion_final/analisis_por_intervalo.csv"
)

# Directorio de salida
OUT = "resultados/comparacion_final/graficos"
os.makedirs(OUT, exist_ok=True)

# Configuración general
plt.rcParams.update({
    "figure.figsize": (9, 5),
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.labelsize": 11
})

# --------------------------------------------------
# 1. DISTRIBUCIÓN DE PUNTUACIONES REALES (0-100)
# --------------------------------------------------

plt.figure()
plt.hist(
    df["puntuacion"],
    bins=np.arange(0, 106, 5),
    edgecolor="black"
)
plt.xlabel("Puntuación real")
plt.ylabel("Cantidad de reseñas")
plt.title("Distribución de puntuaciones en el conjunto de test")
plt.xlim(0, 100)
plt.xticks(range(0, 101, 10))
plt.tight_layout()
plt.savefig(f"{OUT}/01_distribucion_puntuaciones.png", dpi=150)
plt.close()

# --------------------------------------------------
# 2. MAE POR INTERVALO
# --------------------------------------------------

x = np.arange(len(intervalos))
width = 0.35

plt.figure()
plt.bar(
    x - width / 2,
    intervalos["mae_ridge"],
    width,
    label="TF-IDF + Ridge"
)
plt.bar(
    x + width / 2,
    intervalos["mae_distilbert"],
    width,
    label="DistilBERT"
)

plt.xticks(x, intervalos["intervalo"], rotation=45)
plt.xlabel("Intervalo de puntuación real")
plt.ylabel("MAE")
plt.title("Error absoluto medio por intervalo")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/02_mae_por_intervalo.png", dpi=150)
plt.close()

# --------------------------------------------------
# 3. SESGO POR INTERVALO
# --------------------------------------------------

plt.figure()
plt.bar(
    x - width / 2,
    intervalos["sesgo_ridge"],
    width,
    label="TF-IDF + Ridge"
)
plt.bar(
    x + width / 2,
    intervalos["sesgo_distilbert"],
    width,
    label="DistilBERT"
)

plt.axhline(0, linestyle="--", linewidth=1)
plt.xticks(x, intervalos["intervalo"], rotation=45)
plt.xlabel("Intervalo de puntuación real")
plt.ylabel("Error medio con signo")
plt.title("Sesgo de predicción por intervalo")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/03_sesgo_por_intervalo.png", dpi=150)
plt.close()

# --------------------------------------------------
# 4. PUNTUACIÓN REAL VS. PREDICCIONES (0-100)
# --------------------------------------------------

plt.figure(figsize=(8, 7))

plt.scatter(
    df["puntuacion"],
    df["prediccion_ridge"],
    alpha=0.65,
    label="TF-IDF + Ridge"
)
plt.scatter(
    df["puntuacion"],
    df["prediccion_distilbert"],
    alpha=0.65,
    label="DistilBERT"
)

plt.plot([0, 100], [0, 100], "--", label="Predicción perfecta")

plt.xlabel("Puntuación real")
plt.ylabel("Puntuación predicha")
plt.title("Puntuaciones reales frente a predicciones")
plt.xlim(0, 100)
plt.ylim(0, 100)
plt.xticks(range(0, 101, 10))
plt.yticks(range(0, 101, 10))
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT}/04_real_vs_predicho.png", dpi=150)
plt.close()

# --------------------------------------------------
# 5. DISTRIBUCIÓN DE ERRORES ABSOLUTOS
# --------------------------------------------------

plt.figure()

plt.boxplot(
    [df["error_ridge"], df["error_distilbert"]],
    tick_labels=["TF-IDF + Ridge", "DistilBERT"],
    showmeans=True
)

plt.ylabel("Error absoluto")
plt.title("Distribución de errores absolutos")
plt.tight_layout()
plt.savefig(f"{OUT}/05_distribucion_errores.png", dpi=150)
plt.close()

print("\nGráficos generados:")
for archivo in sorted(os.listdir(OUT)):
    print(f"- {archivo}")

print(f"\nDirectorio: {OUT}")
