mock_provider "azurerm" {
  mock_resource "azurerm_virtual_network_gateway" {
    defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/nexoandes-lab/providers/Microsoft.Network/virtualNetworkGateways/nexoandes-vpn" }
  }
  mock_resource "azurerm_local_network_gateway" {
    defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/nexoandes-lab/providers/Microsoft.Network/localNetworkGateways/nexoandes-lng-aws" }
  }
  mock_resource "azurerm_storage_account" {
    defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/nexoandes-lab/providers/Microsoft.Storage/storageAccounts/nexoandestest" }
  }
  mock_resource "azurerm_public_ip" {
    defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/nexoandes-lab/providers/Microsoft.Network/publicIPAddresses/nexoandes-vpn-ip" }
  }
  mock_resource "azurerm_subnet" {
    defaults = { id = "/subscriptions/00000000-0000-0000-0000-000000000001/resourceGroups/nexoandes-lab/providers/Microsoft.Network/virtualNetworks/nexoandes-vnet/subnets/GatewaySubnet" }
  }
}
variables {
  subscription_id      = "00000000-0000-0000-0000-000000000001"
  tenant_id            = "00000000-0000-0000-0000-000000000002"
  storage_account_name = "nexoandestest"
  enable_vpn_gateway   = true
  aws_gateway_ip       = "198.51.100.10"
  vpn_shared_key       = "solo-mock-sin-acceso-a-nubes-20261104"
  backup_operator_object_id = "00000000-0000-0000-0000-000000000003"
}
run "encender" {
  command = apply
  variables {
    encendido = true
  }
  assert {
    condition     = length(azurerm_virtual_network_gateway.main) == 1
    error_message = "El encendido debe crear el gateway cuando se habilita."
  }
}
run "apagar" {
  command = plan
  variables {
    encendido = false
  }
  assert {
    condition     = length(azurerm_virtual_network_gateway.main) == 0 && length(azurerm_public_ip.vpn) == 0
    error_message = "Apagar debe retirar el gateway y su IP facturable."
  }
  assert {
    condition     = azurerm_storage_account.backup.name == run.encender.control.storage
    error_message = "Apagar debe conservar los respaldos."
  }
  assert {
    condition = length(azurerm_role_assignment.backup_operator) == 1 && azurerm_role_assignment.backup_operator[0].scope == "${azurerm_storage_account.backup.id}/blobServices/default/containers/postgresql" && azurerm_role_assignment.backup_operator[0].role_definition_name == "Storage Blob Data Contributor"
    error_message = "Apagar conserva el permiso de datos, limitado al contenedor de respaldos."
  }
}
