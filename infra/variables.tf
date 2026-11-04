variable "project_name" {
  description = "Name used to identify the project's Azure resources"
  type        = string
  default     = "task-management-api"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "location" {
  description = "Azure region where resources will be deployed"
  type        = string
  default     = "Central India"
}

variable "image_tag" {
  description = "Docker image tag deployed to Azure Container Apps"
  type        = string
  default     = "latest"
}