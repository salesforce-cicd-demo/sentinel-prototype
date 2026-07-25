resource "azurerm_resource_group" "main" {
  name     = "${var.prefix}-sentinel-rg"
  location = var.location
}
