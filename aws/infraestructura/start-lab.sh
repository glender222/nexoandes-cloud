#!/bin/bash
# ============================================
#  AWsAcademy - Script de Arranque Rápido
#  Ejecutar después de cada reinicio del lab
# ============================================
set -e

# Configurar credenciales fuera del script: perfil academy o variables de entorno.
# Ver ../ACCESO.md. No guardar tokens temporales en este archivo.
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""

# IDs fijos de recursos (no cambian entre reinicios)
ASG_NAME="AWsAcademy-ASG"
TG_NAME="AWsAcademy-TG"
ALB_NAME="AWsAcademy-ALB"
ALB_DNS="AWsAcademy-ALB-1953310462.us-east-1.elb.amazonaws.com"

echo "============================================"
echo "  AWsAcademy - Arranque de infraestructura"
echo "============================================"

# 1. Verificar credenciales
echo "[1/6] Verificando credenciales..."
aws sts get-caller-identity --query 'Account' --output text || {
  echo "ERROR: Credenciales inválidas. Pega las nuevas de Vocareum."
  exit 1
}

# 2. Verificar EC2 (el ASG debería lanzarlas solas)
echo "[2/6] Verificando instancias EC2..."
DESIRED=$(aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names "$ASG_NAME" \
  --query 'AutoScalingGroups[0].DesiredCapacity' --output text)
echo "  ASG desired: $DESIRED"

# Si el ASG está en 0, forzarlo a 2
if [ "$DESIRED" = "0" ]; then
  echo "  ASG en 0, subiendo a 2..."
  aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name "$ASG_NAME" \
    --desired-capacity 2 --min-size 2
fi

# 3. Esperar a que las instancias estén running
echo "[3/6] Esperando instancias running..."
for i in $(seq 1 12); do
  COUNT=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=AWsAcademy-App" "Name=instance-state-name,Values=running" \
    --query 'length(Reservations[*].Instances[*])' --output text 2>/dev/null || echo 0)
  echo "  Running: $COUNT/2"
  if [ "$COUNT" -ge 2 ]; then break; fi
  sleep 15
done

# 4. Recrear listener del ALB (siempre se pierde)
echo "[4/6] Configurando ALB..."
TG_ARN=$(aws elbv2 describe-target-groups --names "$TG_NAME" \
  --query 'TargetGroups[0].TargetGroupArn' --output text)
ALB_ARN=$(aws elbv2 describe-load-balancers --names "$ALB_NAME" \
  --query 'LoadBalancers[0].LoadBalancerArn' --output text)

# Ver si ya tiene listener
LISTENER_COUNT=$(aws elbv2 describe-listeners --load-balancer-arn "$ALB_ARN" \
  --query 'length(Listeners)' --output text 2>/dev/null || echo 0)

if [ "$LISTENER_COUNT" = "0" ]; then
  echo "  Creando listener HTTP 80..."
  aws elbv2 create-listener \
    --load-balancer-arn "$ALB_ARN" \
    --protocol HTTP --port 80 \
    --default-actions Type=forward,TargetGroupArn="$TG_ARN"
else
  echo "  Listener ya existe."
fi

# 5. Registrar instancias en Target Group
echo "[5/6] Registrando instancias en Target Group..."
INSTANCE_IDS=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=AWsAcademy-App" "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].InstanceId' --output text)

for id in $INSTANCE_IDS; do
  aws elbv2 register-targets --target-group-arn "$TG_ARN" --targets Id=$id,Port=80
  echo "  Registrado: $id"
done

# 6. Verificar salud
echo "[6/6] Verificando salud... (espera ~30s)"
sleep 30
aws elbv2 describe-target-health --target-group-arn "$TG_ARN" \
  --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' --output table

echo ""
echo "============================================"
echo "  ARRANQUE COMPLETADO"
echo "============================================"
echo "  URL: http://$ALB_DNS"
echo ""
echo "  Probar: curl http://$ALB_DNS"
echo "============================================"