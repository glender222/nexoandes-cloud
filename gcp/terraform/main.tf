provider "google" {
  project = var.project
  region  = var.region
}

# Red VPC dedicada para NexoAndes en Google Cloud
resource "google_compute_network" "vpc" {
  name                    = "nexoandes-gcp-vpc"
  auto_create_subnetworks = false
  description             = "VPC de NexoAndes en GCP (red 10.30.0.0/16)"
}

resource "google_compute_subnetwork" "subnet" {
  name          = "nexoandes-gcp-subnet"
  ip_cidr_range = "10.30.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Regla de firewall para administración remota
resource "google_compute_firewall" "allow_ssh" {
  name    = "nexoandes-gcp-allow-ssh"
  network = google_compute_network.vpc.id

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = var.admin_cidrs
  target_tags   = ["nexoandes"]
}

# Bucket de Cloud Storage para respaldos cruzados
resource "google_storage_bucket" "backups" {
  name                        = "nexoandes-backup-${var.project}"
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 14 }
  }
  lifecycle { prevent_destroy = true }
}

# Máquina virtual en contingencia (Free Tier e2-micro con disco de 10GB)
resource "google_compute_instance" "vm" {
  count          = 1
  name           = "nexoandes-gcp-standby"
  machine_type   = "e2-micro"
  zone           = "${var.region}-a"
  desired_status = var.encendido ? "RUNNING" : "TERMINATED"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 10
      type  = "pd-standard"
    }
  }

  network_interface {
    subnetwork = google_compute_subnetwork.subnet.id
    network_ip = "10.30.1.10"
    access_config {
      // IP pública efímera
    }
  }

  tags = ["nexoandes", "standby"]
  metadata = {
    ssh-keys               = join("\n", compact(["nexoandes:${var.ssh_public_key}", var.ssh_gateway_public_key != "" ? "nexoandes:${var.ssh_gateway_public_key}" : ""]))
    block-project-ssh-keys = "true"
    serial-port-enable     = "false"
    startup-script = templatefile("${path.module}/templates/standby.sh.tftpl", {
      app_code = file("${path.module}/../../integracion/health_app.py")
    })
  }
  attached_disk {
    source      = google_compute_disk.postgresql.id
    device_name = "nexoandes-data"
  }
  lifecycle { prevent_destroy = true }
}

resource "google_compute_disk" "postgresql" {
  name = "nexoandes-gcp-postgresql"
  type = "pd-standard"
  zone = "${var.region}-a"
  size = 20
  lifecycle { prevent_destroy = true }
}
resource "google_compute_firewall" "ipsec" {
  count   = var.aws_peer_ip != "" ? 1 : 0
  name    = "nexoandes-gcp-ipsec"
  network = google_compute_network.vpc.id
  allow {
    protocol = "udp"
    ports    = ["500", "4500"]
  }
  source_ranges = ["${var.aws_peer_ip}/32"]
  target_tags   = ["standby"]
}
resource "google_compute_firewall" "web" {
  name    = "nexoandes-gcp-web"
  network = google_compute_network.vpc.id
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["standby"]
}
