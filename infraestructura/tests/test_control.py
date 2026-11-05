import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import tempfile

spec = importlib.util.spec_from_file_location("control", Path(__file__).parents[1] / "control.py")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def plan(kind, actions):
    return {"resource_changes": [{"mode": "managed", "type": kind, "address": kind + ".test",
                                   "change": {"actions": actions}}]}


class ProteccionDeDatos(unittest.TestCase):
    def test_no_elimina_datos_ni_credenciales(self):
        for kind in ["aws_ebs_volume", "aws_instance", "aws_s3_bucket", "azurerm_storage_account",
                     "azurerm_storage_container", "oci_core_instance", "oci_objectstorage_bucket",
                     "google_compute_instance", "google_compute_disk", "google_storage_bucket"]:
            for actions in [["delete"], ["delete", "create"], ["create", "delete"]]:
                with self.subTest(kind=kind, actions=actions), self.assertRaises(control.ControlError):
                    control.guard_plan(plan(kind, actions), "encender")

    def test_apagar_no_inicializa_una_cuenta_vacia(self):
        for kind in ["aws_s3_bucket", "aws_lb", "aws_nat_gateway", "oci_core_instance"]:
            with self.subTest(kind=kind), self.assertRaises(control.ControlError):
                control.guard_plan(plan(kind, ["create"]), "apagar")

    def test_apagar_admite_retirar_recursos_temporales(self):
        for kind in control.EPHEMERAL:
            with self.subTest(kind=kind):
                self.assertEqual(len(control.guard_plan(plan(kind, ["delete"]), "apagar")), 1)

    def test_apagar_admite_detener_la_misma_instancia(self):
        for kind in ["aws_ec2_instance_state", "oci_core_instance"]:
            self.assertEqual(len(control.guard_plan(plan(kind, ["update"]), "apagar")), 1)

    def test_solo_gateway_aws_es_descartable_no_la_base_de_datos(self):
        gateway = plan("aws_instance", ["delete"])
        gateway['resource_changes'][0]['address'] = 'aws_instance.vpn[0]'
        self.assertEqual(len(control.guard_plan(gateway, 'apagar')), 1)
        gateway['resource_changes'][0]['address'] = 'aws_instance.db'
        with self.assertRaises(control.ControlError):
            control.guard_plan(gateway, 'apagar')

    def test_marcador_s3_no_equivale_a_borrar_el_bucket(self):
        marker = plan("terraform_data", ["delete", "create"])
        marker["resource_changes"][0]["address"] = "terraform_data.backup"
        self.assertEqual(len(control.guard_plan(marker, "encender")), 1)
        with self.assertRaises(control.ControlError):
            control.guard_plan(marker, "apagar")

    def test_otros_marcadores_no_pueden_reemplazarse(self):
        with self.assertRaises(control.ControlError):
            control.guard_plan(plan("terraform_data", ["delete", "create"]), "encender")


class ReconstruccionS3(unittest.TestCase):
    def test_head_403_no_se_interpreta_como_bucket_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(control.subprocess, "run", return_value=SimpleNamespace(returncode=1, stderr="(403) Forbidden")):
                with self.assertRaises(control.ControlError):
                    control.bucket_generation({"cuenta": "849533029543", "region": "us-east-1"}, {}, Path(tmp)/"state", "encender")


class LecturaDeCredenciales(unittest.TestCase):
    def test_tres_formatos_compatibles(self):
        expected = {"AWS_ACCESS_KEY_ID": "ejemplo-id", "AWS_SECRET_ACCESS_KEY": "ejemplo-secreto", "AWS_SESSION_TOKEN": "ejemplo-token=="}
        variants = [
            '\n'.join(f'export {key}="{value}"' for key, value in expected.items()),
            '\n'.join(f'{key}={value}' for key, value in expected.items()),
            '[default]\n' + '\n'.join(f'{key.lower()} = {value}' for key, value in expected.items()),
        ]
        for value in variants:
            self.assertEqual(control.parse_aws_credentials(value), expected)

    def test_no_ejecuta_contenido_de_shell(self):
        text = 'export AWS_ACCESS_KEY_ID="$(touch /tmp/no-ejecutar)"\nAWS_SECRET_ACCESS_KEY=x\nAWS_SESSION_TOKEN=y'
        self.assertEqual(control.parse_aws_credentials(text)["AWS_ACCESS_KEY_ID"], "$(touch /tmp/no-ejecutar)")

    def test_no_mezcla_perfiles(self):
        with self.assertRaises(control.ControlError):
            control.parse_aws_credentials('[otro]\naws_access_key_id=x\naws_secret_access_key=y\naws_session_token=z')


class SesionesCaducadas(unittest.TestCase):
    def test_apagar_continua_con_azure_si_aws_ha_caducado(self):
        config = {
            "aws": {"habilitada": True, "cuenta": "849533029543", "region": "us-east-1"},
            "azure": {"habilitada": True, "suscripcion": "example", "variables": {"location": "northcentralus"}},
            "gcp": {"habilitada": False},
        }
        def identity(cloud, *_args):
            if cloud == "aws":
                raise control.ControlError("ExpiredToken")
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            azure = {"cloud": "azure", "config": config["azure"], "prefix": ["terraform", "-chdir=azure"],
                     "env": {}, "planfile": base/"azure.tfplan", "changes": True}
            with patch.object(control, "PRIVATE", base), patch.object(control, "configure", return_value=config), \
                 patch.object(control, "cloud_environment", return_value=({}, {})), \
                 patch.object(control, "check_identity", side_effect=identity), \
                 patch.object(control, "make_plan", return_value=azure) as make, \
                 patch.object(control, "backup_states"), patch.object(control, "run") as execute:
                with self.assertRaisesRegex(control.ControlError, "Apagado parcial"):
                    control.main(["apagar"])
                self.assertEqual(make.call_args.args[0], "azure")
                self.assertIn("apply", execute.call_args.args[0])
            import json
            status = json.loads(next((base/"operaciones").glob('*/estado.json')).read_text())
            self.assertEqual(status["fase"], "apagado-parcial")
            self.assertEqual(status["completadas"], ["azure"])
            self.assertIn("aws", status["errores"])


if __name__ == "__main__":
    unittest.main()
