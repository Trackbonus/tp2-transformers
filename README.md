# TP2 Transformers: infraestructura Docker

Esta configuración proporciona tres entornos independientes para el trabajo: `teoria`, `practica` y `auditoria`. Los contenedores usan Python 3.12 sobre Debian slim, ejecutan como usuario no root (`10001:10001`) y permanecen activos para recibir comandos mediante `docker compose exec`.

## Requisitos

- Docker Desktop con el motor Linux activo (contexto `desktop-linux`) y Docker Compose v2.
- PowerShell o una terminal compatible con Docker Compose.
- No se requiere GPU.

## Acceso, montajes y recursos

| Servicio | Red | Montajes del proyecto | CPU | Memoria | Escritura esperada |
|---|---|---|---:|---:|---|
| `teoria` | `teoria_net` (bridge propia) | `parte1/` en `/workspace/parte1` | 2 | 2 GiB | `parte1/` |
| `practica` | `practica_net` (bridge propia) | `parte2/` en `/workspace/parte2` | 2 | 4 GiB | `parte2/` |
| `auditoria` | `auditoria_net` (bridge propia) | `parte1/` y `parte2/` de solo lectura; `auditoria/` | 2 | 2 GiB | `auditoria/` |

No se monta la raíz del repositorio en los contenedores. El sistema de archivos de cada imagen es de solo lectura y `/tmp` es temporal. Los permisos efectivos de escritura en bind mounts, especialmente sobre Windows con Docker Desktop, se deben comprobar en ejecución; no se presuponen por usar UID 10001. Cada servicio está conectado solo a su propia red bridge: los servicios quedan separados entre sí y la configuración permite conexiones salientes a Internet. No se publican puertos. La conectividad saliente no se ha probado.

## Construir y validar la configuración

Desde la raíz del repositorio:

```powershell
docker compose config
docker compose build
```

`docker compose config` valida y muestra la configuración resuelta. `docker compose build` construye una vez la imagen compartida `tp2-python:3.12`, usada por los tres servicios. El `.dockerignore` excluye del contexto de construcción los proyectos, auditoría, enunciado, `.git/` y `.vscode/`.

## Iniciar y comprobar los servicios

```powershell
docker compose up -d
docker compose ps
docker compose exec teoria python --version
docker compose exec practica python --version
docker compose exec auditoria python --version
```

Cada servicio permanece activo con `sleep infinity`. Los comandos de proyecto se ejecutan en el servicio correspondiente, por ejemplo:

```powershell
docker compose exec teoria python codigo/mi_script.py
docker compose exec practica python codigo/mi_script.py
docker compose exec auditoria python --version
```

Las rutas relativas se resuelven desde el directorio de trabajo asignado a cada servicio: `/workspace/parte1`, `/workspace/parte2` o `/workspace/auditoria`.

## Comprobar permisos y aislamiento

Los resultados de ejecución confirmados por el usuario están registrados en [auditoria/verificaciones/infraestructura.md](auditoria/verificaciones/infraestructura.md). Los comandos exactos y salidas completas de algunos intentos de acceso/escritura no se proporcionaron; el registro distingue esas confirmaciones de las propiedades inferidas de Compose. No se deben considerar completadas las pruebas pendientes allí señaladas.

1. Confirmar usuario no root con `docker compose exec <servicio> id`.
2. Confirmar que teoría ve `/workspace/parte1` y que `/workspace/parte2` no está disponible o no es visible desde ese contenedor; comprobar lo inverso en práctica.
3. Intentar crear un archivo temporal en el montaje asignado a teoría y práctica. Registrar si la escritura funciona; Docker Desktop puede aplicar permisos de bind mount de forma distinta al filesystem del contenedor.
4. Desde auditoría, leer un archivo de cada proyecto y luego intentar crear archivos temporales en ambos montajes. La lectura debe funcionar y la escritura debe fallar por ser montajes `read_only`.
5. Confirmar que auditoría puede crear un archivo temporal en `/workspace/auditoria` y retirarlo al finalizar.
6. Revisar montajes y límites resueltos con `docker compose config` y, con contenedores iniciados, `docker inspect`.

En pruebas adicionales, no usar archivos importantes: emplear nombres temporales y limpiar los que se hayan creado. No registrar una prueba como aprobada si no hay salida o evidencia que la respalde.

## Ejecutar comandos y detener

```powershell
docker compose exec teoria <comando>
docker compose exec practica <comando>
docker compose exec auditoria <comando>
docker compose down
```

Los bind mounts persisten en el computador después de detener o eliminar los contenedores.

## Dependencias reproducibles

`requirements.txt` comienza vacío. Cuando el código requiera paquetes, registrar versiones exactas (`paquete==versión`) e incorporarlas allí. La imagen instala el archivo durante la construcción solo si contiene dependencias. Para fijar también la imagen base con máxima reproducibilidad, sustituir la etiqueta `python:3.12-slim-bookworm` por un digest verificado y documentar su actualización.

## Límite del aislamiento de Codex

Los montajes limitan los procesos que corren dentro de los contenedores. Codex se ejecuta en Windows; Docker no limita por sí solo los archivos que la sesión de Codex puede leer o modificar desde el anfitrión. Para mantener separados los contextos, usar sesiones independientes y ejecutar el trabajo de cada rol dentro del servicio correspondiente, evitando herramientas del anfitrión que accedan al proyecto completo. Documentar las limitaciones y el método realmente utilizado en `auditoria/HANDOFF.md`.
