# Plan de cierre por criterio — Entregable 2

Actualizado el 05/11/2026 tras revisar visualmente el Word vigente. El documento ya contiene imágenes en las reservas R01–R19 y tres comparaciones antes/después. Este archivo es seguimiento, no parte del informe. Las evidencias técnicas corresponden a pruebas fechadas; no se consultó el estado actual de las nubes.

## 1. Evolución V1 → V2 — secciones 2–6

**Disponible:** comparación por componente, diagramas V1/V2 y tres bloques de imágenes antes/después. Se distingue que ALB y ASG ya existían en V1.

**Cierre:** confirmar el número de equipo y los integrantes de portada, y actualizar el índice en Word. Si existen observaciones reales del docente, añadirlas con la acción correspondiente; no atribuirle el diagnóstico técnico. Las imágenes R09–R11 ya están colocadas: sus pies aclaran qué muestra cada imagen y remiten a los ensayos cuando corresponde.

## 2. Amenazas y vulnerabilidades — secciones 8 y 19

**Disponible:** matriz de activos, amenazas, vulnerabilidades, impacto y controles, y tabla de riesgos residuales. El Word también explica el tratamiento propuesto y las prioridades, identificando las medidas pendientes.

**Cierre:** el equipo debe revisar las probabilidades y el impacto, y acordar responsables y plazos para los riesgos que decida tratar. Priorizar revisión de privilegios y MFA, cifrado pendiente y protección de respaldos. No afirmar que estos controles adicionales ya se implementaron. La rúbrica no exige un plazo concreto; incorporarlo haría más operativo el plan.

## 3. Controles de seguridad — secciones 7, 9, 10 y 14

**Disponible:** imágenes R01–R08 y R12 insertadas, matriz de controles, red, IAM y monitoreo. La asignación acotada Azure no elimina el Owner heredado; LabRole es amplio y MFA no fue verificado.

**Cierre:** comprobar legibilidad y que los pies indiquen lo que realmente muestra cada imagen. R01 y R02 muestran vistas administrativas de Supabase, no acreditan por sí solas rechazo sin token o acceso al portal; esas pruebas tienen sus propios registros e imágenes. R06 muestra reglas de salida; la entrada a 5432 se respalda por configuración y prueba separada. Una revisión más profunda de privilegios, MFA y alertas es una mejora técnica pendiente, no se presume ejecutada.

## 4. Escalabilidad, disponibilidad y tolerancia a fallos — secciones 11–13 y 15

**Disponible:** R09–R11 y R13–R16 con capturas y pies. El ensayo registra escalado 2→4, 2.137 HTTP 200 y promoción manual PG15; los escenarios de 100 a 5.000 usuarios son proyecciones. Una vista de configuración de ASG o de una VM no demuestra por sí sola un ensayo.

**Cierre:** conservar identificables los registros de [escalado](../../integracion/evidencias/20261104/escalabilidad.json), [promoción y retorno](../../integracion/evidencias/20261104/failover.json) y [restauración](../../integracion/evidencias/20261104/restauracion-ciclo.json) junto al Word al preparar la entrega, si el docente admite anexos digitales. En caso contrario, agregar una captura legible del registro pertinente solo si la evidencia actual no basta. El failover automático, 5.000 usuarios y HA de Auth no están acreditados. La restauración integral de Supabase permanece fuera del trabajo activo por decisión previa.

## 5. Evidencias, pruebas y documentación — secciones 16–18 y 20

**Disponible:** 33 imágenes incrustadas en total, incluyendo figuras, capturas y comparaciones; R01–R19 contienen imágenes. R16 muestra resultados de integridad/restauración y R17–R19 muestran pantallas económicas.

**Cierre:** revisar las imágenes a tamaño de lectura y ocultar cualquier secreto. Asegurar que las capturas de costos indiquen período, moneda y ámbito; los costos de una cuenta completa no equivalen necesariamente a los del proyecto. El subtotal AWS de US$138,92/mes sigue siendo una estimación parcial y no es una factura ni un total multicloud; completar una estimación conjunta solo si se obtienen datos suficientes. Confirmar portada y actualizar la tabla de contenido en Microsoft Word.

## Orden práctico

1. Usuario/equipo: confirmar número de equipo, integrantes y retroalimentación docente, si corresponde.
2. Revisar imágenes existentes y pies; agregar un cuadro vacío únicamente si se identifica una evidencia específica que no esté ya cubierta.
3. Preparar con el Word los registros JSON citados si el formato de entrega admite anexos; de lo contrario decidir qué prueba necesita una captura legible adicional.
4. Decidir responsables y plazos de riesgos y si se ampliará la cotización multicloud.
5. Actualizar el índice y revisar el documento final en Word.

No se solicita repetir todas las capturas. Cambios de infraestructura, pruebas adicionales, fechas y valores económicos deben basarse en acceso real y resultados verificables. La nota la determina el docente.
