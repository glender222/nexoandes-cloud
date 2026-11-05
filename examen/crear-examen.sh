#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PROJECT_DIR="$SCRIPT_DIR/.."
AWS="$PROJECT_DIR/aws/infraestructura/academy-aws"
EVIDENCIAS="$SCRIPT_DIR/evidencias"
mkdir -p "$EVIDENCIAS"

printf "=== DESPLIEGUE EXAMEN PRÁCTICO CLOUD COMPUTING ===\n"
printf "Estudiante: Glender Vargas\n"
printf "Fecha: 22/10/2026\n\n"

# 1. Comprobar identidad
printf "1. Comprobando sesión AWS...\n"
"$AWS" sts get-caller-identity > "$EVIDENCIAS/01_sts_identity.json"
ACCOUNT_ID=$(jq -r .Account "$EVIDENCIAS/01_sts_identity.json")
printf "Autenticado en cuenta: %s\n" "$ACCOUNT_ID"

# 2. Crear VPC
printf "2. Creando VPC (10.20.0.0/16)...\n"
VPC_ID=$("$AWS" ec2 create-vpc \
  --cidr-block 10.20.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-VPC},{Key=Evaluacion,Value=ExamenSemana7}]' \
  --query 'Vpc.VpcId' --output text)

printf "VPC creada: %s\n" "$VPC_ID"
"$AWS" ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames '{"Value":true}'
"$AWS" ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-support '{"Value":true}'
"$AWS" ec2 describe-vpcs --vpc-ids "$VPC_ID" > "$EVIDENCIAS/02_vpc.json"

# 3. Crear Subnet pública
printf "3. Creando Subnet pública (10.20.10.0/24)...\n"
SUBNET_ID=$("$AWS" ec2 create-subnet \
  --vpc-id "$VPC_ID" \
  --cidr-block 10.20.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-SUBNET-PUB}]' \
  --query 'Subnet.SubnetId' --output text)

printf "Subnet creada: %s\n" "$SUBNET_ID"
"$AWS" ec2 modify-subnet-attribute --subnet-id "$SUBNET_ID" --map-public-ip-on-launch
"$AWS" ec2 describe-subnets --subnet-ids "$SUBNET_ID" > "$EVIDENCIAS/03_subnet.json"

# 4. Crear Internet Gateway
printf "4. Creando y asociando Internet Gateway...\n"
IGW_ID=$("$AWS" ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-IGW}]' \
  --query 'InternetGateway.InternetGatewayId' --output text)

printf "Internet Gateway creado: %s\n" "$IGW_ID"
"$AWS" ec2 attach-internet-gateway --vpc-id "$VPC_ID" --internet-gateway-id "$IGW_ID"
"$AWS" ec2 describe-internet-gateways --internet-gateway-ids "$IGW_ID" > "$EVIDENCIAS/04_igw.json"

# 5. Crear Route Table y ruta 0.0.0.0/0 -> IGW
printf "5. Configurando Route Table...\n"
RT_ID=$("$AWS" ec2 create-route-table \
  --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-RT}]' \
  --query 'RouteTable.RouteTableId' --output text)

printf "Route Table creada: %s\n" "$RT_ID"
"$AWS" ec2 create-route --route-table-id "$RT_ID" --destination-cidr-block 0.0.0.0/0 --gateway-id "$IGW_ID"
"$AWS" ec2 associate-route-table --subnet-id "$SUBNET_ID" --route-table-id "$RT_ID"
"$AWS" ec2 describe-route-tables --route-table-ids "$RT_ID" > "$EVIDENCIAS/05_route_table.json"

# 6. Crear Security Group
printf "6. Creando Security Group (HTTP 80, SSH 22)...\n"
SG_ID=$("$AWS" ec2 create-security-group \
  --group-name EXAMEN-GLENDERVARGAS-SG \
  --description "Security Group para servidor web de examen InnovaTech" \
  --vpc-id "$VPC_ID" \
  --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-SG}]' \
  --query 'GroupId' --output text)

printf "Security Group creado: %s\n" "$SG_ID"
"$AWS" ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0
"$AWS" ec2 authorize-security-group-ingress --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0
"$AWS" ec2 describe-security-groups --group-ids "$SG_ID" > "$EVIDENCIAS/06_security_group.json"

# 7. Preparar UserData para EC2
cat << 'USERDATA_EOF' > "$SCRIPT_DIR/userdata.sh"
#!/bin/bash
dnf update -y
dnf install -y httpd
systemctl enable httpd
systemctl start httpd

cat << 'HTML' > /var/www/html/index.html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EXAMEN CLOUD COMPUTING</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #f0f4f8;
      color: #232f3e;
      margin: 0;
      padding: 40px 20px;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 80vh;
    }
    .card {
      background: #ffffff;
      border-radius: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
      max-width: 650px;
      width: 100%;
      padding: 40px;
      border-top: 6px solid #ff9900;
    }
    h1 {
      color: #1a2530;
      font-size: 26px;
      margin-top: 0;
      margin-bottom: 12px;
      border-bottom: 2px solid #eaeded;
      padding-bottom: 12px;
    }
    .badge {
      display: inline-block;
      background-color: #0073bb;
      color: #ffffff;
      padding: 6px 14px;
      border-radius: 20px;
      font-weight: 600;
      font-size: 14px;
      margin-bottom: 20px;
    }
    .info-group {
      margin: 14px 0;
      font-size: 16px;
      line-height: 1.6;
    }
    .info-label {
      font-weight: 700;
      color: #555;
      display: inline-block;
      width: 190px;
    }
    .info-value {
      color: #111;
      font-weight: 600;
    }
    .footer {
      margin-top: 30px;
      padding-top: 15px;
      border-top: 1px dashed #d5dbdb;
      font-size: 13px;
      color: #767676;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>EXAMEN CLOUD COMPUTING</h1>
    <div class="badge">Servidor implementado en AWS</div>
    <div class="info-group">
      <span class="info-label">Estudiante:</span>
      <span class="info-value">Glender Vargas</span>
    </div>
    <div class="info-group">
      <span class="info-label">Caso de evaluación:</span>
      <span class="info-value">InnovaTech Perú &mdash; Servidor Web Linux</span>
    </div>
    <div class="info-group">
      <span class="info-label">Docente:</span>
      <span class="info-value">Asin Gomez Fernando Manuel</span>
    </div>
    <div class="info-group">
      <span class="info-label">Fecha:</span>
      <span class="info-value">22 / 10 / 2026</span>
    </div>
    <div class="info-group">
      <span class="info-label">Plataforma:</span>
      <span class="info-value">AWS Academy Learner Lab (Amazon Linux 2023)</span>
    </div>
    <div class="footer">
      Servidor Apache HTTPD activo &bull; Puerto 80 &bull; Arquitectura VPC propia
    </div>
  </div>
</body>
</html>
HTML
USERDATA_EOF

# 8. Lanzar Instancia EC2
printf "7. Lanzando instancia EC2 EXAMEN-GLENDERVARGAS-WEB (t3.micro)...\n"
INSTANCE_ID=$("$AWS" ec2 run-instances \
  --image-id ami-08c46876c64a927b8 \
  --instance-type t3.micro \
  --key-name vockey \
  --subnet-id "$SUBNET_ID" \
  --security-group-ids "$SG_ID" \
  --associate-public-ip-address \
  --user-data "file://$SCRIPT_DIR/userdata.sh" \
  --tag-specifications \
    'ResourceType=instance,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-WEB}]' \
    'ResourceType=volume,Tags=[{Key=Name,Value=EXAMEN-GLENDERVARGAS-WEB-ROOT}]' \
  --query 'Instances[0].InstanceId' --output text)

printf "Instancia EC2 creada: %s. Esperando estado 'running'...\n" "$INSTANCE_ID"
"$AWS" ec2 wait instance-running --instance-ids "$INSTANCE_ID"
"$AWS" ec2 describe-instances --instance-ids "$INSTANCE_ID" > "$EVIDENCIAS/07_ec2.json"

PUBLIC_IP=$(jq -r '.Reservations[0].Instances[0].PublicIpAddress' "$EVIDENCIAS/07_ec2.json")
PRIVATE_IP=$(jq -r '.Reservations[0].Instances[0].PrivateIpAddress' "$EVIDENCIAS/07_ec2.json")
printf "EC2 Running!\nIP Privada: %s\nIP Pública: %s\n" "$PRIVATE_IP" "$PUBLIC_IP"

# 9. Crear Bucket S3 y cargar archivos
BUCKET_NAME="examen-cloud-gv-${ACCOUNT_ID}"
printf "8. Creando Bucket S3: %s...\n" "$BUCKET_NAME"

"$AWS" s3api create-bucket --bucket "$BUCKET_NAME" --region us-east-1 > /dev/null
"$AWS" s3api put-public-access-block --bucket "$BUCKET_NAME" \
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Crear archivos de ejemplo para cada prefijo
mkdir -p "$SCRIPT_DIR/s3_archivos"
echo "Política de seguridad y control de acceso - InnovaTech Perú" > "$SCRIPT_DIR/s3_archivos/politica_seguridad_innovatech.txt"
echo "Evidencia técnica de arquitectura y despliegue en AWS" > "$SCRIPT_DIR/s3_archivos/evidencia_despliegue_arquitectura.txt"
echo "Respaldo de configuración httpd y sitio web de InnovaTech Perú" > "$SCRIPT_DIR/s3_archivos/respaldo_configuracion_web.txt"

"$AWS" s3 cp "$SCRIPT_DIR/s3_archivos/politica_seguridad_innovatech.txt" "s3://$BUCKET_NAME/documentos/politica_seguridad_innovatech.txt"
"$AWS" s3 cp "$SCRIPT_DIR/s3_archivos/evidencia_despliegue_arquitectura.txt" "s3://$BUCKET_NAME/evidencias/evidencia_despliegue_arquitectura.txt"
"$AWS" s3 cp "$SCRIPT_DIR/s3_archivos/respaldo_configuracion_web.txt" "s3://$BUCKET_NAME/backup/respaldo_configuracion_web.txt"

"$AWS" s3api get-public-access-block --bucket "$BUCKET_NAME" > "$EVIDENCIAS/08_s3_public_access_block.json"
"$AWS" s3api list-objects-v2 --bucket "$BUCKET_NAME" > "$EVIDENCIAS/09_s3_objetos.json"

# 10. Guardar variables de recursos para el informe y destrucción
cat << EOF_ENV > "$SCRIPT_DIR/recursos_examen.env"
ACCOUNT_ID="$ACCOUNT_ID"
VPC_ID="$VPC_ID"
SUBNET_ID="$SUBNET_ID"
IGW_ID="$IGW_ID"
RT_ID="$RT_ID"
SG_ID="$SG_ID"
INSTANCE_ID="$INSTANCE_ID"
PUBLIC_IP="$PUBLIC_IP"
PRIVATE_IP="$PRIVATE_IP"
BUCKET_NAME="$BUCKET_NAME"
EOF_ENV

printf "\n=== DESPLIEGUE FINALIZADO EXITOSAMENTE ===\n"
printf "URL Pública del Servidor Web: http://%s\n" "$PUBLIC_IP"
