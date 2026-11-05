variable "backup_operator_object_id" {
  description = "Object ID del usuario Entra autorizado para copiar respaldos; vacío deshabilita la asignación."
  type        = string
  default     = ""
  validation {
    condition     = var.backup_operator_object_id == "" || can(regex("^[0-9a-fA-F-]{36}$", var.backup_operator_object_id))
    error_message = "Indica un Object ID UUID de Entra o deja vacío."
  }
}

# No depende de encendido: el respaldo debe seguir accesible con el cómputo apagado.
resource "azurerm_role_assignment" "backup_operator" {
  count                = var.backup_operator_object_id != "" ? 1 : 0
  scope                = "${azurerm_storage_account.backup.id}/blobServices/default/containers/${azurerm_storage_container.backup.name}"
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.backup_operator_object_id
  principal_type       = "User"
}
