# Informe de auditoría independiente: Parte 1 del TP2

Fecha de revisión: 12 de noviembre de 2026

## Resumen general

La revisión confirma que las implementaciones contienen una atención explícita por productos matriciales y una comparación teacher–student con divisiones 512/128/128. `actividad4.py` mantiene pesos iniciales y minibatches iguales entre configuraciones, repite con dos semillas, registra normas separadas y globales, selecciona por validación y solo calcula la pérdida de test para la configuración seleccionada. El CSV respalda pérdidas finales de train/validación y 1000 pasos para las seis corridas.

La entrega visible de Parte 1 está incompleta para una evaluación integral: no se encontró un informe narrativo que discuta los experimentos o concluya sobre ellos; la evidencia de test de Actividad 4 solo se imprime en consola y no está guardada en los resultados; tampoco se conservan salidas numéricas de la prueba de gradientes de Actividad 3. El PDF de actividades 1–2 se leyó íntegramente con el visor PDF de Chrome (5 páginas); se verificaron sus operaciones y derivaciones principales, sin errores aritméticos comprobados. No se ejecutaron los scripts para evitar sobrescribir los resultados existentes.

## Archivos y evidencias revisadas

- `auditoria/desarrollo_actividades_1_2.pdf` (219 055 bytes; 5 páginas), leído en el visor PDF nativo de Chrome mediante texto accesible. No está escaneado; no requirió OCR. Se inspeccionaron los cálculos de las actividades 1 y 2. Las herramientas especializadas de extracción y OCR comprobadas y ausentes se detallan en el anexo de actualización.
- `parte1/codigo/actividad3.py`, inspección estática completa.
- `parte1/codigo/actividad4.py`, inspección estática completa.
- `parte1/resultados/tabla_optimizadores.csv` y los gráficos `curvas_entrenamiento.png`, `comparacion_perdidas.png`, `comparacion_gradientes.png`; los tres PNG fueron inspeccionados visualmente.
- `parte1/PROMPTS.md`, que indica que no se han registrado prompts de desarrollo.
- `enunciado/enunciado.txt`, secciones 3.1–3.5 y rúbrica 6.1, como fuente de requisitos. También se consultó la estructura del repositorio.
- No se encontraron otros informes/conclusiones de Parte 1 en `parte1/` aparte del código y resultados listados.

## Hallazgos correctos

- **[Correcto, evidencia estática] Atención y dimensiones.** En `actividad3.py:27-40` y `actividad4.py:39-48`, para entrada por lote `(B,4,8)` y pesos `(8,8)`, Q/K/V quedan `(B,4,8)`, S y A `(B,4,4)`, y H `(B,4,8)`. El escalado usa `sqrt(8)` y softmax opera sobre la última dimensión (las posiciones clave), como corresponde. No se reemplaza el cálculo por un módulo de atención prefabricado.
- **[Correcto, evidencia estática] Síntesis y partición.** `actividad3.py:4-15` y `actividad4.py:55-71` fijan semilla y crean 768 entradas `4×8`, con 512 train, 128 validación y 128 test, sin solapamiento de índices dentro de cada partición. El conjunto sintético no requiere una fuente externa.
- **[Correcto, evidencia estática] Entrenamiento de Actividad 3.** `actividad3.py:83-95,103-136` documenta MSE, batch 32, 1000 pasos, Adam y tasa 0.001; el ciclo calcula pérdida, retropropaga y actualiza WQ, WK y WV. Se conservan pesos iniciales para medir cambios (`158-162`) y se grafica train/validación (`164-177`).
- **[Correcto, evidencia estática] Comparación controlada de Actividad 4.** `actividad4.py:14-32` usa semillas 42 y 123, 1000 pasos, batch 32, Adam con tasas 0.001 y 0.003, y SGD con tasa 0.05. `55-114` genera un experimento por semilla y precomputa 1000 minibatches; `121-139` clona los mismos pesos iniciales para cada configuración. Así, dentro de cada semilla se mantienen datos, teacher, inicialización y minibatches.
- **[Correcto, evidencia CSV] Métricas respaldadas.** `tabla_optimizadores.csv` registra para cada método ambas semillas y promedios. El promedio de validación menor es Adam 0.003 (0.00006048), frente a SGD 0.05 (0.015601) y Adam 0.001 (0.056495). Esto respalda que Adam 0.003 fue la mejor de las tres configuraciones probadas bajo este diseño, no una afirmación general sobre optimizadores.
- **[Correcto, evidencia estática y gráfico] Normas.** `actividad4.py:168-184` obtiene gradientes antes del `step`, registra normas de WQ, WK, WV y calcula la global como `sqrt(||gQ||²+||gK||²+||gV||²)`, equivalente a la norma Euclídea del gradiente concatenado. `440-480` genera cuatro paneles y `comparacion_gradientes.png` muestra las seis corridas. Las curvas decrecen globalmente, aunque con ruido minibatch y sin discusión cuantitativa adjunta.
- **[Correcto, uso de test en Actividad 4]** La selección está basada en validación (`actividad4.py:343-359`); test se evalúa luego solamente para la configuración seleccionada (`362-387`). La construcción de objetivos teacher de test ocurre antes, pero no se computa ni utiliza allí la pérdida de test para seleccionar hiperparámetros.

## Errores o problemas detectados

- **[Posible problema] Actividad 3 evalúa el modelo student sobre test antes de entrenarlo.** `actividad3.py:69-76` hace predicción sobre `X_test` antes del entrenamiento. No se observa cálculo o uso de pérdida de test en ese punto, así que no hay evidencia de filtración o selección; sin embargo, es acceso innecesario al conjunto reservado y contradice una lectura estricta de “test exclusivamente evaluación final”. Recomiendo quitar esa predicción en una revisión futura o documentar que no se usó para decisiones.
- **[Posible problema] Error relativo puede dividir por cero.** `actividad3.py:245-255` calcula `error_abs / abs(grad_auto)` sin tolerancia cuando el gradiente analítico es cero o muy pequeño. Puede producir infinito/NaN o un porcentaje numéricamente engañoso. Los errores absolutos siguen siendo válidos, pero habría que usar denominador protegido e informar error absoluto y relativo con tolerancia definida.
- **[Error comprobado de trazabilidad] No hay evidencia persistida de los valores de prueba de gradientes.** Actividad 3 imprime tres gradientes y sus errores (`201-255`), pero el directorio de resultados no incluye el log ni una tabla. El código describe epsilon 1e-3 y minibatch fijo de 32 (`182-186`), y conserva demás parámetros al perturbar una entrada, pero no justifica epsilon ni reporta resultados observados que permitan comprobar la coincidencia autograd–diferencias finitas.
- **[Error comprobado de entregable visible] Falta informe/discusión y conclusiones de Parte 1.** El árbol disponible no contiene un informe de las actividades 1–4 ni conclusiones experimentales. Los gráficos y el CSV no sustituyen la discusión requerida por 3.5 y rúbrica 6.1. Por tanto, no hay afirmaciones narrativas que auditar por respaldo y no se puede evaluar si las conclusiones están justificadas.
- **[Posible problema de persistencia] Test de Actividad 4 no queda registrado en archivo.** `actividad4.py:368-387` imprime test para cada semilla después de seleccionar Adam 0.003, pero `tabla_optimizadores.csv` no incluye columna ni filas de test. En la evidencia entregada no se pueden verificar los valores finales de prueba sin reejecutar el script; tampoco deben inferirse del gráfico de validación.
- **[Posible problema de control de fallas] Promedio marca presupuesto fijo aunque haya detención anticipada.** En `actividad4.py:310-317`, la fila “Promedio” escribe siempre `PASOS` y `detenido=False`, incluso si una corrida individual se detuvo por no finitud. Las corridas visibles en CSV registran 1000 y False, por lo que no invalida esos números actuales; sí es un defecto latente del resumen.
- **[Posible problema] Justificación de tasas ausente.** `actividad4.py:19-31` declara valores, pero no se encontró explicación de por qué se eligió SGD 0.05 frente a las tasas Adam ni de estabilidad/velocidad. Los resultados permiten comparación empírica, pero no satisfacen por sí solos la justificación solicitada.

## Discrepancias y aspectos que requieren validación humana

- **[Verificado] Derivaciones de actividades 1 y 2.** La lectura del PDF y el contraste matemático se documentan en el anexo de actualización. No se detectaron errores aritméticos en las matrices, pérdidas, gradiente y actualización revisados. Se señalan matices de notación y explicación conceptual, no fallos numéricos.
- **[No verificable] Resultados numéricos de gradientes de Actividad 3.** No hay stdout o archivo con los valores. La comparación implementada es central y mantiene fijo el minibatch, pero no puede determinarse si los errores observados son pequeños ni si el epsilon funciona adecuadamente.
- **[No verificable] Procedencia y reproducibilidad de las imágenes.** El código apunta a esos archivos de salida, y sus aspectos visuales son coherentes con las curvas esperables, pero no se ejecutó el código ni hay log, hashes, registro de versión de PyTorch o instrucciones de ejecución de Parte 1 para vincular de forma reproducible PNG/CSV con una corrida específica. Fechas de modificación son metadatos, no prueba de procedencia.
- **[No verificable] Conclusiones.** No se encontró texto de conclusiones para comprobar sobreajuste, velocidad, estabilidad, diferencias de seed ni relación entre norma y actualizaciones/pérdida.
- **[No verificable] Validación humana de la auditoría y cálculos manuales.** `auditoria/VALIDACION_HUMANA.md` existente se refiere a Parte 0; no documenta revisión personal de Parte 1. `parte1/PROMPTS.md` sigue vacío de prompts de desarrollo. Esto no afecta la corrección matemática por sí misma, pero deja incompleta la evidencia de trazabilidad/validación del trabajo.

## Recomendaciones

1. Registrar la validación humana de las actividades 1 y 2 página por página, contrastando los resultados del anexo con cálculos propios y consignando evidencia y decisión.
2. Incorporar un informe de Parte 1 con derivaciones legibles, descripción de la atención/dimensiones, metodología, justificación de las tasas, tabla, lectura de curvas, normas de gradientes, limitaciones y conclusiones acotadas a dos semillas y tres configuraciones.
3. Conservar como archivos versionados los valores de prueba de gradientes de Actividad 3 (autograd, diferencias finitas, error absoluto/relativo, parámetro elegido, minibatch, epsilon y precisión numérica) y la salida de consola relevante.
4. En una ejecución futura, guardar métricas test de Actividad 4 en un artefacto independiente junto con la configuración seleccionada; mantener la separación actual de selección por validación y test final.
5. Evitar consultas a test antes del cierre del entrenamiento, proteger el denominador del error relativo y hacer que filas promedio reporten pasos/detención reales.
6. Añadir instrucciones concretas de reproducción (directorio de ejecución, comando, dependencias y outputs) sin ejecutar sobre los resultados actuales durante la auditoría.

## Evaluación final del cumplimiento

**Cumplimiento parcial con brechas importantes de evidencia y entrega.** Actividades 3–4 tienen una implementación estructuralmente alineada con el enunciado: cabeza explícita, particiones solicitadas, entrenamiento teacher–student, comparación con dos semillas y controles razonables, selección por validación y gráficos que incluyen las cuatro normas pedidas. El CSV respalda las pérdidas finales de train/validación y el presupuesto actual.

Las actividades 1–2 se revisaron y no presentan errores aritméticos comprobados en las operaciones auditadas, aunque conviene precisar la notación y la explicación sobre codificación posicional. No se demuestra documentalmente el acierto cuantitativo de las pruebas de gradientes ni los valores de test de Actividad 4, y no está presente la discusión escrita exigida para justificar tasas e interpretar resultados. Por ello, la evidencia disponible no permite concluir que la Parte 1 completa cumpla el encargo ni declarar correctas todas sus conclusiones.

## Anexo de actualización: revisión directa del PDF (12 de noviembre de 2026)

La limitación de lectura consignada arriba queda **resuelta**. Se comprobó la disponibilidad de herramientas: `pdftotext`, `pdfinfo`, `pdftoppm` y `tesseract` no están instalados; el Python activo (`C:\Python314\python.exe`) no tiene `fitz`/PyMuPDF, `pytesseract`, `pdfplumber` ni `pypdf`. Sin embargo, el archivo se abrió en el visor PDF nativo de Chrome. El visor informó **5 páginas**, mostró contenido y expuso el texto por página en su árbol de accesibilidad. Por ello el PDF contiene texto digital seleccionable; no es necesario rasterizarlo ni usar OCR. No se pudo hacer OCR ni conversión de imágenes porque no hay herramientas para ello, pero no son necesarias para interpretar el contenido digital accesible. Se revisó el contenido completo de las páginas 1–5 mediante ese visor. El PDF no se modificó.

### Actividad 1, páginas 1–2

- **Conceptos:** la explicación de Query, Key, Value, scores, pesos softmax y salida ponderada es sustancialmente correcta. También distingue parámetros entrenables `WQ, WK, WV` de coeficientes `Aij` calculados por entrada; la explicación conceptual de información posicional y múltiples cabezas es adecuada al nivel solicitado.
- **Dimensiones:** para `X∈R^{n×d}`, `WQ,WK∈R^{d×dk}`, `WV∈R^{d×dv}`, resultan `Q,K∈R^{n×dk}`, `S=QKᵀ∈R^{n×n}`, `A∈R^{n×n}` y `V,H∈R^{n×dv}`. Los productos descritos son compatibles. El documento alterna la grafía `QKT`/`QKᵀ`; se interpreta como transpuesta de K.
- **Elección de matrices:** `X=[[1,1],[0,1]]` tiene determinante 1; no es identidad ni nula. Las matrices de pesos cumplen entradas en `{−1,0,1}`. Verificado manualmente: `Q=[[2,−1],[1,−1]]`, `K=[[0,1],[−1,0]]`, `S=(1/√2)[[−1,−2],[−1,−1]]` y `V=[[1,0],[1,−1]]`.
- **Softmax y H:** las filas de S se normalizan por separado. La primera fila de A es `(e^{−1/√2},e^{−2/√2})/(e^{−1/√2}+e^{−2/√2})`; la segunda es `(1/2,1/2)`. Al multiplicar por V se obtiene `H=[[1,−e^{−2/√2}/(e^{−1/√2}+e^{−2/√2})],[1,−1/2]]`. La expresión en el PDF corresponde a esta operación y es correcta. Las fracciones exponenciales se dejan exactas, sin aproximación decimal, lo cual es aceptable.
- **Observación menor, posible problema de precisión conceptual:** decir que `H1` es una combinación de values es correcto si el subíndice 1 denota la primera posición de salida, pero puede confundirse con la salida de la iteración 1 de Actividad 2. Conviene aclarar la notación. La frase “el orden 123 no será lo mismo que 321” es una motivación intuitiva; en el mecanismo mostrado, sin codificación posicional, la atención por sí sola es equivariante a permutaciones y no representa orden absoluto. No invalida los productos del ejercicio, pero la explicación debería precisar que la información posicional se añade al mecanismo para que el modelo pueda distinguir posiciones.

### Actividad 2, páginas 3–5

- **Derivación de gradiente:** con `L=1/2||H−T||_F²` y `H=AXWV`, fijando A y X, `∂L/∂H=H−T` y `∇_{WV}L=(AX)ᵀ(H−T)=XᵀAᵀ(AXWV−T)`. Las dimensiones quedan `(d×n)(n×dv)=d×dv`, iguales a WV. La justificación de tratar A fija es correcta para la derivada parcial respecto de WV, dado que A depende de WQ/WK.
- **Notación de derivación:** la línea que multiplica `∂L/∂E · ∂E/∂H` y escribe `E·1` (página 3) es una abreviatura informal de derivación matricial, no una multiplicación escalar ordinaria. El resultado `H−T` es correcto; sería más claro justificarlo mediante diferencial/gradiente de Frobenius.
- **Cálculo manual:** usando `X=[[1,1],[0,1]]`, `WV=[[0,1],[1,−1]]`, `A=[[1/4,3/4],[1/2,1/2]]`, `T=[[1,0],[0,−1]]`, se obtiene `AX=[[1/4,1],[1/2,1]]`, `H0=[[1,−3/4],[1,−1/2]]`, `E0=[[0,−3/4],[1,1/2]]` y `L0=29/32=0.90625`. El documento calcula `G=[[1/2,1/16],[1,−1/4]]`, consistente con `XᵀAᵀE0`.
- **Actualización y pérdida:** para `η=1/2`, `Wv(1)=[[-1/4,31/32],[1/2,−7/8]]`, correcto. Entonces `H1=[[7/16,−81/128],[3/8,−25/64]]` y `H1−T=[[-9/16,−81/128],[3/8,39/64]]`. La pérdida `L1=20133/32768≈0.61441`, correcta. Disminuye de `0.90625` a aproximadamente `0.61441`; la conclusión está acotada a esta instancia y advierte adecuadamente que la tasa de aprendizaje no garantiza descenso universal.
- **Softmax:** la demostración por cociente de `∂ai/∂sj=ai(δij−aj)` es correcta y distingue los casos del numerador. La explicación final identifica correctamente que, en el modelo completo, la dependencia vía Q/K cambia los scores, A y la pérdida; no pretende desarrollar los gradientes completos, conforme al enunciado.

### Revisión de legibilidad y evaluación matemática actualizada

El visor mostró texto legible y ecuaciones identificables en las cinco páginas. No se observó ninguna página ilegible en el texto accesible; no se necesitó OCR. Se verificaron las multiplicaciones y fracciones principales de Actividad 1 y el gradiente y la actualización de Actividad 2. **No se detectaron errores aritméticos comprobados** en esos cálculos. Se mantienen las dos observaciones de notación/explicación señaladas (derivación matricial abreviada y la afirmación sobre orden/posiciones), ambas de precisión conceptual menor y no errores del resultado numérico.

La evaluación final del informe sigue siendo de cumplimiento parcial por las brechas de evidencia y entrega de Actividades 3–4 descritas antes; ya no corresponde clasificar las derivaciones 1–2 como no verificables. Esta actualización se basa en lectura accesible del PDF, no en OCR ni en la inspección de una rasterización página por página.
