# Registro de trazabilidad de prompts: Parte 1

Este registro cubre las interacciones de Codex recuperadas de sesiones locales. Los prompts en bloques son transcripciones textuales integramente extraidas de los mensajes del usuario. Las fechas corresponden al dia de la sesion; el modelo especifico no esta disponible en los metadatos revisados. Las asociaciones de archivos y resultados se distinguen entre lo pedido, lo realizado segun la respuesta de Codex y los artefactos actuales.

## Intervenciones recuperadas

### 1. Planificacion de Parte 1 antes de resolver actividades

- **Fecha:** 2026-11-08.
- **Agente/herramienta:** Codex (sesion de planificacion).
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** No se modificaron archivos. Consulte README, configuracion Docker y enunciado PDF; entrego plan de actividades y dependencias. El prompt establecio que los calculos manuales de Actividades 1 y 2 debian hacerlos los estudiantes antes de pedir una solucion. No constituye una solicitud de resolucion de esas actividades.
- **Prompt textual integro:**

````text
Estamos comenzando la Parte 1 del TP2 de Álgebra Lineal y Optimización: «Fundamentos y entrenamiento de Transformers».

Trabajaremos exclusivamente en la Parte 1.

## Contexto del proyecto

El repositorio se encuentra en:

`C:\Users\sebau\Downloads\Tarea2ALODS\tp2-transformers`

La infraestructura Docker ya está preparada. Debes trabajar utilizando el servicio `teoria` y limitar tus modificaciones al directorio `parte1/`.

Antes de comenzar:

1. Revisa el README y la configuración Docker para entender cómo ejecutar comandos en el contenedor `teoria`.
2. Revisa el enunciado original para identificar todas las actividades, restricciones y entregables de la Parte 1.
3. No modifiques archivos de `parte2/`, `auditoria/` ni la infraestructura.

## Forma de trabajo

Quiero avanzar progresivamente, actividad por actividad.

- Explica los conceptos matemáticos antes de implementarlos.
- No generes el informe completo de una sola vez.
- Prioriza código sencillo, verificable y reproducible.
- Conserva los experimentos, resultados y decisiones relevantes.
- Registra los prompts utilizados en `parte1/PROMPTS.md`.
- No inventes resultados experimentales ni afirmes haber ejecutado código que no ejecutaste.
- Ayúdame a comprender y justificar personalmente las operaciones, los gradientes y las conclusiones.

Por ahora, realiza únicamente la revisión del enunciado completo de la Parte 1 y presenta una planificación de sus actividades, entregables y dependencias. No comiences todavía a resolverlas.
````

### 2. Auditoria independiente inicial de Parte 1

- **Fecha:** 2026-11-11.
- **Agente/herramienta:** Codex, sesion independiente; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Se consultaron PDF de actividades 1 y 2, scripts y resultados. Resultado: se creo `auditoria/informe_auditoria.md`; la primera revision no pudo leer el PDF y dejo esas derivaciones como no verificables. No se atribuyen a Codex cambios en los originales ni ejecucion de experimentos.
- **Prompt textual integro:**

````text
# Auditoría independiente del TP2: Álgebra Lineal y Optimización

Actúa como agente auditor independiente. Tu tarea es revisar el trabajo implementado en la Parte 1 del TP2.

## Restricciones

- No modifiques ningún archivo del código original.
- No corrijas errores directamente.
- No sobrescribas resultados ni ejecutes experimentos que alteren los archivos existentes.
- Puedes ejecutar pruebas adicionales si son necesarias, siempre que no modifiques los archivos originales.
- Guarda tu informe exclusivamente en `/workspace/auditoria/informe_auditoria.md`.

## Elementos que debes auditar

1. **Derivaciones matemáticas:** revisa las expresiones y derivaciones de atención, sus dimensiones, operaciones y justificaciones matemáticas presentes en el trabajo.
2. **Implementación:** revisa `actividad3.py` y `actividad4.py`, prestando atención a la correspondencia entre el código y los requisitos del enunciado.
3. **Pruebas de gradientes:** verifica la comparación entre autograd y diferencias finitas, incluyendo el uso de los mismos parámetros, minibatch y valor de epsilon.
4. **Experimentos y métricas:** revisa las divisiones de datos, inicializaciones, semillas, presupuestos de entrenamiento, tasas de aprendizaje, optimizadores y cálculo de las pérdidas.
5. **Validación y prueba:** comprueba que las configuraciones se seleccionan mediante validación y que el conjunto de prueba se utiliza únicamente para la evaluación final.
6. **Normas de gradientes:** revisa el cálculo y registro de las normas individuales y globales, así como su representación gráfica.
7. **Conclusiones:** evalúa si las conclusiones están respaldadas por los resultados y si existen afirmaciones exageradas o no justificadas.

## Formato del informe

Organiza el informe en:

- Resumen general.
- Archivos y evidencias revisadas.
- Hallazgos correctos.
- Errores o problemas detectados.
- Discrepancias o aspectos que requieren verificación humana.
- Recomendaciones de corrección, sin modificar el código.
- Evaluación final del cumplimiento de los requisitos.

Para cada hallazgo, indica el archivo y la sección o línea correspondiente cuando sea posible. Distingue claramente entre errores comprobados, posibles problemas y aspectos que no puedes verificar.

No declares que todo está correcto sin aportar evidencia concreta. Si algún elemento del trabajo no está disponible para revisar, indícalo expresamente.

Tu objetivo es realizar una auditoría crítica e independiente, no aprobar automáticamente el trabajo.
````

### 3. Seguimiento de auditoria: segundo intento de lectura del PDF

- **Fecha:** 2026-11-12.
- **Agente/herramienta:** Codex, sesion de auditoria; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Se actualizaron unicamente los hallazgos del informe `auditoria/informe_auditoria.md`. Codex informo que pudo revisar las cinco paginas en el visor de Chrome, que el texto era accesible y que no necesito OCR. Indico que no quedaron paginas sin interpretar y que no modifico el PDF ni otros originales.
- **Prompt textual integro:**

````text
Necesito que intentes nuevamente revisar `/workspace/auditoria/desarrollo_actividades_1_2.pdf`.

No des por terminada la revisión solo porque no tienes una herramienta especializada. Comprueba si tienes disponibles `pdftotext`, `pdfinfo`, Python con PyMuPDF (`fitz`) o herramientas OCR como Tesseract.

Intenta extraer el texto y, si el PDF contiene páginas escaneadas, intenta convertirlas a imágenes para inspeccionarlas mediante OCR.

No modifiques el PDF ni ningún archivo original. Si consigues leerlo, completa la revisión matemática y actualiza `informe_auditoria.md`. Si no es posible, explica exactamente qué herramientas faltan y qué páginas no pudiste interpretar.
````

### 4. Correccion de hallazgos 4.1, 4.2 y 4.6

- **Fecha:** 2026-11-16.
- **Agente/herramienta:** Codex; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Archivos de codigo modificados: `parte1/codigo/actividad3.py` y `actividad4.py`. Elimino la prediccion previa no usada de `X_test`, anadio tolerancia `1e-12` para marcar como no definido el error relativo de gradientes pequenos y corrigio el resumen de pasos/detencion usando las corridas. La sintaxis paso; no pudo correr experimentos por falta local de PyTorch y acceso Docker denegado.
- **Prompt textual integro:**

````text
Necesito implementar tres correcciones identificadas en `auditoria/informe_auditoria.md`, correspondientes a los hallazgos 4.1, 4.2 y 4.6.

**Antes de modificar nada**, revisa el código de `parte1` y localiza exactamente los fragmentos relacionados con estos hallazgos.

### 1. Predicción innecesaria sobre X_test (hallazgo 4.1)

En la Actividad 3 se realiza una predicción sobre `X_test` antes del entrenamiento.

- Comprueba dónde ocurre.
- Elimina esa predicción si efectivamente no se utiliza.
- No alteres la separación train/validation/test ni el procedimiento de entrenamiento.

### 2. Cálculo del error relativo (hallazgo 4.2)

En el gradient check se calcula el error relativo usando el valor absoluto del gradiente analítico como denominador.

- Evita divisiones por cero o valores numéricamente demasiado pequeños.
- Mantén el cálculo del error absoluto.
- Implementa un tratamiento numéricamente razonable para el error relativo y deja claro cómo se manejan esos casos.
- No modifiques el procedimiento de comparación entre autograd y diferencias finitas.

### 3. Resumen de entrenamiento (hallazgo 4.6)

En la Actividad 4, el resumen promedio informa siempre 1000 pasos y `detenido=False`, independientemente de lo que ocurra en cada ejecución.

- Revisa cómo se registra actualmente el número de pasos y la detención anticipada.
- Corrige el resumen para que refleje los valores reales de cada ejecución.
- Si corresponde, calcula los promedios a partir de los registros individuales, sin asumir que todas las ejecuciones completan 1000 pasos.

### Restricciones

- No cambies hiperparámetros, semillas, arquitectura, funciones de pérdida ni configuración experimental.
- No modifiques los resultados experimentales deliberadamente.
- No realices cambios ajenos a estos tres hallazgos.
- Conserva el estilo y la estructura actual del proyecto.

### Verificación

Después de implementar:

1. Ejecuta las comprobaciones pertinentes.
2. Comprueba que el código sigue funcionando.
3. Indica qué archivos modificaste y qué cambios realizaste.
4. Informa los comandos ejecutados y sus resultados.
5. Señala cualquier problema que impida verificar alguna corrección.

No redactes todavía el informe final ni modifiques `VALIDACION_HUMANA.md`. Primero quiero revisar las correcciones.
````

### 5. Solicitud de verificacion funcional de Actividades 3 y 4

- **Fecha:** 2026-11-16.
- **Agente/herramienta:** Codex; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** No modifico codigo/configuracion. `docker compose config` se valido; el acceso al motor Docker y la comprobacion de dependencias dentro del contenedor fallaron por permisos. No pudo verificar las ejecuciones ni los resultados funcionales.
- **Prompt textual integro:**

````text
Necesito verificar funcionalmente las modificaciones realizadas en `actividad3.py` y `actividad4.py`.

1. Revisa `compose.yaml` y el `Dockerfile` para identificar cómo se construye y ejecuta el servicio `teoria`.
2. Comprueba si el contenedor tiene instaladas las dependencias necesarias, especialmente PyTorch y Matplotlib.
3. Si el entorno está correctamente configurado, ejecuta las actividades 3 y 4 utilizando los comandos previstos por el proyecto.
4. Comprueba que ambas ejecuciones terminan correctamente y que los resultados se generan en las ubicaciones esperadas.
5. Verifica especialmente que:
   - El gradient check de la actividad 3 funciona con el tratamiento del error relativo.
   - La actividad 4 genera correctamente los resultados y el resumen de pasos/detención.
   - Los resultados experimentales existentes no se sobrescriben sin necesidad.

No modifiques código ni configuración todavía. Si falta alguna dependencia o existe un problema con Docker, informa el problema y propone la solución antes de aplicarla.
````

### 6. Persistencia de resultados de gradient check y evaluacion test

- **Fecha:** 2026-11-16.
- **Agente/herramienta:** Codex; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Modifico `actividad3.py` y `actividad4.py` para anexar filas a `parte1/resultados/gradient_check.csv` y `evaluacion_test.csv`. La comprobacion sintactica paso. En esa intervencion no ejecuto scripts; los resultados existentes que hoy estan en esos archivos fueron generados despues por el estudiante, no por Codex.
- **Prompt textual integro:**

````text
Vamos a completar las evidencias pendientes identificadas en la auditoría de Parte 1.

Revisa `actividad3.py`, `actividad4.py` y los archivos existentes en `parte1/resultados`.

### 1. Gradient check (Actividad 3)

Actualmente los resultados se imprimen, pero no quedan guardados.

- Guarda los valores de gradientes analíticos y diferencias finitas para WQ, WK y WV.
- Incluye errores absolutos y relativos.
- Conserva el procedimiento y los valores calculados; no cambies el experimento.
- Guarda la evidencia en un archivo CSV o TXT dentro de `parte1/resultados`.

### 2. Evaluación en test (Actividad 4)

Los resultados de test para las semillas 42 y 123 tampoco quedan guardados como evidencia independiente.

- Guarda los valores de test de ambas semillas.
- Incluye la configuración del optimizador seleccionado.
- Mantén los resultados existentes y no alteres los experimentos.

### Restricciones

- No cambies arquitectura, hiperparámetros, semillas ni procedimiento experimental.
- No inventes ni reproduzcas manualmente valores que no se hayan calculado.
- No sobrescribas archivos existentes sin necesidad.
- Mantén el estilo del proyecto.

### Verificación

Indica qué archivos modificaste y cuáles creaste. Ejecuta las comprobaciones que puedas y explica claramente qué evidencias quedaron guardadas y cuáles requieren volver a ejecutar los experimentos.

No redactes todavía el informe final ni modifiques otros documentos.
````

### 7. Documentacion de reproducibilidad de Actividades 3 y 4

- **Fecha:** 2026-11-16.
- **Agente/herramienta:** Codex; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Creo `parte1/README.md` con parametros, comandos Docker, rutas y descripcion de artefactos. No ejecuto actividades ni modifico resultados.
- **Prompt textual integro:**

````text
Vamos a completar la documentación de reproducibilidad de Parte 1, según los requisitos del enunciado y las observaciones de la auditoría.

Revisa:

- `compose.yaml`
- `Dockerfile`
- `parte1/requirements.txt`
- `parte1/codigo/actividad3.py`
- `parte1/codigo/actividad4.py`
- Los archivos existentes en `parte1/resultados`

Necesito documentar:

### 1. Configuración experimental

Para las actividades 3 y 4, identifica los parámetros reales utilizados en el código:

- Dimensiones y generación de datos.
- Particiones de entrenamiento, validación y test.
- Semillas.
- Arquitectura y función de pérdida.
- Optimizadores y tasas de aprendizaje.
- Número de pasos y tamaño de batch.
- Procedimiento de evaluación y selección del modelo.

No inventes parámetros ni confundas valores de distintas actividades.

### 2. Comandos de reproducción

Documenta los comandos necesarios para:

- Construir la imagen Docker, si corresponde.
- Levantar el servicio `teoria`.
- Ejecutar las actividades 3 y 4.
- Consultar los resultados generados.

Considera que los scripts deben ejecutarse desde `/workspace/parte1/codigo` para que sus rutas relativas apunten a `parte1/resultados`.

### 3. Origen de las curvas y evidencias

Identifica cada gráfico y archivo generado:

- Qué actividad y ejecuciones lo producen.
- Qué información representa.
- Qué archivos CSV respaldan los resultados.
- Dónde queda almacenada cada evidencia.

### Entrega

Incorpora esta documentación en un README de `parte1`, o actualiza el README existente si ya lo hay. No dupliques información innecesariamente.

### Restricciones

- No modifiques los experimentos ni sus resultados.
- No vuelvas a ejecutar los scripts.
- No inventes resultados ni afirmes que algo es reproducible si no está respaldado por los comandos y la configuración.
- No modifiques `VALIDACION_HUMANA.md` ni redactes todavía el informe final.

Al terminar, indica qué archivo modificaste y resume los comandos y parámetros documentados.
````

### 8. Revision de exactitud del README

- **Fecha:** 2026-11-16.
- **Agente/herramienta:** Codex; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Consulte el README, scripts, configuracion Docker y resultados; no modifico archivos. Informo que los datos estaban respaldados y senalo una imprecision menor: la frase sobre los archivos presentes omitia `.gitkeep`, con propuesta de redaccion corregida.
- **Prompt textual integro:**

````text
Revisa el README de Parte 1 que acabamos de preparar y contrástalo directamente con `actividad3.py`, `actividad4.py`, `compose.yaml`, `Dockerfile` y los archivos existentes en `parte1/resultados`.

Quiero una revisión de exactitud, no una reescritura.

Comprueba específicamente:

1. Que todos los parámetros experimentales y procedimientos descritos coincidan con el código.
2. Que la descripción de la atención y las dimensiones sea correcta.
3. Que los comandos Docker funcionen con la estructura y rutas reales del proyecto.
4. Que los archivos mencionados efectivamente existan y que su comportamiento de escritura (sobrescritura o anexado) esté bien descrito.
5. Que la descripción de las curvas y CSV corresponda a su contenido real.
6. Que las afirmaciones sobre las ejecuciones actuales estén respaldadas por los archivos existentes.

Entrega una lista de:

- Afirmaciones correctas.
- Errores o imprecisiones concretas, indicando dónde están.
- Correcciones necesarias, con su redacción propuesta.

No modifiques ningún archivo. No inventes discrepancias ni sugieras cambios meramente estilísticos.
````

### 9. Solicitud de completar el registro de trazabilidad de Parte 1

- **Fecha:** 2026-11-16.
- **Agente/herramienta:** Codex; modelo no identificado.
- **Proposito:** segun la instruccion textual que sigue.
- **Archivos/resultados asociados:** Consulte el PROMPTS existente, codigo, resultados, handoff/validacion y sesiones disponibles; modifico `parte1/PROMPTS.md`. Esta entrada documenta esa intervencion de trazabilidad; no se atribuye a Codex el origen de los experimentos.
- **Prompt textual integro:**

````text
Necesito completar `parte1/PROMPTS.md` como registro de trazabilidad del trabajo realizado en la Parte 1 del TP2.

Primero, revisa el contenido actual de:

- `parte1/PROMPTS.md`
- `parte1/codigo/`
- `parte1/resultados/`
- `auditoria/HANDOFF_P1.md` (si existe)
- `auditoria/VALIDACION_HUMANA.md` (si existe)

También revisa el historial de conversaciones o sesiones de Codex disponible en el entorno, si tienes acceso a él.

**Objetivo:** documentar fielmente cómo se desarrolló la Parte 1, sin inventar prompts ni atribuir acciones que no estén respaldadas.

Incluye, para cada intervención que puedas verificar:

1. Número u orden de la intervención.
2. Agente utilizado (Codex u otro, solo si está identificado).
3. Objetivo de la intervención.
4. Prompt utilizado, preferentemente textual.
5. Archivos creados o modificados.
6. Resultado obtenido.

Criterios importantes:

- No inventes prompts textuales a partir de descripciones del trabajo.
- Si no puedes recuperar un prompt exacto, indícalo como reconstrucción o resumen.
- Distingue entre trabajo realizado por Codex y decisiones o validaciones realizadas por el estudiante.
- Incluye las correcciones recientes de Actividad 3 y Actividad 4, pero no atribuyas a Codex las ejecuciones que realizó el estudiante.
- No confundas los archivos de resultados generados con los archivos de código modificados.
- No agregues información irrelevante ni repitas documentación que corresponda al README.
- Si no tienes acceso al historial necesario, indícalo claramente y prepara un registro parcial con la información verificable.

**Antes de modificar el archivo**, presenta un breve diagnóstico de qué información pudiste recuperar y qué información falta. No inventes datos para completar los vacíos.

Luego, si la información es suficiente, actualiza `parte1/PROMPTS.md` directamente. Al terminar, informa qué incorporaste, qué quedó pendiente y si utilizaste prompts textuales o reconstrucciones.
````

## Desarrollo por actividad y limites de atribucion

- **Actividades 1 y 2:** el unico prompt recuperado sobre su desarrollo es la planificacion inicial. Expresamente pide que los estudiantes completen los calculos manuales antes de solicitar soluciones. La auditoria posterior examino el PDF `auditoria/desarrollo_actividades_1_2.pdf`; no se recupero una instruccion a Codex para producir esos calculos. No se atribuye su autoria a Codex.
- **Actividad 3:** no se recupero un prompt inicial de implementacion. Se recuperaron las solicitudes posteriores de correccion y persistencia de la evidencia. No se afirma quien escribio la version inicial de `actividad3.py`.
- **Actividad 4:** no se recupero un prompt inicial de implementacion o comparacion de optimizadores. Si se recuperaron las solicitudes de correccion del resumen, guardado de test y revision. No se afirma quien escribio la version inicial de `actividad4.py`.
- **Actividad 5:** se representa en el historial recuperado mediante la auditoria independiente y la revision humana. La aceptacion/rechazo de hallazgos y las ejecuciones actuales de los scripts corresponden al estudiante segun la documentacion y la informacion aportada, no a Codex.
- No se recupero una solicitud de Codex para redactar conclusiones o un informe final de Parte 1. No existe `auditoria/HANDOFF_P1.md` en los archivos revisados; `auditoria/HANDOFF.md` antecede a esta parte.

## Ejecuciones y resultados del estudiante

Los CSV y PNG actualmente presentes en `parte1/resultados/` son artefactos experimentales, no archivos de codigo modificados. Segun la aclaracion del estudiante y las marcas de tiempo, las ejecuciones que los produjeron fueron realizadas por el estudiante despues de las modificaciones. Codex informo expresamente que no ejecuto los scripts en las sesiones de correccion y persistencia por falta de PyTorch local y bloqueo de Docker. No se atribuye a Codex la generacion de `curvas_entrenamiento.png`, `gradient_check.csv`, `tabla_optimizadores.csv`, `evaluacion_test.csv`, `comparacion_perdidas.png` ni `comparacion_gradientes.png`.

## Delegaciones automaticas

Se revisaron las sesiones locales listadas en `session_index.jsonl`, las sesiones archivadas accesibles y los registros de la Parte 1. No se encontro una llamada de delegacion ni un prompt de subagente asociado al desarrollo de Parte 1. El directorio `.agents/` no esta presente en el workspace. Esta conclusion se limita a los registros disponibles; no prueba que no hubiera delegaciones fuera del historial local conservado.

## Limitaciones de recuperacion

Las sesiones recuperables documentan planificacion, auditoria, cambios posteriores de codigo y documentacion. No permiten reconstruir prompts de desarrollo inicial de las actividades 1 a 4, porque no aparecen en el indice ni en los rollouts locales accesibles. No se inventan fechas, modelos, agentes, autorias ni resultados para llenar esos vacios. La revision de Auditoria de Parte 0 y otras conversaciones ajenas al desarrollo de Parte 1 no se duplica aque.
