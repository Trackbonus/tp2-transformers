# Handoff de la Parte 1 — borrador para revisión estudiantil

> Preparado por Codex a partir del estado actual del repositorio, de los informes disponibles y de las respuestas conservadas en las sesiones. Este documento queda pendiente de revisión por los estudiantes; no constituye su aprobación.

## 1. Objetivo y estado

La Parte 1 aborda atención y sus derivaciones manuales (Actividades 1 y 2), una implementación teacher–student de una cabeza de atención (Actividad 3), la comparación controlada de optimizadores (Actividad 4) y una auditoría independiente seguida de validación humana (Actividad 5). El apartado 3.7 requiere además un informe escrito de 8–12 páginas sugeridas, código y resultados reproducibles, registros íntegros de prompts, este handoff revisado por estudiantes y validaciones humanas con responsable, método, evidencia, resultado y correcciones.

| Actividad | Estado respaldado por los archivos actuales | Qué no permite afirmar la evidencia |
|---|---|---|
| 1. Atención y cálculos matriciales | El desarrollo está en `auditoria/desarrollo_actividades_1_2.pdf`. La auditoría del 12 de noviembre revisó sus cinco páginas y no encontró errores aritméticos principales; `VALIDACION_HUMANA.md` indica que los cálculos fueron comprobados por el estudiante. | No se encontró un informe narrativo completo de Parte 1 ni una identificación nominal del responsable de la comprobación humana. Subsisten comentarios de notación/explicación conceptual, uno de ellos aceptado por el estudiante. |
| 2. Gradiente, actualización y softmax | El mismo PDF contiene la derivación y el cálculo manual. El informe auditor no encontró errores aritméticos principales; la validación humana los marca como revisados. | El handoff no sustituye una verificación individual adicional ni resuelve las observaciones de notación de la auditoría. |
| 3. Entrenamiento teacher–student y gradient check | Existe `actividad3.py`, una curva de entrenamiento y `gradient_check.csv`. El código contiene la corrección de la predicción previa no usada sobre `X_test`, y evita calcular el error relativo cuando el gradiente analítico tiene magnitud `≤ 1e-12`. El CSV actual compara autograd y diferencias finitas centrales para WQ/WK/WV. | No se recuperó un prompt de implementación inicial. El gradiente de test final de Actividad 3 se calcula/imprime en el script, pero no aparece en un CSV específico de evaluación test de esa actividad. Tampoco hay discusión escrita que justifique epsilon y la precisión numérica o interprete el resultado conforme al enunciado. |
| 4. Optimizadores y tasas | `actividad4.py` compara Adam 0.001, Adam 0.003 y SGD 0.05 con semillas 42 y 123. La tabla actual contiene las seis corridas, promedios, pasos y estado de detención; los dos PNG comparan pérdidas y normas. `evaluacion_test.csv` contiene test para ambas semillas después de seleccionar Adam 0.003 por validación. | No se encontró la discusión de estabilidad/velocidad y convergencia solicitada por el enunciado ni la justificación de las tasas. El archivo de resultados muestra las métricas, pero no sustituye esa interpretación. |
| 5. Auditoría y validación humana | Existe `auditoria/informe_auditoria.md` y `auditoria/VALIDACION_HUMANA.md`; este último registra decisiones aceptadas/rechazadas y la revisión de cálculos manuales. | La validación humana no refleja todavía las correcciones y evidencias agregadas después de la auditoría. No se pudo verificar un registro individual completo con responsable nominal, método, evidencia, resultado y correcciones para cada revisión. |

La actividad de entrenamiento fue ejecutada posteriormente por el estudiante, según la información proporcionada y las marcas de tiempo de los artefactos. Codex modificó código y documentación en intervenciones separadas, pero no ejecutó las corridas experimentales: las sesiones registran que faltaba PyTorch en el Python local y que Docker no era accesible desde ese entorno. No se atribuye a Codex la generación de los CSV ni de los gráficos actuales.

## 2. Arquitectura Docker pertinente

La arquitectura se define en el Compose y Dockerfile de la raíz. `teoria` es el servicio para Parte 1: usa la imagen compartida `tp2-python:3.12`, construida desde `python:3.12-slim-bookworm`, monta `parte1/` con escritura en `/workspace/parte1` y ejecuta comandos desde ese directorio de trabajo. Tiene 2 CPU, límite de memoria de 2 GiB, usuario `10001:10001`, filesystem de imagen de solo lectura y `/tmp` temporal. La dependencia PyTorch se instala desde el índice CPU y el `requirements.txt` raíz contiene `numpy` y `matplotlib`; ninguna de estas versiones ni la imagen base están fijadas exactamente. No existe `parte1/requirements.txt`.

Compose también declara `practica` para Parte 2 y `auditoria` con montajes de solo lectura de Parte 1 y Parte 2 y escritura en `auditoria/`. Cada servicio usa su propia red bridge. Las inspecciones de Parte 0 registradas en `auditoria/verificaciones/verificaciones_complementarias.md` confirmaron UID/GID, límites efectivos, redes distintas y ausencia de puertos publicados en la fecha de esa inspección. No se probaron tráfico entre servicios ni conectividad a Internet. Codex se ejecutó en Windows, fuera de esos contenedores; los montajes de Docker no confinan por sí solos las herramientas de Codex en el anfitrión.

Para el detalle de Parte 0 y sus limitaciones, consúltense `auditoria/HANDOFF.md` y los registros de `auditoria/verificaciones/`. Ese HANDOFF antecede al trabajo de Parte 1 y contiene la afirmación histórica de que las Partes 1 y 2 aún no habían comenzado; no es evidencia del estado actual de Parte 1 ni reemplaza este archivo.

## 3. Comandos de reproducción

Los comandos siguientes se contrastaron con `parte1/README.md`, Compose y las rutas usadas por los scripts. Se ejecutan desde la raíz del repositorio:

```powershell
docker compose build teoria
docker compose up -d teoria
docker compose ps teoria
docker compose exec teoria python --version
docker compose exec teoria python -c "import torch, matplotlib; print('torch', torch.__version__); print('matplotlib', matplotlib.__version__)"
docker compose exec teoria sh -c "cd /workspace/parte1/codigo && python actividad3.py"
docker compose exec teoria sh -c "cd /workspace/parte1/codigo && python actividad4.py"
docker compose exec teoria ls -lh /workspace/parte1/resultados
```

El cambio a `/workspace/parte1/codigo` es necesario porque los scripts usan rutas relativas a su directorio actual para guardar algunos gráficos y la tabla. Los artefactos quedan en `parte1/resultados/`, visible también en el anfitrión por el bind mount. El README indica que repetir Actividad 3 reemplaza `curvas_entrenamiento.png` y anexa tres filas a `gradient_check.csv`; Actividad 4 reemplaza su tabla y gráficos comparativos y anexa dos filas a `evaluacion_test.csv`. Conviene conservar copias si se quieren retener ejecuciones anteriores.

El historial disponible no prueba que todos los comandos de reproducción del README se hayan ejecutado en una única corrida documentada. Codex informó que no pudo verificar la ejecución funcional de ambas actividades por bloqueo de Docker en su entorno; los artefactos actuales fueron producidos por el estudiante.

## 4. Implementación y evidencias actuales

### Actividad 3

`parte1/codigo/actividad3.py` implementa explícitamente Q, K, V, scores escalados por `√8`, softmax en posiciones clave y salida de atención. Usa 768 ejemplos aleatorios de forma `4×8`, partición 512/128/128, semilla 42, teacher de pesos aleatorios y estudiante con pesos distintos. Entrena WQ/WK/WV con MSE, Adam a 0.001, batch 32 y 1000 pasos, evaluando train/validación cada 10 pasos. Tras el entrenamiento calcula el gradient check sobre un minibatch fijo de 32 ejemplos de train, para el elemento `[0,0]` de cada matriz y epsilon `1e-3`; las diferencias finitas son centrales.

Artefactos existentes:

- `resultados/curvas_entrenamiento.png`: curva de MSE de train y validación.
- `resultados/gradient_check.csv`: una tanda registrada el 16 de noviembre de 2026. Los errores relativos informados son aproximadamente 0.0195% (WQ), 0.0430% (WK) y 0.0305% (WV); el CSV también contiene gradientes autograd y diferencias finitas, error absoluto y estado del error relativo.

### Actividad 4

`parte1/codigo/actividad4.py` reutiliza el diseño teacher–student con semillas 42 y 123. En cada semilla precomputa minibatches y parte de los mismos pesos iniciales para las tres configuraciones. Registra normas de gradiente de WQ, WK, WV y la norma global. La selección se basa en la pérdida promedio de validación; el CSV actual muestra menor promedio para Adam 0.003 entre las tres opciones registradas. Las seis corridas actuales completaron 1000 pasos y el campo `detenido` es `False` en cada una; el código ahora calcula esos campos desde los registros individuales.

Artefactos existentes:

- `resultados/tabla_optimizadores.csv`: seis filas de corridas y tres filas promedio.
- `resultados/evaluacion_test.csv`: evaluación final de la configuración seleccionada Adam 0.003: MSE 0.0000845031 para semilla 42 y 0.0000508340 para semilla 123, con fecha registrada.
- `resultados/comparacion_perdidas.png`: curvas de train y validación para las configuraciones y semillas.
- `resultados/comparacion_gradientes.png`: normas individuales y global a lo largo de las corridas.

Los CSV y PNG son resultados experimentales, no archivos de código. También existe `.gitkeep` en la carpeta de resultados; no es un artefacto experimental.

## 5. Auditoría, validación y trazabilidad

`auditoria/informe_auditoria.md` registra la auditoría independiente de Parte 1 y la lectura del PDF. La revisión confirmó la estructura de atención, particiones, entrenamiento, comparación controlada, selección por validación y cálculos manuales principales. También señaló falta de informe narrativo, falta inicial de persistencia de gradient check y test, acceso previo innecesario a `X_test`, riesgo de división por cero en error relativo y limitaciones para justificar e interpretar resultados.

`auditoria/VALIDACION_HUMANA.md` acepta las observaciones sobre acceso previo a test, error relativo, persistencia inicial, resumen de pasos y ausencia de informe narrativo; marca como verificadas las derivaciones manuales principales. Rechaza la exigencia de justificar tasas de aprendizaje y algunas observaciones de notación/validación. Hay una discrepancia que debe tenerse presente: el apartado 3.5.B del enunciado sí dice “Justifique las tasas de aprendizaje elegidas para cada uno”. Por ello, la decisión de rechazo no elimina la necesidad de documentar esa justificación en la entrega.

Ambos documentos son históricos frente al estado actual: el informe de auditoría está fechado el 12 de noviembre y precede a las modificaciones y artefactos del 16 de noviembre; describe como ausentes archivos de evidencia que ahora existen. `VALIDACION_HUMANA.md` conserva recomendaciones como pendientes de implementación aunque el código actual ya contiene las correcciones. Deben actualizarse tras revisar las correcciones y las nuevas evidencias. Además, el enunciado pide que el registro humano identifique responsable, método, evidencia, resultado y correcciones; no todos esos elementos quedan identificados de forma verificable en el archivo actual.

`parte1/PROMPTS.md` contiene nueve prompts textuales recuperados y separa ejecuciones del estudiante de modificaciones de Codex. Indica que no se recuperaron los prompts iniciales de implementación de Actividades 3 y 4 ni solicitudes de Codex para los cálculos manuales. No se encontró evidencia accesible de delegaciones automáticas para Parte 1. El modelo específico de Codex tampoco pudo identificarse.

## 6. Limitaciones y pendientes antes de la entrega

- Elaborar o localizar el informe narrativo requerido, con discusión de curvas, estabilidad/velocidad, resultados, convergencia o sobreajuste y conclusiones respaldadas.
- Justificar las tasas de aprendizaje de cada optimizador, como pide expresamente el apartado 3.5.B; documentar también la elección de epsilon y la precisión/error observado en el gradient check.
- Actualizar `auditoria/VALIDACION_HUMANA.md` con la revisión de las correcciones y CSV actuales, identificando responsable, método, evidencia y resultado; volver a evaluar las observaciones aceptadas/rechazadas con el texto del enunciado a la vista.
- Revisar este handoff como estudiantes antes de considerarlo aceptado. El archivo se presenta como borrador del agente auditor.
- La imagen base y las dependencias no están fijadas a versiones exactas, por lo que una reconstrucción futura no garantiza entornos idénticos. PyTorch aparece instalado dos veces en el Dockerfile; no se evaluó aquí el efecto de esa duplicación.
- El informe y los registros de ejecución no demuestran aislamiento técnico de Codex en Windows ni conectividad de red; las inspecciones Docker de Parte 0 tampoco probaron tráfico entre contenedores ni salida a Internet.
- La auditoría original indica que no ejecutó scripts ni volvió a generar salidas. Las ejecuciones y artefactos actuales se atribuyen al estudiante, según la información proporcionada. No se reprodujeron en esta preparación del handoff.

Este documento resume el estado que puede respaldarse con los archivos disponibles. No declara completada la Parte 1 ni reemplaza el informe final, los registros de ejecución o la validación individual requeridos.
