# # Storage account required by Azure Functions runtime
# resource "azurerm_storage_account" "functions" {
#   name                     = "${replace(var.prefix, "-", "")}fnstore"
#   resource_group_name      = azurerm_resource_group.main.name
#   location                 = azurerm_resource_group.main.location
#   account_tier             = "Standard"
#   account_replication_type = "LRS"
# }

# # Consumption plan (pay-per-execution, effectively free at prototype scale)
# resource "azurerm_service_plan" "functions" {
#   name                = "${var.prefix}-fn-plan"
#   resource_group_name = azurerm_resource_group.main.name
#   location            = azurerm_resource_group.main.location
#   os_type             = "Linux"
#   sku_name            = "Y1"
# }

# # Function App — receives GitHub webhooks and forwards to Log Analytics
# resource "azurerm_linux_function_app" "webhook_receiver" {
#   name                       = "${var.prefix}-gh-webhook"
#   resource_group_name        = azurerm_resource_group.main.name
#   location                   = azurerm_resource_group.main.location
#   storage_account_name       = azurerm_storage_account.functions.name
#   storage_account_access_key = azurerm_storage_account.functions.primary_access_key
#   service_plan_id            = azurerm_service_plan.functions.id

#   site_config {
#     application_stack {
#       python_version = "3.12"
#     }
#   }

#   app_settings = {
#     # Log Analytics connection — the function uses these to POST events
#     LOG_ANALYTICS_WORKSPACE_ID  = azurerm_log_analytics_workspace.main.workspace_id
#     LOG_ANALYTICS_WORKSPACE_KEY = azurerm_log_analytics_workspace.main.primary_shared_key

#     # Set this after generating the webhook secret in GitHub
#     # GITHUB_WEBHOOK_SECRET = "your-secret-here"

#     FUNCTIONS_WORKER_RUNTIME = "python"
#     AzureWebJobsFeatureFlags = "EnableWorkerIndexing"
#   }
# }
