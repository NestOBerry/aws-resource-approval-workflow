# Setup Guide

## Initial Setup

### 1. Create Your Configuration File

Copy the template and customize it:

```bash
cp infrastructure/config.template.json config.json
```

Then edit `config.json` with your values:
- `naming.prefix`: Your environment prefix (e.g., "dev-", "prod-", "yourname-")
- `aws.accountId`: Your AWS account ID
- `api.endpoint`: Your API Gateway endpoint
- `email.fromEmail`: Your verified SES email

**Important:** `config.json` is in `.gitignore` and will NOT be committed to Git.

### 2. Deploy Resources

Follow the deployment guides:
- `DEPLOYMENT.md` - Complete deployment steps
- `QUICK_REFERENCE.md` - Quick reference

### 3. Update Resource Names

When creating AWS resources, use the prefix from your `config.json`:
- DynamoDB: `${prefix}EC2ApprovalRequests`
- S3 Bucket: `${prefix}ec2-approval-portal`
- Lambda Roles: `${prefix}LambdaRole-*`
- Step Functions: `${prefix}EC2ApprovalDemo`

## For Team Members

Each team member should:
1. Clone the repository
2. Copy `infrastructure/config.template.json` to `config.json`
3. Fill in their own values
4. Never commit `config.json` to Git

## Environment-Specific Deployments

### Development
```json
{
  "naming": { "prefix": "dev-" }
}
```

### Production
```json
{
  "naming": { "prefix": "prod-" }
}
```

### Personal R&D
```json
{
  "naming": { "prefix": "yourname-" }
}
```

## Security Notes

- Never commit `config.json` (contains personal info)
- Never commit AWS credentials
- Never commit API keys or secrets
- Use AWS Secrets Manager for production secrets
