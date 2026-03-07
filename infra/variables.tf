variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix for resource names"
  type        = string
  default     = "ai-sahayak"
}

# URL your backend exposes for calendar alerts (Lambda will POST upcoming events here)
variable "backend_webhook_url" {
  description = "Backend URL to POST calendar alerts (e.g. https://your-api.com/v1/webhook/calendar)"
  type        = string
  default     = ""
}

variable "calendar_schedule_cron" {
  description = "Cron for daily calendar check (default 6 AM IST = 00:30 UTC)"
  type        = string
  default     = "cron(30 0 * * ? *)"
}
