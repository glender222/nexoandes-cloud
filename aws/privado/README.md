# Configurar AWS Academy en tu laptop

1. Inicia tu Learner Lab en Vocareum y abre **AWS Details**.
2. Desde la raíz del repositorio, crea tu archivo de sesión local a partir de la plantilla. Usa estos comandos al configurarlo por primera vez.

   ```bash
   cp -n aws/privado/academy-session.env.example aws/privado/academy-session.env
   chmod 600 aws/privado/academy-session.env
   ```

3. Completa las tres variables en `academy-session.env` con las credenciales temporales de tu laboratorio. Deja los campos de `academy-session.env.example` vacíos.
4. Comprueba que la cuenta sea la de tu laboratorio antes de operar.

   ```bash
   ./aws/infraestructura/academy-aws sts get-caller-identity
   ```

Git ignora el archivo de sesión y las claves SSH. Si las credenciales caducan, actualiza tu archivo local desde **AWS Details**. Consulta la [guía de acceso](../ACCESO.md) para más detalles.
