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

variable "ecr_repo_name" {
  type        = string
  description = "ECR repository name for the backend container."
  default     = "upc-backend"
}

variable "image_tag" {
  type        = string
  description = "Image tag to deploy from the ECR repository."
  default     = "latest"
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
