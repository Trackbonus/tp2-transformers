# Parte 1: actividades 3 y 4

Este README describe la configuración que implementan los scripts, cómo ejecutarlos en el servicio Docker `teoria` y qué evidencia dejan en `resultados/`. Los comandos se ejecutan desde la raíz del repositorio, salvo que se indique otra ruta.

## Entorno

`teoria` se construye con el `Dockerfile` de la raíz, usa Python 3.12 sobre `python:3.12-slim-bookworm`, instala PyTorch para CPU y las dependencias del `requirements.txt` de la raíz (`numpy` y `matplotlib`). No existe un `parte1/requirements.txt`. Las versiones de paquetes y la etiqueta de la imagen base no están fijadas a versiones exactas; por ello, los comandos reproducen el flujo configurado, pero no garantizan una instalación idéntica en el tiempo.

El servicio monta esta carpeta en `/workspace/parte1` y arranca inactivo con `sleep infinity`. Los scripts guardan gráficos y la tabla principal mediante rutas relativas a su directorio actual; ejecútalos desde `/workspace/parte1/codigo` para que esas rutas apunten a `/workspace/parte1/resultados`.

## Configuración experimental

Ambas actividades usan atención de una cabeza implementada explícitamente. Cada entrada tiene forma `4 × 8`; `WQ`, `WK` y `WV` tienen forma `8 × 8`. Se calculan `Q = XWQ`, `K = XWK`, `V = XWV`, scores `QKᵀ/√8`, softmax sobre la dimensión de posiciones clave y salida `AV`. Los objetivos son salidas de un modelo teacher con la misma operación y pesos de referencia aleatorios. La función de pérdida de entrenamiento y evaluación es MSE.

| Parámetro | Actividad 3 (`actividad3.py`) | Actividad 4 (`actividad4.py`) |
|---|---|---|
| Datos | `torch.randn(768, 4, 8)` | `torch.randn(768, 4, 8)` por semilla |
| Semilla | `42` | `42` y `123` |
| Partición aleatoria | 512 train, 128 validación, 128 test | 512 train, 128 validación, 128 test |
| Optimizador | Adam, tasa `0.001` | Adam `0.001`, Adam `0.003`, SGD `0.05` |
| Pasos y batch | 1000 pasos, batch 32 | 1000 pasos, batch 32 |
| Minibatches | Muestreados aleatoriamente desde train durante el ciclo | Precomputados por semilla con generador `semilla + 10000`; iguales entre configuraciones de una semilla |
| Evaluación | Pérdidas train/validación cada 10 pasos; evaluación final en train, validación y test | Pérdidas train/validación cada 10 pasos y al final; test solo después de seleccionar la configuración |

En Actividad 4, cada configuración parte de los mismos pesos iniciales dentro de una semilla. La selección se hace por menor pérdida promedio de validación entre las dos semillas; después se evalúa en test la configuración seleccionada para cada semilla. El `tabla_optimizadores.csv` disponible registra `Adam_lr_0.003` como la de menor validación promedio.

En Actividad 3, el gradient check se ejecuta después del entrenamiento sobre los primeros 32 ejemplos de train. Compara autograd con diferencias finitas centrales para el peso `[0, 0]` de `WQ`, `WK` y `WV`, con epsilon `1e-3`. El error relativo se deja sin definir cuando la magnitud del gradiente analítico es `≤ 1e-12`; el error absoluto siempre se conserva.

## Construir y ejecutar

Desde la raíz del repositorio, con Docker Desktop y Compose v2 disponibles:

```powershell
docker compose build teoria
docker compose up -d teoria
docker compose ps teoria
docker compose exec teoria python --version
docker compose exec teoria python -c "import torch, matplotlib; print('torch', torch.__version__); print('matplotlib', matplotlib.__version__)"
docker compose exec teoria sh -c "cd /workspace/parte1/codigo && python actividad3.py"
docker compose exec teoria sh -c "cd /workspace/parte1/codigo && python actividad4.py"
```

La imagen instala PyTorch para CPU; no se requiere GPU. Comprueba que Docker Desktop permita escritura en el montaje `parte1/`, porque los scripts generan y actualizan archivos allí.

Para consultar los archivos dentro del contenedor:

```powershell
docker compose exec teoria ls -lh /workspace/parte1/resultados
docker compose exec teoria sh -c "cat /workspace/parte1/resultados/tabla_optimizadores.csv"
docker compose exec teoria sh -c "cat /workspace/parte1/resultados/gradient_check.csv"
docker compose exec teoria sh -c "cat /workspace/parte1/resultados/evaluacion_test.csv"
```

También se pueden consultar directamente desde el anfitrión en `parte1/resultados/`. La carpeta está montada desde el proyecto.

> **Efecto de volver a ejecutar:** Actividad 3 reemplaza `curvas_entrenamiento.png` y añade tres filas a `gradient_check.csv`. Actividad 4 reemplaza `tabla_optimizadores.csv`, `comparacion_perdidas.png` y `comparacion_gradientes.png`, y añade dos filas a `evaluacion_test.csv`. Copia los archivos que quieras conservar antes de repetir una actividad.

## Resultados y evidencia disponible

| Archivo | Producido por | Contenido |
|---|---|---|
| `resultados/curvas_entrenamiento.png` | Actividad 3, una ejecución con semilla 42 | Pérdida MSE de train y validación a lo largo de los pasos registrados (cada 10 pasos) |
| `resultados/gradient_check.csv` | Actividad 3, al terminar gradient check | Autograd, diferencias finitas centrales, error absoluto y error relativo porcentual de WQ/WK/WV; incluye fecha y estado del error relativo |
| `resultados/tabla_optimizadores.csv` | Actividad 4, las seis corridas (tres configuraciones por dos semillas) | MSE final de train y validación, pasos ejecutados y detención; incluye filas promedio por configuración |
| `resultados/evaluacion_test.csv` | Actividad 4, una vez seleccionada la configuración por validación | MSE de test por semilla, configuración seleccionada, optimizador, tasa y fecha de ejecución |
| `resultados/comparacion_perdidas.png` | Actividad 4, seis corridas | Curvas de train y validación para cada configuración y semilla |
| `resultados/comparacion_gradientes.png` | Actividad 4, seis corridas | Normas de los gradientes de WQ, WK, WV y la norma global a lo largo de los pasos |

Los CSV presentes corresponden a una ejecución guardada en `gradient_check.csv` y una evaluación de test de las semillas 42 y 123 en `evaluacion_test.csv`; `tabla_optimizadores.csv` contiene los registros y promedios de las seis corridas. Los PNG y CSV son los archivos que existen actualmente en `resultados/`; una nueva ejecución actualizará o anexará según se describe arriba.
