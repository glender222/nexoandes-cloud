variable "subscription_id" {
  type = string
}
variable "tenant_id" {
  type = string
}
variable "location" {
  type    = string
  default = "eastus"
}
variable "encendido" {
  type    = bool
  default = false
}
variable "enable_vpn_gateway" {
  type    = bool
  default = false
}
variable "aws_gateway_ip" {
  type    = string
  default = ""
}
variable "vpn_shared_key" {
  type      = string
  default   = null
  sensitive = true
}
variable "enable_monitoring" {
  type    = bool
  default = false
}
variable "storage_account_name" {
  type = string
  validation {
    condition     = can(regex("^[a-z0-9]{3,24}$", var.storage_account_name))
    error_message = "Configura un nombre global único de 3 a 24 letras minúsculas o dígitos."
  }
}
locals {
  tags = {
    proyecto         = "nexoandes"
    nube             = "azure"
    administrado_por = "terraform"
    entorno          = "laboratorio"
  }
}
resource "azurerm_resource_group" "main" {
  name     = "nexoandes-lab"
  location = var.location
  tags     = local.tags
  lifecycle {
    prevent_destroy = true
  }
}
resource "azurerm_virtual_network" "main" {
  name                = "nexoandes-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.20.0.0/16"]
  tags                = local.tags
}
resource "azurerm_subnet" "gateway" {
  name                 = "GatewaySubnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.20.255.0/27"]
}
resource "azurerm_storage_account" "backup" {
  name                            = var.storage_account_name
  resource_group_name             = azurerm_resource_group.main.name
  location                        = azurerm_resource_group.main.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  account_kind                    = "StorageV2"
  access_tier                     = "Hot"
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  tags                            = local.tags
  blob_properties {
    versioning_enabled = true
    delete_retention_policy {
      days = 7
    }
    container_delete_retention_policy {
      days = 7
    }
  }
  lifecycle {
    prevent_destroy = true
  }
}
resource "azurerm_storage_container" "backup" {
  name                  = "postgresql"
  storage_account_id    = azurerm_storage_account.backup.id
  container_access_type = "private"
  lifecycle {
    prevent_destroy = true
  }
}
resource "azurerm_storage_management_policy" "backup" {
  storage_account_id = azurerm_storage_account.backup.id
  rule {
    name    = "postgresql-14-dias"
    enabled = true
    filters {
      blob_types   = ["blockBlob"]
      prefix_match = ["postgresql/"]
    }
    actions {
      base_blob {
        delete_after_days_since_modification_greater_than = 14
      }
      snapshot {
        delete_after_days_since_creation_greater_than = 14
      }
      version {
        delete_after_days_since_creation = 14
      }
    }
  }
}
resource "azurerm_log_analytics_workspace" "main" {
  count               = var.enable_monitoring ? 1 : 0
  name                = "nexoandes-monitor"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  daily_quota_gb      = 0.1
  tags                = local.tags
  lifecycle {
    prevent_destroy = true
  }
}
resource "azurerm_public_ip" "vpn" {
  count               = var.encendido && var.enable_vpn_gateway ? 1 : 0
  name                = "nexoandes-vpn-ip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = local.tags
}
resource "azurerm_virtual_network_gateway" "main" {
  count               = var.encendido && var.enable_vpn_gateway ? 1 : 0
  name                = "nexoandes-vpn"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  type                = "Vpn"
  vpn_type            = "RouteBased"
  active_active       = false
  bgp_enabled         = false
  sku                 = "VpnGw1"
  generation          = "Generation1"
  ip_configuration {
    name                          = "gateway"
    public_ip_address_id          = azurerm_public_ip.vpn[0].id
    private_ip_address_allocation = "Dynamic"
    subnet_id                     = azurerm_subnet.gateway.id
  }
  tags = local.tags
}
resource "azurerm_local_network_gateway" "aws" {
  count               = var.encendido && var.enable_vpn_gateway ? 1 : 0
  name                = "nexoandes-lng-aws"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  gateway_address     = var.aws_gateway_ip
  address_space       = ["10.10.0.0/16"]
  tags                = local.tags
}
resource "azurerm_virtual_network_gateway_connection" "aws" {
  count                      = var.encendido && var.enable_vpn_gateway ? 1 : 0
  name                       = "nexoandes-vpn-connection-aws"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  type                       = "IPsec"
  virtual_network_gateway_id = azurerm_virtual_network_gateway.main[0].id
  local_network_gateway_id   = azurerm_local_network_gateway.aws[0].id
  shared_key                 = var.vpn_shared_key
  tags                       = local.tags
  lifecycle {
    precondition {
      condition     = var.vpn_shared_key != null && var.aws_gateway_ip != ""
      error_message = "La VPN opcional requiere IP vigente y PSK privada explicita; no hay valores incrustados."
    }
  }
}
output "control" {
  value = {
    suscripcion     = var.subscription_id
    tenant          = var.tenant_id
    encendido       = var.encendido
    resource_group  = azurerm_resource_group.main.name
    storage         = azurerm_storage_account.backup.name
    container       = azurerm_storage_container.backup.name
    vpn_ip          = try(azurerm_public_ip.vpn[0].ip_address, null)
    vpn_configurada = var.enable_vpn_gateway
    vpn_connection  = try(azurerm_virtual_network_gateway_connection.aws[0].id, null)
  }
}
