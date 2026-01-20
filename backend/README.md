# UPC Validator Backend

## Deployment

### Prerequisites

- Terraform >= 1.5
- AWS credentials with permissions for ECR, Lambda, IAM
- Docker

### Commands (logical deployment sequence)

```bash
# configure credentials
aws configure

# install deps (optional for local work)
cd /backend
pip install -r requirements.txt


# deploy with Terraform
cd backend/infra/terraform
terraform init
terraform apply

cd ..
cd ..

# build the image (Lambda runtime, ARM64)
docker build --platform linux/arm64 -t upc-backend .

# login to ECR (replace region/account)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin 539148045575.dkr.ecr.us-east-1.amazonaws.com

# create repo if needed, then tag + push
# aws ecr create-repository --repository-name upc-backend --region us-east-1
docker tag upc-backend:latest 539148045575.dkr.ecr.us-east-1.amazonaws.com/upc-backend:latest
docker push 539148045575.dkr.ecr.us-east-1.amazonaws.com/upc-backend:latest

cd /infra/terraform
terraform apply

```

### Optional: Run locally

```bash
docker run --rm --name upc-backend -p 9000:8080 upc-backend

curl -X POST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -H "Content-Type: application/json" \
  -d "$(cat <<'JSON'
{
  "files": [
    {
      "filename": "sample.pdf",
      "content_type": "application/pdf",
      "base64": "'"$(base64 -i sample.pdf | tr -d '\n')"'" 
    }
  ]
}
JSON
)"
```

Notes:
- Lambda is configured for ARM64, so use `--platform linux/arm64` when building.
- Terraform outputs include the ECR repo URL, Lambda name, and Function URL.
