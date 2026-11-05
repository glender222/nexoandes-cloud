#!/bin/bash
set -e
export AWS_PROFILE=academy
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/infra-params.env"

echo "============================================"
echo "  FASE 2: Launch Template + Auto Scaling"
echo "============================================"

# Usar el instance profile existente del lab
INSTANCE_PROFILE="LabInstanceProfile"
echo "[1/4] Usando IAM Instance Profile existente: $INSTANCE_PROFILE"

# Buscar AMI más reciente de Amazon Linux 2023
echo "[2/4] Buscando AMI..."
AMI_ID=$(aws ec2 describe-images --owners amazon --filters 'Name=name,Values=al2023-ami-2023*-x86_64' 'Name=state,Values=available' --query 'sort_by(Images,&CreationDate)[-1].ImageId' --output text)
echo "  AMI: $AMI_ID"

# User data mantenido en este directorio para que pueda revisarse antes de desplegar.
if [[ ! -f "$SCRIPT_DIR/user-data.sh" ]]; then
  echo "Falta user-data.sh" >&2
  exit 1
fi
if grep -q 'TEAM_NUMBER="XX"' "$SCRIPT_DIR/user-data.sh"; then
  echo "Define el número real de equipo en user-data.sh antes de desplegar" >&2
  exit 1
fi
if [[ -z "${TG_ARN:-}" ]]; then
  echo "Falta TG_ARN en infra-params.env" >&2
  exit 1
fi

USER_DATA_B64=$(base64 -w0 "$SCRIPT_DIR/user-data.sh")

echo "[3/4] Creando Launch Template..."
LAUNCH_TEMPLATE_ID=$(aws ec2 create-launch-template \
  --launch-template-name AWsAcademy-LT \
  --version-description "v1 - AL2023 + Apache" \
  --launch-template-data "{
    \"ImageId\": \"$AMI_ID\",
    \"InstanceType\": \"t3.micro\",
    \"KeyName\": \"AWsAcademy-Key\",
    \"SecurityGroupIds\": [\"$SG_APP\"],
    \"IamInstanceProfile\": {\"Name\": \"$INSTANCE_PROFILE\"},
    \"MetadataOptions\": {\"HttpTokens\": \"required\"},
    \"UserData\": \"$USER_DATA_B64\",
    \"TagSpecifications\": [{
      \"ResourceType\": \"instance\",
      \"Tags\": [{\"Key\": \"Name\", \"Value\": \"AWsAcademy-App\"}]
    }]
  }" \
  --query 'LaunchTemplate.LaunchTemplateId' --output text)
echo "  Launch Template: $LAUNCH_TEMPLATE_ID"

echo "[4/4] Creando Auto Scaling Group..."
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name AWsAcademy-ASG \
  --launch-template "LaunchTemplateId=$LAUNCH_TEMPLATE_ID,Version=\$Latest" \
  --min-size 2 \
  --max-size 4 \
  --desired-capacity 2 \
  --vpc-zone-identifier "$SUBNET_APP_A,$SUBNET_APP_B" \
  --target-group-arns "$TG_ARN" \
  --health-check-type ELB \
  --health-check-grace-period 120 \
  --tags "Key=Name,Value=AWsAcademy-App,PropagateAtLaunch=true"

echo "  ASG: AWsAcademy-ASG (min=2, max=4, desired=2)"

echo "  Esperando instancias..."
sleep 15
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=AWsAcademy-App" "Name=instance-state-name,Values=pending,running" \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,PrivateIpAddress,Placement.AvailabilityZone]' \
  --output table

echo ""
echo "============================================"
echo "  FASE 2 COMPLETADA"
echo "============================================"
