variable "tenancy_ocid" {
  type = string
}
variable "user_ocid" {
  type = string
}
variable "fingerprint" {
  type = string
}
variable "private_key_path" {
  type = string
}
variable "compartment_ocid" {
  type = string
}
variable "region" {
  type = string
}
variable "availability_domain" {
  type = string
}
variable "image_ocid" {
  type = string
}
variable "encendido" {
  type    = bool
  default = false
}
variable "shape" {
  type    = string
  default = "VM.Standard.A1.Flex"
  validation {
    condition     = var.shape == "VM.Standard.A1.Flex"
    error_message = "Este módulo está limitado a Ampere A1 Always Free. No cambia automáticamente a formas de pago."
  }
}
variable "aws_vpn_peer_ips" {
  type    = set(string)
  default = []
  validation {
    condition     = alltrue([for ip in var.aws_vpn_peer_ips : can(cidrnetmask("${ip}/32"))])
    error_message = "Los extremos VPN deben ser direcciones IPv4 individuales."
  }
}
variable "bastion_client_cidrs" {
  type    = list(string)
  default = []
  validation {
    condition     = alltrue([for cidr in var.bastion_client_cidrs : can(cidrnetmask(cidr)) && cidr != "0.0.0.0/0"])
    error_message = "Bastion requiere redes autorizadas, nunca acceso global."
  }
}
data "oci_identity_region_subscriptions" "main" {
  tenancy_id = var.tenancy_ocid
}
data "oci_objectstorage_namespace" "main" {
  compartment_id = var.tenancy_ocid
}
locals {
  home_region = one([for region in data.oci_identity_region_subscriptions.main.region_subscriptions : region.region_name if region.is_home_region])
  tags = {
    proyecto         = "nexoandes"
    nube             = "oci"
    administrado_por = "terraform"
  }
  ipsec_rules = { for rule in setproduct(var.aws_vpn_peer_ips, ["500", "4500"]) : "${rule[0]}-${rule[1]}" => { ip = rule[0], port = rule[1] } }
}
resource "oci_core_vcn" "main" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = ["10.30.0.0/16"]
  display_name   = "nexoandes-vcn"
  dns_label      = "nexoandes"
  freeform_tags  = local.tags
  lifecycle {
    precondition {
      condition     = var.region == local.home_region
      error_message = "Compute Always Free solo se permite en la región home de la tenancy."
    }
  }
}
resource "oci_core_internet_gateway" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  enabled        = true
  display_name   = "nexoandes-igw"
}
resource "oci_core_route_table" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.main.id
  }
}
resource "oci_core_security_list" "main" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "nexoandes-sin-ingreso-publico"
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
}
resource "oci_core_subnet" "main" {
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_vcn.main.id
  cidr_block                 = "10.30.1.0/24"
  display_name               = "nexoandes-replica"
  dns_label                  = "replica"
  route_table_id             = oci_core_route_table.main.id
  security_list_ids          = [oci_core_security_list.main.id]
  prohibit_public_ip_on_vnic = false
}
resource "oci_core_network_security_group" "replica" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.main.id
  display_name   = "nexoandes-replica"
}
resource "oci_core_network_security_group_security_rule" "ipsec" {
  for_each                  = local.ipsec_rules
  network_security_group_id = oci_core_network_security_group.replica.id
  direction                 = "INGRESS"
  protocol                  = "17"
  source                    = "${each.value.ip}/32"
  source_type               = "CIDR_BLOCK"
  udp_options {
    destination_port_range {
      min = tonumber(each.value.port)
      max = tonumber(each.value.port)
    }
  }
}
resource "oci_core_network_security_group_security_rule" "ssh_bastion" {
  count                     = length(var.bastion_client_cidrs) > 0 ? 1 : 0
  network_security_group_id = oci_core_network_security_group.replica.id
  direction                 = "INGRESS"
  protocol                  = "6"
  source                    = "10.30.1.0/24"
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
}
resource "oci_bastion_bastion" "main" {
  count                        = length(var.bastion_client_cidrs) > 0 ? 1 : 0
  bastion_type                 = "STANDARD"
  compartment_id               = var.compartment_ocid
  target_subnet_id             = oci_core_subnet.main.id
  client_cidr_block_allow_list = var.bastion_client_cidrs
  name                         = "nexoandes"
}
resource "oci_objectstorage_bucket" "backup" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.main.namespace
  name           = "nexoandes-postgresql"
  access_type    = "NoPublicAccess"
  storage_tier   = "Standard"
  versioning     = "Enabled"
  freeform_tags  = local.tags
  lifecycle {
    prevent_destroy = true
  }
}
resource "oci_objectstorage_object_lifecycle_policy" "backup" {
  namespace = data.oci_objectstorage_namespace.main.namespace
  bucket    = oci_objectstorage_bucket.backup.name
  rules {
    name        = "respaldos-7-dias"
    action      = "DELETE"
    is_enabled  = true
    target      = "objects"
    time_amount = 7
    time_unit   = "DAYS"
    object_name_filter {
      inclusion_prefixes = ["postgresql/"]
    }
  }
  rules {
    name        = "versiones-previas-7-dias"
    action      = "DELETE"
    is_enabled  = true
    target      = "previous-object-versions"
    time_amount = 7
    time_unit   = "DAYS"
    object_name_filter {
      inclusion_prefixes = ["postgresql/"]
    }
  }
}
resource "oci_core_instance" "replica" {
  compartment_id       = var.compartment_ocid
  availability_domain  = var.availability_domain
  display_name         = "nexoandes-postgresql-replica"
  shape                = var.shape
  state                = var.encendido ? "RUNNING" : "STOPPED"
  preserve_boot_volume = true
  shape_config {
    ocpus         = 2
    memory_in_gbs = 12
  }
  source_details {
    source_type             = "image"
    source_id               = var.image_ocid
    boot_volume_size_in_gbs = 50
  }
  create_vnic_details {
    subnet_id        = oci_core_subnet.main.id
    assign_public_ip = true
    nsg_ids          = [oci_core_network_security_group.replica.id]
  }
  metadata = {
    user_data = base64encode(file("${path.module}/templates/replica.yaml"))
  }
  freeform_tags = local.tags
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [source_details, metadata]
  }
}
output "control" {
  value = {
    tenancy                 = var.tenancy_ocid
    region                  = var.region
    compartment             = var.compartment_ocid
    encendido               = var.encendido
    instance                = oci_core_instance.replica.id
    replica_ip              = oci_core_instance.replica.private_ip
    ipsec_public_ip         = oci_core_instance.replica.public_ip
    bucket                  = oci_objectstorage_bucket.backup.name
    namespace               = data.oci_objectstorage_namespace.main.namespace
    bastion                 = try(oci_bastion_bastion.main[0].id, null)
    replicacion_configurada = false
  }
}
