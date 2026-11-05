#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_DIR="$SCRIPT_DIR/.."
AWS="$PROJECT_DIR/aws/infraestructura/academy-aws"

if [[ ! -f "$SCRIPT_DIR/recursos_examen.env" ]]; then
  printf "No se encontró recursos_examen.env. Nada que destruir.\n"
  exit 0
fi

source "$SCRIPT_DIR/recursos_examen.env"

printf "=== ELIMINACIÓN DE RECURSOS DEL EXAMEN ===\n"
printf "VPC: %s\nInstancia: %s\nBucket: %s\n\n" "$VPC_ID" "$INSTANCE_ID" "$BUCKET_NAME"

# 1. Terminar EC2
if [[ -n "${INSTANCE_ID:-}" ]]; then
  printf "Terminando instancia EC2 %s...\n" "$INSTANCE_ID"
  "$AWS" ec2 terminate-instances --instance-ids "$INSTANCE_ID" || true
  printf "Esperando a que la instancia termine...\n"
  "$AWS" ec2 wait instance-terminated --instance-ids "$INSTANCE_ID" || true
fi

# 2. Vaciar y eliminar Bucket S3
if [[ -n "${BUCKET_NAME:-}" ]]; then
  printf "Vaciando y eliminando bucket S3 %s...\n" "$BUCKET_NAME"
  "$AWS" s3 rm "s3://$BUCKET_NAME" --recursive || true
  "$AWS" s3api delete-bucket --bucket "$BUCKET_NAME" --region us-east-1 || true
fi

# 3. Eliminar Security Group
if [[ -n "${SG_ID:-}" ]]; then
  printf "Eliminando Security Group %s...\n" "$SG_ID"
  "$AWS" ec2 delete-security-group --group-id "$SG_ID" || true
fi

# 4. Desasociar y eliminar Route Table
if [[ -n "${RT_ID:-}" ]]; then
  printf "Eliminando Route Table %s...\n" "$RT_ID"
  ASSOC_ID=$("$AWS" ec2 describe-route-tables --route-table-ids "$RT_ID" --query 'RouteTables[0].Associations[?SubnetId!=null].RouteTableAssociationId' --output text || true)
  for a in $ASSOC_ID; do
    "$AWS" ec2 disassociate-route-table --association-id "$a" || true
  done
  "$AWS" ec2 delete-route-table --route-table-id "$RT_ID" || true
fi

# 5. Eliminar Subnet
if [[ -n "${SUBNET_ID:-}" ]]; then
  printf "Eliminando Subnet %s...\n" "$SUBNET_ID"
  "$AWS" ec2 delete-subnet --subnet-id "$SUBNET_ID" || true
fi

# 6. Desasociar y eliminar IGW
if [[ -n "${IGW_ID:-}" ]]; then
  printf "Desasociando y eliminando Internet Gateway %s...\n" "$IGW_ID"
  "$AWS" ec2 detach-internet-gateway --internet-gateway-id "$IGW_ID" --vpc-id "$VPC_ID" || true
  "$AWS" ec2 delete-internet-gateway --internet-gateway-id "$IGW_ID" || true
fi

# 7. Eliminar VPC
if [[ -n "${VPC_ID:-}" ]]; then
  printf "Eliminando VPC %s...\n" "$VPC_ID"
  "$AWS" ec2 delete-vpc --vpc-id "$VPC_ID" || true
fi

printf "Recursos del examen eliminados exitosamente. (NexoAndes permanece intacto).\n"
rm -f "$SCRIPT_DIR/recursos_examen.env"
