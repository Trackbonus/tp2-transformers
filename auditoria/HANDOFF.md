# Handoff integrado — TP2 Transformers

## 1. Propósito, alcance y método de revisión

El TP2 se organiza en dos partes. La Parte 1 desarrolla atención de una cabeza, derivaciones y experimentos teacher–student con optimizadores. La Parte 2 predice puntuaciones de reseñas musicales de Metal Archives y compara TF-IDF + Ridge con DistilBERT. Este documento reúne el estado técnico y la evidencia para una revisión independiente; no reemplaza el informe escrito de cada parte ni la validación humana requerida.

La revisión final combinó: (a) inspección estática del código, documentos, Compose y Dockerfile desde el host; (b) consultas de solo lectura ejecutadas en el contenedor `auditoria` sobre los datos, resultados y permisos de montaje; y (c) contraste de los CSV/JSON persistidos. No se volvieron a ejecutar entrenamientos ni scripts que regeneren resultados.

Se usan tres niveles de evidencia:

- **Runtime verificado:** observado al consultar servicios/archivos desde Docker durante esta revisión.
- **Inspección estática:** constatado en código, configuración o artefactos sin repetir la ejecución del experimento.
- **Pendiente/no verificable:** no existe evidencia suficiente en esta revisión para afirmar la propiedad.

## 2. Arquitectura Docker utilizada

La configuración real está en `compose.yaml` y `Dockerfile` en la raíz. `docker compose ps` mostró los tres servicios activos (`Up`) y sin puertos publicados.

| Servicio    | Imagen y usuario                 | Recursos configurados | Sistema de archivos, volúmenes y red                                                                                                                                               |
| ----------- | -------------------------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `teoria`    | `tp2-python:3.12`; `10001:10001` | 2 CPU; límite 2 GiB   | `read_only: true` para el filesystem de imagen y `/tmp` temporal; `parte1` montado en `/workspace/parte1` sin `read_only` en el bind (escribible según Compose). Red `teoria_net`. |
| `practica`  | `tp2-python:3.12`; `10001:10001` | 2 CPU; límite 4 GiB   | `parte2` montado en `/workspace/parte2`; Compose no declara `read_only` ni `tmpfs` para este servicio. `gpus: all`. Red `default` de Compose.                                      |
| `auditoria` | `tp2-python:3.12`; `10001:10001` | 2 CPU; límite 2 GiB   | `read_only: true` y `/tmp` temporal; `parte1` y `parte2` montadas como solo lectura; `auditoria` montada con escritura. Red `auditoria_net`.                                       |

**Verificación runtime del servicio auditor:** `docker compose exec auditoria id` informó UID/GID 10001; `python --version` informó Python 3.12.16. Intentos de abrir archivos nuevos dentro de `/workspace/parte1` y `/workspace/parte2` fallaron con `OSError` errno 30 (`Read-only file system`). Los intentos no crearon archivos. La enumeración y lectura de archivos de ambas partes funcionó.

`teoria_net` y `auditoria_net` son redes bridge explícitas. `practica` usa la red `default`; `practica_net` está declarada pero no asignada. No se afirma aislamiento de tráfico, conectividad a Internet ni acceso funcional a GPU: no se ejecutaron pruebas de tráfico ni una prueba de uso de GPU. El Compose no monta la raíz completa del repositorio, home, credenciales ni Docker socket. El contenedor `auditoria` tampoco tiene montados `compose.yaml` ni `Dockerfile`; por eso la configuración se contrastó estáticamente desde el host, no desde ese contenedor.

La imagen parte de `python:3.12-slim-bookworm` y crea el usuario 10001. El Dockerfile instala `torch==2.7.1` desde el índice `cu118`, aunque el comentario lo describe como PyTorch para CPU. No se verificó si CUDA está disponible en runtime. `requirements.txt` contiene dependencias parcialmente sin versión fijada y la imagen base no usa digest; la reconstrucción no garantiza dependencias idénticas a futuro.

## 3. Parte 1 — Atención y optimización

### Actividades y método

Las Actividades 1 y 2 contienen el desarrollo manual de atención, gradientes, actualización y derivada de softmax en `auditoria/desarrollo_actividades_1_2.pdf`. El informe anterior de auditoría registra una revisión de ese PDF y no señala errores aritméticos principales. **En esta revisión final no se pudo volver a extraer ni inspeccionar visualmente el PDF**, por lo que esa conclusión se cita como antecedente y no como una nueva verificación independiente.

Las Actividades 3 y 4 implementan una cabeza de atención teacher–student con `Q=XWQ`, `K=XWK`, `V=XWV`, scores escalados por `√8`, softmax y pérdida MSE. Los datos son sintéticos (`768 × 4 × 8`) con particiones 512/128/128.

- **Actividad 3, `parte1/codigo/actividad3.py`:** semilla 42, Adam con tasa 0.001, batch 32 y 1.000 pasos. Registra curvas de train/validación y al final evalúa los conjuntos; ejecuta un gradient check central con `epsilon=1e-3` para `[0,0]` de WQ, WK y WV.
- **Actividad 4, `parte1/codigo/actividad4.py`:** semillas 42 y 123; compara Adam 0.001, Adam 0.003 y SGD 0.05 durante 1.000 pasos, batch 32. Para cada semilla, las configuraciones comparten pesos iniciales y minibatches precomputados. Selecciona por pérdida MSE media de validation y evalúa después la configuración elegida en test.

### Resultados persistidos

`parte1/resultados/gradient_check.csv` contiene una tanda de tres parámetros. Los errores relativos guardados son WQ 0.0195267 %, WK 0.0430442 % y WV 0.0305261 %. Esos valores se comprobaron leyendo el CSV dentro de `auditoria`; no se volvió a calcular el gradiente.

`parte1/resultados/tabla_optimizadores.csv` contiene las seis corridas y promedios. Las pérdidas MSE medias de validation son:

| Configuración  | MSE media validation |
| -------------- | -------------------: |
| Adam, LR 0.001 |         0.0564954970 |
| Adam, LR 0.003 |         0.0000604765 |
| SGD, LR 0.05   |         0.0156010594 |

La configuración de menor validation registrada es Adam 0.003. `parte1/resultados/evaluacion_test.csv` registra MSE 0.0000845031 para la semilla 42 y 0.0000508340 para la semilla 123 con esa configuración. `actividad3.py` imprime su evaluación final, pero no se encontró un CSV separado que persista su métrica de test.

Archivos relevantes adicionales: `parte1/resultados/curvas_entrenamiento.png`, `comparacion_perdidas.png`, `comparacion_gradientes.png`, `parte1/README.md` y `parte1/PROMPTS.md`.

## 4. Parte 2 — Predicción de puntuaciones de reseñas

### Dataset y partición

El archivo de origen `parte2/datos/resenas_metal_archives_2000_final.csv` contiene 2.000 filas y 11 columnas. `parte2/codigo/auditar_dataset.py` agrega `longitud_caracteres` y `longitud_palabras` antes de guardar `parte2/resultados/dataset_auditado.csv`; por ello, el CSV auditado y los splits contienen **13 columnas**, no 11. Esta diferencia corrige la descripción imprecisa de handoffs anteriores. La variable objetivo es `puntuacion`; las columnas originales incluyen reseña/texto, banda, álbum, autor, fecha y otros identificadores. Hay 1.618 bandas únicas.

En el contenedor `auditoria` se leyeron los CSV actuales: train 1.588, validation 200 y test 212 (suma 2.000); las tres intersecciones de bandas fueron vacías. La unión de `review_url` de los splits coincidió con las 2.000 URL del origen, sin URL duplicadas en la concatenación. En el dataset auditado se contaron cero puntuaciones no numéricas, textos vacíos, bandas vacías y URLs duplicadas. Estos controles fueron ejecutados en esta revisión sobre los archivos persistidos.

`parte2/codigo/dividir_dataset.py` usa `GroupShuffleSplit` en dos etapas con `random_state=42`, agrupando por banda, y contiene aserciones para disjunción y conservación. Esto permite evaluar generalización a bandas no vistas, según la partición actual.

### Modelos y selección

- **Baseline TF-IDF + Ridge:** `parte2/codigo/baseline_tfidf.py` y `optimizar_ridge.py`. TF-IDF se ajusta con train; la búsqueda prueba alpha 0.01, 0.1, 1, 10 y 100. `parte2/resultados/ridge/optimizacion_ridge.csv` registra alpha 0.01 como mejor por MAE de validation (MAE 10.1135800; RMSE 14.5259770).
- **DistilBERT:** `distilbert-base-uncased`, una salida de regresión, truncamiento/padding a 512 tokens, batch size 8; normaliza puntuaciones dividiendo por 100 y calcula MAE/RMSE de vuelta a escala 0–100. `optimizar_distilbert.py` fija semilla 42 y selecciona por menor MAE de validation.

| Experimento     | Learning rate | Épocas | Weight decay | MAE validation | RMSE validation |
| --------------- | ------------: | -----: | -----------: | -------------: | --------------: |
| `lr_3e5`        |          3e-5 |      3 |         0.01 |      9.4469719 |      14.3746120 |
| `baseline`      |          2e-5 |      3 |         0.01 |      9.6983252 |      14.5165558 |
| `epochs4_wd005` |          2e-5 |      4 |         0.05 |      9.7223454 |      14.5779183 |
| `epochs2`       |          2e-5 |      2 |         0.01 |      9.8383322 |      14.5361771 |
| `lr_1e5`        |          1e-5 |      3 |         0.01 |     10.2297850 |      15.0372239 |

La tabla proviene de `parte2/resultados/distilbert/optimizacion_6_experimentos/resultados_optimizacion.csv`; la mejor configuración es `lr_3e5`. El evaluador final carga el modelo optimizado de `distilbert/optimizacion_6_experimentos/mejor_modelo/` y el Ridge guardado en `resultados/ridge/`. `entrenar_distilbert_final.py` crea además un artefacto train+validation en `distilbert/modelo_final_train_val/`, pero `evaluar_modelos_finales.py` no carga ese artefacto.

### Evaluación final

Las métricas se contrastaron en `parte2/resultados/comparacion_final/metricas_comparacion.csv` y `resultados_finales.json`; coinciden a la precisión reportada (las últimas cifras binarias de RMSE pueden diferir mínimamente entre serializaciones).

| Modelo         |   MAE test |  RMSE test |
| -------------- | ---------: | ---------: |
| TF-IDF + Ridge | 10.1357551 | 14.1945100 |
| DistilBERT     |  9.3908163 | 13.5589577 |

El JSON, para 212 reseñas, registra mejoras relativas de DistilBERT de 7.3496140 % en MAE y 4.4774515 % en RMSE. Se revisaron también `comparacion_final/predicciones_test.csv`, `analisis_errores.csv`, `analisis_por_intervalo.csv`, `distribucion_puntuaciones.csv` y los gráficos bajo `comparacion_final/graficos/`. Test ya fue usado en evaluaciones persistidas; no debe usarse para ajustes nuevos.

## 5. Reproducibilidad y comandos

Los comandos siguientes corresponden a scripts presentes y a los `working_dir` de Compose. Ejecutarlos regenera o anexa resultados; no se ejecutaron durante esta revisión salvo los comandos runtime descritos en la sección 7.

Desde PowerShell en la raíz del repositorio:

```powershell
docker compose config
docker compose ps
docker compose exec teoria python --version
docker compose exec practica python --version
docker compose exec auditoria python --version
```

Reproducción de Actividades 3 y 4, desde `teoria` (los scripts usan rutas relativas para resultados):

```powershell
docker compose exec teoria sh -c "cd /workspace/parte1/codigo && python actividad3.py"
docker compose exec teoria sh -c "cd /workspace/parte1/codigo && python actividad4.py"
docker compose exec teoria sh -c "cat /workspace/parte1/resultados/gradient_check.csv"
docker compose exec teoria sh -c "cat /workspace/parte1/resultados/tabla_optimizadores.csv"
docker compose exec teoria sh -c "cat /workspace/parte1/resultados/evaluacion_test.csv"
```

Flujo de Parte 2, dentro de `practica`:

```powershell
docker compose exec practica python /workspace/parte2/codigo/auditar_dataset.py
docker compose exec practica python /workspace/parte2/codigo/dividir_dataset.py
docker compose exec practica python /workspace/parte2/codigo/baseline_tfidf.py
docker compose exec practica python /workspace/parte2/codigo/optimizar_ridge.py
docker compose exec practica python /workspace/parte2/codigo/entrenar_distilbert.py
docker compose exec practica python /workspace/parte2/codigo/optimizar_distilbert.py
docker compose exec practica python /workspace/parte2/codigo/evaluar_modelos_finales.py
docker compose exec practica python /workspace/parte2/codigo/analizar_errores.py
docker compose exec practica python /workspace/parte2/codigo/analizar_por_puntuacion.py
docker compose exec practica python /workspace/parte2/codigo/analizar_distribucion.py
docker compose exec practica python /workspace/parte2/codigo/graficar_resultados.py
```

Para consultar evidencia desde el servicio auditor, que solo tiene lectura en Parte 1/2:

```powershell
docker compose exec auditoria sh -c "cat /workspace/parte1/resultados/gradient_check.csv"
docker compose exec auditoria sh -c "cat /workspace/parte2/resultados/comparacion_final/metricas_comparacion.csv"
docker compose exec auditoria sh -c "cat /workspace/parte2/resultados/comparacion_final/resultados_finales.json"
```

`auditoria` no puede regenerar resultados en los bind mounts de Parte 1/2: se comprobó que los intentos de escritura fallan con EROFS. Para reproducir experimentos sin vulnerar esa restricción, se deben ejecutar únicamente en `teoria` o `practica`, que son los servicios destinados a cada parte, y registrar las salidas. El contenedor auditor no puede leer el Compose/Dockerfile ni usar Docker socket porque esos elementos no están montados; la inspección de configuración corresponde al host. El PDF de Actividades 1–2 está montado bajo `/workspace/auditoria`, pero no se pudo reextraer visualmente en esta revisión. No se deben instalar herramientas ni cambiar los montajes para eludir esa limitación.

## 6. Auditoría, hallazgos y asuntos pendientes

### Verificaciones de esta revisión

- **Runtime en Docker:** los tres servicios aparecieron `Up`; `auditoria` ejecutó Python 3.12.16 e informó UID/GID 10001. Lectura de ambas partes funcionó; intentos de escritura en sus montajes fallaron con `EROFS`.
- **Runtime sobre datos/resultados desde `auditoria`:** conteos y columnas de origen/auditado; calidad del dataset; filas, cobertura por `review_url`, duplicados y disjunción de bandas; lectura de métricas finales y CSV de optimización; lectura de los CSV persistidos de Parte 1.
- **Inspección estática desde host:** scripts, rutas, README de Parte 1, `compose.yaml`, `Dockerfile`, `requirements.txt`, handoffs, informes, registros de prompts y validación humana.
- **No ejecutado:** entrenamientos, optimizaciones, scripts de análisis, construcción de imagen, prueba funcional de GPU, conectividad de red ni auditoría visual nueva del PDF.

### Hallazgos y discrepancias

1. **Esquema del dataset:** handoffs previos describían 11 columnas en el dataset auditado. La fuente tiene 11, pero el CSV auditado y los splits tienen 13 porque `auditar_dataset.py` agrega dos atributos de longitud. Se corrigió aquí esa descripción.
2. **Dockerfile/dependencias:** `HANDOFF_P1.md` describe instalación CPU y solo numpy/matplotlib; la configuración actual usa índice PyTorch `cu118` y `requirements.txt` incluye Pillow, pandas, scikit-learn, transformers, accelerate y joblib, algunas sin pin. El comentario de Dockerfile “para CPU” no concuerda claramente con el índice; la disponibilidad de CUDA no se verificó.
3. **Validación de Parte 1:** `auditoria/VALIDACION_HUMANA.md` conserva una decisión histórica que rechaza la necesidad de justificar las tasas, pero su sección posterior reconoce que el enunciado sí pide justificarlas. La discrepancia fue revisada y aclarada durante la validación humana; no constituye un pendiente vigente. El documento se titula Parte 1 y no contiene validación humana específica de Parte 2.
4. **Parte 1, Actividades 1–2:** el informe auditor anterior documenta una revisión del PDF y de sus cálculos; esta revisión final no pudo reabrirlo. Su contenido y legibilidad requieren confirmación humana o una revisión con visor/extractor disponible.
5. **Informe narrativo de Parte 1:** El informe narrativo que discuta curvas, convergencia/estabilidad y conclusiones está pendiente de elaboración por el estudiante, según el handoff P1.
6. **Reproducibilidad:** imagen base por etiqueta y varias dependencias sin versión exacta; no hay evidencia de tiempos de entrenamiento ni de consumo máximo de GPU/memoria.
7. **Aislamiento:** las asignaciones de redes y montajes se constatan en Compose; solo la denegación de escritura del auditor sobre Parte 1/2 se comprobó runtime en esta sesión. No se probaron tráfico entre servicios ni salida a Internet. UID, RAM/CPU y GPU de los otros servicios se documentan como configuración estática; no se verificaron mediante inspección runtime en esta revisión.
8. **Artefactos de test:** hay evaluaciones de test persistidas; deben tratarse como evaluación ya consumida y no reutilizarse para selección o ajustes adicionales.

## 7. Uso de IA y responsabilidad del estudiante

`parte1/PROMPTS.md` conserva prompts recuperados y señala lagunas del historial, incluidas solicitudes iniciales no recuperadas. `parte2/PROMPTS.md` es una síntesis temática con ejemplos reconstruidos, no transcripciones literales ni exhaustivas. `auditoria/PROMPTS.md` contiene el historial de infraestructura y una sección de instrucciones reconstruidas para la auditoría de Parte 2; esta última no acredita por sí sola que otro agente ejecutara cada comprobación.

Los asistentes apoyaron implementación, depuración, análisis metodológico y documentación según los registros disponibles. Los artefactos y los registros atribuyen las ejecuciones experimentales de Parte 1/2 al estudiante; esta revisión no volvió a entrenar modelos ni regeneró resultados. La validación humana existente es histórica y necesita actualizarse frente a las correcciones de Parte 1 y los resultados de Parte 2; no se presenta aquí como aprobación final del proyecto.
