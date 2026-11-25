# VALIDACIÓN HUMANA – PARTE 1

## 1. Resumen general

La revisión siguió el mismo orden y estructura del informe de auditoría. Se analizaron los hallazgos positivos, los problemas detectados, las discrepancias, las recomendaciones y la evaluación final. También se revisaron las observaciones específicas del anexo correspondiente a las actividades 1 y 2.

Las observaciones se clasificaron como aceptadas o rechazadas, según su validez y su correspondencia con los requisitos del trabajo.

## 2. Archivos y evidencias revisadas

El informe del agente auditor identificó los siguientes archivos y evidencias como parte de su revisión:

- `auditoria/desarrollo_actividades_1_2.pdf`
- `actividad3.py`
- `actividad4.py`
- `tabla_optimizadores.csv`
- `curvas_entrenamiento.png`
- `comparacion_perdidas.png`
- `comparacion_gradientes.png`
- `parte1/PROMPTS.md`
- `enunciado/enunciado.txt`

## 3. Hallazgos correctos

**Decisión: Aceptados.**

Se aceptan los hallazgos positivos identificados por el agente auditor, ya que son hechos, no hay razón alguna para rechazarlos.

- Atención y dimensiones
- Síntesis y partición
- Entrenamiento de actividad 3
- Comparación controlada de actividad 4
- Métricas respaldadas
- Normas de gradiente
- Uso de test en actividad 4

## 4. Errores o problemas detectados

### 4.1. Predicción sobre el conjunto de test antes del entrenamiento

**Decisión: Aceptada.**

La Actividad 3 realiza una predicción sobre X_test antes de entrenar el modelo estudiante. Aunque esta predicción no se utiliza para actualizar los pesos ni para seleccionar el modelo, es una operación innecesaria dentro del experimento.

### 4.2. Posible división por cero en el error relativo del gradient check

**Decisión: Aceptada.**

El cálculo del error relativo utiliza el valor absoluto del gradiente analítico como denominador. Si este valor es cero o muy cercano a cero, el cálculo puede producir resultados indefinidos. No afectó a los resultados pero si es un problema porque es algo que podría ocurrir.

### 4.3. Ausencia de resultados persistidos del gradient check

**Decisión: Aceptada.**

Al momento de la auditoría, esta parte de la documentación todavía estaba pendiente.

### 4.4. Ausencia del informe narrativo y las conclusiones de Parte 1

**Decisión: Aceptada.**

Igual que la anterior. al momento de realizarse la auditoría, el informe narrativo de Parte 1 todavía no había comenzado a elaborarse.

### 4.5. Resultados de test de Actividad 4 no guardados en un archivo

**Decisión: Aceptada.**

Los resultados del test fueron calculados después de seleccionar la configuración mediante los resultados de validación, pero todavía faltaba guardarlos como evidencia permanente.

### 4.6. Registro incorrecto de los pasos y la detención anticipada en el resumen de promedios

**Decisión: Aceptada.**

El resumen de promedios asigna un presupuesto fijo de 1000 pasos y registra detenido=False, independientemente del resultado real de cada ejecución.
Sin embargo, este problema no afectó los resultados actuales, ya que las seis ejecuciones completaron los 1000 pasos sin detención anticipada. Pero se acepta la observación porque el registro podría ser incorrecto si en futuras ejecuciones se produjera una detención anticipada.

### 4.7. Ausencia de justificación para las tasas de aprendizaje

**Decisión: Rechazada.**

Se rechaza la observación porque el enunciado solicita experimentar con diferentes tasas de aprendizaje, pero no exige justificar la elección de cada valor ni establecer un procedimiento riguroso para seleccionarlos. Con seleccionar distintas configuraciones ya se cumple con lo establecido.

## 5. Discrepancias y aspectos que requieren validación humana

### 5.1. Desarrollos matemáticos de las actividades 1 y 2

**Decisión: Aceptada y verificada.**

Se revisaron los desarrollos matemáticos de ambas actividades. Los cálculos principales fueron comprobados y no se identificaron errores.

### 5.2. Resultados numéricos del gradient check no verificables independientemente

**Decisión: Aceptada.**

El auditor no pudo verificar independientemente los valores del gradient check porque no existía un archivo o registro con esos resultados. Se acepta porque esta parte de la documentación todavía estaba pendiente al momento de la auditoría.

### 5.3. Procedencia y reproducibilidad de las imágenes

**Decisión: Rechazada.**

El auditor señala que no pudo verificar completamente la procedencia de las imágenes mediante registros de ejecución, hashes y otros elementos adicionales.Se rechaza esta discrepancia en cuanto plantea esos elementos como requisitos, porque no todos están exigidos expresamente por el enunciado.

Las imágenes fueron generadas por el código desarrollado y cumplen la función solicitada. La falta de hashes o registros adicionales no constituye evidencia de que las imágenes sean incorrectas.

No obstante, se reconoce que el enunciado sí exige entregar código, configuración, registros y resultados reproducibles. Estos requisitos se consideran pendientes de completar.

### 5.4. Conclusiones no verificables por ausencia del informe narrativo

**Decisión: Aceptada.**

Al momento de la auditoría, el informe de la parte 1 todavía no estaba elaborado, por lo que no existían conclusiones que pudieran ser verificadas.

### 5.5. Validación humana incompleta

**Decisión: Rechazada.**

Se rechaza la observación como incumplimiento debido a que no tiene sentido estabelcerla como inclumplimiento. La validación humana de la parte 1 es precisamente el procedimiento solicitado por la actividad 5 y debe realizarse después de la auditoría.

### 5.6. Archivo parte1/PROMPTS.md incompleto

**Decisión: Aceptada.**

Se acepta la observación porque el enunciado exige explícitamente registrar los prompts enviados a los agentes, algo que aún está pendiente de registrar.

## 6. Recomendaciones

### 6.1. Validar manualmente los desarrollos de las actividades 1 y 2

**Decisión: Aceptada y cumplida.**

Los desarrollos matemáticos fueron revisados y sus cálculos fueron verificados.

### 6.2. Elaborar el informe narrativo de Parte 1

**Decisión: Aceptada.**

Como ya se comentó, es algo que está pendiente.

### 6.3. Persistir los resultados del gradient check

**Decisión: Aceptada.**

Se guardarán en un archivo los resultados de autograd y diferencias finitas centrales.

### 6.4. Persistir los resultados de test de Actividad 4

**Decisión: Aceptada.**

Se guardarán los resultados de test obtenidos para las configuraciones seleccionadas para que queden disponibles como evidencia.

### 6.5. Corregir los detalles de implementación identificados

**Decisión: Aceptada.**

Se acepta esta recomendación, los tres aspectos ya fueron evaluados y aceptados previamente durante la validación humana y
quedan pendientes de implementación.

### 6.6. Agregar instrucciones y evidencias de reproducibilidad

**Decisión: Aceptada**

Se acepta la recomendación ya que son requisitos explícitos del enunciado. Por lo tanto, se reconoce que estos elementos deben incorporarse a la entrega y quedan pendientes.

## 7. Evaluación final del cumplimiento

**Decisión: Aceptada.**

Se acepta la evaluación final del auditor, que considera que la parte 1 presenta un cumplimiento parcial.

La implementación y los experimentos realizados presentan resultados favorables, y los desarrollos matemáticos de las actividades 1 y 2 fueron verificados sin encontrar errores. Sin embargo, como ya vimos, todavía existen entregables y evidencias pendientes.

## 8. Anexo: revisión del PDF de actividades 1 y 2

### 8.1. Actividad 1: notación de \(H_1\)

**Decisión: Aceptada.**

Se acepta la observación de que la notación \(H_1\) puede resultar ambigua al utilizarse con significados diferentes en ambas actividades. Se considera conveniente aclarar esta diferencia para evitar confusiones.

### 8.2. Actividad 1: explicación del orden y la información posicional

**Decisión: Rechazada.**

Se rechaza la observación. La frase utilizada en el documento, "el orden 123 no será lo mismo que 321", comunica adecuadamente que el orden de los elementos influye en su interpretación, no requiere modificaciones para cumplir el objetivo del ejercicio.

### 8.3. Actividad 2: notación de la derivación del gradiente

**Decisión: Rechazada.**

Se rechaza la observación sobre el uso de una abreviatura informal en la derivación de \(\partial L/\partial H=H-T\). El resultado obtenido es correcto y el enunciado no exige una notación específica para desarrollar esta derivación.

### 8.4. Actividad 2: cálculo manual del gradiente y actualización

**Decisión: Aceptada y verificada.**

El auditor verificó los cálculos manuales utilizando las matrices indicadas en el documento. No se encontraron errores.

### 8.5. Actividad 2: demostración de la derivada del softmax

**Decisión: Aceptada y verificada.**

Se confirma que la demostración es correcta y distingue adecuadamente los casos correspondientes.

---

## 9. Segunda etapa: estado posterior a las correcciones y ejecuciones

Esta sección complementa el registro anterior, no reemplaza ni altera sus decisiones iniciales.

### 9.1. Hallazgo 4.1: predicción previa sobre X_test

- **Observación inicial:** actividad3.py predecía con el modelo estudiante sobre X_test antes del entrenamiento.
- **Decisión inicial:** aceptada, la predicción no se utilizaba para actualizar pesos ni seleccionar el modelo, pero era acceso innecesario al conjunto de prueba.
- **Corrección:** Se eliminó esa predicción previa y su impresión en actividad 3.

### 9.2. Hallazgo 4.2: error relativo con gradientes pequeños

- **Observación inicial:** el error relativo dividía por la magnitud del gradiente analítico sin proteger el caso cero o cercano a cero.
- **Decisión inicial:** aceptada.
- **Corrección:** Se añadió en actividad 3 el umbral 1e-12. Cuando |gradiente_autograd| ≤ 1e-12, conserva el error absoluto y registra el error relativo como no definido, en los demás casos calcula el porcentaje.

### 9.3. Hallazgo 4.3: persistencia del gradient check

- **Observación inicial:** la comparación se imprimía, pero sus valores no quedaban guardados para revisión independiente.
- **Decisión inicial:** aceptada.
- **Corrección:** Se modificó actividad 3 para anexar gradientes de autograd y diferencias finitas, errores absolutos/relativos, estado del error relativo y fecha a gradient_check.csv.

### 9.4. Hallazgo 4.5: persistencia de la evaluación en test de Actividad 4

- **Observación inicial:** los valores de test se obtenían tras seleccionar configuración por validación, pero no se guardaban como evidencia independiente.
- **Decisión inicial:** aceptada en la sección 4.5.
- **Corrección:** Se modificó actividad 4 para anexar a evaluacion_test.csv la configuración seleccionada, optimizador, tasa, semilla, pérdida de test y timestamp.

### 9.5. Hallazgo 4.6: resumen de pasos y detención

- **Observación inicial:** la fila promedio registraba siempre 1000 pasos y detenido=False, sin derivarlos de las corridas individuales.
- **Decisión inicial:** aceptada. Se indicó que el defecto no alteraba las seis corridas entonces visibles, que completaron el presupuesto, pero podía producir un resumen incorrecto en otras ejecuciones.
- **Corrección:** Se cambió actividad 4 para calcular el promedio de pasos a partir de las corridas individuales y marcar detención si alguna corrida del grupo se detuvo.

### 9.6. Hallazgo 4.7: justificación de las tasas de aprendizaje

- **Decisión histórica:** inicialmente se rechazó la observación del auditor y se sostuvo que el enunciado solo pedía experimentar con distintas tasas.
- **Reevaluación de esta etapa:** el apartado 3.5.B del enunciado dice expresamente: “Justifique las tasas de aprendizaje elegidas para cada uno”. Por instrucción del estudiante se corrige la decisión anterior: justificar las tasas sí es un requisito de la entrega. Se conserva el rechazo original como antecedente, pero no como conclusión vigente.

### 9.7. Responsable de la revisión humana

- **Responsable:** Sebastián Ulloa

- **Alcance de la revisión:** revisión de las correcciones correspondientes a los hallazgos del auditor.

- **Método:** revisión del código fuente de las actividades 3 y 4, inspección de los archivos CSV generados y contraste de los resultados con el enunciado y las observaciones del auditor.

- **Resultado:** se revisaron las correcciones y posteriormente se llevaron a cabo en la sección 9. La justificación de las tasas de aprendizaje se aborda por separado en el informe de Parte 1.

- **Evidencia:** actividad3.py, actividad4.py, gradient_check.csv, tabla_optimizadores.csv, evaluacion_test.csv y figuras de resultados.

- **Observaciones:** la revisión humana se distingue de las modificaciones e inspecciones realizadas por Codex.

## Validación humana — Parte 2

Esta sección propone puntos de revisión humana basados en los hallazgos y evidencias resumidos en `auditoria/HANDOFF.md`. No contiene decisiones predeterminadas: el revisor debe marcar una opción y justificarla. Las conclusiones del auditor no sustituyen la comprobación ni aprobación humana.

### 1. Dataset y partición

#### 1.1. Columnas de origen y auditado

- **Conclusión del auditor:** el CSV de origen tiene 11 columnas; el auditado y los splits tienen 13 porque se agregan `longitud_caracteres` y `longitud_palabras`.
- **Evidencia:** `parte2/datos/resenas_metal_archives_2000_final.csv`, `parte2/resultados/dataset_auditado.csv`, `parte2/datos/train.csv`; implementación en `parte2/codigo/auditar_dataset.py`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 1.2. Calidad y tamaño de las particiones

- **Conclusión del auditor:** en el dataset auditado se encontraron cero puntuaciones no numéricas, textos vacíos, bandas vacías y URLs duplicadas; hay 1.618 bandas únicas. Train tiene 1.588 filas, validation 200 y test 212.
- **Evidencia:** resultado de lectura de CSV desde el contenedor `auditoria`, descrito en `auditoria/HANDOFF.md`; `parte2/resultados/dataset_auditado.csv` y los tres CSV bajo `parte2/datos/`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 1.3. Agrupación y ausencia de fuga entre bandas

- **Conclusión del auditor:** `dividir_dataset.py` usa `GroupShuffleSplit`, agrupando por banda con semilla 42. En los archivos actuales la suma de filas es 2.000, no hubo bandas compartidas, la cobertura de `review_url` coincidió con el origen y no hubo URL duplicadas en los splits.
- **Evidencia:** `parte2/codigo/dividir_dataset.py`; comprobaciones runtime de los CSV en `auditoria/HANDOFF.md`.
- **Decisión humana:**
- **Observaciones:** ************\*\*************\_\_************\*\*************

### 2. Modelos y metodología

#### 2.1. Baseline TF-IDF + Ridge

- **Conclusión del auditor:** el vectorizador se ajusta con train y la búsqueda prueba alpha 0.01, 0.1, 1, 10 y 100; alpha 0.01 obtuvo el menor MAE de validation.
- **Evidencia:** `parte2/codigo/baseline_tfidf.py`, `parte2/codigo/optimizar_ridge.py` y `parte2/resultados/ridge/optimizacion_ridge.csv`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 2.2. Fine-tuning de DistilBERT

- **Conclusión del auditor:** `distilbert-base-uncased` se ajusta para regresión; usa truncamiento/padding de 512 tokens, batch size 8 y etiquetas normalizadas dividiendo la puntuación por 100. La evaluación expresa MAE/RMSE en la escala original.
- **Evidencia:** `parte2/codigo/entrenar_distilbert.py`, `parte2/codigo/optimizar_distilbert.py` y parámetros de los resultados persistidos.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 2.3. Selección y uso de test

- **Conclusión del auditor:** Ridge y DistilBERT seleccionan hiperparámetros mediante validation. Test tiene evaluaciones persistidas y ya se utilizó; no debe utilizarse para ajustes nuevos. El evaluador comparativo carga el Ridge optimizado y el DistilBERT de `optimizacion_6_experimentos/mejor_modelo/`, no el artefacto `modelo_final_train_val`.
- **Evidencia:** `optimizar_ridge.py`, `optimizar_distilbert.py`, `evaluar_modelos_finales.py`, `mejor_configuracion.json` y `resultados_finales.json`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

### 3. Resultados

#### 3.1. Métricas finales

- **Conclusión del auditor:** para 212 registros, Ridge obtuvo MAE 10.1357551 y RMSE 14.1945100; DistilBERT obtuvo MAE 9.3908163 y RMSE 13.5589577. CSV y JSON concuerdan a la precisión informada.
- **Evidencia:** `parte2/resultados/comparacion_final/metricas_comparacion.csv` y `resultados_finales.json`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 3.2. Mejora y análisis complementario

- **Conclusión del auditor:** el JSON registra una mejora de DistilBERT de 7.3496140 % en MAE y 4.4774515 % en RMSE respecto de Ridge. Hay predicciones, análisis de errores, análisis por intervalo, distribución y gráficos persistidos.
- **Evidencia:** `resultados_finales.json`, `predicciones_test.csv`, `analisis_errores.csv`, `analisis_por_intervalo.csv`, `distribucion_puntuaciones.csv` y `comparacion_final/graficos/`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

### 4. Reproducibilidad

#### 4.1. Comandos y rutas

- **Conclusión del auditor:** los comandos de ejecución incluidos en el handoff corresponden a los scripts presentes y a los directorios de trabajo de `teoria` y `practica`. Reejecutarlos puede regenerar o anexar resultados.
- **Evidencia:** comandos de `auditoria/HANDOFF.md`, `parte1/README.md`, `parte2/codigo/` y `compose.yaml`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 4.2. Ejecuciones realizadas frente a comandos propuestos

- **Conclusión del auditor:** sí se ejecutaron comprobaciones de lectura y permisos desde `auditoria`; no se volvieron a ejecutar entrenamientos, optimizaciones ni scripts de análisis. Los comandos de reproducción del handoff son instrucciones, no evidencia de ejecuciones en esta auditoría.
- **Evidencia:** sección de verificación y límites de `auditoria/HANDOFF.md`; `docker compose ps`, `id`, versión de Python y consultas de datos/resultados descritas allí.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

### 5. Arquitectura Docker

#### 5.1. Servicios, recursos, usuarios, montajes, redes y GPU

- **Conclusión del auditor:** Compose configura `teoria` (2 CPU/2 GiB, usuario 10001, `teoria_net`), `practica` (2 CPU/4 GiB, GPU declarada y red `default`) y `auditoria` (2 CPU/2 GiB, usuario 10001, montajes de Parte 1/2 read-only y escritura en auditoria, `auditoria_net`). `practica_net` está declarada pero no asignada.
- **Evidencia:** inspección estática de `compose.yaml` y `Dockerfile` desde el host; `docker compose ps` y comprobaciones runtime del usuario auditor descritas en `auditoria/HANDOFF.md`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

#### 5.2. Alcance y límites de las comprobaciones

- **Conclusión del auditor:** se confirmó por runtime Python y UID/GID del servicio auditor y el fallo EROFS al intentar escribir en Parte 1/2. No se verificó runtime de recursos de los otros servicios, funcionalidad de GPU, conectividad ni aislamiento de tráfico. Compose/Dockerfile no están montados dentro del contenedor auditor; se revisaron estáticamente desde el host.
- **Evidencia:** comprobaciones runtime y limitaciones descritas en las secciones Docker y auditoría de `auditoria/HANDOFF.md`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

### 6. Uso de IA y responsabilidad del estudiante

- **Conclusión del auditor:** `parte1/PROMPTS.md` registra prompts recuperados y lagunas; `parte2/PROMPTS.md` presenta una síntesis temática y prompts reconstruidos, no transcripciones literales. Los artefactos y registros atribuyen las ejecuciones experimentales a la persona estudiante; esta auditoría no reentrenó modelos ni regeneró resultados.
- **Evidencia:** `parte1/PROMPTS.md`, `parte2/PROMPTS.md` y sección de uso de IA de `auditoria/HANDOFF.md`.
- **Decisión humana:** Aceptar
- **Observaciones:** ************\*\*************\_\_************\*\*************

## Observaciones generales

---

---

## Incidencias que requieran corrección

---

---

## Resultado de la validación humana de Parte 2

**Pendiente.** No se han marcado decisiones ni se anticipa una aprobación.

**Nombre del revisor:** **********\*\*\*\***********\_**********\*\*\*\***********

**Fecha:** **\*\*\*\***\_\_\_\_**\*\*\*\***

**Firma o identificación:** **********\*\***********\_\_**********\*\***********
