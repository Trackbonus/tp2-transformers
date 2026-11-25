# Registro de prompts de infraestructura y auditoría de Parte 0

Registrar cronológicamente los prompts enviados al agente auditor, la herramienta/modelo, el propósito, el orden y los archivos/resultados asociados. Incluir los prompts accesibles de delegaciones automáticas; no incluir secretos ni razonamiento privado del modelo.

## Entradas

La numeración sigue el orden cronológico reconstruido a partir de las sesiones locales accesibles. No todas las fechas pudieron recuperarse; cuando faltan, el orden indicado es relativo y no se atribuye una fecha exacta.

## Prompts reales de preparación de infraestructura de Parte 0

Las entradas siguientes son instrucciones del usuario dirigidas a Codex durante el diseño, implementación y documentación de la infraestructura. **No son prompts enviados al agente auditor**, y no prueban que Codex se haya ejecutado dentro de Docker. Se transcriben del historial disponible; el modelo específico y las fechas de cada mensaje no están registrados.

### 1. Propuesta inicial de diseño

- Herramienta/agente: Codex; modelo específico no indicado.
- Propósito: proponer la configuración de infraestructura antes de editar.
- Archivos/resultados asociados: propuesta en conversación para `compose.yaml`, `Dockerfile`, `README.md` y `requirements.txt`; no se solicitó una modificación en ese mensaje.

```text
Quiero implementar la infraestructura exigida.

Propón el diseño de los siguientes archivos:
- compose.yaml
- Dockerfile
- README.md
- requirements.txt (si corresponde)

Considera obligatoriamente:

1. Tres servicios: teoria, practica y auditoria.
2. teoria solo debe tener acceso a parte1/.
3. practica solo debe tener acceso a parte2/.
4. auditoria debe poder leer parte1/ y parte2/ mediante
   montajes de solo lectura, y escribir en auditoria/.
5. Límites: 2 CPU y 2 GiB para teoria; 2 CPU y 4 GiB
   para practica; 2 CPU y 2 GiB para auditoria.
6. Imágenes ligeras de Python y dependencias reproducibles.
7. Ejecución como usuario no root.
8. No montar el directorio personal, claves de API ni docker.sock.
9. No utilizar GPU.

Además:
- Explica cómo se garantiza que teoria y practica no puedan
  acceder a los archivos de la otra parte.
- Propón pruebas concretas para verificar todos los permisos.
- Explica cómo ejecutar comandos en cada servicio.
- Distingue el aislamiento de Docker del aislamiento de
  las sesiones de Codex, que actualmente se ejecuta en Windows.

No modifiques archivos todavía. Presenta primero la propuesta
y señala cualquier limitación.
```

### 2. Ajustes a la propuesta

- Herramienta/agente: Codex; modelo específico no indicado.
- Propósito: corregir el ciclo de vida del contenedor, no asumir permisos de bind mounts, evitar redes innecesarias y preparar dependencias.
- Archivos/resultados asociados: propuesta revisada en conversación; todavía sin editar archivos.

```text
La propuesta está bien encaminada. Quiero que ajustes algunos puntos:

1. Cambia el comando de los tres servicios para que los contenedores
   permanezcan activos y podamos utilizar docker compose exec.
   Puedes utilizar sleep infinity.

2. Considera que read_only: true protege el sistema de archivos
   del contenedor, pero los montajes bind siguen teniendo sus
   propios permisos. No asumas que el usuario 10001 puede escribir
   en las carpetas de Windows: debemos comprobarlo en la práctica.

3. No necesitamos comunicación entre los servicios ni publicar
   puertos. Evita agregar redes innecesarias.

4. Deja prevista la instalación reproducible de requirements.txt
   en el Dockerfile, aunque inicialmente no instalemos paquetes
   adicionales si todavía no están definidos.

5. Actualiza la sección de limitaciones: Docker Desktop ya está
   funcionando. Mi último docker info confirmó el servidor activo,
   con contexto desktop-linux.

6. Mantén la separación de montajes y todos los límites de recursos
   establecidos en el enunciado.

Presenta la propuesta corregida. No modifiques archivos todavía.
```

### 3. Implementación de infraestructura aprobada

- Herramienta/agente: Codex; modelo específico no indicado.
- Propósito: implementar archivos de configuración, documentación y estructura inicial; validar y construir sin iniciar servicios.
- Archivos/resultados asociados: `compose.yaml`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `README.md`, documentación inicial de auditoría y carpetas del proyecto; `docker compose config` y `docker compose build` se ejecutaron según los mensajes de ejecución registrados en la conversación.

```text
La propuesta corregida está aprobada. Puedes implementar la infraestructura.

Realiza lo siguiente:

1. Crea `compose.yaml` y `Dockerfile` siguiendo la propuesta.
2. Agrega `init: true` a los tres servicios.
3. Crea `requirements.txt`, inicialmente vacío.
4. Crea `.dockerignore` para excluir los directorios de trabajo, el enunciado, `.git/` y `.vscode/` del contexto de construcción.
5. Crea `README.md` con instrucciones concretas para construir, iniciar, comprobar y detener los servicios.
6. Completa la estructura de directorios exigida por el enunciado, incluyendo los archivos de documentación iniciales que correspondan. No inventes resultados de pruebas.
7. No modifiques el PDF ni el texto original del enunciado.

Después de implementar:

- Muéstrame el contenido de los archivos creados.
- Ejecuta `docker compose config`.
- Si la configuración es válida, ejecuta `docker compose build`.
- No inicies todavía los contenedores ni declares verificadas las pruebas de aislamiento.
- Informa cualquier error encontrado y cómo lo resolviste.

Quiero que expliques brevemente las decisiones técnicas y mantengas la documentación en español.
```

### 4. Revisión final de la implementación de infraestructura

- Herramienta/agente: Codex; modelo no indicado.
- Fecha/orden: 7 de noviembre de 2026, después de la implementación inicial y antes de los ajustes de red posteriores, según el historial de esa sesión.
- Propósito: revisar estructura y configuración sin modificar ni iniciar contenedores.
- Archivos/resultados asociados: consulta del árbol del proyecto, `compose.yaml`, montajes/límites y resultados previamente reportados de `docker compose config` y `docker compose build`. No se pidió modificar archivos.
- Prompt textual recuperado:

```text
Haz una revisión final de la implementación de la Parte 0.

1. Muestra el árbol completo de directorios y archivos.
2. Confirma que existen los tres servicios en compose.yaml.
3. Resume los montajes, permisos y límites de CPU/RAM de cada uno.
4. Confirma que docker compose config y docker compose build
   terminaron correctamente.
5. Indica qué archivos de documentación están creados y cuáles
   siguen pendientes.
6. No modifiques nada ni inicies los contenedores.
```

### 5. Revisión de las consecuencias de `network_mode: none`

- Herramienta/agente: Codex; modelo específico no indicado.
- Propósito: evaluar el impacto en servicios remotos y proponer redes con salida a Internet y aislamiento entre servicios; investigar la advertencia de acceso al archivo de configuración Docker.
- Archivos/resultados asociados: análisis en conversación; no se modificaron archivos en ese mensaje.

```text
Quiero revisar dos aspectos de la infraestructura.

1. Explica las consecuencias de utilizar network_mode: none
   en los tres servicios, especialmente para ejecutar agentes
   remotos que necesitan conectarse a Internet.

2. Propón una alternativa que permita conexiones salientes
   a Internet, pero mantenga aislados los tres servicios
   entre sí y sin publicar puertos.

3. Investiga la advertencia:
   Error loading config file:
   C:\Users\sebau\.docker\config.json: Access is denied.

   Identifica su posible causa y propone cómo solucionarla
   sin modificar permisos ni archivos todavía.

No modifiques ningún archivo ni inicies los contenedores.
```

### 6. Cambio de redes en Compose

- Herramienta/agente: Codex; modelo específico no indicado.
- Propósito: reemplazar `network_mode: none` por tres redes bridge independientes y validar la configuración.
- Archivos/resultados asociados: `compose.yaml`; `docker compose config` terminó correctamente según la salida registrada en la conversación. No se iniciaron contenedores en respuesta a ese prompt.

```text
Implementa el cambio de red en compose.yaml:

- Elimina network_mode: none de los tres servicios.
- Crea una red bridge independiente para teoria, practica y auditoria.
- Cada servicio debe conectarse exclusivamente a su propia red.
- No agregues puertos publicados.
- Mantén intactos los demás parámetros de seguridad,
  recursos, usuarios y volúmenes.

Después ejecuta docker compose config para validar
la configuración.

No inicies los contenedores ni declares pruebas de
aislamiento como realizadas. Muéstrame el diff.
```

### 7. Registro de pruebas de Parte 0, apartado 2.5

- Herramienta/agente: Codex; modelo específico no indicado.
- Propósito: documentar resultados de pruebas ya ejecutadas, distinguirlos de inferencias y dejar pendiente la auditoría independiente.
- Archivos/resultados asociados: `auditoria/verificaciones/infraestructura.md`, `auditoria/VALIDACION_HUMANA.md`, `auditoria/HANDOFF.md` y revisión de `README.md`/registros de prompts.

```text
Quiero completar la documentación de las pruebas de infraestructura de la Parte 0, apartado 2.5 del enunciado.

Primero, lee el enunciado completo y revisa los archivos actuales del proyecto, especialmente:

- `compose.yaml`
- `Dockerfile`
- `requirements.txt`
- `README.md`
- `auditoria/HANDOFF.md`
- `auditoria/VALIDACION_HUMANA.md`
- `auditoria/verificaciones/`
- Los tres archivos `PROMPTS.md`.

**No modifiques `compose.yaml`, `Dockerfile`, `requirements.txt` ni los archivos de las partes 1 y 2. No inicies ni detengas contenedores.**

Registra en `auditoria/verificaciones/` las pruebas que ya se ejecutaron, utilizando exclusivamente estos resultados confirmados:

1. `docker compose up -d`: los tres servicios iniciaron correctamente y se crearon tres redes independientes.
2. `docker compose ps`: los tres contenedores aparecen en estado `Up`, sin puertos publicados.
3. `docker compose exec [servicio] python --version`: los tres ejecutaron Python 3.12.16.
4. Teoría: puede escribir en `/workspace/parte1` y no tiene acceso a `/workspace/parte2`.
5. Práctica: puede escribir en `/workspace/parte2` y no tiene acceso a `/workspace/parte1`.
6. Auditoría: puede leer archivos de `/workspace/parte1` y `/workspace/parte2`; los intentos de escritura en ambos montajes fallaron con `EROFS` (read-only file system); puede escribir en `/workspace/auditoria`.
7. La lectura efectiva de `parte1/PROMPTS.md` y `parte2/PROMPTS.md` fue exitosa.

Conserva los comandos y salidas relevantes. Distingue claramente pruebas ejecutadas de características inferidas de la configuración. No inventes resultados ni afirmes que se probaron cosas que no se probaron.

Actualiza `VALIDACION_HUMANA.md` con los resultados y pendientes reales.

Actualiza `HANDOFF.md` para describir la arquitectura efectiva, contrastando `compose.yaml` y `Dockerfile`: servicios, imagen, CPU/RAM, montajes, permisos, redes, dependencias, herramientas de IA y limitaciones. Indica expresamente que Codex se ejecutó en Windows, no dentro de los contenedores. No afirmes que el agente auditor ya fue ejecutado de forma independiente.

Revisa el README y los PROMPTS.md. Si falta documentación exigida, propón los cambios, pero no inventes interacciones con agentes ni prompts que no se hayan usado.

Al terminar, muestra un resumen de archivos modificados y pendientes. No ejecutes pruebas nuevas ni declares completado el apartado 2.5: la auditoría independiente todavía está pendiente.
```

### 8. Auditoría independiente de la Parte 0

- Herramienta/agente: Codex en una sesión nueva; modelo específico no identificable en la evidencia conservada.
- Fecha/orden: 7 de noviembre de 2026; sesión titulada «Auditar infraestructura de Parte 0», posterior a la preparación inicial.
- Propósito: evaluar de forma independiente la Parte 0 con inspección documental, sin ejecutar Docker ni pruebas nuevas.
- Archivos consultados indicados por el prompt: enunciado, `compose.yaml`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `README.md`, `auditoria/HANDOFF.md`, `auditoria/VALIDACION_HUMANA.md`, `auditoria/PROMPTS.md`, `auditoria/verificaciones/infraestructura.md` y documentación de auditoría pertinente.
- Archivos/resultados asociados: se creó `auditoria/verificaciones/auditoria_independiente.md` y se actualizó este registro. El informe clasifica requisitos, hallazgos y límites; afirma que fue una auditoría documental y no una ejecución de pruebas.
- Naturaleza del prompt: transcripción textual recuperada del archivo adjunto de la sesión (`.codex/attachments/5e552186-2e43-47f6-b27a-cbd8ea29fd98/Pasted text.txt`), reproducida íntegramente abajo.

```text
# Auditoría independiente de la Parte 0 – TP2 Transformers

Actúa como auditor independiente de la implementación de infraestructura de la Parte 0 del trabajo práctico.

Esta es una sesión nueva. No debes asumir que las decisiones tomadas durante el desarrollo son correctas: verifica cada afirmación contrastándola con el enunciado y los archivos actuales del proyecto.

## 1. Objetivo

Determinar si la implementación cumple los requisitos de la Parte 0, identificar incumplimientos, riesgos, inconsistencias y aspectos que no pueden verificarse con la evidencia disponible.

La auditoría debe ser crítica e independiente. No busques justificar las decisiones de implementación.

## 2. Material que debes revisar

Lee el enunciado completo de la Parte 0 y contrástalo con:

- `compose.yaml`
- `Dockerfile`
- `.dockerignore`
- `requirements.txt`
- `README.md`
- `auditoria/HANDOFF.md`
- `auditoria/VALIDACION_HUMANA.md`
- `auditoria/PROMPTS.md`
- `auditoria/verificaciones/infraestructura.md`
- El resto de los archivos de documentación de `auditoria/` que sean relevantes.

Si no encuentras el enunciado completo, indícalo expresamente y no supongas cuáles son sus requisitos.

## 3. Aspectos que debes evaluar

Revisa, como mínimo:

1. Existencia de los tres servicios: `teoria`, `practica` y `auditoria`.
2. Separación de los directorios y montajes disponibles para cada servicio.
3. Permisos de lectura y escritura de cada servicio.
4. Límites de CPU y memoria.
5. Uso de usuario no root.
6. Protección del sistema de archivos y uso de directorios temporales.
7. Redes: aislamiento entre servicios, conectividad saliente y ausencia de puertos publicados.
8. Imágenes utilizadas y reproducibilidad de las dependencias.
9. Ausencia de montajes innecesarios, directorio personal, credenciales, `docker.sock` y privilegios elevados.
10. Documentación de comandos para construir, iniciar, comprobar y detener los servicios.
11. Calidad y suficiencia de las evidencias de las pruebas.
12. Correspondencia entre la arquitectura real, el HANDOFF y el README.
13. Cumplimiento del requisito de auditoría independiente.

## 4. Restricciones importantes

Esta auditoría se ejecuta desde Codex en Windows, fuera de los contenedores Docker.

Por tanto:

- No afirmes que los montajes de solo lectura del contenedor `auditoria` restringen automáticamente los permisos de esta sesión de Codex.
- No confundas independencia de contexto conversacional con aislamiento técnico de permisos.
- Distingue las restricciones configuradas en Docker de las restricciones efectivas de las herramientas que se ejecutan en Windows.
- No declares que se ha comprobado un permiso si solo se deduce de la configuración.
- No presentes pruebas documentadas como si las hubieras ejecutado personalmente.
- No inventes resultados ni evidencias.

**No ejecutes comandos de Docker, no inicies ni detengas contenedores y no realices pruebas nuevas.** Esta auditoría debe basarse en la inspección del enunciado, la configuración y las evidencias documentadas.

## 5. Clasificación de hallazgos

Para cada requisito, utiliza uno de estos estados:

- **Cumplido:** existe evidencia suficiente.
- **Parcialmente cumplido:** se cumple solo una parte o la evidencia es incompleta.
- **No cumplido:** existe un incumplimiento identificable.
- **No verificable:** no hay evidencia suficiente para determinarlo.

Para cada hallazgo incluye:

- Requisito relacionado.
- Estado.
- Evidencia concreta (archivo y sección o líneas, cuando sea posible).
- Explicación del problema o justificación del cumplimiento.
- Gravedad: alta, media o baja.
- Recomendación, si corresponde.

Distingue claramente los problemas reales de las mejoras opcionales.

## 6. Entregable

Crea el archivo:

`auditoria/verificaciones/auditoria_independiente.md`

Debe contener:

1. Alcance y metodología de la auditoría.
2. Archivos revisados.
3. Tabla de evaluación de requisitos.
4. Hallazgos detallados, ordenados por gravedad.
5. Inconsistencias entre documentación y configuración.
6. Limitaciones de la auditoría.
7. Conclusión general: si la Parte 0 puede considerarse cumplida, parcialmente cumplida o pendiente.

Actualiza también `auditoria/PROMPTS.md` para registrar este prompt como la primera instrucción enviada al agente auditor. Identifica la herramienta utilizada y el modelo, únicamente si puedes comprobarlos; no inventes esos datos.

## 7. Límites de modificación

Puedes crear el informe anterior y actualizar `auditoria/PROMPTS.md`.

No modifiques:

- `compose.yaml`
- `Dockerfile`
- `.dockerignore`
- `requirements.txt`
- `README.md`
- `parte1/`
- `parte2/`
- Los demás archivos de auditoría.

No corrijas los problemas que encuentres: tu función es identificarlos y documentarlos para que podamos decidir posteriormente cómo resolverlos.

Al finalizar, muestra el contenido completo de `auditoria_independiente.md`, el diff de `PROMPTS.md` y confirma qué archivos modificaste.
```

### 9. Verificaciones complementarias de infraestructura

- Herramienta/agente: Codex; modelo no indicado.
- Fecha/orden: sesión posterior a la auditoría inicial; el historial disponible sitúa las verificaciones complementarias el 7 de noviembre de 2026.
- Propósito: inspeccionar identidad efectiva, límites de recursos, redes y reproducibilidad, y guardar evidencia sin cambiar infraestructura.
- Archivos asociados: se pidió crear `auditoria/verificaciones/verificaciones_complementarias.md`; no modificar configuración ni el informe inicial. Los resultados quedaron en el archivo referido desde el handoff.
- Prompt textual recuperado de la sesión local:

````text
# Verificaciones complementarias de infraestructura – Parte 0

A partir de los hallazgos de `auditoria/verificaciones/auditoria_independiente.md`, quiero completar algunas verificaciones técnicas pendientes de la Parte 0.

En esta etapa tu función es exclusivamente verificar y recopilar evidencia. No debes modificar la infraestructura ni corregir archivos.

## 1. Verificación del usuario efectivo

Comprueba el usuario efectivo de los tres servicios:
```bash
docker compose exec teoria id
docker compose exec practica id
docker compose exec auditoria id
```

Registra las salidas completas y comprueba si los tres servicios se ejecutan con UID/GID 10001, sin privilegios de root.

## 2. Verificación de límites de recursos

Inspecciona los límites efectivos de CPU y memoria configurados en los tres contenedores mediante `docker inspect`.

Comprueba que correspondan a:

| Servicio  | CPU | Memoria |
| --------- | --- | ------- |
| teoria    | 2   | 2 GiB   |
| practica  | 2   | 4 GiB   |
| auditoria | 2   | 2 GiB   |

No confundas límites máximos con memoria reservada ni con consumo actual.

Registra los comandos utilizados, las salidas relevantes y una interpretación breve.

## 3. Verificación de redes

Inspecciona las redes Docker y las conexiones de cada contenedor.

Comprueba:

- Que cada servicio esté conectado exclusivamente a su propia red.
- Que las tres redes sean distintas.
- Que no existan puertos publicados.
- Que la configuración no conecte directamente los servicios entre sí.

Puedes utilizar `docker inspect` y `docker network inspect`.

**Importante:** esta inspección permite comprobar la configuración de redes, pero no demuestra por sí sola la conectividad efectiva a Internet ni la imposibilidad de comunicarse entre servicios. No afirmes que esas pruebas se realizaron.

## 4. Revisión de reproducibilidad

Revisa `Dockerfile` y `requirements.txt`.

Determina:

- Qué versión de Python se utiliza.
- Si la imagen base está fijada por digest.
- Si existen dependencias adicionales.
- Si sus versiones están fijadas.
- Qué aspectos de la reconstrucción son reproducibles y cuáles no.

No cambies la imagen ni agregues dependencias.

## 5. Registro de evidencias

Crea el archivo:

`auditoria/verificaciones/verificaciones_complementarias.md`

Incluye:

1. Fecha de ejecución.
2. Objetivo de cada comprobación.
3. Comandos exactos ejecutados.
4. Salidas relevantes completas.
5. Resultado e interpretación.
6. Limitaciones de las comprobaciones.

Distingue claramente entre inspección de configuración y pruebas de comportamiento.

## 6. Restricciones

- No modifiques `compose.yaml`, `Dockerfile`, `.dockerignore`, `requirements.txt` ni ningún archivo de Parte 1 o Parte 2.
- No cambies los límites de recursos.
- No reconstruyas imágenes.
- No ejecutes `docker compose down`.
- No elimines ni reinicies contenedores.
- No modifiques el informe de auditoría independiente.
- No actualices todavía `HANDOFF.md`.
- No declares completada la Parte 0.

Puedes ejecutar los comandos de inspección y las comprobaciones indicadas, pero no realices pruebas adicionales fuera de este alcance.

## 7. Entrega

Al finalizar:

- Muestra el contenido completo de `verificaciones_complementarias.md`.
- Indica los comandos ejecutados y si todos terminaron correctamente.
- Señala cualquier discrepancia con la configuración documentada.
- Confirma que no modificaste ningún archivo fuera del nuevo registro de verificaciones.
````

### 10. Actualización documental posterior a las inspecciones

- Herramienta/agente: Codex; modelo no indicado.
- Propósito: incorporar al handoff y al informe independiente los resultados complementarios, manteniendo límites y afirmaciones respaldados.
- Archivos asociados: `auditoria/HANDOFF.md` y `auditoria/verificaciones/auditoria_independiente.md`; el prompt también restringió expresamente el resto de archivos. Los cambios aparecen descritos en ambos documentos.
- Prompt textual recuperado de la sesión local:

```text
# Actualización documental final – Parte 0

Quiero actualizar la documentación de la Parte 0 del TP2 Transformers a partir de los resultados de las verificaciones complementarias realizadas el 7 de noviembre de 2026.

Tu tarea es exclusivamente documental. Debes modificar únicamente estos dos archivos:

1. `auditoria/HANDOFF.md`
2. `auditoria/verificaciones/auditoria_independiente.md`

No modifiques ningún otro archivo.

## 1. Actualizar HANDOFF.md

Revisa su contenido actual y complétalo para que refleje fielmente el estado final de la infraestructura.

Incorpora los resultados de `auditoria/verificaciones/verificaciones_complementarias.md`, especialmente:

- Los tres servicios se ejecutan efectivamente con UID/GID 10001.
- Los límites efectivos son 2 CPU y 2 GiB para `teoria`, 2 CPU y 4 GiB para `practica`, y 2 CPU y 2 GiB para `auditoria`.
- Los límites de memoria son máximos, no reservas ni mediciones de consumo.
- Cada servicio está conectado a una red bridge independiente.
- Las inspecciones muestran un único contenedor por red y `PortBindings={}`.
- No se realizaron pruebas de tráfico entre contenedores ni de conectividad a Internet.
- La imagen base `python:3.12-slim-bookworm` no está fijada por digest.
- `requirements.txt` está vacío y no declara dependencias adicionales.

Conserva la información válida que ya existe en HANDOFF.md. No reemplaces el documento por un resumen ni elimines detalles importantes de arquitectura, comandos, montajes, permisos, redes o limitaciones.

Añade una referencia explícita a:

- `auditoria/verificaciones/auditoria_independiente.md`
- `auditoria/verificaciones/verificaciones_complementarias.md`

Explica brevemente qué contiene cada uno.

## 2. Actualizar auditoria_independiente.md

Revisa el informe original y actualízalo teniendo en cuenta las verificaciones complementarias.

Actualiza la evaluación de los hallazgos:

- **Usuario no root (B1):** cerrar como verificado. Las salidas de `id` confirman UID/GID 10001 en los tres servicios.
- **Límites efectivos de recursos:** cerrar como verificados mediante `docker inspect`.
- **Redes (M1):** actualizar la evaluación. La separación de redes y ausencia de puertos publicados están verificadas mediante inspección, pero la conectividad efectiva y el aislamiento de tráfico siguen sin probarse.
- **Reproducibilidad (M2):** mantener la observación. La imagen no está fijada por digest y `requirements.txt` está vacío.
- **Evidencias (M3):** actualizar indicando que ahora existen salidas completas de las inspecciones complementarias. Mantener la distinción entre esas salidas y las pruebas anteriores recuperadas de la conversación.
- **Pruebas de permisos (M4):** conservar las limitaciones originales. No afirmar que se realizaron pruebas nuevas de modificación de archivos ajenos.
- **Independencia de Codex (A1):** mantener la limitación. Una sesión nueva aporta independencia de contexto, pero no aislamiento técnico de los permisos de Codex en Windows.

No marques como cumplidas comprobaciones que no se realizaron.

## 3. Criterios de documentación

- Distingue siempre entre configuración declarada, inspección efectiva y comportamiento probado.
- No confundas límites de memoria con reservas o consumo.
- No afirmes que las redes impiden toda comunicación posible ni que carecen de acceso a Internet.
- No presentes la falta de fijación por digest como un error que obligue necesariamente a reconstruir la infraestructura.
- No declares la Parte 0 completamente cumplida si persisten limitaciones.
- Mantén un tono técnico, objetivo y coherente con el resto de los documentos.
- Evita repetir información innecesariamente entre ambos archivos; utiliza referencias cruzadas cuando corresponda.
- No inventes fechas, comandos, salidas, pruebas ni resultados.

## 4. Restricciones

- Modifica únicamente `auditoria/HANDOFF.md` y `auditoria/verificaciones/auditoria_independiente.md`.
- No modifiques `compose.yaml`, `Dockerfile`, `.dockerignore`, `requirements.txt`, README, PROMPTS ni ningún archivo de Parte 1 o Parte 2.
- No ejecutes comandos Docker ni pruebas adicionales.
- No reconstruyas imágenes ni reinicies contenedores.
- No elimines ni sobrescribas evidencia existente.
- No cambies la conclusión general de la auditoría a "completamente cumplida" sin fundamento.

## 5. Entrega

Al finalizar:

1. Muestra un resumen de los cambios realizados en cada archivo.
2. Confirma expresamente que solo modificaste los dos archivos autorizados.
3. Indica si encontraste contradicciones entre la documentación existente y las verificaciones nuevas.
4. Muestra la conclusión actualizada de la auditoría.
5. No realices ninguna otra modificación.
```

### 11. Revisión final de cumplimiento de Parte 0

- Herramienta/agente: Codex; modelo no indicado.
- Propósito: contrastar requisitos textuales de la Parte 0 con infraestructura y evidencias, distinguiendo requisitos obligatorios de recomendaciones.
- Archivos consultados: configuración raíz, documentación de auditoría y sus evidencias, detallados en la solicitud original.
- Archivos/resultados asociados: se pidió entregar una matriz en la conversación, sin modificar archivos ni ejecutar Docker. No se identifica un artefacto escrito por esta intervención.
- Prompt textual recuperado de la sesión local:

```text
# Revisión final de cumplimiento – Parte 0 del TP2 Transformers

Quiero realizar una revisión final de la Parte 0 del Trabajo Práctico 2, contrastando los requisitos del enunciado con la infraestructura implementada, la documentación y las evidencias disponibles.

Tu función es actuar como revisor técnico independiente. En esta etapa debes evaluar el cumplimiento, no corregir ni modificar el proyecto.

## 1. Alcance de la revisión

Lee íntegramente el apartado 2 del enunciado, incluidas sus subsecciones (2.1 a 2.5), y revisa los siguientes archivos:

- `compose.yaml`
- `Dockerfile`
- `.dockerignore`
- `requirements.txt`
- `README.md`
- `auditoria/PROMPTS.md`
- `auditoria/HANDOFF.md`
- `auditoria/VALIDACION_HUMANA.md`
- `auditoria/verificaciones/README.md`
- `auditoria/verificaciones/infraestructura.md`
- `auditoria/verificaciones/verificaciones_complementarias.md`
- `auditoria/verificaciones/auditoria_independiente.md`

Si el enunciado contiene requisitos adicionales dentro del apartado 2, inclúyelos también.

No revises el contenido académico de Parte 1 ni Parte 2, salvo cuando sea necesario comprobar algún requisito explícito de la infraestructura.

## 2. Método de evaluación

Construye una matriz que relacione cada requisito concreto del enunciado con:

- Requisito textual o paráfrasis fiel.
- Archivo, configuración o evidencia que lo respalda.
- Evaluación: **Cumplido**, **Parcialmente cumplido**, **No cumplido** o **No verificable**.
- Justificación técnica.
- Acción necesaria, si corresponde.

Es fundamental distinguir entre:

1. Requisitos obligatorios explícitos del enunciado.
2. Recomendaciones o buenas prácticas que no son exigencias explícitas.
3. Limitaciones documentadas que no necesariamente implican incumplimiento.

No conviertas automáticamente una mejora recomendable en un requisito obligatorio.

## 3. Consideraciones importantes

Ten en cuenta los resultados ya disponibles:

- Los tres servicios se ejecutan efectivamente con UID/GID 10001.
- Los límites efectivos de CPU y memoria fueron comprobados mediante `docker inspect`.
- Cada servicio está conectado a una red bridge independiente.
- Las inspecciones muestran un contenedor por red y `PortBindings={}`.
- No se realizaron pruebas de tráfico entre servicios ni de conectividad a Internet.
- Las pruebas de montajes y permisos están documentadas, pero algunas evidencias provienen de registros recuperados de conversaciones y no de logs originales.
- Codex se ejecuta en Windows, fuera de los contenedores. Una conversación nueva no constituye aislamiento técnico de sus permisos sobre los archivos del host.
- La imagen base `python:3.12-slim-bookworm` no está fijada por digest.
- `requirements.txt` está vacío.

No repitas pruebas que ya se realizaron ni inventes resultados.

## 4. Preguntas que debes resolver

Al finalizar la evaluación, responde explícitamente:

1. ¿Se cumplen todos los requisitos obligatorios del apartado 2?
2. ¿Qué requisitos siguen parcialmente cumplidos o no verificables?
3. ¿Cuáles son limitaciones de la solución y cuáles son incumplimientos reales?
4. ¿Es necesario modificar la infraestructura para cumplir el enunciado?
5. ¿Es necesario realizar nuevas pruebas o basta con la evidencia disponible?
6. ¿Qué cambios mínimos serían necesarios antes de entregar, si corresponde?

Presta especial atención a si el enunciado exige realmente:

- Aislamiento técnico de la sesión de Codex.
- Pruebas efectivas de conectividad o aislamiento de red.
- Fijación de la imagen Docker por digest.
- Logs originales de cada prueba.
- Pruebas de modificación de archivos ajenos.

No asumas que estos elementos son obligatorios sin encontrar respaldo en el texto del enunciado.

## 5. Conclusión final

Entrega una conclusión clara que diferencie:

- **Cumplimiento del enunciado:** si la Parte 0 satisface o no los requisitos obligatorios.
- **Calidad de la evidencia:** qué tan bien está respaldado ese cumplimiento.
- **Mejoras recomendables:** qué podría mejorarse sin ser necesariamente obligatorio.

No uses la conclusión de la auditoría independiente como sustituto de tu propia comparación con el enunciado.

Si concluyes que la Parte 0 está incompleta, identifica exactamente qué requisito textual no se satisface y qué acción concreta lo resolvería.

## 6. Restricciones

- No modifiques ningún archivo.
- No ejecutes comandos Docker.
- No reconstruyas imágenes ni reinicies contenedores.
- No agregues pruebas nuevas.
- No cambies la arquitectura.
- No declares incumplimientos basándote únicamente en buenas prácticas que el enunciado no exige.

Entrega el análisis completo en la conversación, con la matriz de cumplimiento y una recomendación final concreta sobre si la Parte 0 está lista para entregar.
```

### 12. Revisión de permisos de Codex en Windows

- Herramienta/agente: Codex; modelo no indicado.
- Propósito: determinar si los permisos externos de Codex ejecutado en Windows satisfacen el requisito de limitar al auditor, separando sandbox declarado y accesos efectivos.
- Archivos asociados: se pidió inspeccionar configuración efectiva de Codex, sin editar archivos ni cambiar permisos. Resultado no atribuido aquí porque la respuesta completa no quedó guardada en los documentos de auditoría consultados.
- Prompt textual recuperado de la sesión local:

```text
# Revisión de permisos y configuración de Codex – Parte 0

Necesito determinar si la ejecución de Codex en Windows cumple el requisito del enunciado que exige limitar los permisos externos del auditor cuando trabaja fuera de Docker.

## 1. Inspección de configuración

Revisa la configuración efectiva de Codex y los mecanismos de sandbox disponibles en el entorno actual.

Presta especial atención a:

- `sandbox` y su valor efectivo.
- Políticas de aprobación y ejecución de comandos.
- Restricciones de lectura y escritura de archivos.
- Directorio de trabajo autorizado.
- Posibilidad de limitar al auditor para que lea los archivos de Parte 1 y Parte 2 y escriba exclusivamente en `auditoria/`.

## 2. Evaluación

Determina si la configuración actual proporciona aislamiento técnico efectivo o si Codex conserva acceso a otros archivos del host.

Distingue entre:

- Configuración declarada.
- Restricciones efectivamente aplicadas.
- Permisos que siguen disponibles.

Evalúa si existe un mecanismo compatible con Windows para restringir efectivamente los permisos de una sesión de auditoría.

## 3. Sesiones de teoría y práctica

Considera que, según la información disponible, Parte 1 y Parte 2 aparentemente se trabajaron desde una misma conversación de Codex.

No inventes sesiones independientes ni intentes reconstruir una separación que no existió.

Indica cómo debe documentarse honestamente esta situación y si existe alguna forma de mitigarla sin rehacer el trabajo académico.

## 4. Restricciones

- No modifiques ningún archivo.
- No cambies `config.toml`.
- No modifiques permisos de Windows.
- No alteres la configuración de Docker.
- No ejecutes pruebas destructivas.
- No afirmes que existe aislamiento si solo hay separación de contexto.
- No realices cambios sin autorización.

## 5. Entrega

Presenta:

1. Configuración efectiva encontrada.
2. Restricciones reales de acceso.
3. Brechas respecto del enunciado.
4. Alternativas concretas para resolverlas.
5. Recomendación mínima para dejar la Parte 0 correctamente documentada y, si es posible, cumplir el requisito pendiente.
```

## Delegaciones automáticas

Se revisaron las sesiones locales listadas en `session_index.jsonl` y los registros accesibles de la sesión de auditoría. No se encontró en ellos un prompt enviado a un subagente o una delegación automática asociada a la auditoría de Parte 0. No se encontró el directorio `.agents/` en el workspace ni un registro de delegaciones recuperable en los archivos accesibles. No se puede afirmar que no hubiera delegaciones fuera del historial conservado; sus prompts no están disponibles para transcribir.

## Límites de recuperación

El registro conserva los siete prompts de infraestructura ya transcritos, incorpora íntegro el prompt inicial de auditoría independiente y transcribe literalmente los prompts recuperados de las entradas 9–12. La numeración refleja el orden cronológico reconstruido; algunas fechas exactas no están disponibles. El modelo específico no está identificado. No se inventan salidas de herramientas ni archivos modificados cuando no aparecen respaldados en el historial o los documentos presentes.

## Parte 2: Auditoría del desarrollo aplicado

### Alcance y naturaleza de este registro

Esta sección propone instrucciones para orientar una auditoría del desarrollo aplicado de la Parte 2. Los prompts siguientes son **ejemplos reconstruidos**, no transcripciones literales de conversaciones. Describen tareas que el agente auditor debería realizar; no acreditan que esas verificaciones ya se hayan ejecutado. No se atribuyen resultados ni hallazgos sin evidencia documentada.

### Prompts representativos reconstruidos

#### 1. Estructura y reproducibilidad

> Revisa la organización de `parte2/codigo`, `parte2/datos` y `parte2/resultados`. Contrasta las rutas que usan los scripts con los archivos existentes; identifica dependencias, entradas y salidas esperadas. Separa lo que puede confirmarse por inspección de lo que requeriría reproducir una ejecución.

#### 2. Dataset y división

> Examina la auditoría del dataset de reseñas de Metal Archives y la división train/validation/test. Contrasta los 2.000 registros y revisa el uso de `GroupShuffleSplit` agrupado por banda. Verifica en los CSV que no haya bandas compartidas ni registros perdidos, sin asumir que las aserciones del script prueban por sí solas el estado de los archivos ya generados.

#### 3. Modelos y experimentos

> Inspecciona la implementación de TF-IDF + Ridge y DistilBERT para regresión. Revisa la optimización de hiperparámetros y confirma qué conjunto se usa para seleccionar configuraciones. Contrasta las rutas de los modelos seleccionados con las que carga el evaluador final.

#### 4. Resultados

> Contrasta las métricas de MAE y RMSE con los CSV y JSON generados para validation y test. Comprueba que la comparación final corresponda a los modelos seleccionados y que test no se use para nuevos ajustes. Registra las discrepancias con la ruta del archivo fuente y no inventes cifras.

#### 5. Seguridad y aislamiento

> Revisa `compose.yaml` y `Dockerfile`: por servicio, documenta usuario, límites de CPU y memoria, montajes, permisos, redes y acceso a GPU. Comprueba la separación entre servicios y si el contenedor auditor puede escribir en los directorios de Parte 1 y Parte 2. Distingue la configuración estática de las pruebas efectivas de permisos; no declares una prueba runtime como realizada si no hay comando y evidencia de salida.

### Estado de las verificaciones

Las instrucciones anteriores constituyen un plan de auditoría reconstruido, no un registro de ejecución. La inspección de los archivos del repositorio puede respaldar observaciones estáticas sobre rutas, código, resultados persistidos y configuración Docker. La ausencia de bandas compartidas o registros perdidos debe verificarse contra los CSV actuales; la capacidad efectiva de escritura debe probarse en el entorno pertinente y documentarse con evidencia. Esta sección no afirma que el agente auditor haya ejecutado esas comprobaciones ni anticipa sus hallazgos.