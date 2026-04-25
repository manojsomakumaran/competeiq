#requires -Version 7
<#
.SYNOPSIS
    Build, push, and deploy the CompeteIQ UI image to AWS ECS Fargate.

.PARAMETER Region
    AWS region (e.g. us-east-1).

.PARAMETER AccountId
    12-digit AWS account ID.

.PARAMETER ImageTag
    Optional tag for the image. Defaults to the short git SHA.

.PARAMETER Cluster
    ECS cluster name. Defaults to "competeiq".

.PARAMETER Service
    ECS service name. Defaults to "competeiq-ui".

.PARAMETER TaskDefinitionFile
    Path to the task definition JSON. Defaults to deploy/aws/task-definition.json.

.EXAMPLE
    ./deploy/aws/deploy.ps1 -Region us-east-1 -AccountId 123456789012
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $Region,
    [Parameter(Mandatory)] [string] $AccountId,
    [string] $ImageTag           = (git rev-parse --short HEAD),
    [string] $Cluster            = 'competeiq',
    [string] $Service            = 'competeiq-ui',
    [string] $Repository         = 'competeiq-ui',
    [string] $TaskDefinitionFile = 'deploy/aws/task-definition.json',
    [string] $DockerfilePath     = 'deploy/Dockerfile.ui'
)

$ErrorActionPreference = 'Stop'

$registry  = "$AccountId.dkr.ecr.$Region.amazonaws.com"
$imageUri  = "${registry}/${Repository}:${ImageTag}"
$latestUri = "${registry}/${Repository}:latest"

Write-Host "==> Logging in to ECR $registry" -ForegroundColor Cyan
aws ecr get-login-password --region $Region |
    docker login --username AWS --password-stdin $registry

Write-Host "==> Building $imageUri" -ForegroundColor Cyan
docker build -f $DockerfilePath -t $imageUri -t $latestUri .

Write-Host "==> Pushing $imageUri" -ForegroundColor Cyan
docker push $imageUri
docker push $latestUri

Write-Host "==> Rendering task definition" -ForegroundColor Cyan
$rendered = (Get-Content $TaskDefinitionFile -Raw) `
    -replace '<ACCOUNT_ID>', $AccountId `
    -replace '<REGION>',     $Region

$tmp = [System.IO.Path]::GetTempFileName() + '.json'
Set-Content -Path $tmp -Value $rendered -Encoding UTF8

Write-Host "==> Registering new task definition revision" -ForegroundColor Cyan
$registered = aws ecs register-task-definition `
    --cli-input-json file://$tmp `
    --region $Region |
    ConvertFrom-Json

$taskDefArn = $registered.taskDefinition.taskDefinitionArn
Write-Host "    -> $taskDefArn"

Write-Host "==> Updating ECS service $Service" -ForegroundColor Cyan
aws ecs update-service `
    --cluster $Cluster `
    --service $Service `
    --task-definition $taskDefArn `
    --force-new-deployment `
    --region $Region | Out-Null

Write-Host "==> Waiting for service to stabilise" -ForegroundColor Cyan
aws ecs wait services-stable `
    --cluster $Cluster `
    --services $Service `
    --region $Region

Write-Host "==> Deployment complete: $imageUri" -ForegroundColor Green
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
