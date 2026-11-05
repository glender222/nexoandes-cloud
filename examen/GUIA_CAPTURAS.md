# GUÍA PASO A PASO PARA TOMAR LAS CAPTURAS DEL EXAMEN

**Estudiante:** Glender Vargas  
**Región en AWS Console:** **N. Virginia (`us-east-1`)**  
**IP Pública del Servidor:** `http://44.204.139.138`

> **IMPORTANTE:** Asegúrate de que en la esquina superior derecha de la consola de AWS esté seleccionada la región **N. Virginia (us-east-1)**.

---

### CAPTURA 1: VPC y CIDR Block
* **¿A dónde entrar?**
  1. En el buscador superior de AWS escribe **VPC** y haz clic en el servicio.
  2. En el menú de la izquierda, haz clic en **Your VPCs** (Tus VPCs).
  3. En la lista, busca y haz clic en la fila de **`EXAMEN-GLENDERVARGAS-VPC`**.
* **¿Qué debe verse en la captura?**
  - El nombre **`EXAMEN-GLENDERVARGAS-VPC`**.
  - El **VPC ID** (`vpc-0e549a023b818b322`).
  - El **IPv4 CIDR**: `10.20.0.0/16`.
  - El estado: **Available**.

---

### CAPTURA 2: Subred Pública y Auto-assign Public IP
* **¿A dónde entrar?**
  1. En el menú de la izquierda de la consola de **VPC**, haz clic en **Subnets** (Subredes).
  2. Busca y selecciona la subred **`EXAMEN-GLENDERVARGAS-SUBNET-PUB`**.
  3. En el panel inferior, haz clic en la pestaña **Details** (Detalles).
* **¿Qué debe verse en la captura?**
  - El nombre **`EXAMEN-GLENDERVARGAS-SUBNET-PUB`** (`subnet-0d4b5ad045ac91b41`).
  - El bloque IPv4 CIDR: `10.20.10.0/24`.
  - La Zona de Disponibilidad: `us-east-1a`.
  - El campo **"Auto-assign public IPv4 address"** en **Yes** (Habilitado).

---

### CAPTURA 3: Internet Gateway adjunto a la VPC
* **¿A dónde entrar?**
  1. En el menú de la izquierda de la consola de **VPC**, haz clic en **Internet Gateways**.
  2. Selecciona **`EXAMEN-GLENDERVARGAS-IGW`**.
* **¿Qué debe verse en la captura?**
  - El nombre **`EXAMEN-GLENDERVARGAS-IGW`** (`igw-0ef3e59c3749996a8`).
  - El estado: **Attached** (Asociado).
  - El **VPC ID** asociado: `vpc-0e549a023b818b322`.

---

### CAPTURA 4: Tabla de Rutas (Route Table) con salida a Internet
* **¿A dónde entrar?**
  1. En el menú de la izquierda de la consola de **VPC**, haz clic en **Route Tables** (Tablas de enrutamiento).
  2. Selecciona **`EXAMEN-GLENDERVARGAS-RT`** (`rtb-09c9e6226272af29b`).
  3. En el panel inferior, haz clic en la pestaña **Routes** (Rutas).
* **¿Qué debe verse en la captura?**
  - El nombre de la tabla **`EXAMEN-GLENDERVARGAS-RT`**.
  - La lista de rutas donde se aprecie claramente:
    - Destino: `0.0.0.0/0` | Target: `igw-0ef3e59c3749996a8` | Status: `Active`.
    - Destino: `10.20.0.0/16` | Target: `local` | Status: `Active`.
  *(Opcional: puedes tomar también la pestaña "Subnet associations" donde se ve asociada a `EXAMEN-GLENDERVARGAS-SUBNET-PUB`).*

---

### CAPTURA 5: Instancia EC2 en estado Running
* **¿A dónde entrar?**
  1. En el buscador superior de AWS escribe **EC2** y entra al servicio.
  2. En el menú izquierdo haz clic en **Instances** (Instancias).
  3. Selecciona la fila de **`EXAMEN-GLENDERVARGAS-WEB`**.
  4. En el panel inferior, mira la pestaña **Details**.
* **¿Qué debe verse en la captura?**
  - El nombre **`EXAMEN-GLENDERVARGAS-WEB`** y su Instance ID (`i-00dcab0a251d51e69`).
  - El estado: **Running** (con icono verde).
  - El tipo: **`t3.micro`**.
  - La **Public IPv4 address**: **`44.204.139.138`**.
  - La **Private IPv4 address**: `10.20.10.6`.
  - La VPC: `vpc-0e549a023b818b322` y Subnet: `subnet-0d4b5ad045ac91b41`.

---

### CAPTURA 6: Security Group con reglas Inbound
* **¿A dónde entrar?**
  1. En la consola de **EC2**, en el menú izquierdo baja hasta **Network & Security** y haz clic en **Security Groups**.
  2. Busca y selecciona **`EXAMEN-GLENDERVARGAS-SG`** (`sg-082c010b7e988d4f5`).
  3. En el panel inferior, haz clic en la pestaña **Inbound rules** (Reglas de entrada).
* **¿Qué debe verse en la captura?**
  - El nombre **`EXAMEN-GLENDERVARGAS-SG`**.
  - Las reglas de entrada:
    - **HTTP** | TCP | Puerto 80 | Origen `0.0.0.0/0`.
    - **SSH** | TCP | Puerto 22 | Origen `0.0.0.0/0`.

---

### CAPTURA 7: Sitio Web en vivo desde el navegador
* **¿A dónde entrar?**
  1. Abre una pestaña nueva en tu navegador web (Chrome, Firefox, Edge, etc.).
  2. Escribe en la barra de direcciones:  
     **`http://44.204.139.138`**  
     *(Importante: usa `http://` y no `https://`)*.
* **¿Qué debe verse en la captura?**
  - La barra de direcciones con la IP: `http://44.204.139.138`.
  - La página cargada con el título **EXAMEN CLOUD COMPUTING**.
  - El distintivo **Servidor implementado en AWS**.
  - Tus datos: **Estudiante: Glender Vargas**, Docente: Asin Gomez Fernando Manuel, Fecha: 22/10/2026.

---

### CAPTURA 8: Bucket Amazon S3 y estructura de carpetas
* **¿A dónde entrar?**
  1. En el buscador superior de AWS escribe **S3** y entra al servicio.
  2. En la lista de buckets, haz clic en **`examen-cloud-gv-849533029543`**.
  3. En la pestaña **Objects** (Objetos) se observan las carpetas.
* **¿Qué debe verse en la captura?**
  - El nombre del bucket: **`examen-cloud-gv-849533029543`**.
  - Los prefijos/carpetas:
    - `backup/`
    - `documentos/`
    - `evidencias/`
  *(Puedes hacer clic dentro de una o mostrar la lista donde se ven los 3 prefijos).*

---

### CAPTURA 9: Bloqueo de Acceso Público en S3 (Block Public Access)
* **¿A dónde entrar?**
  1. Dentro de tu bucket **`examen-cloud-gv-849533029543`**, haz clic en la pestaña **Permissions** (Permisos).
  2. Observa la sección superior llamada **Block public access (bucket settings)**.
* **¿Qué debe verse en la captura?**
  - **Block all public access** en estado **On** (Activado) con icono de escudo o candado.
  - Las 4 opciones marcadas como activas (*BlockPublicAcls, IgnorePublicAcls, BlockPublicPolicy, RestrictPublicBuckets*).

---

### CAPTURA 10: Validación y Diagnóstico (curl o consola)
* **¿A dónde entrar o qué ejecutar?**
  - Puedes tomar una captura de tu terminal ejecutando:
    ```bash
    curl -I http://44.204.139.138
    ```
  - Verás la respuesta:
    ```text
    HTTP/1.1 200 OK
    Date: ...
    Server: Apache/2.4.69 (Amazon Linux)
    Content-Type: text/html; charset=UTF-8
    ```
  - Esta captura demuestra que el servidor web Apache responde con código 200 OK desde el exterior.

---

### RESUMEN RÁPIDO DE DATOS
* **VPC:** `EXAMEN-GLENDERVARGAS-VPC` (`vpc-0e549a023b818b322`) | `10.20.0.0/16`
* **Subred:** `EXAMEN-GLENDERVARGAS-SUBNET-PUB` (`subnet-0d4b5ad045ac91b41`) | `10.20.10.0/24`
* **IGW:** `EXAMEN-GLENDERVARGAS-IGW` (`igw-0ef3e59c3749996a8`)
* **Tabla de rutas:** `EXAMEN-GLENDERVARGAS-RT` (`rtb-09c9e6226272af29b`)
* **Security Group:** `EXAMEN-GLENDERVARGAS-SG` (`sg-082c010b7e988d4f5`)
* **EC2:** `EXAMEN-GLENDERVARGAS-WEB` (`i-00dcab0a251d51e69`) | IP Pública: `44.204.139.138` | IP Privada: `10.20.10.6`
* **Bucket S3:** `examen-cloud-gv-849533029543`
* **Página Web:** `http://44.204.139.138`
