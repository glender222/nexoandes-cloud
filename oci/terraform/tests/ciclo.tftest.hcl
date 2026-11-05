mock_provider "oci" {
  mock_data "oci_identity_region_subscriptions" {
    defaults = {
      region_subscriptions = [{ is_home_region = true, region_name = "us-ashburn-1" }]
    }
  }
  mock_data "oci_objectstorage_namespace" {
    defaults = { namespace = "nexoandestest" }
  }
}
variables {
  tenancy_ocid        = "ocid1.tenancy.oc1..example"
  user_ocid           = "ocid1.user.oc1..example"
  fingerprint         = "00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00"
  private_key_path    = "/tmp/clave-no-usada-en-mock.pem"
  compartment_ocid    = "ocid1.compartment.oc1..example"
  region              = "us-ashburn-1"
  availability_domain = "example:US-ASHBURN-AD-1"
  image_ocid          = "ocid1.image.oc1.iad.example"
}
run "encender" {
  command = apply
  variables {
    encendido = true
  }
  assert {
    condition     = oci_core_instance.replica.state == "RUNNING"
    error_message = "El encendido debe dejar la VM en RUNNING."
  }
}
run "apagar" {
  command = plan
  variables {
    encendido = false
  }
  assert {
    condition     = oci_core_instance.replica.state == "STOPPED" && oci_core_instance.replica.id == run.encender.control.instance
    error_message = "Apagar debe detener la misma VM sin eliminarla."
  }
  assert {
    condition     = oci_objectstorage_bucket.backup.name == run.encender.control.bucket
    error_message = "Los respaldos deben persistir."
  }
}
