# Log Analytics workspace — the backing store for Sentinel
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.prefix}-sentinel-law"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# Enable Microsoft Sentinel on the workspace
resource "azurerm_sentinel_log_analytics_workspace_onboarding" "main" {
  workspace_id = azurerm_log_analytics_workspace.main.id
}
