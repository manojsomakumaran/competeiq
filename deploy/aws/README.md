# AWS ECS Fargate deployment assets

These templates deploy the CompeteIQ Gradio UI to AWS ECS Fargate behind
an Application Load Balancer.

## Files

| File | Purpose |
|---|---|
| [`task-definition.json`](task-definition.json) | ECS task definition (1 vCPU / 2 GB, EFS volume, Secrets Manager refs, CloudWatch Logs) |
| [`service.json`](service.json) | ECS service (1 replica, ALB target group, circuit-breaker rollback, sticky sessions) |
| [`target-group.json`](target-group.json) | ALB target group on `:7860`, HTTP healthcheck against `/` |
| [`deploy.ps1`](deploy.ps1) | One-shot script: build, push to ECR, register task def, update service |

## Placeholders

Replace these tokens **everywhere** before applying:

| Token | Example |
|---|---|
| `<ACCOUNT_ID>` | `123456789012` |
| `<REGION>` | `us-east-1` |
| `<VPC_ID>` | `vpc-0abc…` |
| `<PRIVATE_SUBNET_1>`, `<PRIVATE_SUBNET_2>` | `subnet-0abc…` (>=2 AZs) |
| `<SG_ECS_TASK>` | SG that allows :7860 from the ALB SG |
| `<TG_ID>` | suffix returned when you create the target group |
| `<EFS_FILESYSTEM_ID>` | `fs-0abc…` (mount target in each task subnet) |

## One-time bootstrap (per AWS account)

```powershell
# 1. ECR repos
aws ecr create-repository --repository-name competeiq-ui  --region <REGION>
aws ecr create-repository --repository-name competeiq     --region <REGION>

# 2. Secrets Manager
aws secretsmanager create-secret --name competeiq/openai_api_key      --secret-string "$env:OPENAI_API_KEY"      --region <REGION>
aws secretsmanager create-secret --name competeiq/langfuse_secret_key --secret-string "$env:LANGFUSE_SECRET_KEY" --region <REGION>
aws secretsmanager create-secret --name competeiq/langfuse_public_key --secret-string "$env:LANGFUSE_PUBLIC_KEY" --region <REGION>

# 3. IAM roles (create these manually or via Terraform/CloudFormation):
#    - competeiq-ecs-task-execution: AmazonECSTaskExecutionRolePolicy + secretsmanager:GetSecretValue on the 3 secrets
#    - competeiq-ecs-task:           elasticfilesystem:ClientMount/Write on the EFS, logs:* on /ecs/competeiq-ui

# 4. ECS cluster
aws ecs create-cluster --cluster-name competeiq --region <REGION>

# 5. ALB + target group + listener
aws elbv2 create-target-group --cli-input-json file://target-group.json --region <REGION>
# ... then create ALB and HTTPS listener forwarding to that target group

# 6. EFS file system + mount targets in each private subnet (one-time)
```

## Deploy a new image

```powershell
.\deploy.ps1 -Region us-east-1 -AccountId 123456789012
```

The script:
1. `docker build -f deploy/Dockerfile.ui -t competeiq-ui:latest .`
2. tags + pushes to `<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/competeiq-ui:latest`
3. `aws ecs register-task-definition --cli-input-json file://task-definition.json`
4. `aws ecs update-service --cluster competeiq --service competeiq-ui --task-definition competeiq-ui --force-new-deployment`

The ECS deployment circuit breaker auto-rolls-back if the new task fails
its healthcheck, so a bad image cannot take the service down.

## Observability

- **Logs**: CloudWatch group `/ecs/competeiq-ui`, stream prefix `ui/<task-id>`.
- **Traces**: every agent span ships to Langfuse (`LANGFUSE_HOST`).
- **Metrics**: ECS service publishes CPU/Memory/RunningCount to CloudWatch by default.

## Persistent state

ChromaDB lives on EFS at `/competeiq` so the embedding index survives
task replacements and rolling deploys.

## Cost (rough order of magnitude)

- 1 task × 1 vCPU × 2 GB Fargate ≈ $30/month (us-east-1, on-demand).
- ALB ≈ $20/month + LCU.
- EFS: $0.30 / GB-month (CompeteIQ's index is sub-100 MB).
- Secrets Manager: $0.40/secret/month × 3.

Total baseline: **~$60–70/month** plus OpenAI/Langfuse usage.

See [../../docs/deployment-aws.md](../../docs/deployment-aws.md) for the
narrative version of this doc.
