# AWS Deployment

CompeteIQ runs as a single ECS Fargate service fronted by an Application
Load Balancer.  Secrets are delivered from AWS Secrets Manager; container
images live in ECR; logs stream to CloudWatch Logs.

## Components

```
   Internet  ──▶  ALB (HTTPS)  ──▶  Target group :7860  ──▶  ECS service (Fargate)
                                                               │
                                                               ├─ Secrets Manager  (OpenAI, Langfuse)
                                                               ├─ CloudWatch Logs  (/ecs/competeiq)
                                                               └─ Optional: EFS for persistent .chroma
```

## Expected AWS resources

You must pre-create these (Terraform/CloudFormation left outside this repo):

- VPC with 2+ private subnets + NAT, 2+ public subnets with ALB
- Security groups: `sg-alb` (80/443 in), `sg-ecs` (7860 in only from `sg-alb`)
- ALB + HTTPS listener + ACM cert
- Target group on port 7860, health-check path `/`
- ECS cluster (Fargate)
- ECR repository `competeiq`
- Secrets Manager entries, e.g.:
  - `competeiq/openai-api-key`
  - `competeiq/langfuse-secret-key`
  - `competeiq/langfuse-public-key`
- Task execution role with `AmazonECSTaskExecutionRolePolicy` + permission
  to read the above secrets
- Task role (optional; permissions for tracing sidecars etc.)

## Repository assets

| Path | Purpose |
|---|---|
| `deploy/Dockerfile.ui` | Container image for the Gradio service |
| `deploy/aws/task-definition.json` | ECS task definition template |
| `deploy/aws/service.json` | ECS service configuration template |
| `deploy/aws/target-group.json` | ALB target group configuration template |
| `deploy/aws/deploy.ps1` | One-shot build + push + deploy helper script |
| `deploy/aws/README.md` | Step-by-step bootstrap + placeholder reference |
| `.gitlab-ci.yml` | `publish-ecr` + `deploy-staging` / `deploy-prod` jobs |

Before applying, substitute `<ACCOUNT_ID>`, `<REGION>`, subnet / SG IDs and
secret ARNs in the templates.

## First deploy (manual)

```bash
# 1. Build + push image
docker build -f deploy/Dockerfile.ui -t competeiq:local .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCT>.dkr.ecr.us-east-1.amazonaws.com
docker tag competeiq:local <ACCT>.dkr.ecr.us-east-1.amazonaws.com/competeiq:latest
docker push <ACCT>.dkr.ecr.us-east-1.amazonaws.com/competeiq:latest

# 2. Register task definition
aws ecs register-task-definition --cli-input-json file://deploy/aws/task-definition.json

# 3. Create service
aws ecs create-service --cli-input-json file://deploy/aws/service.json
```

## Subsequent deploys

GitLab CI's `deploy-staging` runs on every push to `main` and issues an
`aws ecs update-service --force-new-deployment`; `deploy-prod` is a manual
job that runs on tags.

## Rollback

```bash
aws ecs update-service --cluster competeiq-prod --service competeiq \
  --task-definition competeiq:<PREVIOUS_REVISION>
```

## Observability

- CloudWatch Logs group: `/ecs/competeiq`
- Langfuse traces: linked per-session via `COMPETEIQ_SESSION_PREFIX`
- ALB access logs: enable to an S3 bucket in production
