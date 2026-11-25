# Evidencia de infraestructura: Parte 0, apartado 2.5

## Procedencia y formato de evidencia

Los resultados de ejecución listados en la sección 3 fueron confirmados por el usuario. Los bloques de permisos y lectura de la sección 3 se recuperaron de la conversación, junto con sus salidas confirmadas; no son transcripciones originales de logs de PowerShell. No se ejecutaron pruebas nuevas al redactar este registro.

Las pruebas estáticas de configuración/build de la sección 2 corresponden a las ejecuciones anteriores documentadas en esta misma tarea. Las propiedades inferidas de los archivos se separan de los resultados de ejecución.

## 1. Configuración y construcción registradas previamente

### `docker compose config`

- Resultado registrado: código de salida 0; configuración resuelta correctamente.
- La salida confirmó tres servicios, `init: true`, usuario `10001:10001`, 2 CPU por servicio, límites de RAM de 2/4/2 GiB, los montajes declarados y ausencia de publicaciones de puertos.
- En ese momento la configuración de redes era distinta a la actual; no usar esa salida como prueba de las tres redes bridge actuales. La configuración actual define una red bridge exclusiva por servicio, y el usuario confirmó después que se crearon tres redes independientes al iniciar los servicios.
- Advertencia no fatal observada en ejecución restringida: `WARNING: Error loading config file: open C:\Users\sebau\.docker\config.json: Access is denied.`

### Validación posterior del cambio a redes bridge

- `docker compose config` se ejecutó nuevamente después de reemplazar `network_mode: none` por tres redes bridge independientes. Resultado registrado: código de salida 0.
- La salida resuelta asignó `teoria` solo a `teoria_net`, `practica` solo a `practica_net` y `auditoria` solo a `auditoria_net`; las tres redes tienen driver `bridge`. No se declararon puertos.
- La advertencia de acceso a `C:\Users\sebau\.docker\config.json` volvió a aparecer, sin impedir la validación.
- Esta validación confirma la configuración declarada, no la conectividad efectiva ni el aislamiento por pruebas de tráfico. La creación de las tres redes en `up -d` fue confirmada después por el usuario.

### `docker compose build`

- Resultado registrado: código de salida 0; se construyó `tp2-python:3.12` desde `python:3.12-slim-bookworm`.
- `requirements.txt` estaba vacío; la etapa condicional de instalación terminó correctamente.
- El primer intento en el sandbox falló con `CreateFile C:\Users\sebau\.docker\buildx\instances: Access is denied.` La repetición autorizada fuera del sandbox finalizó con código 0.
- La sesión de PowerShell fuera del sandbox mostró además un error de carga del perfil por política de ejecución (`PSSecurityException`, scripts deshabilitados); no impidió que Docker Compose construyera la imagen.
- Esta sección conserva la evidencia anterior; el build no se repitió para esta actualización documental.

## 2. Propiedades inferidas del estado actual de archivos

Contraste estático de `compose.yaml`, `Dockerfile` y `requirements.txt` (no es prueba de ejecución):

- `teoria` monta solo `parte1/` como lectura/escritura y solicita 2 CPU / 2 GiB.
- `practica` monta solo `parte2/` como lectura/escritura y solicita 2 CPU / 4 GiB.
- `auditoria` monta `parte1/` y `parte2/` como solo lectura, y `auditoria/` para escritura; solicita 2 CPU / 2 GiB.
- Cada servicio usa UID/GID `10001:10001`, `init: true`, filesystem raíz de solo lectura y `/tmp` temporal.
- Cada servicio pertenece solo a su red `bridge` (`teoria_net`, `practica_net` o `auditoria_net`). No hay sección `ports`.
- El Dockerfile define la imagen Python liviana y la instalación condicional desde `requirements.txt`; este archivo está vacío al momento de la inspección.
- No se monta el directorio personal, credenciales ni `docker.sock`; no hay modo privilegiado configurado.
- La configuración bridge permite salida de red en principio, pero no se informó una prueba de salida a Internet. No se informó prueba de conectividad entre contenedores.

## 3. Ejecuciones confirmadas por el usuario

Fecha/hora y responsable nominal de estas pruebas: no informados. Los resultados no son logs originales; son confirmaciones del usuario.

### Inicio y estado

```text
docker compose up -d
```

Resultado informado: los tres servicios iniciaron correctamente y se crearon tres redes independientes. La salida literal completa no fue suministrada.

```text
docker compose ps
```

Resultado informado: los tres contenedores aparecen en estado `Up`; no hay puertos publicados. La salida literal completa no fue suministrada.

### Versión de Python

```text
docker compose exec teoria python --version
docker compose exec practica python --version
docker compose exec auditoria python --version
```

Resultado confirmado para cada comando:

```text
Python 3.12.16
```

### Permisos y lectura: comandos y resultados recuperados de la conversación

Los siguientes bloques de comandos y resultados se recuperaron de la conversación. Las salidas fueron confirmadas por el usuario; **no son transcripciones originales de logs de PowerShell** y estas pruebas no se volvieron a ejecutar al redactar este registro.

#### Teoría

```powershell
@'
import os
import tempfile

assert os.path.isdir("/workspace/parte1")
assert not os.path.exists("/workspace/parte2"), "ERROR: teoria puede acceder a parte2"

fd, path = tempfile.mkstemp(dir="/workspace/parte1", prefix=".tp2_test_")
os.close(fd)
os.unlink(path)

print("OK: puede escribir en parte1")
print("OK: no tiene acceso a parte2")
'@ | docker compose exec -T teoria python -
```

Salida confirmada:

```text
OK: puede escribir en parte1
OK: no tiene acceso a parte2
```

#### Práctica

```powershell
@'
import os
import tempfile

assert os.path.isdir("/workspace/parte2")
assert not os.path.exists("/workspace/parte1"), "ERROR: practica puede acceder a parte1"

fd, path = tempfile.mkstemp(dir="/workspace/parte2", prefix=".tp2_test_")
os.close(fd)
os.unlink(path)

print("OK: puede escribir en parte2")
print("OK: no tiene acceso a parte1")
'@ | docker compose exec -T practica python -
```

Salida confirmada:

```text
OK: puede escribir en parte2
OK: no tiene acceso a parte1
```

#### Auditoría

La prueba inicial de auditoría capturaba únicamente `PermissionError`. La corrección comprueba `OSError.errno` y acepta `EROFS`, `EACCES` o `EPERM`, incluyendo el error `EROFS` devuelto por los montajes de solo lectura.

```powershell
@'
import os
import errno
import tempfile

for directory in ["/workspace/parte1", "/workspace/parte2"]:
    assert os.path.isdir(directory)
    print(f"OK: puede leer {directory}")

    try:
        fd, path = tempfile.mkstemp(dir=directory, prefix=".tp2_test_")
        os.close(fd)
        os.unlink(path)
        raise AssertionError(f"ERROR: pudo escribir en {directory}")
    except OSError as e:
        if e.errno not in (errno.EROFS, errno.EACCES, errno.EPERM):
            raise
        print(f"OK: escritura bloqueada en {directory}")

fd, path = tempfile.mkstemp(
    dir="/workspace/auditoria", prefix=".tp2_test_"
)
os.close(fd)
os.unlink(path)

print("OK: puede escribir en auditoria")
'@ | docker compose exec -T auditoria python -
```

Salida confirmada:

```text
OK: puede leer /workspace/parte1
OK: escritura bloqueada en /workspace/parte1
OK: puede leer /workspace/parte2
OK: escritura bloqueada en /workspace/parte2
OK: puede escribir en auditoria
```

#### Lectura efectiva de archivos

```powershell
@'
for path in [
    "/workspace/parte1/PROMPTS.md",
    "/workspace/parte2/PROMPTS.md"
]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"OK: lectura de {path} ({len(content)} caracteres)")
'@ | docker compose exec -T auditoria python -
```

Salida confirmada:

```text
OK: lectura de /workspace/parte1/PROMPTS.md (373 caracteres)
OK: lectura de /workspace/parte2/PROMPTS.md (373 caracteres)
```

### Acceso y permisos

Resumen de resultados ya registrados arriba; consultar esos bloques para los comandos recuperados de la conversación.

- `teoria`: escritura en `/workspace/parte1` exitosa; sin acceso a `/workspace/parte2`.
- `practica`: escritura en `/workspace/parte2` exitosa; sin acceso a `/workspace/parte1`.
- `auditoria`: lectura de archivos en `/workspace/parte1` y `/workspace/parte2` exitosa; intentos de escritura en ambos montajes fallaron con `EROFS` (`read-only file system`); escritura en `/workspace/auditoria` exitosa.
- Lectura efectiva de `parte1/PROMPTS.md` y `parte2/PROMPTS.md`: exitosa.

### Auditoría independiente

El usuario confirmó que la revisión se realizó desde una segunda conversación de Codex, nueva e independiente de la conversación de preparación. El informe quedó guardado en `auditoria/verificaciones/auditoria_independiente.md` y registra alcance, clasificación de requisitos, hallazgos y limitaciones. El prompt está registrado en `auditoria/PROMPTS.md`. La auditoría inicial fue documental; las inspecciones complementarias del 7 de noviembre de 2026 se registran por separado en `auditoria/verificaciones/verificaciones_complementarias.md`.

La sesión nueva acredita independencia de contexto conversacional. Codex se ejecutó en Windows, fuera de los contenedores; no hay evidencia de que sus permisos de anfitrión estuvieran restringidos a `auditoria/` ni de que los montajes del contenedor auditor limitaran esa sesión. No se debe confundir el resultado de la sesión con un confinamiento técnico.

## 4. Estado frente a las cinco pruebas obligatorias de 2.5

1. **Servicios y carpetas esperadas — cumplido según evidencia disponible:** `up -d`, `ps`, las versiones de Python y los montajes/directorios de trabajo aparecen en los resultados confirmados por el usuario; la estructura del repositorio también está presente. Las salidas originales completas de arranque/estado no se adjuntaron.
2. **Separación teoría/práctica — parcialmente acreditada:** los scripts confirman que el directorio ajeno no es visible y que se puede crear/borrar un temporal en el directorio propio. Compose monta únicamente la parte propia. No se intentó modificar un archivo ajeno existente, por lo que el resultado se limita a visibilidad y configuración de montajes.
3. **Auditoría — cumplido según resultados confirmados:** lectura en ambas partes, intento de escritura bloqueado (`EROFS`) y escritura en `auditoria/` están documentados con sus bloques de comandos y salidas recuperados de la conversación.
4. **Comandos, límites y dependencias — cumplido documentalmente, con salvedad:** README documenta `config`, `build`, inicio, estado, versiones, `exec` y `down`; configuración/inspecciones identifican límites y dependencias. La imagen base no está fijada por digest; `requirements.txt` está vacío.
5. **Agente auditor independiente — cumplido en sesión y entrega, con limitación de permisos:** el usuario confirmó una conversación nueva e independiente; el informe está guardado bajo `auditoria/verificaciones/`. No se acreditó que el proceso Codex en Windows estuviera técnicamente confinado a esos montajes o a ese directorio.

La auditoría independiente ya no está pendiente; sí queda pendiente la revisión personal de sus hallazgos por el/la estudiante. El apartado 2.5 está parcialmente acreditado por la limitación del punto 2 y la evidencia incompleta de algunos logs. No se declara completada la Parte 0 en su conjunto.
