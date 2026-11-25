# Verificaciones complementarias de infraestructura – Parte 0

Fecha de ejecución: 2026-11-07 (hora local de Santiago; las marcas temporales de Docker se muestran en UTC).

## 1. Usuario efectivo

**Objetivo:** comprobar dentro de cada contenedor el UID, GID y grupos efectivos, distinguiendo la configuración declarada de la ejecución observada.

**Comandos ejecutados:**

```powershell
docker compose exec teoria id
docker compose exec practica id
docker compose exec auditoria id
```

La primera ejecución desde el sandbox no logró conectar con Docker; se repitieron los mismos tres comandos con acceso al motor Docker autorizado. En la repetición PowerShell mostró una advertencia de perfil por la política de ejecución de scripts, pero los comandos devolvieron las salidas siguientes:

```text
uid=10001(app) gid=10001(app) groups=10001(app)
uid=10001(app) gid=10001(app) groups=10001(app)
uid=10001(app) gid=10001(app) groups=10001(app)
```

**Resultado e interpretación:** los tres servicios corren con UID 10001 y GID 10001; ninguno corre como UID/GID 0 (root). Esto confirma el usuario efectivo al momento de la inspección.

## 2. Límites efectivos de CPU y memoria

**Objetivo:** inspeccionar límites configurados en los contenedores y distinguir máximos de reservas y consumo actual.

**Comandos ejecutados para identificar contenedores:**

```powershell
docker compose ps -q teoria
docker compose ps -q practica
docker compose ps -q auditoria
```

**Salidas:**

```text
cabd30a0feae8ab78ec2bf699c4d175788c0bf9eabde7a0a63099ac4ce4e4c6d
405b0c3c01817ce011e36dbb7d39ea88012448eb82b77d2ad8127e2818d1dd83
05e50111d7ee1890dc46c826bd8b5b07cef9716eafc313d8965ba6ebbad0955a
```

**Comandos de inspección ejecutados:**

```powershell
docker inspect --format '{{.Name}} ID={{.Id}} NanoCpus={{.HostConfig.NanoCpus}} Memory={{.HostConfig.Memory}} MemoryReservation={{.HostConfig.MemoryReservation}} PortBindings={{json .HostConfig.PortBindings}} Networks={{json .NetworkSettings.Networks}}' cabd30a0feae8ab78ec2bf699c4d175788c0bf9eabde7a0a63099ac4ce4e4c6d
docker inspect --format '{{.Name}} ID={{.Id}} NanoCpus={{.HostConfig.NanoCpus}} Memory={{.HostConfig.Memory}} MemoryReservation={{.HostConfig.MemoryReservation}} PortBindings={{json .HostConfig.PortBindings}} Networks={{json .NetworkSettings.Networks}}' 405b0c3c01817ce011e36dbb7d39ea88012448eb82b77d2ad8127e2818d1dd83
docker inspect --format '{{.Name}} ID={{.Id}} NanoCpus={{.HostConfig.NanoCpus}} Memory={{.HostConfig.Memory}} MemoryReservation={{.HostConfig.MemoryReservation}} PortBindings={{json .HostConfig.PortBindings}} Networks={{json .NetworkSettings.Networks}}' 05e50111d7ee1890dc46c826bd8b5b07cef9716eafc313d8965ba6ebbad0955a
```

**Salidas completas relevantes:**

```text
/tp2-transformers-teoria-1 ID=cabd30a0feae8ab78ec2bf699c4d175788c0bf9eabde7a0a63099ac4ce4e4c6d NanoCpus=2000000000 Memory=2147483648 MemoryReservation=0 PortBindings={} Networks={"tp2-transformers_teoria_net":{"Aliases":["tp2-transformers-teoria-1","teoria"],"DNSNames":["tp2-transformers-teoria-1","teoria","cabd30a0feae"],"EndpointID":"a37f146cefc5b3eebd12b027bc5bd003bd85e3ab1dc969fc153f36b0c47039fc","Gateway":"172.21.0.1","GlobalIPv6Address":"","GlobalIPv6PrefixLen":0,"GwPriority":0,"IPAMConfig":null,"IPAddress":"172.21.0.2","IPPrefixLen":16,"IPv6Gateway":"","Links":null,"MacAddress":"8e:93:27:a0:15:ef","NetworkID":"4dceec60c8227641981dac327ca7284a71ad13110437b535ca3abf40605d4121"}}
/tp2-transformers-practica-1 ID=405b0c3c01817ce011e36dbb7d39ea88012448eb82b77d2ad8127e2818d1dd83 NanoCpus=2000000000 Memory=4294967296 MemoryReservation=0 PortBindings={} Networks={"tp2-transformers_practica_net":{"Aliases":["tp2-transformers-practica-1","practica"],"DNSNames":["tp2-transformers-practica-1","practica","405b0c3c0181"],"EndpointID":"dbba2495ab60415c97e4e8e4f155d7207aae029e36731d26415cab354f1c0b46","Gateway":"172.19.0.1","GlobalIPv6Address":"","GlobalIPv6PrefixLen":0,"GwPriority":0,"IPAMConfig":null,"IPAddress":"172.19.0.2","IPPrefixLen":16,"IPv6Gateway":"","Links":null,"MacAddress":"f2:1c:ea:44:71:fb","NetworkID":"9eb63df5b28b8a469e8b2dead5528563cdd48a596c7c78f3628c86685b426227"}}
/tp2-transformers-auditoria-1 ID=05e50111d7ee1890dc46c826bd8b5b07cef9716eafc313d8965ba6ebbad0955a NanoCpus=2000000000 Memory=2147483648 MemoryReservation=0 PortBindings={} Networks={"tp2-transformers_auditoria_net":{"Aliases":["tp2-transformers-auditoria-1","auditoria"],"DNSNames":["tp2-transformers-auditoria-1","auditoria","05e50111d7ee"],"EndpointID":"de905e0b9110fda6df9740406b7197359f3bc50e9388f2f4e5baaf6c1f0a15c1","Gateway":"172.20.0.1","GlobalIPv6Address":"","GlobalIPv6PrefixLen":0,"GwPriority":0,"IPAMConfig":null,"IPAddress":"172.20.0.2","IPPrefixLen":16,"IPv6Gateway":"","Links":null,"MacAddress":"a6:a6:c4:ff:e5:5a","NetworkID":"74e10783021bf489f76b727b87e0135b231ec20818170f3f6d650dfd45793bba"}}
```

**Resultado e interpretación:** `NanoCpus=2000000000` equivale a un máximo de 2 CPU en cada contenedor. `Memory=2147483648` bytes equivale a 2 GiB para `teoria` y `auditoria`; `Memory=4294967296` equivale a 4 GiB para `practica`. `MemoryReservation=0` indica que estos datos no están declarando una reserva de memoria. No se consultó ni se reporta consumo actual.

## 3. Redes y puertos

**Objetivo:** confirmar redes asociadas, su driver e identidad, contenedores conectados y puertos publicados según los metadatos inspeccionados.

**Comandos ejecutados:**

```powershell
docker network inspect tp2-transformers_teoria_net
docker network inspect tp2-transformers_practica_net
docker network inspect tp2-transformers_auditoria_net
```

**Salidas relevantes completas:**

```text
Name=tp2-transformers_teoria_net
Id=4dceec60c8227641981dac327ca7284a71ad13110437b535ca3abf40605d4121
Driver=bridge; Internal=false
Containers={"cabd30a0feae8ab78ec2bf699c4d175788c0bf9eabde7a0a63099ac4ce4e4c6d":{"Name":"tp2-transformers-teoria-1","EndpointID":"a37f146cefc5b3eebd12b027bc5bd003bd85e3ab1dc969fc153f36b0c47039fc","MacAddress":"8e:93:27:a0:15:ef","IPv4Address":"172.21.0.2/16","IPv6Address":""}}

Name=tp2-transformers_practica_net
Id=9eb63df5b28b8a469e8b2dead5528563cdd48a596c7c78f3628c86685b426227
Driver=bridge; Internal=false
Containers={"405b0c3c01817ce011e36dbb7d39ea88012448eb82b77d2ad8127e2818d1dd83":{"Name":"tp2-transformers-practica-1","EndpointID":"dbba2495ab60415c97e4e8e4f155d7207aae029e36731d26415cab354f1c0b46","MacAddress":"f2:1c:ea:44:71:fb","IPv4Address":"172.19.0.2/16","IPv6Address":""}}

Name=tp2-transformers_auditoria_net
Id=74e10783021bf489f76b727b87e0135b231ec20818170f3f6d650dfd45793bba
Driver=bridge; Internal=false
Containers={"05e50111d7ee1890dc46c826bd8b5b07cef9716eafc313d8965ba6ebbad0955a":{"Name":"tp2-transformers-auditoria-1","EndpointID":"de905e0b9110fda6df9740406b7197359f3bc50e9388f2f4e5baaf6c1f0a15c1","MacAddress":"a6:a6:c4:ff:e5:5a","IPv4Address":"172.20.0.2/16","IPv6Address":""}}
```

**Resultado e interpretación:** los tres nombres e IDs de red son distintos, todas usan `bridge`, y cada red inspeccionada enumera únicamente el contenedor del servicio correspondiente. Cada `docker inspect` mostró una sola red por contenedor y `PortBindings={}`; no hay publicaciones de puertos configuradas para esos contenedores. Esto acredita la configuración de conexiones y puertos observada en Docker.

Las redes tienen `Internal=false`, pero esta inspección no prueba conectividad efectiva a Internet. Tampoco demuestra por sí sola imposibilidad de comunicación entre servicios por todos los mecanismos posibles. No se hicieron pruebas de tráfico.

## 4. Revisión de reproducibilidad

**Objetivo:** revisar la versión base de Python, fijación por digest y dependencias adicionales, sin modificar archivos ni reconstruir imágenes.

**Comandos de inspección estática ejecutados:**

```powershell
Get-Content Dockerfile
Get-Content requirements.txt
```

**Contenido revisado de `Dockerfile`:**

```dockerfile
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app \
    && mkdir -p /workspace \
    && chown -R app:app /workspace

WORKDIR /workspace

COPY requirements.txt /tmp/requirements.txt
RUN if [ -s /tmp/requirements.txt ]; then \
        python -m pip install --no-cache-dir -r /tmp/requirements.txt; \
    fi \
    && rm /tmp/requirements.txt

USER 10001:10001
CMD ["sleep", "infinity"]
```

**Contenido revisado de `requirements.txt`:** archivo vacío (0 bytes).

**Resultado e interpretación:** la imagen declara Python 3.12, variante `slim-bookworm`. La referencia usa una etiqueta y no incluye `@sha256:...`, por lo que la imagen base no está fijada por digest. No hay dependencias Python adicionales declaradas; por tanto, no hay versiones de paquetes adicionales que evaluar. El Dockerfile copia el archivo de requisitos e instala sus paquetes si tiene contenido, pero sin un pin de imagen base, una reconstrucción futura puede resolver una imagen distinta bajo la misma etiqueta. Si se agregan paquetes sin versiones exactas, su resolución también puede variar. La estructura del build y la versión principal/secundaria de Python están documentadas, pero la reconstrucción binaria exacta no queda asegurada.

## 5. Comandos y estado de ejecución

Los comandos Docker de comprobación se ejecutaron primero en el sandbox y fallaron al intentar acceder a `npipe:////./pipe/docker_engine` con `permission denied`. Se repitieron con acceso al motor Docker autorizado y completaron correctamente. El arranque de PowerShell elevado emitió una advertencia `PSSecurityException` porque no pudo cargar `C:\Users\sebau\Documents\WindowsPowerShell\profile.ps1`; esto no impidió que los comandos Docker devolvieran las salidas registradas.

No se ejecutaron comandos para detener, reiniciar, reconstruir ni alterar contenedores o redes.

## 6. Limitaciones

- `docker inspect` y `docker network inspect` muestran configuración y conexiones observadas en el momento de consulta; no son pruebas de conectividad de red.
- `PortBindings={}` y la ausencia de puertos publicados aplican a los contenedores inspeccionados en ese momento.
- No se midió consumo de CPU o memoria; los valores de memoria son límites (`HostConfig.Memory`), no consumo ni reserva (`MemoryReservation=0`).
- La revisión de reproducibilidad fue estática y no reconstruyó la imagen.
- Los comandos Docker se ejecutaron desde PowerShell en Windows y requirieron acceso al motor fuera del sandbox. La advertencia de perfil se conserva aquí para explicar el entorno de ejecución.
