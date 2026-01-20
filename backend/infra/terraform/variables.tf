variable "aws_region" {
  type        = string
  description = "AWS region to deploy into."
  default     = "us-east-1"
}

variable "lambda_name" {
  type        = string
  description = "Name of the Lambda function."
  default     = "upc-backend"
}

variable "image_uri" {
  type        = string
  description = "Full ECR image URI (including tag) for the Lambda image."
  default = "539148045575.dkr.ecr.us-east-1.amazonaws.com/upc-backend:latest"
}

variable "lambda_timeout" {
  type        = number
  description = "Lambda timeout in seconds."
  default     = 60
}

variable "lambda_memory" {
  type        = number
  description = "Lambda memory size in MB."
  default     = 1536
}
