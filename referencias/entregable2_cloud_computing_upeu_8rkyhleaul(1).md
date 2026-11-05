#### **UNIVERSIDAD PERUANA UNIÓN** 

Facultad de Ingeniería y Arquitectura Escuela Profesional de Ingeniería de Sistemas 

**CURSO: CLOUD COMPUTING   ·   PROYECTO INTEGRADOR** 

# **Entregable 2** 

Seguridad, optimización, escalabilidad y resiliencia de la solución _Arquitectura V1  →  Arquitectura V2_ 

|**NOMBRE DEL PROYECTO**|_[Nombre del proyecto]_|
|---|---|
|**INTEGRANTES**|_[Apellidos y nombres — código]_|
||_[Apellidos y nombres — código]_|
||_[Apellidos y nombres — código]_|
||_[Apellidos y nombres — código]_|
|**EQUIPO**|_[Equipo XX]_|
|**DOCENTE**|_[Nombre del docente]_|
|**FECHA**|_[dd/mm/aaaa]_|



Lima, Perú 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

## **Contenido** 

_Para actualizar el índice: clic derecho sobre él → Actualizar campo → Actualizar toda la tabla._ 

**Página** 1 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

_Este entregable no comienza desde cero: se toma la arquitectura del Entregable 1, se analiza, se mejora y se obtiene la Arquitectura V2._ 

> **Arquitectura V1 → Análisis → Mejoras → Arquitectura V2** 

###### **INDICACIÓN** 

_Según el sílabo, en esta unidad se trabajan implementación y gestión de servicios, monitoreo, redes, serverless, escalabilidad y tolerancia a fallos._ 

_El producto de la Unidad 2 exige explícitamente un plan integral de seguridad que incluya controles de seguridad, amenazas y vulnerabilidades, y cumplimiento de normas o estándares._ 

### **02   Resumen del Entregable 1** 

###### **INDICACIÓN** 

_Máximo una página. Sintetice el punto de partida de esta segunda versión._ 



<!-- Start of picture text -->
Problema<br>Solución planteada<br>Proveedor utilizado<br>Arquitectura implementada<br>Principales problemas<br>encontrados<br><!-- End of picture text -->

### **03   Arquitectura V1** 

###### **INDICACIÓN** 

_Inserte nuevamente el diagrama presentado en el Entregable 1._ 

**Página** 2 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

_[ Insertar aquí el diagrama de la Arquitectura V1 ]_ 

_Figura 1. Arquitectura Cloud V1 — [Nombre del proyecto]_ 

### **04   Retroalimentación recibida** 

###### **INDICACIÓN** 

_Registre las observaciones recibidas en el Entregable 1 y la acción realizada para atender cada una._ 

|**Observación**<br>**Problema encontrado**<br>**Acción realizada**|
|---|





### **05   Comparación V1 versus V2** 

###### **INDICACIÓN** 

_Compare ambas versiones aspecto por aspecto y explique la mejora obtenida._ 

|**Aspecto**|**V1**|**V2**|**Mejora**|
|---|---|---|---|
|**Cómputo**||||
|**Red**||||
|**Seguridad**||||



**Página** 3 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

|**Aspecto**|**V1**|**V2**|**Mejora**|
|---|---|---|---|
|**Escalabilidad**||||
|**Disponibilidad**||||
|**Monitoreo**||||
|**Backup**||||



### **06   Arquitectura Cloud V2** 



<!-- Start of picture text -->
INDICACIÓN<br>Presente la arquitectura mejorada. Ejemplo conceptual:<br>                         INTERNET<br>                            |<br>                            v<br>                    [Load Balancer]<br>                      /           \<br>                     /             \<br>                 Web-01           Web-02<br>                    \               /<br>                     \             /<br>                      +-----------+<br>                           |<br>                           v<br>                     Base de Datos<br>                           |<br>                   +-------+-------+<br>                   |               |<br>                 Backup         Monitoreo<br>El diagrama real debe utilizar los servicios correspondientes del proveedor seleccionado.<br><!-- End of picture text -->



<!-- Start of picture text -->
[ Insertar aquí el diagrama de la Arquitectura V2 ]<br><!-- End of picture text -->

**Página** 4 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

_Figura 2. Arquitectura Cloud V2 — [Nombre del proyecto]_ 

### **07   Seguridad** 

###### **INDICACIÓN** 

_Desarrolle cada dimensión indicando el control aplicado y el servicio o herramienta que lo implementa. AWS también considera IAM, VPC, CloudTrail, filtrado de tráfico, cifrado, security groups y CloudWatch como elementos de seguridad arquitectónica._ 

|**Dimensión**|**Control implementado**|**Servicio / herramienta**|
|---|---|---|
|**Identidad**|||
|**Autenticación**|||
|**Autorización**|||
|**Mínimo privilegio**|||
|**Firewall / security groups**|||
|**Segmentación**|||
|**Cifrado**|||
|**Respaldo**|||
|**Registros**|||
|**Monitoreo**|||



### **08   Análisis de amenazas y vulnerabilidades** 

###### **INDICACIÓN** 

_Para cada activo identifique la amenaza, la vulnerabilidad que la hace posible, su impacto y el control aplicado._ 

|**Activo**|**Amenaza**|**Vulnerabilidad**|**Impacto**|**Control**|
|---|---|---|---|---|
|**Servidor Web**|||||
|**Base de datos**|||||
|**Red**|||||
|**Credenciales**|||||
|**Información**|||||



**Página** 5 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

### **09   IAM** 

###### **INDICACIÓN** 

_Indique usuarios, grupos, roles, políticas y privilegios. Aplique el principio de mínimo privilegio._ 

|**Tipo**|**Nombre**|**Función**|**Políticas asignadas**|**Privilegios**|
|---|---|---|---|---|
|**Usuario**|||||
|**Usuario**|||||
|**Grupo**|||||
|**Grupo**|||||
|**Rol**|||||
|**Rol**|||||



##### **Aplicación del mínimo privilegio** 

_Explique cómo se restringieron los permisos a lo estrictamente necesario…_ 

### **10   Seguridad de red** 

**INDICACIÓN** 

_Documente:_ 

- _Subred pública_ 

- _Subred privada_ 

- _Reglas de entrada_ 

- _Reglas de salida_ 

- _Puertos permitidos_ 

- _Servicios expuestos_ 

##### **10.1  Subredes** 

|**Subred**|**Tipo**|**CIDR**|**Zona de**<br>**disponibilidad**|**Recursos alojados**|
|---|---|---|---|---|
||Pública||||
||Pública||||
||Privada||||
||Privada||||



**Página** 6 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

##### **10.2  Reglas de entrada y salida / puertos permitidos** 

|**Regla / SG**|**Dirección**|**Protocolo**|**Puerto**|**Origen / Destino**|**Propósito**|
|---|---|---|---|---|---|
||Entrada|||||
||Entrada|||||
||Entrada|||||
||Salida|||||
||Salida|||||



##### **10.3  Servicios expuestos** 

|**Servicio**|**Puerto**|**Expuesto a**|**Justificación**|
|---|---|---|---|





### **11   Escalabilidad** 

###### **INDICACIÓN** 

_Explique cómo respondería la arquitectura ante un crecimiento progresivo de usuarios:_ 100 usuarios  →  500 usuarios  →  1 000 usuarios  →  5 000 usuarios 

|**Usuarios**|**Comportamiento**<br>**esperado**|**Recursos /**<br>**instancias**|**Mecanismo de**<br>**escalamiento**|**Servicio Cloud**|
|---|---|---|---|---|
|**100**|||||
|**500**|||||
|**1 000**|||||
|**5 000**|||||



### **12   Alta disponibilidad y tolerancia a fallos** 

###### **INDICACIÓN** 

_Responda cada pregunta con base en la Arquitectura V2._ 

_Las buenas prácticas arquitectónicas de AWS incluyen diseñar para fallos, elasticidad, seguridad por capas y desacoplamiento._ 

**Página** 7 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

|**Pregunta**|**Respuesta**|
|---|---|
|**¿Qué sucede si falla una VM?**||
|**¿Qué sucede si falla la aplicación?**||
|**¿Qué sucede si falla la base de**<br>**datos?**||
|**¿Existen componentes redundantes?**<br>**¿Cuáles?**||



### **13   Eliminación de SPOF** 

###### **INDICACIÓN** 

_Compare los puntos únicos de falla identificados en V1 con la solución implementada en V2._ 

|**SPOF identificado en V1**<br>**Solución implementada en V2**|**Resultado**|
|---|---|





### **14   Monitoreo** 

**INDICACIÓN** _Especifique recurso, métrica, umbral, herramienta y acción. Ejemplo:_ Recurso      Métrica          Umbral    Acción VM           CPU              > 80 %    Alerta Aplicación   Disponibilidad   < 99 %    Notificación Disco        Uso              > 85 %    Alerta 

|**Recurso**<br>**Métrica**<br>**Umbral**|**Herramienta**<br>**Acción**|
|---|---|





**Página** 8 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

### **15   Backup y recuperación** 

###### **INDICACIÓN** 

_Indique qué se respalda, con qué periodicidad, dónde, por cuánto tiempo y cómo se recupera._ 

|**Qué se respalda**|
|---|
|**Periodicidad**|
|**Ubicación**|
|**Retención**|



##### **Procedimiento de recuperación** 

_Describa paso a paso cómo se restaura el servicio a partir del respaldo…_ 

### **16   Pruebas realizadas** 

###### **INDICACIÓN** 

_Registre al menos las siguientes pruebas._ 

|**Prueba**|**Procedimiento**|**Resultado esperado**|**Resultado obtenido**|
|---|---|---|---|
|**Acceso Web**||||
|**Seguridad**||||
|**Fallo**||||
|**Escalabilidad**||||
|**Recuperación**||||



**Página** 9 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

### **17   Evidencias** 

**INDICACIÓN** _Incluya capturas antes y después de cada mejora. Copie y pegue el bloque tantas veces como sea necesario._ 



<!-- Start of picture text -->
Mejora 01  —   [Nombre de la mejora]<br>ANTES (V1) DESPUÉS (V2)<br>[ Captura antes ] [ Captura después ]<br>Descripción de la mejora<br>Servicio / configuración<br>Resultado obtenido<br>Mejora 02  —   [Nombre de la mejora]<br>ANTES (V1) DESPUÉS (V2)<br>[ Captura antes ] [ Captura después ]<br>Descripción de la mejora<br>Servicio / configuración<br>Resultado obtenido<br><!-- End of picture text -->

**Página** 10 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 



<!-- Start of picture text -->
Mejora 03  —   [Nombre de la mejora]<br>ANTES (V1) DESPUÉS (V2)<br>[ Captura antes ] [ Captura después ]<br>Descripción de la mejora<br>Servicio / configuración<br>Resultado obtenido<br><!-- End of picture text -->

### **18   Costos preliminares** 

###### **INDICACIÓN** 

_No se busca todavía una estimación financiera exhaustiva, sino demostrar que la arquitectura tiene impacto económico._ 



<!-- Start of picture text -->
Costo aproximado<br>Servicio Cantidad Uso estimado<br>(USD/mes)<br>COSTO TOTAL ESTIMADO<br>19   Riesgos residuales<br>INDICACIÓN<br>Identifique los riesgos que permanecen después de las mejoras. Probabilidad e impacto: Alta / Media / Baja.<br><!-- End of picture text -->

**Página** 11 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

Cloud Computing · Proyecto Integrador 

**Entregable 2 — Arquitectura V2** 

|**Riesgo**<br>**Probabilidad**|**Impacto**|**Tratamiento**|
|---|---|---|
|**20Conclusiones técnicas**|||
|**INDICACIÓN**<br>_Explique qué mejoró entre V1 y V2 y qué quedará pend    i_<br>**¿Qué mejoró entre V1 y V2?**|_iente para el pro i_|_ducto final._|
|_Escriba aquí…_|||
|**¿Qué queda pendiente para el producto final?**|||
|_Escriba aquí…_|||



**Página** 12 

Universidad Peruana Unión · E.P. Ingeniería de Sistemas 

