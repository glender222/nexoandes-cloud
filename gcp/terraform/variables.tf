variable "project" {
  type        = string
  description = "ID del proyecto de Google Cloud"
}

variable "region" {
  type        = string
  description = "Región de Google Cloud"
  default     = "us-central1"
}

variable "encendido" {
  type        = bool
  description = "Estado de despliegue de recursos de cómputo en GCP"
  default     = false
}
variable "admin_cidrs" {
  type        = list(string)
  description = "IP de administracion autorizada; nunca abrir SSH a Internet"
  validation {
    condition     = length(var.admin_cidrs) > 0 && alltrue([for cidr in var.admin_cidrs : can(cidrhost(cidr, 0)) && cidr != "0.0.0.0/0"])
    error_message = "Configura CIDR administrativos explicitos y restringidos."
  }
}
variable "ssh_public_key" {
  type        = string
  description = "Clave publica; la privada permanece en integracion/privado"
}
variable "aws_peer_ip" {
  type    = string
  default = ""
}
variable "ssh_gateway_public_key" {
  type    = string
  default = ""
}
