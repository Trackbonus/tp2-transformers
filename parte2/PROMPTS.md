# Uso de ChatGPT durante el desarrollo de la Parte 2

## Introducción

ChatGPT se utilizó como asistente en distintas etapas del desarrollo de la Parte 2, mediante numerosas interacciones iterativas. Debido al volumen del trabajo y a que no se conserva una transcripción completa de todas las conversaciones, este documento sintetiza las principales tareas. Los ejemplos incluidos son **reconstrucciones representativas**: no son transcripciones literales ni exhaustivas y no deben interpretarse como prompts originales.

## Interacciones por etapa

### A. Preparación y auditoría del dataset

Se trabajó en consolidar las reseñas de Metal Archives y revisar columnas, puntuaciones, textos vacíos, duplicados y consistencia. El dataset auditado contiene 2.000 registros.

**Ejemplos representativos reconstruidos (no literales):**

- «Ayúdame a revisar la calidad del CSV de reseñas: columnas, puntuaciones, textos vacíos, duplicados y consistencia; documenta los controles y conserva los registros válidos.»
- «Prepara una salida auditada de 2.000 reseñas e identifica los problemas de calidad sin asumir resultados que no estén en los datos.»

### B. División de datos

Se diseñó una partición de train, validation y test agrupando por banda con `GroupShuffleSplit` y semilla 42. El agrupamiento busca evitar que reseñas de una misma banda aparezcan en distintos conjuntos y reducir la fuga de información entre particiones.

**Ejemplo representativo reconstruido (no literal):**

- «Propón una división reproducible de train, validation y test agrupada por banda; verifica que se conserven los registros y que no haya bandas compartidas.»

Resultado documentado: train 1.588, validation 200 y test 212 registros.

### C. Modelo baseline

Se implementó TF-IDF + Ridge como referencia tradicional. Se probaron valores de `alpha` y se evaluaron con MAE y RMSE.

**Ejemplo representativo reconstruido (no literal):**

- «Implementa un baseline de regresión con TF-IDF y Ridge; compara distintos valores de alpha en validation y calcula MAE y RMSE.»

### D. Modelo Transformer

Se implementó fine-tuning de `distilbert-base-uncased` para regresión. El flujo incluye normalización de puntuaciones, tokenización con longitud máxima de 512 tokens y entrenamiento con batch size 8. La evaluación usa MAE y RMSE en la escala original de puntuaciones.

**Ejemplo representativo reconstruido (no literal):**

- «Adapta DistilBERT para predecir puntuaciones como una variable de regresión; normaliza las etiquetas para entrenar y vuelve a la escala original al calcular MAE y RMSE.»

### E. Optimización

Se optimizó Ridge probando distintos valores de `alpha` y se compararon cinco configuraciones de DistilBERT. La selección de hiperparámetros se realizó con validation. Los artefactos registran como mejores Ridge con `alpha=0.01` y DistilBERT con learning rate `3e-5`, 3 épocas, batch size 8 y weight decay 0.01.

**Ejemplos representativos reconstruidos (no literales):**

- «Compara los valores de alpha para Ridge con MAE y RMSE en validation y conserva la configuración con menor MAE.»
- «Evalúa cinco configuraciones de DistilBERT en validation y selecciona la de menor MAE, sin usar test para ajustar hiperparámetros.»

### F. Evaluación final

Los modelos seleccionados se evaluaron sobre test y se compararon mediante MAE y RMSE. También se trabajó en el análisis de errores y la generación de gráficos.

| Modelo | MAE | RMSE |
|---|---:|---:|
| TF-IDF + Ridge | 10.1358 | 14.1945 |
| DistilBERT | 9.3908 | 13.5590 |

**Ejemplos representativos reconstruidos (no literales):**

- «Evalúa una vez en test los modelos seleccionados con validation; compara MAE y RMSE y guarda las predicciones y métricas.»
- «Analiza los errores por grupos de puntuación y genera gráficos que ayuden a interpretar la comparación, distinguiendo resultados calculados de interpretaciones.»

Las cifras se contrastaron con `parte2/resultados/comparacion_final/metricas_comparacion.csv` y `resultados_finales.json`.

## Aporte de ChatGPT y responsabilidad del estudiante

ChatGPT apoyó la implementación, depuración, interpretación de resultados y revisión metodológica durante el proceso iterativo. El estudiante ejecutó los experimentos en el entorno Docker, revisó sus resultados y tomó las decisiones finales. Por ello, las ejecuciones y verificaciones locales se atribuyen al estudiante; este registro no presenta los prompts reconstruidos como conversaciones originales ni atribuye a ChatGPT acciones realizadas localmente.
