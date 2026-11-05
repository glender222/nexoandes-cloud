#!/usr/bin/env bash
set -euo pipefail

# Todas las llamadas a AWS de este script son describe/get/list.
# Guarda JSON localmente para sustentar el Entregable 1.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
AWS="$SCRIPT_DIR/academy-aws"
OUT_DIR=${1:-"$SCRIPT_DIR/../evidencias/inventario-actual"}
mkdir -p "$OUT_DIR"

"$AWS" sts get-caller-identity --query '{Account:Account,Arn:Arn}' --output json > "$OUT_DIR/identidad.json"
"$AWS" ec2 describe-vpcs --filters 'Name=tag:Name,Values=AWsAcademy-VPC' --query 'Vpcs[].{Id:VpcId,Cidr:CidrBlock,State:State}' --output json > "$OUT_DIR/vpc.json"
VPC_ID=$("$AWS" ec2 describe-vpcs --filters 'Name=tag:Name,Values=AWsAcademy-VPC' --query 'Vpcs[0].VpcId' --output text)
if [[ -z "$VPC_ID" || "$VPC_ID" == None ]]; then
  printf 'No se encontró la VPC AWsAcademy-VPC\n' >&2
  exit 1
fi

"$AWS" ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[].{Id:SubnetId,Cidr:CidrBlock,AZ:AvailabilityZone,PublicIP:MapPublicIpOnLaunch,Name:Tags[?Key==`Name`].Value|[0]}' --output json > "$OUT_DIR/subredes.json"
"$AWS" ec2 describe-route-tables --filters "Name=vpc-id,Values=$VPC_ID" --query 'RouteTables[].{Id:RouteTableId,Routes:Routes[].{Dest:DestinationCidrBlock,Gateway:GatewayId,NAT:NatGatewayId,State:State},Subnets:Associations[].SubnetId,Name:Tags[?Key==`Name`].Value|[0]}' --output json > "$OUT_DIR/rutas.json"
"$AWS" ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" --query 'SecurityGroups[].{Id:GroupId,Name:GroupName,Ingress:IpPermissions,Egress:IpPermissionsEgress}' --output json > "$OUT_DIR/grupos-seguridad.json"
"$AWS" ec2 describe-instances --filters 'Name=tag:Name,Values=AWsAcademy-App,AWsAcademy-DB' --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Name:Tags[?Key==`Name`].Value|[0],AZ:Placement.AvailabilityZone,PrivateIP:PrivateIpAddress,Type:InstanceType}' --output json > "$OUT_DIR/instancias.json"
"$AWS" autoscaling describe-auto-scaling-groups --auto-scaling-group-names AWsAcademy-ASG --query 'AutoScalingGroups[].{Name:AutoScalingGroupName,Desired:DesiredCapacity,Min:MinSize,Max:MaxSize,HealthCheck:HealthCheckType,Targets:TargetGroupARNs,LaunchTemplate:LaunchTemplate,Instances:Instances[].{Id:InstanceId,State:LifecycleState,Health:HealthStatus}}' --output json > "$OUT_DIR/asg.json"
"$AWS" elbv2 describe-load-balancers --names AWsAcademy-ALB --query 'LoadBalancers[].{Arn:LoadBalancerArn,DNS:DNSName,State:State.Code,Scheme:Scheme,Subnets:AvailabilityZones[].SubnetId}' --output json > "$OUT_DIR/alb.json"
"$AWS" elbv2 describe-target-groups --names AWsAcademy-TG --query 'TargetGroups[].{Arn:TargetGroupArn,VpcId:VpcId,Protocol:Protocol,Port:Port,HealthPath:HealthCheckPath,LoadBalancers:LoadBalancerArns}' --output json > "$OUT_DIR/target-group.json"
ALB_ARN=$(jq -r '.[0].Arn // empty' "$OUT_DIR/alb.json")
TG_ARN=$(jq -r '.[0].Arn // empty' "$OUT_DIR/target-group.json")
if [[ -n "$ALB_ARN" ]]; then
  "$AWS" elbv2 describe-listeners --load-balancer-arn "$ALB_ARN" --query 'Listeners[].{Arn:ListenerArn,Protocol:Protocol,Port:Port,Actions:DefaultActions}' --output json > "$OUT_DIR/listeners.json"
fi
if [[ -n "$TG_ARN" ]]; then
  "$AWS" elbv2 describe-target-health --target-group-arn "$TG_ARN" --query 'TargetHealthDescriptions[].{Id:Target.Id,State:TargetHealth.State,Reason:TargetHealth.Reason}' --output json > "$OUT_DIR/target-health.json"
fi
"$AWS" ssm describe-instance-information --query 'InstanceInformationList[].{Id:InstanceId,Status:PingStatus,Platform:PlatformName}' --output json > "$OUT_DIR/ssm.json"
"$AWS" cloudwatch describe-alarms --alarm-name-prefix AWsAcademy --query 'MetricAlarms[].{Name:AlarmName,State:StateValue,Metric:MetricName,Actions:ActionsEnabled}' --output json > "$OUT_DIR/alarmas.json"
"$AWS" s3api list-objects-v2 --bucket awsacademy-backup-1789674826 --max-keys 1 --query '{ObjectCount:KeyCount,IsTruncated:IsTruncated}' --output json > "$OUT_DIR/s3-objetos.json"
LT_ID=$(jq -r '.[0].LaunchTemplate.LaunchTemplateId // empty' "$OUT_DIR/asg.json")
if [[ -n "$LT_ID" ]]; then
  "$AWS" ec2 describe-launch-template-versions --launch-template-id "$LT_ID" --versions '$Latest' --query 'LaunchTemplateVersions[].{Version:VersionNumber,Created:CreateTime,Image:LaunchTemplateData.ImageId,Type:LaunchTemplateData.InstanceType,Metadata:LaunchTemplateData.MetadataOptions}' --output json > "$OUT_DIR/launch-template.json"
fi

date -u '+%Y-%m-%dT%H:%M:%SZ' > "$OUT_DIR/consultado_utc.txt"
printf 'Inventario AWS de solo lectura: %s\n' "$OUT_DIR"
