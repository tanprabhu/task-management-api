output "resource_group_name" {
  description = "Azure resource group containing the project"
  value       = azurerm_resource_group.main.name
}

output "container_registry_login_server" {
  description = "Address used to push and pull Docker images"
  value       = azurerm_container_registry.main.login_server
}

output "postgresql_host" {
  description = "PostgreSQL server hostname"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "api_url" {
  description = "Public HTTPS URL of the deployed API"
  value       = "https://${azurerm_container_app.api.latest_revision_fqdn}"
}