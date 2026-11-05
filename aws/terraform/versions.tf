terraform {
  required_version = "~> 1.17.0"
  backend "local" {}
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 6.70.0"
    }
  }
}

provider "aws" {
  region              = var.region
  allowed_account_ids = [var.expected_account_id]
  default_tags {
    tags = {
      proyecto         = "nexoandes"
      nube             = "aws"
      administrado_por = "terraform"
      entorno          = "laboratorio"
    }
  }
}
