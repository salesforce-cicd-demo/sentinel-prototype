variable "azure_subscription_id" {
  description = "Azure subscription ID"
}

variable "location" {
  description = "Azure region for all resources"
  default     = "eastus"
}

variable "prefix" {
  description = "Short prefix for resource names (3-8 chars)"
  default     = "sfcicd"
}
