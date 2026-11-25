# Auditoría independiente de la Parte 0

Fecha: 2026-11-07

## Alcance y metodología

La auditoría inicial contrastó el apartado 2 completo del enunciado (secciones 2.1–2.5) con la configuración y los registros disponibles, sin ejecutar Docker ni pruebas. Posteriormente, el 7 de noviembre de 2026, se realizaron las inspecciones complementarias de usuario efectivo, límites, redes/puertos y configuración de dependencias documentadas en `verificaciones/verificaciones_complementarias.md`. Estas inspecciones no incluyeron pruebas de tráfico ni nuevas pruebas de permisos sobre archivos. Los resultados anteriores de permisos y arranque siguen tratados como confirmaciones atribuidas al usuario, no como pruebas ejecutadas por esta auditoría.

Esta auditoría se realizó en una conversación nueva de Codex, como pidió el prompt. Eso aporta independencia de contexto conversacional, pero no demuestra aislamiento técnico de permisos: las herramientas de esta sesión se ejecutan en Windows y tienen acceso al workspace del anfitrión. Los montajes de `auditoria` en Compose no restringen por sí solos esos permisos.

El enunciado se encontró como `enunciado/Trabajo Práctico 2.pdf` y como extracción textual `enunciado/enunciado.txt`. Se revisó en particular el apartado 2, incluidas las pruebas obligatorias del 2.5. Los requisitos citados en este informe se ubican en 2.1 (aislamiento), 2.2 (preparación y configuración), 2.3 (sesiones del agente) y 2.5 (evidencias y handoff).

## Archivos revisados

- `enunciado/Trabajo Práctico 2.pdf` y `enunciado/enunciado.txt`.
- `compose.yaml`, `Dockerfile`, `.dockerignore`, `requirements.txt`, `README.md`.
- `auditoria/HANDOFF.md`, `auditoria/VALIDACION_HUMANA.md`, `auditoria/PROMPTS.md`.
- `auditoria/verificaciones/infraestructura.md` y `auditoria/verificaciones/README.md`.
- `auditoria/verificaciones/verificaciones_complementarias.md`.

No se revisó el contenido de los proyectos `parte1/` y `parte2/`: no es necesario para valorar la configuración de Parte 0 y el alcance pedido se centra en infraestructura y evidencia.

## Tabla de evaluación

| Requisito | Estado | Evidencia principal | Gravedad si hay brecha |
|---|---|---|---|
| Tres servicios con nombres exigidos | Cumplido | `compose.yaml:1-2,23,41`; `infraestructura.md`, sección 3 | — |
| Separación de montajes y rol auditor | Cumplido según configuración y evidencia reportada | `compose.yaml:18-21,36-39,55-65`; pruebas reportadas en `infraestructura.md`, sección 3 | — |
| Permisos efectivos sobre bind mounts | Parcialmente cumplido | `infraestructura.md`, sección 3; comandos/salidas originales no adjuntos | Media |
| Límites de CPU/RAM | Cumplido y verificado mediante inspección | `docker inspect`, registrado en `verificaciones_complementarias.md`, sección 2 | — |
| Usuario no root | Cumplido y verificado mediante `id` | Salidas de los tres servicios en `verificaciones_complementarias.md`, sección 1 | — |
| Filesystem de imagen protegido y temporales | Cumplido según configuración | `compose.yaml:15-17,33-35,51-53`; `Dockerfile:9-10` | — |
| Redes separadas y sin puertos publicados | Configuración y membresías inspeccionadas; comportamiento de tráfico no probado | `docker inspect` y `docker network inspect`, `verificaciones_complementarias.md`, secciones 2–3 | Media |
| Imágenes y dependencias reproducibles | Parcialmente cumplido | `Dockerfile:1,14-18`; `requirements.txt` vacío; `README.md:76-78` | Media |
| Sin mounts de home/credenciales/socket ni privilegios elevados | Cumplido en la configuración inspeccionada | `compose.yaml` completo; `.dockerignore` | — |
| Comandos de build, inicio, comprobación y detención | Cumplido documentalmente | `README.md:21-50,65-74` | — |
| Evidencia de pruebas suficiente y reproducible | Parcialmente cumplido | `infraestructura.md`, secciones 1–4; `verificaciones_complementarias.md`; `VALIDACION_HUMANA.md:5-17` | Media |
| Correspondencia entre arquitectura y handoff/README | Cumplido con las limitaciones explícitas documentadas | `HANDOFF.md`; `README.md:11-19,76-82`; configuración e inspecciones referenciadas | — |
| Auditoría independiente, sesión y hallazgos en `auditoria/` | Parcialmente cumplido | Este informe y `PROMPTS.md`; independencia conversacional sí, aislamiento técnico de Codex en Windows no demostrado | Alta para completar 2.5 |

## Hallazgos detallados

### Gravedad alta

#### A1. Independencia de contexto no equivale a aislamiento de permisos del auditor

- **Requisito:** 2.1 y 2.3 requieren controlar qué archivos puede leer cada agente y usar una sesión nueva e independiente para auditoría.
- **Estado:** Parcialmente cumplido.
- **Evidencia:** `compose.yaml:55-65` limita los montajes del contenedor `auditoria`; `HANDOFF.md` advierte que Codex se ejecutó en Windows fuera de Docker y que las herramientas del anfitrión no quedan confinadas por esos mounts. La solicitud de la auditoría especifica una conversación nueva. En esa sesión, las herramientas del anfitrión tuvieron acceso al workspace del proyecto.
- **Evaluación:** Hay independencia del contexto conversacional en la sesión actual, y el informe se escribe bajo `auditoria/`. No hay evidencia de que el proceso Codex haya corrido dentro del contenedor ni de que sus permisos de Windows estuvieran restringidos a `auditoria/`. Por ello no puede afirmarse que se cumplió el aislamiento técnico del auditor. Esto coincide con la limitación explícita del enunciado para clientes ejecutados en el anfitrión.
- **Recomendación:** Mantener en el handoff el mecanismo realmente usado y la falta de prueba sobre permisos externos. No describir los mounts de Docker como controles efectivos de esta sesión Windows.

### Gravedad media

#### M1. Redes separadas y puertos inspeccionados; tráfico no probado

- **Requisito:** 2.2–2.3 requieren arquitectura reproducible que permita el flujo de trabajo con agentes; el diseño documenta salida a Internet.
- **Estado:** Parcialmente cumplido.
- **Evidencia:** `docker inspect` mostró una única red por contenedor y `PortBindings={}`; `docker network inspect` mostró tres IDs distintos, driver `bridge` y un solo contenedor miembro en cada red. Los comandos y salidas están en `verificaciones/verificaciones_complementarias.md`, secciones 2–3. `compose.yaml:13-14,31-32,49-50,67-73` declara esas redes sin membresías compartidas.
- **Evaluación:** La separación de redes, la membresía observada y la ausencia de puertos publicados están verificadas mediante inspección. No se probaron tráfico entre contenedores ni conectividad a Internet. `Internal=false` tampoco demuestra por sí solo la conectividad efectiva; la inspección no permite afirmar que toda comunicación posible esté impedida.
- **Recomendación:** Mantener el alcance de la conclusión limitado a configuración y membresías observadas. Registrar por separado cualquier prueba de tráfico que se realice en el futuro.

#### M2. La reproducibilidad de imagen y dependencias es incompleta

- **Requisito:** 2.2 pide imágenes ligeras de Python con dependencias documentadas y reproducibles.
- **Estado:** Parcialmente cumplido.
- **Evidencia:** `Dockerfile:1` usa `python:3.12-slim-bookworm` por etiqueta mutable, sin digest. `Dockerfile:14-18` instala desde `requirements.txt` solo cuando no está vacío. `requirements.txt` está vacío. `README.md:76-78` reconoce que fijar la imagen por digest queda como mejora futura.
- **Evaluación:** La imagen es liviana y la instalación de paquetes queda centralizada en build; actualmente no hay dependencias adicionales que fijar. La etiqueta no fija una imagen inmutable, y no hay versiones ni hashes de paquetes si en el futuro se agregan. La reproducibilidad exacta del entorno no queda asegurada.
- **Recomendación:** Si el curso exige reproducibilidad fuerte, fijar una versión/digest de imagen y mantener dependencias con versiones exactas (y, cuando proceda, hashes), documentando cómo actualizarlas.

#### M3. Algunas pruebas están registradas como confirmaciones, sin logs originales

- **Requisito:** 2.5 solicita conservar comandos ejecutados, salidas relevantes y comprobaciones.
- **Estado:** Parcialmente cumplido.
- **Evidencia:** `infraestructura.md`, “Procedencia y formato de evidencia” y sección 3, declara que los resultados fueron confirmados por el usuario, pero no son logs originales; fecha, responsable nominal y algunos comandos exactos no se informaron. `VALIDACION_HUMANA.md:5-17` indica igualmente que las salidas completas no están adjuntas.
- **Evaluación:** Ahora hay comandos y salidas completas relevantes para las inspecciones complementarias de identidad, límites, redes y puertos, además de la revisión estática del Dockerfile y dependencias; constan en `verificaciones/verificaciones_complementarias.md`. Esto es evidencia nueva de inspección, distinta de los resultados anteriores de arranque y permisos, que fueron recuperados/confirmados desde la conversación y no cuentan con logs originales completos. Las inspecciones no constituyen pruebas de comportamiento de red ni nuevas pruebas de permisos.
- **Recomendación:** Conservar ambas procedencias diferenciadas. Para las pruebas anteriores, adjuntar logs originales, fecha y comandos exactos si están disponibles; no reconstruir salidas ausentes.

#### M4. Las pruebas de usuario y permisos no cubren expresamente todos los requisitos

- **Requisito:** 2.5 exige confirmar que los tres servicios inician y tienen carpetas esperadas, que teoría/práctica no puedan modificar archivos ajenos y que auditoría lea ambas partes pero falle al escribir.
- **Estado:** Parcialmente cumplido.
- **Evidencia:** `infraestructura.md`, sección 3, registra inicio, versiones y pruebas reportadas de acceso/escritura. Esas pruebas comprueban que teoría/práctica no ven el directorio ajeno y escriben en el propio; no intentan modificar un archivo ajeno existente. `verificaciones_complementarias.md` aporta salidas de `id` e inspecciones de recursos, redes y puertos, pero no nuevas pruebas de permisos. `README.md:56-61` propone comprobaciones que no constan como realizadas.
- **Evaluación:** Los resultados de permisos previos siguen siendo confirmaciones reportadas, sin logs originales completos. Las verificaciones complementarias no modificaron archivos ni probaron escritura en rutas ajenas. Por tanto, no se amplía la evidencia de comportamiento de permisos más allá de lo registrado originalmente.
- **Recomendación:** Conservar la distinción de procedencia; no presentar inspecciones de configuración como pruebas de permisos sobre archivos.

### Hallazgos cerrados por evidencia complementaria

#### B1. Usuario efectivo no root verificado

- **Requisito:** ejecución de los servicios con usuario no root.
- **Estado:** Cumplido y verificado.
- **Evidencia:** `docker compose exec <servicio> id` devolvió en los tres servicios `uid=10001(app) gid=10001(app) groups=10001(app)`. Las salidas están en `verificaciones/verificaciones_complementarias.md`, sección 1.
- **Evaluación:** Las salidas confirman que los tres procesos inspeccionados usan UID/GID 10001 y no UID/GID 0.

#### B2. Límites efectivos de CPU y memoria verificados

- **Requisito:** 2 CPU / 2 GiB para teoría, 2 CPU / 4 GiB para práctica y 2 CPU / 2 GiB para auditoría.
- **Estado:** Cumplido y verificado mediante `docker inspect`.
- **Evidencia:** `NanoCpus=2000000000` en los tres; `Memory=2147483648` para teoría y auditoría y `Memory=4294967296` para práctica; `MemoryReservation=0`. Véase `verificaciones/verificaciones_complementarias.md`, sección 2.
- **Evaluación:** Los campos confirman máximos configurados. No representan reservas de memoria ni consumo actual, que no se midió.

## Inconsistencias y observaciones documentales

1. **Handoff:** el documento fue actualizado para referenciar este informe y las verificaciones complementarias. Mantiene separado el estado de los resultados previamente reportados, las inspecciones nuevas y las limitaciones de comportamiento no probado.
2. **README:** la documentación de comandos cubre configuración, build, inicio, comprobación, exec y down. La tabla y la descripción de redes coinciden con Compose. `README.md:19` matiza que egress no se probó y `:80-82` diferencia correctamente el aislamiento del contenedor respecto a Codex en Windows.
3. **Permisos de los bind mounts:** `compose.yaml` solicita mounts lectura/escritura para los directorios propios de teoría/práctica y auditoría. Su efecto en el anfitrión depende de Docker Desktop y del sistema de archivos; la configuración por sí sola no demuestra permisos efectivos. Las pruebas reportadas son evidencia de ejecución comunicada, pero carecen de logs originales.
4. **`requirements.txt`:** que esté vacío es coherente con no declarar paquetes de proyecto; no demuestra que futuras dependencias queden fijadas reproduciblemente.
5. **Auditoría independiente:** el prompt de auditoría está registrado en `PROMPTS.md`; herramienta: Codex, modelo específico no expuesto en la información verificable de la sesión.

## Limitaciones

- La auditoría inicial fue estática y no ejecutó Docker. Las inspecciones complementarias posteriores sí ejecutaron `id`, `docker inspect` y `docker network inspect`; no se realizaron pruebas de tráfico ni nuevas pruebas de permisos.
- Las pruebas previas de arranque y permisos se conocen mediante registros que atribuyen los resultados al usuario; no se inspeccionaron sus logs originales. Las inspecciones complementarias sí consultaron los metadatos de los contenedores activos.
- La sesión conversacional actual es nueva según el contexto recibido, pero no hay evidencia de aislamiento del proceso Codex en Windows más allá del alcance externo de herramientas disponible. Los permisos efectivos no se deducen de los mounts de Compose.
- No se verificó conectividad real entre redes o a Internet.
- No se evaluaron las Partes 1 y 2 ni el contenido académico, fuera de comprobar que la configuración evita montarlas en los servicios que no corresponden.

## Conclusión general

La Parte 0 está **parcialmente cumplida** según la evidencia disponible. Las inspecciones complementarias verificaron UID/GID 10001 en los tres servicios, los máximos de CPU/memoria esperados, una red bridge distinta por servicio, un único contenedor miembro observado por red y ausencia de puertos publicados. No se probó tráfico entre contenedores ni conectividad a Internet; tampoco se hicieron pruebas adicionales de permisos. Para parte de las pruebas anteriores de arranque y permisos faltan logs originales. La imagen base no está fijada por digest y `requirements.txt` está vacío. La sesión nueva aporta independencia de contexto, pero no demuestra aislamiento técnico de los permisos de Codex en Windows. El handoff actualizado referencia ambos informes. Por estas limitaciones, no corresponde declarar Parte 0 completamente cumplida.
