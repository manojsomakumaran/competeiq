# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a vulnerability

Please report vulnerabilities privately via GitHub's "Report a vulnerability"
feature or email the maintainer directly. Do **not** open a public issue for
security concerns.

## Secrets handling

- API keys live in `.env` and are never committed.
- In production (AWS ECS), keys are sourced from AWS Secrets Manager.
- In CI, keys are injected via masked/protected variables.
