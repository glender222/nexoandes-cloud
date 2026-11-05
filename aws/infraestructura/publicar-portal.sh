#!/usr/bin/env bash
set -euo pipefail

# Publica el portal en las EC2 actuales por SSM y en el Launch Template
# para que sus reemplazos mantengan la misma versión.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
AWS="$SCRIPT_DIR/academy-aws"
TEAM_NUMBER=${1:-}
if [[ ! "$TEAM_NUMBER" =~ ^[[:alnum:]-]+$ ]]; then
  printf 'Uso: %s NUMERO_EQUIPO\n' "$0" >&2
  exit 2
fi

ACCOUNT=$("$AWS" sts get-caller-identity --query Account --output text)
if [[ "$ACCOUNT" != 669186512136 ]]; then
  printf 'Cuenta AWS inesperada: %s\n' "$ACCOUNT" >&2
  exit 1
fi

ASG_NAME=AWsAcademy-ASG
TG_ARN=$("$AWS" elbv2 describe-target-groups --names AWsAcademy-TG --query 'TargetGroups[0].TargetGroupArn' --output text)
ASG_TARGETS=$("$AWS" autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --query 'AutoScalingGroups[0].TargetGroupARNs' --output text)
if [[ " $ASG_TARGETS " != *" $TG_ARN "* ]]; then
  printf 'El ASG aún no está asociado al Target Group; revisar antes de publicar\n' >&2
  exit 1
fi

LT_ID=$("$AWS" autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --query 'AutoScalingGroups[0].LaunchTemplate.LaunchTemplateId' --output text)
LT_VERSION=$("$AWS" autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --query 'AutoScalingGroups[0].LaunchTemplate.Version' --output text)
if [[ -z "$LT_ID" || "$LT_ID" == None ]]; then
  printf 'No se encontró el Launch Template del ASG\n' >&2
  exit 1
fi

read -r -a APP_IDS <<< "$("$AWS" autoscaling describe-auto-scaling-groups --auto-scaling-group-names "$ASG_NAME" --query 'AutoScalingGroups[0].Instances[].InstanceId' --output text)"
if (( ${#APP_IDS[@]} < 2 )); then
  printf 'Se esperaban dos instancias web en el ASG\n' >&2
  exit 1
fi

# Solo se reemplaza el marcador en memoria; el archivo base sigue revisable.
USER_DATA_B64=$(sed "s/^TEAM_NUMBER=\"XX\"$/TEAM_NUMBER=\"$TEAM_NUMBER\"/" "$SCRIPT_DIR/user-data.sh" | base64 -w0)
CURRENT_B64=$("$AWS" ec2 describe-launch-template-versions --launch-template-id "$LT_ID" --versions '$Latest' --query 'LaunchTemplateVersions[0].LaunchTemplateData.UserData' --output text)
if [[ "$CURRENT_B64" != "$USER_DATA_B64" ]]; then
  NEW_VERSION=$("$AWS" ec2 create-launch-template-version \
    --launch-template-id "$LT_ID" --source-version '$Latest' \
    --version-description "NexoAndes Equipo $TEAM_NUMBER" \
    --launch-template-data "{\"UserData\":\"$USER_DATA_B64\",\"MetadataOptions\":{\"HttpTokens\":\"required\"}}" \
    --query 'LaunchTemplateVersion.VersionNumber' --output text)
  printf 'Launch Template: nueva versión %s\n' "$NEW_VERSION"
else
  NEW_VERSION=$("$AWS" ec2 describe-launch-template-versions --launch-template-id "$LT_ID" --versions '$Latest' --query 'LaunchTemplateVersions[0].VersionNumber' --output text)
  printf 'Launch Template: versión %s ya contiene el portal\n' "$NEW_VERSION"
fi

if [[ "$LT_VERSION" != '$Latest' && "$LT_VERSION" != "$NEW_VERSION" ]]; then
  "$AWS" autoscaling update-auto-scaling-group --auto-scaling-group-name "$ASG_NAME" \
    --launch-template "LaunchTemplateId=$LT_ID,Version=$NEW_VERSION"
fi

PARAMETERS=$(jq -nc --arg payload "$USER_DATA_B64" \
  '{commands:["printf %s "+$payload+" | base64 -d > /tmp/nexoandes-user-data.sh", "bash /tmp/nexoandes-user-data.sh"]}')
COMMAND_ID=$("$AWS" ssm send-command --document-name AWS-RunShellScript \
  --instance-ids "${APP_IDS[@]}" --parameters "$PARAMETERS" \
  --comment "Publicar portal NexoAndes Equipo $TEAM_NUMBER" \
  --query 'Command.CommandId' --output text)
printf 'SSM Command ID: %s\n' "$COMMAND_ID"
printf 'Instancias: %s\n' "${APP_IDS[*]}"

for id in "${APP_IDS[@]}"; do
  for attempt in {1..15}; do
    STATUS=$("$AWS" ssm get-command-invocation --command-id "$COMMAND_ID" --instance-id "$id" --query Status --output text 2>/dev/null || true)
    if [[ "$STATUS" == Success ]]; then
      printf '%s: Success\n' "$id"
      break
    fi
    if [[ "$STATUS" == Failed || "$STATUS" == Cancelled || "$STATUS" == TimedOut ]]; then
      printf '%s: %s\n' "$id" "$STATUS" >&2
      exit 1
    fi
    if (( attempt == 15 )); then
      printf '%s: espera agotada; revisar SSM Command ID %s\n' "$id" "$COMMAND_ID" >&2
      exit 1
    fi
    sleep 3
  done
done

printf 'Portal aplicado. Verificar ALB y guardar evidencias antes de afirmar éxito público.\n'
