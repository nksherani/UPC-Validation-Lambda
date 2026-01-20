output "lambda_function_name" {
  description = "Lambda function name."
  value       = aws_lambda_function.backend.function_name
}

output "function_url" {
  description = "Lambda Function URL for direct invocation."
  value       = aws_lambda_function_url.backend.function_url
}
