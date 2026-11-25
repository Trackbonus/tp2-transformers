
import copy
import csv
import math
from datetime import datetime
from pathlib import Path

import torch
import matplotlib.pyplot as plt


# ============================================================
# 1. Configuración general
# ============================================================

SEMILLAS = [42, 123]
PASOS = 1000
BATCH_SIZE = 32
DIMENSION = 8

CONFIGURACIONES = {
    "Adam_lr_0.001": {
        "optimizador": "Adam",
        "lr": 0.001
    },
    "Adam_lr_0.003": {
        "optimizador": "Adam",
        "lr": 0.003
    },
    "SGD_lr_0.05": {
        "optimizador": "SGD",
        "lr": 0.05
    }
}


# ============================================================
# 2. Modelo de atención
# ============================================================

def atencion(X, WQ, WK, WV):
    Q = X @ WQ
    K = X @ WK
    V = X @ WV

    S = (Q @ K.transpose(-2, -1)) / (DIMENSION ** 0.5)
    A = torch.softmax(S, dim=-1)
    H = A @ V

    return H


# ============================================================
# 3. Preparación de datos para cada semilla
# ============================================================

def crear_experimento(semilla):

    torch.manual_seed(semilla)

    # Datos
    X = torch.randn(768, 4, 8)

    # División de datos
    indices = torch.randperm(768)

    indices_train = indices[:512]
    indices_val = indices[512:640]
    indices_test = indices[640:]

    X_train = X[indices_train]
    X_val = X[indices_val]
    X_test = X[indices_test]

    # Pesos del profesor
    WQ_ref = torch.randn(8, 8) / (8 ** 0.5)
    WK_ref = torch.randn(8, 8) / (8 ** 0.5)
    WV_ref = torch.randn(8, 8) / (8 ** 0.5)

    # Resultados del profesor
    with torch.no_grad():
        H_teacher_train = atencion(
            X_train, WQ_ref, WK_ref, WV_ref
        )
        H_teacher_val = atencion(
            X_val, WQ_ref, WK_ref, WV_ref
        )
        H_teacher_test = atencion(
            X_test, WQ_ref, WK_ref, WV_ref
        )

    # Inicialización del estudiante
    WQ_inicial = torch.randn(8, 8) / (8 ** 0.5)
    WK_inicial = torch.randn(8, 8) / (8 ** 0.5)
    WV_inicial = torch.randn(8, 8) / (8 ** 0.5)

    # Minibatches predeterminados para comparar
    generador = torch.Generator().manual_seed(semilla + 10000)

    minibatches = [
        torch.randperm(512, generator=generador)[:BATCH_SIZE]
        for _ in range(PASOS)
    ]

    return {
        "X_train": X_train,
        "X_val": X_val,
        "X_test": X_test,
        "H_train": H_teacher_train,
        "H_val": H_teacher_val,
        "H_test": H_teacher_test,
        "WQ_inicial": WQ_inicial,
        "WK_inicial": WK_inicial,
        "WV_inicial": WV_inicial,
        "minibatches": minibatches
    }


# ============================================================
# 4. Entrenamiento de una configuración
# ============================================================

def entrenar(datos, configuracion):

    # Cada experimento parte de los mismos pesos iniciales
    WQ = datos["WQ_inicial"].clone().requires_grad_(True)
    WK = datos["WK_inicial"].clone().requires_grad_(True)
    WV = datos["WV_inicial"].clone().requires_grad_(True)

    criterio = torch.nn.MSELoss()

    if configuracion["optimizador"] == "Adam":
        optimizador = torch.optim.Adam(
            [WQ, WK, WV],
            lr=configuracion["lr"]
        )
    else:
        optimizador = torch.optim.SGD(
            [WQ, WK, WV],
            lr=configuracion["lr"]
        )

    historial_train = []
    historial_val = []
    historial_gradientes = {
        "WQ": [],
        "WK": [],
        "WV": [],
        "global": []
    }
    pasos_registrados = []

    detenido = False

    for paso in range(PASOS):

        indices = datos["minibatches"][paso]
        X_batch = datos["X_train"][indices]
        H_batch = datos["H_train"][indices]

        optimizador.zero_grad()

        H_pred = atencion(X_batch, WQ, WK, WV)
        perdida = criterio(H_pred, H_batch)

        if not torch.isfinite(perdida):
            detenido = True
            break

        perdida.backward()

        # Norma global del gradiente antes de actualizar los pesos
        norma_WQ = torch.norm(WQ.grad).item()
        norma_WK = torch.norm(WK.grad).item()
        norma_WV = torch.norm(WV.grad).item()

        norma_global = math.sqrt(
            norma_WQ**2 + norma_WK**2 + norma_WV**2
        )

        historial_gradientes["WQ"].append(norma_WQ)
        historial_gradientes["WK"].append(norma_WK)
        historial_gradientes["WV"].append(norma_WV)
        historial_gradientes["global"].append(norma_global)

        optimizador.step()

        # Registrar pérdidas cada 10 pasos
        if (paso + 1) % 10 == 0:

            with torch.no_grad():
                pred_train = atencion(
                    datos["X_train"], WQ, WK, WV
                )
                pred_val = atencion(
                    datos["X_val"], WQ, WK, WV
                )

                loss_train = criterio(
                    pred_train, datos["H_train"]
                ).item()

                loss_val = criterio(
                    pred_val, datos["H_val"]
                ).item()

            historial_train.append(loss_train)
            historial_val.append(loss_val)
            pasos_registrados.append(paso + 1)

    # Evaluación final en entrenamiento y validación
    with torch.no_grad():
        pred_train = atencion(datos["X_train"], WQ, WK, WV)
        pred_val = atencion(datos["X_val"], WQ, WK, WV)

        loss_train_final = criterio(
            pred_train, datos["H_train"]
        ).item()

        loss_val_final = criterio(
            pred_val, datos["H_val"]
        ).item()

    if not math.isfinite(loss_train_final) or not math.isfinite(loss_val_final):
        detenido = True
        loss_train_final = float("inf")
        loss_val_final = float("inf")

    return {
        "train": loss_train_final,
        "val": loss_val_final,
        "historial_train": historial_train,
        "historial_val": historial_val,
        "historial_gradientes": historial_gradientes,
        "pasos": pasos_registrados,
        "WQ": WQ.detach().clone(),
        "WK": WK.detach().clone(),
        "WV": WV.detach().clone(),
        "detenido": detenido
    }


# ============================================================
# 5. Ejecutar los experimentos
# ============================================================

resultados = {}

for semilla in SEMILLAS:

    print(f"\n{'=' * 55}")
    print(f"EXPERIMENTOS CON SEMILLA {semilla}")
    print(f"{'=' * 55}")

    datos = crear_experimento(semilla)

    for nombre, configuracion in CONFIGURACIONES.items():

        print(f"\nEjecutando {nombre}...")

        resultado = entrenar(datos, configuracion)

        resultados[(semilla, nombre)] = resultado

        print(f"Train: {resultado['train']:.6f}")
        print(f"Validación: {resultado['val']:.6f}")
        print(
            f"Pasos ejecutados: "
            f"{len(resultado['historial_gradientes']['global'])}"
        )

        if resultado["detenido"]:
            print("Advertencia: el entrenamiento se detuvo por inestabilidad.")


# ============================================================
# 6. Resumen de resultados
# ============================================================

# ============================================================
# 6. Resumen de resultados
# ============================================================

resumen = []

for nombre in CONFIGURACIONES:

    valores_train = []
    valores_val = []

    for semilla in SEMILLAS:

        resultado = resultados[(semilla, nombre)]

        valores_train.append(resultado["train"])
        valores_val.append(resultado["val"])

        resumen.append({
            "semilla": semilla,
            "configuracion": nombre,
            "train": resultado["train"],
            "validacion": resultado["val"],
            "pasos_ejecutados": len(
                resultado["historial_gradientes"]["global"]
            ),
            "detenido": resultado["detenido"]
        })

    promedio_train = sum(valores_train) / len(valores_train)
    promedio_val = sum(valores_val) / len(valores_val)
    resultados_configuracion = [
        resultados[(semilla, nombre)] for semilla in SEMILLAS
    ]
    promedio_pasos = sum(
        len(resultado["historial_gradientes"]["global"])
        for resultado in resultados_configuracion
    ) / len(resultados_configuracion)
    alguna_detencion = any(
        resultado["detenido"] for resultado in resultados_configuracion
    )

    resumen.append({
        "semilla": "Promedio",
        "configuracion": nombre,
        "train": promedio_train,
        "validacion": promedio_val,
        "pasos_ejecutados": promedio_pasos,
        "detenido": alguna_detencion
    })

    print(f"\n{nombre}")
    print(f"Train promedio: {promedio_train:.6f}")
    print(f"Validación promedio: {promedio_val:.6f}")


# Guardar tabla CSV
with open("../resultados/tabla_optimizadores.csv", "w", newline="") as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=[
            "semilla",
            "configuracion",
            "train",
            "validacion",
            "pasos_ejecutados",
            "detenido"
        ]
    )

    escritor.writeheader()
    escritor.writerows(resumen)


# ============================================================
# 7. Selección de configuración mediante validación
# ============================================================

mejor_configuracion = min(
    [r for r in resumen if r["semilla"] == "Promedio"],
    key=lambda resultado: resultado["validacion"]
)

nombre_mejor = mejor_configuracion["configuracion"]

print("\nCONFIGURACIÓN SELECCIONADA")
print(nombre_mejor)
print(
    f"Validación promedio: "
    f"{mejor_configuracion['validacion']:.6f}"
)


# ============================================================
# 8. Evaluación final en el conjunto de prueba
# ============================================================

criterio = torch.nn.MSELoss()

print("\nEVALUACIÓN FINAL EN TEST")
evidencia_test = []
fecha_ejecucion_test = datetime.now().astimezone().isoformat(
    timespec="seconds"
)
configuracion_seleccionada = CONFIGURACIONES[nombre_mejor]

for semilla in SEMILLAS:

    datos = crear_experimento(semilla)
    resultado = resultados[(semilla, nombre_mejor)]

    with torch.no_grad():
        pred_test = atencion(
            datos["X_test"],
            resultado["WQ"],
            resultado["WK"],
            resultado["WV"]
        )

        loss_test = criterio(
            pred_test, datos["H_test"]
        ).item()

    print(f"Semilla {semilla}: Test = {loss_test:.6f}")
    evidencia_test.append({
        "fecha_ejecucion": fecha_ejecucion_test,
        "configuracion_seleccionada": nombre_mejor,
        "optimizador": configuracion_seleccionada["optimizador"],
        "learning_rate": configuracion_seleccionada["lr"],
        "semilla": semilla,
        "test": loss_test
    })

# Guardar la evaluación final sin reemplazar ejecuciones anteriores
ruta_evidencia_test = (
    Path(__file__).resolve().parent.parent
    / "resultados"
    / "evaluacion_test.csv"
)
archivo_test_existe = ruta_evidencia_test.exists()

with ruta_evidencia_test.open("a", newline="", encoding="utf-8") as archivo:
    escritor = csv.DictWriter(
        archivo,
        fieldnames=[
            "fecha_ejecucion",
            "configuracion_seleccionada",
            "optimizador",
            "learning_rate",
            "semilla",
            "test"
        ]
    )
    if not archivo_test_existe:
        escritor.writeheader()
    escritor.writerows(evidencia_test)


# ============================================================
# 9. Gráfico de pérdidas
# ============================================================

plt.figure(figsize=(10, 6))

for nombre in CONFIGURACIONES:

    for semilla in SEMILLAS:

        resultado = resultados[(semilla, nombre)]

        etiqueta = f"{nombre}, semilla {semilla}"

        plt.plot(
            resultado["pasos"],
            resultado["historial_train"],
            linestyle="--",
            alpha=0.6,
            label=f"Train - {etiqueta}"
        )

        plt.plot(
            resultado["pasos"],
            resultado["historial_val"],
            alpha=0.8,
            label=f"Validación - {etiqueta}"
        )

plt.xlabel("Pasos de entrenamiento")
plt.ylabel("MSE")
plt.title("Comparación de optimizadores y tasas de aprendizaje")
plt.legend(fontsize=7)
plt.grid(True)
plt.tight_layout()
plt.savefig(
    "../resultados/comparacion_perdidas.png",
    dpi=300
)
plt.close()


# ============================================================
# 10. Gráfico de normas de gradientes
# ============================================================

# ============================================================
# 10. Gráfico de normas de gradientes
# ============================================================

fig, ejes = plt.subplots(2, 2, figsize=(12, 8))

componentes = [
    ("WQ", ejes[0, 0]),
    ("WK", ejes[0, 1]),
    ("WV", ejes[1, 0]),
    ("global", ejes[1, 1])
]

for componente, eje in componentes:

    for nombre in CONFIGURACIONES:

        for semilla in SEMILLAS:

            gradientes = resultados[
                (semilla, nombre)
            ]["historial_gradientes"][componente]

            eje.plot(
                range(1, len(gradientes) + 1),
                gradientes,
                label=f"{nombre}, semilla {semilla}",
                alpha=0.8
            )

    eje.set_title(f"Norma del gradiente {componente}")
    eje.set_xlabel("Pasos de entrenamiento")
    eje.set_ylabel("Norma")
    eje.grid(True)
    eje.legend(fontsize=6)

plt.suptitle("Evolución de las normas de los gradientes")
plt.tight_layout()

plt.savefig(
    "../resultados/comparacion_gradientes.png",
    dpi=300
)

plt.close()


print("\nExperimentos terminados.")
print("Archivos guardados en ../resultados/")
