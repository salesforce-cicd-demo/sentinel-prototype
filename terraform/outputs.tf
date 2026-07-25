output "log_analytics_workspace_id" {
  description = "Workspace ID — needed to configure the native Sentinel connector (Option 1)"
  value       = azurerm_log_analytics_workspace.main.workspace_id
}

output "log_analytics_workspace_key" {
  description = "Primary shared key — used by the webhook function to authenticate to Log Analytics"
  value       = azurerm_log_analytics_workspace.main.primary_shared_key
  sensitive   = true
}

# output "function_app_name" {
#   description = "Function App name — used with 'func azure functionapp publish' to deploy the webhook receiver"
#   value       = azurerm_linux_function_app.webhook_receiver.name
# }

# output "function_app_hostname" {
#   description = "Function App hostname — used to construct the GitHub webhook URL"
#   value       = azurerm_linux_function_app.webhook_receiver.default_hostname
# }
