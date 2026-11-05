#!/usr/bin/env python3
"""Control local de Terraform. Nunca ejecuta ni imprime archivos de credenciales."""
from __future__ import annotations

import argparse
import configparser
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "infraestructura/privado"
CONFIG = PRIVATE / "config.json"
CLOUDS = ("aws", "azure", "gcp")
EPHEMERAL = {
    "aws_eip", "aws_nat_gateway", "aws_route", "aws_lb", "aws_lb_listener",
    "aws_lb_target_group", "aws_lb_target_group_attachment", "aws_lb_listener_rule",
    "aws_launch_template", "aws_autoscaling_group",
    "aws_autoscaling_policy", "aws_cloudwatch_metric_alarm",
    "azurerm_public_ip", "azurerm_virtual_network_gateway",
    "azurerm_local_network_gateway", "azurerm_virtual_network_gateway_connection",
}


class ControlError(Exception):
    pass


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temp.chmod(0o600)
    temp.replace(path)


def configure():
    PRIVATE.mkdir(parents=True, exist_ok=True, mode=0o700)
    PRIVATE.chmod(0o700)
    if not CONFIG.exists():
        shutil.copyfile(ROOT / "infraestructura/config.example.json", CONFIG)
        CONFIG.chmod(0o600)
        print("Configuración creada:", CONFIG, flush=True)
    return json.loads(CONFIG.read_text())


def run(args, *, env=None, capture=False, allowed=(0,)):
    result = subprocess.run([str(x) for x in args], env=env, text=True,
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None)
    if result.returncode not in allowed:
        # Las llamadas de identidad solo devuelven identificadores o errores.
        detail = (result.stderr or "").strip() if capture else "Revisa la salida anterior."
        raise ControlError(f"Falló {Path(str(args[0])).name} (código {result.returncode}). {detail}")
    return result


def parse_aws_credentials(text):
    """Acepta export/env e INI [default], sin source/eval ni interpolación."""
    names = {name.lower(): name for name in (
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN")}
    result = {}
    section = "default"
    for raw in text.splitlines():
        line = raw.strip().lstrip("\ufeff")
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if section != "default":
            continue
        match = re.fullmatch(r"(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
        if match and match[1].lower() in names:
            value = match[2].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            if value:
                result[names[match[1].lower()]] = value
    if len(result) != 3:
        raise ControlError("Faltan las tres credenciales temporales AWS en aws/privado/academy-session.env.")
    return result


def cloud_environment(cloud, config):
    env = os.environ.copy()
    variables = dict(config.get("variables", {}))
    # Las credenciales nunca se escriben en tfvars ni en los archivos del plan.
    if cloud == "aws":
        for key in ("AWS_PROFILE", "AWS_DEFAULT_PROFILE", "AWS_ACCESS_KEY_ID",
                    "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_SECURITY_TOKEN",
                    "AWS_ENDPOINT_URL", "AWS_ENDPOINT_URL_STS", "AWS_ENDPOINT_URL_EC2"):
            env.pop(key, None)
        path = ROOT / "aws/privado/academy-session.env"
        if not path.exists():
            raise ControlError(f"Falta {path}")
        env.update(parse_aws_credentials(path.read_text()))
        env.update(AWS_DEFAULT_REGION=config["region"], AWS_REGION=config["region"], AWS_PAGER="")
        variables.update(expected_account_id=config["cuenta"], region=config["region"])
    elif cloud == "azure":
        env["AZURE_CONFIG_DIR"] = config.get("cli_config_dir") or str(ROOT / "azure/privado/az-config")
        # Usar la misma sesión CLI que verifica comprobar(), sin otras identidades ARM.
        for key in list(env):
            if key.startswith("ARM_"):
                env.pop(key)
        env.update(ARM_USE_CLI="true", ARM_SUBSCRIPTION_ID=config["suscripcion"], ARM_TENANT_ID=config["tenant"])
        variables.update(subscription_id=config["suscripcion"], tenant_id=config["tenant"])
    elif cloud == "gcp":
        key_file = config.get("service_account_key")
        if key_file:
            key_path = Path(os.path.expanduser(key_file))
            if not key_path.is_absolute():
                key_path = ROOT / key_path
            if key_path.is_file():
                env["GOOGLE_APPLICATION_CREDENTIALS"] = str(key_path.resolve())
        variables.update(project=config.get("proyecto", ""), region=config.get("region", "us-central1"))
    else:
        env["PATH"] = str(PRIVATE / "bin") + os.pathsep + env.get("PATH", os.defpath)
        path = ROOT / "oci/privado/config"
        parser = configparser.ConfigParser(interpolation=None)
        if not parser.read(path):
            raise ControlError("Falta oci/privado/config con el perfil API de OCI.")
        profile = config.get("perfil", "DEFAULT")
        if profile != "DEFAULT" and not parser.has_section(profile):
            raise ControlError(f"No existe el perfil OCI {profile}.")
        data = parser[profile]
        if data.get("tenancy") != config["tenancy"] or data.get("region") != config["region"]:
            raise ControlError("La tenancy/región del perfil OCI no coincide con la configuración del proyecto.")
        for name in ("user", "fingerprint", "key_file"):
            if not data.get(name):
                raise ControlError(f"Falta {name} en el perfil privado OCI.")
        key = Path(os.path.expanduser(data["key_file"]))
        if not key.is_absolute():
            key = path.parent / key
        if not key.is_file():
            raise ControlError("No se encontró la clave API privada de OCI.")
        if data.get("pass_phrase"):
            env["OCI_PRIVATE_KEY_PASSWORD"] = data["pass_phrase"]
        variables.update(tenancy_ocid=config["tenancy"], user_ocid=data["user"],
                         fingerprint=data["fingerprint"], private_key_path=str(key.resolve()), region=config["region"])
        env.update(OCI_CLI_CONFIG_FILE=str(path), OCI_CLI_PROFILE=profile)
    return env, variables


def identity_key(cloud, config):
    identity = config.get({"aws": "cuenta", "azure": "suscripcion", "gcp": "proyecto", "oci": "tenancy"}.get(cloud, ""), "")
    region = config.get("region", config.get("variables", {}).get("location", ""))
    if not identity or not re.fullmatch(r"[A-Za-z0-9_.-]+", identity + region):
        raise ControlError(f"Configura identidad y región válidas para {cloud}.")
    return identity + "-" + region


def check_identity(cloud, config, env):
    if cloud == "aws":
        data = json.loads(run(["aws", "sts", "get-caller-identity", "--region", config["region"],
                               "--query", "{Account:Account,Arn:Arn}", "--output", "json",
                               "--cli-connect-timeout", "10", "--cli-read-timeout", "20"], env=env, capture=True).stdout)
        if data["Account"] != config["cuenta"]:
            raise ControlError("Cuenta AWS inesperada; no se modifica infraestructura.")
        print(f"AWS: cuenta {data['Account']}, región {config['region']}, acceso vigente.", flush=True)
    elif cloud == "azure":
        data = json.loads(run(["az", "account", "show", "--subscription", config["suscripcion"],
                               "--query", "{id:id,tenant:tenantId}", "--output", "json"], env=env, capture=True).stdout)
        if data["id"] != config["suscripcion"] or data["tenant"] != config["tenant"]:
            raise ControlError("Suscripción/tenant Azure inesperados.")
        providers = ["Microsoft.Network", "Microsoft.Storage"]
        if config.get("variables", {}).get("enable_monitoring"):
            providers.append("Microsoft.OperationalInsights")
        for provider in providers:
            state = run(["az", "provider", "show", "--namespace", provider, "--subscription", config["suscripcion"],
                         "--query", "registrationState", "--output", "tsv"], env=env, capture=True).stdout.strip()
            if state != "Registered":
                raise ControlError(f"Azure: registrar {provider} en la suscripción antes de desplegar.")
        print(f"Azure: suscripción {data['id']}, tenant comprobado.", flush=True)
    elif cloud == "gcp":
        key_path = Path(env.get("GOOGLE_APPLICATION_CREDENTIALS", ROOT / "gcp/privado/sa-key.json"))
        if not key_path.is_file():
            raise ControlError("Falta la llave de cuenta de servicio en gcp/privado/sa-key.json.")
        try:
            with open(key_path) as f:
                key_data = json.load(f)
            project_in_key = key_data.get("project_id", "")
            client_email = key_data.get("client_email", "")
        except Exception as err:
            raise ControlError(f"Archivo de credenciales GCP inválido: {err}")
        if project_in_key != config["proyecto"]:
            raise ControlError(f"El proyecto en la llave ({project_in_key}) no coincide con config.json ({config['proyecto']}).")
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        credentials = service_account.Credentials.from_service_account_file(str(key_path), scopes=["https://www.googleapis.com/auth/compute.readonly"])
        response = AuthorizedSession(credentials).get(
            f"https://compute.googleapis.com/compute/v1/projects/{config['proyecto']}/zones/{config.get('region', 'us-central1')}-a/instances?maxResults=1", timeout=20)
        if not response.ok:
            raise ControlError(f"GCP: la consulta real de Compute no autoriza el acceso (HTTP {response.status_code}).")
        print(f"GCP: proyecto {config['proyecto']}, cuenta de servicio {client_email}, región {config.get('region', 'us-central1')}; API Compute comprobada.", flush=True)
    else:
        # OCI CLI permite una comprobación independiente del proveedor Terraform.
        if not shutil.which("oci", path=env.get("PATH")):
            raise ControlError("Ejecuta ./scripts/instalar-oci-cli.sh y configura oci/privado/config antes de habilitar OCI.")
        run(["oci", "os", "ns", "get", "--region", config["region"],
             "--compartment-id", config["tenancy"]], env=env, capture=True)
        print(f"OCI: acceso al namespace de {config['tenancy']}; región {config['region']}.", flush=True)


def terraform_binary():
    local = PRIVATE / "bin/terraform"
    binary = str(local) if local.is_file() else shutil.which("terraform")
    if not binary:
        raise ControlError("Ejecuta ./scripts/instalar-terraform.sh")
    data = json.loads(run([binary, "version", "-json"], capture=True).stdout)
    if data["terraform_version"] != "1.17.0":
        raise ControlError("Este proyecto usa Terraform 1.17.0. Ejecuta ./scripts/instalar-terraform.sh")
    return binary


def state_path(cloud, config):
    return PRIVATE / "estado" / cloud / (identity_key(cloud, config) + ".tfstate")


def initialized(cloud, config, env):
    binary = terraform_binary()
    root = ROOT / cloud / "terraform"
    state = state_path(cloud, config)
    state.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    env = env.copy()
    env.update(TF_IN_AUTOMATION="1", CHECKPOINT_DISABLE="1",
               TF_WORKSPACE="default",
               TF_DATA_DIR=str(PRIVATE / "proveedores" / cloud / identity_key(cloud, config)))
    # TF_VAR externos no pueden sobreescribir los parámetros fijados para esta operación.
    for key in list(env):
        if key.startswith("TF_VAR_") or key.startswith("TF_CLI_ARGS") or key.startswith("TF_LOG"):
            env.pop(key)
    prefix = [binary, "-chdir=" + str(root)]
    run(prefix + ["init", "-input=false", "-reconfigure", "-no-color", "-backend-config=path=" + str(state)], env=env)
    return prefix, env, state


def guard_plan(plan, action):
    changes = []
    for resource in plan.get("resource_changes", []):
        if resource.get("mode") != "managed":
            continue
        actions = resource["change"]["actions"]
        if actions == ["no-op"]:
            continue
        kind = resource["type"]
        bootstrap_marker = kind == "terraform_data" and resource["address"] == "terraform_data.backup"
        vpn_gateway = kind == "aws_instance" and resource["address"] == "aws_instance.vpn[0]"
        if "delete" in actions and kind not in EPHEMERAL and not bootstrap_marker and not vpn_gateway:
            raise ControlError("El plan intenta eliminar o reemplazar un recurso persistente: " + resource["address"])
        if action == "apagar" and "create" in actions:
            raise ControlError("Apagar no puede crear recursos: " + resource["address"])
        changes.append({"recurso": resource["address"], "acciones": actions})
    return changes


def bucket_generation(config, env, state, action):
    """Detectar un bucket borrado externamente sin ejecutar Object Lock ni crear en plan."""
    generation = "initial"
    managed = False
    if state.exists():
        for resource in json.loads(state.read_text()).get("resources", []):
            if resource["type"] == "terraform_data" and resource["name"] == "backup":
                for instance in resource.get("instances", []):
                    value = instance.get("attributes", {}).get("input", {}).get("value", {})
                    generation = value.get("generation", generation)
                    managed = True
    bucket = f"nexoandes-backup-{config['cuenta']}-{config['region']}"
    result = subprocess.run(["aws", "s3api", "head-bucket", "--bucket", bucket,
                             "--expected-bucket-owner", config["cuenta"], "--region", config["region"]],
                            env=env, text=True, capture_output=True)
    if result.returncode and not any(code in result.stderr for code in ("(404)", "(NoSuchBucket)", "(NotFound)")):
        raise ControlError("No se pudo comprobar el bucket S3: " + result.stderr.strip())
    if result.returncode and managed and action == "encender":
        generation = stamp()
        print("El bucket administrado ya no existe; el plan incluirá su reconstrucción vacía.", flush=True)
    return generation


def make_plan(cloud, config, action, transaction):
    env, variables = cloud_environment(cloud, config)
    state = state_path(cloud, config)
    if action == "apagar" and (not state.exists() or not json.loads(state.read_text()).get("resources")):
        print(f"{cloud}: sin estado administrado; no hay nada que apagar.", flush=True)
        return None
    variables["encendido"] = action == "encender"
    if cloud == "aws":
        variables["bucket_generation"] = bucket_generation(config, env, state, action)
    prefix, env, state = initialized(cloud, config, env)
    tfvars = transaction / (cloud + ".tfvars.json")
    save_json(tfvars, variables)
    planfile = transaction / (cloud + ".tfplan")
    result = run(prefix + ["plan", "-input=false", "-no-color", "-lock-timeout=30s", "-detailed-exitcode",
                           "-var-file=" + str(tfvars), "-out=" + str(planfile)], env=env, allowed=(0, 2))
    planfile.chmod(0o600)
    plan = json.loads(run(prefix + ["show", "-json", planfile], env=env, capture=True).stdout)
    changes = guard_plan(plan, action)
    save_json(transaction / (cloud + "-resumen.json"), {"nube": cloud, "accion": action, "cambios": changes})
    print(f"{cloud}: plan comprobado, {len(changes)} recursos con cambios.", flush=True)
    return {"cloud": cloud, "config": config, "prefix": prefix, "env": env,
            "state": state, "planfile": planfile, "changes": result.returncode == 2}


def backup_states():
    state = PRIVATE / "estado"
    if not state.exists():
        print("Todavía no hay estados que respaldar.", flush=True)
        return
    dest = PRIVATE / "respaldos" / ("estados-" + stamp() + ".tar.gz")
    dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tarfile.open(dest, "w:gz") as archive:
        archive.add(state, arcname="estado")
        if CONFIG.exists():
            archive.add(CONFIG, arcname="config.json")
        continuity = ROOT / "integracion/privado"
        if continuity.exists():
            archive.add(continuity, arcname="continuidad-privado")
    dest.chmod(0o600)
    print("Respaldo local sensible:", dest, flush=True)


def selections(config, selected):
    selected_clouds = CLOUDS if selected == "todas" else (selected,)
    enabled = []
    for cloud in selected_clouds:
        if config[cloud].get("habilitada"):
            identity_key(cloud, config[cloud])
            enabled.append(cloud)
        else:
            print(f"{cloud}: no habilitada; acceso/configuración pendientes.", flush=True)
    if not enabled:
        raise ControlError("No hay nubes habilitadas para esta operación.")
    return enabled


def validate():
    binary = terraform_binary()
    for cloud in CLOUDS:
        env = os.environ.copy()
        env.update(CHECKPOINT_DISABLE="1", TF_DATA_DIR=str(PRIVATE / "validacion" / cloud))
        prefix = [binary, "-chdir=" + str(ROOT / cloud / "terraform")]
        run(prefix + ["fmt", "-check", "-recursive"])
        run(prefix + ["init", "-backend=false", "-input=false", "-no-color"], env=env)
        run(prefix + ["validate", "-no-color"], env=env)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Control Terraform de NexoAndes")
    parser.add_argument("comando", choices=["configurar", "comprobar", "validar", "plan", "encender", "apagar", "estado", "respaldar-estado", "panel"])
    parser.add_argument("accion", nargs="?", choices=["encender", "apagar"])
    parser.add_argument("--nube", choices=[*CLOUDS, "todas"], default="todas")
    args = parser.parse_args(argv)
    os.umask(0o077)
    config = configure()
    if args.comando == "panel":
        os.execv(sys.executable, [sys.executable, str(ROOT / "infraestructura/panel.py")])
    with (PRIVATE / "operacion.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ControlError("Ya hay una operación de NexoAndes en curso.")
        if args.comando == "configurar":
            print("Editar:", CONFIG)
            return
        if args.comando == "validar":
            validate()
            return
        if args.comando == "respaldar-estado":
            backup_states()
            return
        selected = selections(config, args.nube)
        if args.comando == "estado":
            for cloud in selected:
                path = state_path(cloud, config[cloud])
                if not path.exists():
                    print(f"{cloud}: todavía no desplegada con este estado Terraform.")
                    continue
                data = json.loads(path.read_text())
                value = data.get("outputs", {}).get("control", {}).get("value", {})
                print(cloud + " — último estado guardado (no es una prueba en vivo):")
                print(json.dumps(value, ensure_ascii=False, indent=2))
            return
        # Encender requiere todas las identidades. Apagar intenta las demás nubes
        # aunque una sesión haya caducado, para no dejar servicios cobrando.
        failures = {}
        for cloud in selected:
            try:
                env, _ = cloud_environment(cloud, config[cloud])
                check_identity(cloud, config[cloud], env)
            except (ControlError, OSError, KeyError, ValueError) as error:
                if args.comando != "apagar":
                    raise
                failures[cloud] = str(error)
                print(f"{cloud}: acceso fallido; se intentará apagar las otras nubes. {error}", flush=True)
        if args.comando == "comprobar":
            return
        action = args.accion if args.comando == "plan" else args.comando
        if action not in ("encender", "apagar"):
            raise ControlError("Uso: ./nexoandes plan encender|apagar")
        transaction = PRIVATE / "operaciones" / (stamp() + "-" + action)
        transaction.mkdir(parents=True, mode=0o700)
        status = {"accion": action, "fase": "planificando", "nubes": selected, "completadas": [], "errores": failures}
        save_json(transaction / "estado.json", status)
        try:
            plans = []
            for cloud in selected:
                if cloud in failures:
                    continue
                try:
                    plans.append(make_plan(cloud, config[cloud], action, transaction))
                except (ControlError, OSError, KeyError, ValueError) as error:
                    if args.comando != "apagar":
                        raise
                    failures[cloud] = str(error)
                    print(f"{cloud}: no se pudo preparar el apagado; se continúa con las otras nubes. {error}", flush=True)
            if args.comando == "plan":
                status["fase"] = "planes-preparados-sin-aplicar"
                print("Planes revisables guardados en:", transaction, flush=True)
                return
            backup_states()
            status["fase"] = "aplicando"
            save_json(transaction / "estado.json", status)
            # Apagar servicios remotos antes de retirar la red principal de AWS.
            ordered = plans if action == "encender" else list(reversed(plans))
            for plan in ordered:
                if plan is None:
                    continue
                cloud = plan["cloud"]
                try:
                    check_identity(cloud, plan["config"], plan["env"])
                    if plan["changes"]:
                        run(plan["prefix"] + ["apply", "-input=false", "-no-color", "-lock-timeout=30s", plan["planfile"]], env=plan["env"])
                    status["completadas"].append(cloud)
                    save_json(transaction / "estado.json", status)
                    backup_states()
                except (ControlError, OSError, KeyError, ValueError) as error:
                    if args.comando != "apagar":
                        raise
                    failures[cloud] = str(error)
                    backup_states()
                    print(f"{cloud}: apagado fallido; se continúa con las demás nubes. {error}", flush=True)
            if failures:
                status["fase"] = "apagado-parcial"
                raise ControlError("Apagado parcial; revisar las nubes con error: " + ", ".join(failures))
            status["fase"] = "completada"
            print(f"Operación {action} completada en las nubes habilitadas. Ejecuta ./nexoandes estado.", flush=True)
        except BaseException:
            if status["fase"] != "apagado-parcial":
                status["fase"] = "interrumpida-o-fallida"
            backup_states()
            raise
        finally:
            save_json(transaction / "estado.json", status)


if __name__ == "__main__":
    try:
        main()
    except (ControlError, OSError, KeyError, ValueError) as error:
        print("ERROR:", str(error), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Operación interrumpida. Conserva el estado y revisa el próximo plan.", file=sys.stderr)
        sys.exit(130)
