output "ecr_repository_url" {
  description = "ECR repository URL for the backend image."
  value       = aws_ecr_repository.backend.repository_url
}

output "lambda_function_name" {
  description = "Lambda function name."
  value       = aws_lambda_function.backend.function_name
}

output "function_url" {
  description = "Lambda Function URL for direct invocation."
  value       = aws_lambda_function_url.backend.function_url
}
