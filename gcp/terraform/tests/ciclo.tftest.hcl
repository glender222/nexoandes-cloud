mock_provider "google" {}
variables {
  project        = "nexoandes-prueba-sin-nube"
  region         = "us-central1"
  admin_cidrs    = ["192.0.2.10/32"]
  ssh_public_key = "ssh-ed25519 AAAA-clave-publica-simulada"
}
run "encender" {
  command = apply
  variables { encendido = true }
  assert {
    condition     = google_compute_instance.vm[0].desired_status == "RUNNING" && google_compute_disk.postgresql.size == 20
    error_message = "Encender conserva disco independiente y arranca la misma VM."
  }
}
run "apagar" {
  command = plan
  variables { encendido = false }
  assert {
    condition     = length(google_compute_instance.vm) == 1 && google_compute_instance.vm[0].desired_status == "TERMINATED"
    error_message = "Apagar debe detener la VM, nunca borrarla."
  }
  assert {
    condition     = google_compute_disk.postgresql.id == run.encender.control.data_disk
    error_message = "La misma unidad de datos debe conservarse al apagar."
  }
}
