resource "azurerm_user_assigned_identity" "container_app" {
  name                = "${var.project_name}-${var.environment}-identity"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    project     = var.project_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                            = azurerm_container_registry.main.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_user_assigned_identity.container_app.principal_id
  principal_type                   = "ServicePrincipal"
  skip_service_principal_aad_check = true
}
