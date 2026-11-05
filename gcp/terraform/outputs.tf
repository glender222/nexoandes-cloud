output "control" {
  description = "Salida consumida por el controlador multicloud ./nexoandes"
  value = {
    proyecto  = var.project
    region    = var.region
    encendido = var.encendido
    vpc       = google_compute_network.vpc.id
    subnet    = google_compute_subnetwork.subnet.id
    bucket    = google_storage_bucket.backups.name
    vm_id     = google_compute_instance.vm[0].id
    data_disk = google_compute_disk.postgresql.id
    vm_ip     = try(google_compute_instance.vm[0].network_interface[0].access_config[0].nat_ip, null)
  }
}
