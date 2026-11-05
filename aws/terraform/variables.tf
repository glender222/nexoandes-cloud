variable "expected_account_id" {
  type = string
  validation {
    condition     = can(regex("^[0-9]{12}$", var.expected_account_id))
    error_message = "Configura la cuenta AWS explícitamente."
  }
}
variable "region" {
  type    = string
  default = "us-east-1"
  validation {
    condition     = contains(["us-east-1", "us-west-2"], var.region)
    error_message = "El Learner Lab limita el acceso a us-east-1 y us-west-2."
  }
}
variable "encendido" {
  type    = bool
  default = false
}
variable "team_number" {
  type    = string
  default = "XX"
  validation {
    condition     = can(regex("^[A-Za-z0-9-]+$", var.team_number))
    error_message = "Usa un número o identificador de equipo sin espacios."
  }
}
variable "certificate_arn" {
  type    = string
  default = ""
}
variable "ami_id" {
  type    = string
  default = ""
}
variable "bucket_generation" {
  type    = string
  default = "initial"
}

locals {
  prefix = "nexoandes"
  subnets = {
    public_a = { cidr = "10.10.1.0/24", az = 0, public = true }
    public_b = { cidr = "10.10.2.0/24", az = 1, public = true }
    app_a    = { cidr = "10.10.11.0/24", az = 0, public = false }
    app_b    = { cidr = "10.10.12.0/24", az = 1, public = false }
    db       = { cidr = "10.10.20.0/24", az = 0, public = false }
  }
  selected_ami = var.ami_id != "" ? var.ami_id : data.aws_ami.al2023.id
}

data "aws_availability_zones" "available" {
  state = "available"
}
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
data "aws_iam_instance_profile" "lab" {
  name = "LabInstanceProfile"
}
