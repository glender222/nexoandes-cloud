#!/bin/bash
set -e

export AWS_PROFILE=academy
export AWS_DEFAULT_REGION=us-east-1
export AWS_PAGER=""

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
PRIVATE_DIR="$SCRIPT_DIR/../privado"

if [[ -e "$PRIVATE_DIR/AWsAcademy-Key.pem" || -e "$SCRIPT_DIR/infra-params.env" ]]; then
  echo "ERROR: ya existen la clave o los parámetros de infraestructura; revisa los recursos antes de crear otros." >&2
  exit 1
fi

VPC_CIDR="10.10.0.0/16"
PUBLIC_A="10.10.1.0/24"
PUBLIC_B="10.10.2.0/24"
PRIVATE_APP_A="10.10.11.0/24"
PRIVATE_APP_B="10.10.12.0/24"
PRIVATE_DB="10.10.20.0/24"

echo "============================================"
echo "  FASE 1: VPC + Subnets + Gateways"
echo "============================================"

# 1. Crear VPC
echo "[1/12] Creando VPC..."
VPC_ID=$(aws ec2 create-vpc --cidr-block $VPC_CIDR --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=AWsAcademy-VPC}]' --query 'Vpc.VpcId' --output text)
echo "  VPC: $VPC_ID"

aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames '{"Value":true}'
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support '{"Value":true}'

# 2. Crear Internet Gateway
echo "[2/12] Creando Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=AWsAcademy-IGW}]' --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
echo "  IGW: $IGW_ID"

# 3. Crear subnets
echo "[3/12] Creando subnets..."
# Obtener AZs disponibles
AZ_A=$(aws ec2 describe-availability-zones --query 'AvailabilityZones[0].ZoneName' --output text)
AZ_B=$(aws ec2 describe-availability-zones --query 'AvailabilityZones[1].ZoneName' --output text)
echo "  AZs: $AZ_A , $AZ_B"

SUBNET_PUB_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PUBLIC_A --availability-zone $AZ_A --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=AWsAcademy-Public-A}]' --query 'Subnet.SubnetId' --output text)
SUBNET_PUB_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PUBLIC_B --availability-zone $AZ_B --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=AWsAcademy-Public-B}]' --query 'Subnet.SubnetId' --output text)
SUBNET_APP_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PRIVATE_APP_A --availability-zone $AZ_A --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=AWsAcademy-PrivateApp-A}]' --query 'Subnet.SubnetId' --output text)
SUBNET_APP_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PRIVATE_APP_B --availability-zone $AZ_B --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=AWsAcademy-PrivateApp-B}]' --query 'Subnet.SubnetId' --output text)
SUBNET_DB=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block $PRIVATE_DB --availability-zone $AZ_A --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=AWsAcademy-PrivateDB}]' --query 'Subnet.SubnetId' --output text)

echo "  Public A: $SUBNET_PUB_A"
echo "  Public B: $SUBNET_PUB_B"
echo "  Private App A: $SUBNET_APP_A"
echo "  Private App B: $SUBNET_APP_B"
echo "  Private DB: $SUBNET_DB"

# 4. Auto-assign public IP on public subnets
echo "[4/12] Habilitando IPs públicas en subnets públicas..."
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_PUB_A --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_PUB_B --map-public-ip-on-launch

# 5. NAT Gateway (en Public A)
echo "[5/12] Creando NAT Gateway..."
# Necesita Elastic IP
EIP_ALLOC=$(aws ec2 allocate-address --domain vpc --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=AWsAcademy-NAT-EIP}]' --query 'AllocationId' --output text)
echo "  EIP: $EIP_ALLOC"
sleep 3

NAT_GW_ID=$(aws ec2 create-nat-gateway --subnet-id $SUBNET_PUB_A --allocation-id $EIP_ALLOC --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=AWsAcademy-NAT}]' --query 'NatGateway.NatGatewayId' --output text)
echo "  NAT GW: $NAT_GW_ID"

echo "  Esperando a que el NAT Gateway esté disponible (hasta 120s)..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_ID
echo "  NAT Gateway listo."

# 6. Tabla de ruteo pública
echo "[6/12] Configurando tablas de ruteo..."
RTB_PUBLIC=$(aws ec2 create-route-table --vpc-id $VPC_ID --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=AWsAcademy-PublicRT}]' --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $RTB_PUBLIC --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $RTB_PUBLIC --subnet-id $SUBNET_PUB_A
aws ec2 associate-route-table --route-table-id $RTB_PUBLIC --subnet-id $SUBNET_PUB_B
echo "  Ruta pública: $RTB_PUBLIC"

# 7. Tabla de ruteo privada (apps + db)
RTB_PRIVATE=$(aws ec2 create-route-table --vpc-id $VPC_ID --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=AWsAcademy-PrivateRT}]' --query 'RouteTable.RouteTableId' --output text)
aws ec2 create-route --route-table-id $RTB_PRIVATE --destination-cidr-block 0.0.0.0/0 --nat-gateway-id $NAT_GW_ID
aws ec2 associate-route-table --route-table-id $RTB_PRIVATE --subnet-id $SUBNET_APP_A
aws ec2 associate-route-table --route-table-id $RTB_PRIVATE --subnet-id $SUBNET_APP_B
aws ec2 associate-route-table --route-table-id $RTB_PRIVATE --subnet-id $SUBNET_DB
echo "  Ruta privada: $RTB_PRIVATE"

# 8. Security Group - ALB
echo "[7/12] Creando Security Groups..."
SG_ALB=$(aws ec2 create-security-group --group-name AWsAcademy-ALB-SG --description "ALB Security Group" --vpc-id $VPC_ID --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=AWsAcademy-ALB-SG}]' --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_ALB --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ALB --protocol tcp --port 443 --cidr 0.0.0.0/0
echo "  SG ALB: $SG_ALB"

# 9. Security Group - EC2 Apps (solo tráfico desde ALB)
SG_APP=$(aws ec2 create-security-group --group-name AWsAcademy-App-SG --description "EC2 App Security Group" --vpc-id $VPC_ID --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=AWsAcademy-App-SG}]' --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_APP --protocol tcp --port 80 --source-group $SG_ALB
aws ec2 authorize-security-group-ingress --group-id $SG_APP --protocol tcp --port 22 --cidr 0.0.0.0/0
echo "  SG App: $SG_APP"

# 10. Security Group - Database
SG_DB=$(aws ec2 create-security-group --group-name AWsAcademy-DB-SG --description "Database Security Group" --vpc-id $VPC_ID --tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=AWsAcademy-DB-SG}]' --query 'GroupId' --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_DB --protocol tcp --port 5432 --source-group $SG_APP
echo "  SG DB: $SG_DB"

# 11. Key Pair
echo "[8/12] Creando Key Pair..."
mkdir -p "$PRIVATE_DIR"
aws ec2 create-key-pair --key-name AWsAcademy-Key --query 'KeyMaterial' --output text > "$PRIVATE_DIR/AWsAcademy-Key.pem"
chmod 400 "$PRIVATE_DIR/AWsAcademy-Key.pem"
echo "  Key guardada en AWsAcademy-Key.pem"

# 12. Guardar IDs para fases siguientes
echo "[9/12] Guardando parámetros..."
PARAM_FILE="$SCRIPT_DIR/infra-params.env"
cat > $PARAM_FILE << PARAMS
VPC_ID=$VPC_ID
IGW_ID=$IGW_ID
NAT_GW_ID=$NAT_GW_ID
SUBNET_PUB_A=$SUBNET_PUB_A
SUBNET_PUB_B=$SUBNET_PUB_B
SUBNET_APP_A=$SUBNET_APP_A
SUBNET_APP_B=$SUBNET_APP_B
SUBNET_DB=$SUBNET_DB
RTB_PUBLIC=$RTB_PUBLIC
RTB_PRIVATE=$RTB_PRIVATE
SG_ALB=$SG_ALB
SG_APP=$SG_APP
SG_DB=$SG_DB
AZ_A=$AZ_A
AZ_B=$AZ_B
PARAMS
echo "  Parámetros guardados en $PARAM_FILE"

echo ""
echo "============================================"
echo "  FASE 1 COMPLETADA — VPC lista"
echo "============================================"
echo "VPC ID: $VPC_ID"
echo "Subnets públicas: $SUBNET_PUB_A, $SUBNET_PUB_B"
echo "Subnets app privadas: $SUBNET_APP_A, $SUBNET_APP_B"
echo "Subnet DB: $SUBNET_DB"
