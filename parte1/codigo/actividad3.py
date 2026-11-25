import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import torch

# Semilla para reproducibilidad
torch.manual_seed(42)

# Generación de 768 ejemplos de dimensión 4x8
X = torch.randn(768, 4, 8)

# Separación de los conjuntos
indices = torch.randperm(768)

X_train = X[indices[:512]]
X_val = X[indices[512:640]]
X_test = X[indices[640:768]]

# Comprobación de dimensiones
print("Entrenamiento:", X_train.shape)
print("Validación:", X_val.shape)
print("Prueba:", X_test.shape)

# Matrices de referencia del modelo teacher
WQ_ref = torch.randn(8, 8) / (8 ** 0.5)
WK_ref = torch.randn(8, 8) / (8 ** 0.5)
WV_ref = torch.randn(8, 8) / (8 ** 0.5)

# Cabeza de atención: calcula Q, K, V, S, A y H
def atencion(X, WQ, WK, WV):

    Q = X @ WQ
    K = X @ WK
    V = X @ WV

    S = (Q @ K.transpose(-2, -1)) / (8 ** 0.5)

    A = torch.softmax(S, dim=-1)

    H = A @ V

    return H

# Generación de las salidas objetivo del teacher
with torch.no_grad():

    H_teacher_train = atencion(X_train, WQ_ref, WK_ref, WV_ref)
    H_teacher_val = atencion(X_val, WQ_ref, WK_ref, WV_ref)
    H_teacher_test = atencion(X_test, WQ_ref, WK_ref, WV_ref)

# Comprobación de dimensiones
print("Salida entrenamiento:", H_teacher_train.shape)
print("Salida validación:", H_teacher_val.shape)
print("Salida prueba:", H_teacher_test.shape)

# Matrices iniciales del modelo student
WQ = (torch.randn(8, 8) / (8 ** 0.5)).requires_grad_(True)
WK = (torch.randn(8, 8) / (8 ** 0.5)).requires_grad_(True)
WV = (torch.randn(8, 8) / (8 ** 0.5)).requires_grad_(True)

# Guardar copias de los pesos iniciales
WQ_inicial = WQ.detach().clone()
WK_inicial = WK.detach().clone()
WV_inicial = WV.detach().clone()

# Comprobar que las matrices del student son distintas del teacher
print("¿WQ es diferente?", not torch.equal(WQ, WQ_ref))
print("¿WK es diferente?", not torch.equal(WK, WK_ref))
print("¿WV es diferente?", not torch.equal(WV, WV_ref))

# Predicciones iniciales del modelo student
H_student_train = atencion(X_train, WQ, WK, WV)
H_student_val = atencion(X_val, WQ, WK, WV)

print("Predicción student entrenamiento:", H_student_train.shape)
print("Predicción student validación:", H_student_val.shape)

# Error inicial del student respecto del teacher
error_inicial = torch.mean((H_student_train - H_teacher_train) ** 2)

print("Error inicial de entrenamiento:", error_inicial.item())

# Configuración del entrenamiento
learning_rate = 0.001
batch_size = 32
num_steps = 1000

# Función de pérdida
criterio = torch.nn.MSELoss()

# Optimizador
optimizador = torch.optim.Adam(
    [WQ, WK, WV],
    lr=learning_rate
)

# Historial de pérdidas
historial_train = []
historial_val = []
pasos = []


# Ciclo de entrenamiento
for paso in range(num_steps):

    # Seleccionar un minibatch aleatorio
    indices = torch.randperm(X_train.shape[0])[:batch_size]
    X_batch = X_train[indices]
    H_objetivo = H_teacher_train[indices]

    # 1. Calcular predicciones del student
    H_predicho = atencion(X_batch, WQ, WK, WV)

    # 2. Calcular la pérdida
    perdida = criterio(H_predicho, H_objetivo)

    # 3. Calcular gradientes
    optimizador.zero_grad()
    perdida.backward()

    # 4. Actualizar los pesos
    optimizador.step()

    # Evaluar cada 10 pasos
    if (paso + 1) % 10 == 0:

        with torch.no_grad():
            pred_train = atencion(X_train, WQ, WK, WV)
            pred_val = atencion(X_val, WQ, WK, WV)

            loss_train = criterio(pred_train, H_teacher_train)
            loss_val = criterio(pred_val, H_teacher_val)

        historial_train.append(loss_train.item())
        historial_val.append(loss_val.item())
        pasos.append(paso + 1)

    # Mostrar progreso cada 100 pasos
    if (paso + 1) % 100 == 0:
        print(f"Paso {paso + 1}, pérdida: {perdida.item():.6f}")


# Evaluación del student en los conjuntos de datos
with torch.no_grad():
    H_student_train = atencion(X_train, WQ, WK, WV)
    H_student_val = atencion(X_val, WQ, WK, WV)
    H_student_test = atencion(X_test, WQ, WK, WV)

    perdida_train = criterio(H_student_train, H_teacher_train)
    perdida_val = criterio(H_student_val, H_teacher_val)
    perdida_test = criterio(H_student_test, H_teacher_test)

print("\nPérdidas finales:")
print(f"Entrenamiento: {perdida_train.item():.6f}")
print(f"Validación:    {perdida_val.item():.6f}")
print(f"Prueba:        {perdida_test.item():.6f}")

# Comprobar cuánto cambiaron los pesos
print("\nCambios en los pesos:")
print("WQ:", torch.norm(WQ - WQ_inicial).item())
print("WK:", torch.norm(WK - WK_inicial).item())
print("WV:", torch.norm(WV - WV_inicial).item())

# Gráfico de las curvas de entrenamiento y validación
plt.figure(figsize=(10, 5))

plt.plot(pasos, historial_train, label="Entrenamiento")
plt.plot(pasos, historial_val, label="Validación")

plt.xlabel("Pasos de entrenamiento")
plt.ylabel("MSE")
plt.title("Evolución de la pérdida")
plt.legend()
plt.grid(True)

plt.savefig("../resultados/curvas_entrenamiento.png", dpi=300)
plt.show()


# Verificación de gradientes mediante diferencias finitas

epsilon = 1e-3

# Usar un minibatch fijo para todas las evaluaciones
X_grad = X_train[:32]
H_grad = H_teacher_train[:32]

# Calcular gradientes mediante autograd
optimizador.zero_grad()

H_pred = atencion(X_grad, WQ, WK, WV)
loss = criterio(H_pred, H_grad)

loss.backward()

# Guardar los gradientes analíticos
grad_WQ = WQ.grad[0, 0].item()
grad_WK = WK.grad[0, 0].item()
grad_WV = WV.grad[0, 0].item()

print("\nGradientes mediante autograd:")
print("WQ:", grad_WQ)
print("WK:", grad_WK)
print("WV:", grad_WV)

# Calcular gradientes mediante diferencias finitas centrales

def diferencia_finita(matriz, fila, columna):
    with torch.no_grad():

        # Guardar el valor original
        valor_original = matriz[fila, columna].item()

        # Evaluar L(w + epsilon)
        matriz[fila, columna] = valor_original + epsilon
        perdida_mas = criterio(
            atencion(X_grad, WQ, WK, WV), H_grad
        ).item()

        # Evaluar L(w - epsilon)
        matriz[fila, columna] = valor_original - epsilon
        perdida_menos = criterio(
            atencion(X_grad, WQ, WK, WV), H_grad
        ).item()

        # Restaurar el valor original
        matriz[fila, columna] = valor_original

    return (perdida_mas - perdida_menos) / (2 * epsilon)


grad_WQ_fd = diferencia_finita(WQ, 0, 0)
grad_WK_fd = diferencia_finita(WK, 0, 0)
grad_WV_fd = diferencia_finita(WV, 0, 0)

print("\nGradientes mediante diferencias finitas:")
print("WQ:", grad_WQ_fd)
print("WK:", grad_WK_fd)
print("WV:", grad_WV_fd)

# Comparación de gradientes y errores

print("\nComparación de gradientes:")

umbral_gradiente_relativo = 1e-12
evidencia_gradientes = []

for nombre, grad_auto, grad_fd in [
    ("WQ", grad_WQ, grad_WQ_fd),
    ("WK", grad_WK, grad_WK_fd),
    ("WV", grad_WV, grad_WV_fd)
]:
    error_abs = abs(grad_auto - grad_fd)
    error_rel = None

    print(f"{nombre}:")
    print(f"  Error absoluto: {error_abs:.10f}")
    if abs(grad_auto) <= umbral_gradiente_relativo:
        estado_error_relativo = "no definido"
        print(
            "  Error relativo: no definido "
            f"(|gradiente analítico| <= {umbral_gradiente_relativo:g})"
        )
    else:
        error_rel = error_abs / abs(grad_auto)
        estado_error_relativo = "calculado"
        print(f"  Error relativo: {error_rel * 100:.6f}%")

    evidencia_gradientes.append({
        "parametro": nombre,
        "gradiente_autograd": grad_auto,
        "gradiente_diferencias_finitas": grad_fd,
        "error_absoluto": error_abs,
        "error_relativo_porcentaje": (
            "" if error_rel is None else error_rel * 100
        ),
        "estado_error_relativo": estado_error_relativo
    })

# Guardar la evidencia calculada sin reemplazar ejecuciones anteriores
ruta_evidencia = (
    Path(__file__).resolve().parent.parent
    / "resultados"
    / "gradient_check.csv"
)
archivo_existe = ruta_evidencia.exists()

with ruta_evidencia.open("a", newline="", encoding="utf-8") as archivo:
    escritor = csv.DictWriter(
        archivo,
        fieldnames=[
            "fecha_ejecucion",
            "parametro",
            "gradiente_autograd",
            "gradiente_diferencias_finitas",
            "error_absoluto",
            "error_relativo_porcentaje",
            "estado_error_relativo"
        ]
    )
    if not archivo_existe:
        escritor.writeheader()
    fecha_ejecucion = datetime.now().astimezone().isoformat(timespec="seconds")
    for fila in evidencia_gradientes:
        escritor.writerow({"fecha_ejecucion": fecha_ejecucion, **fila})
