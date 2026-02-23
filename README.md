# AWS Resource Approval Workflow

A serverless approval workflow for AWS resource provisioning using AWS Step Functions, Lambda, and API Gateway.

## Overview

This solution provides an email-based approval workflow for provisioning AWS resources. Currently supports EC2 instances, with extensibility for RDS databases and S3 buckets.

## Features

- ✅ Email-based approval workflow
- ✅ Step Functions orchestration
- ✅ DynamoDB request logging with audit trail
- ✅ Web-based request portal
- ✅ Support for optional resource configuration
- ✅ Human-readable timestamps
- ✅ Separate IAM roles following least privilege principle
- ✅ Extensible architecture for multiple resource types

## Supported Resources

### Currently Implemented
- **EC2 Instances**: Full support with optional EBS and network configuration

### Planned
- **RDS Databases**: MySQL, PostgreSQL provisioning
- **S3 Buckets**: Bucket creation with policies
- **Other AWS Resources**: Extensible framework

## Architecture

```
User → Web Portal → API Gateway → Lambda (RequestStarter)
                                      ↓
                                  Step Functions
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
            SendApprovalEmail   LaunchEC2    SendNotification
                    ↓                 ↓                 ↓
                Approver          EC2 Instance      Requester
```

## Components

### Lambda Functions
- `RequestStarter` - Receives requests and starts workflow
- `SendApprovalEmail` - Sends approval email with links
- `ApprovalHandler` - Handles approve/reject clicks
- `LaunchEC2` - Launches EC2 instance
- `SendRequesterNotification` - Notifies requester of decision
- `UpdateRequestStatus` - Updates DynamoDB status

### Infrastructure
- **API Gateway**: HTTP API with CORS
- **Step Functions**: Orchestrates the approval workflow
- **DynamoDB**: Logs all requests and decisions
- **S3**: Hosts the web portal
- **SES**: Sends email notifications

## Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.12+
- Verified SES email addresses
- VPC with subnets and security groups

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd aws-ec2-approval-workflow
   cp config.template.json config.json
   # Edit config.json with your values
   ```

2. **Deploy**
   Follow the step-by-step guide in `FINAL_DEPLOYMENT_GUIDE.md`

3. **Test**
   - Open the S3-hosted website
   - Submit a test request
   - Check email for approval link
   - Verify EC2 instance launches

## Configuration

See `SETUP.md` for detailed configuration instructions.

Key configuration items:
- AWS region and account
- Resource naming prefix
- API Gateway endpoints
- Golden AMI ID
- SES email addresses

## Documentation

- `FINAL_DEPLOYMENT_GUIDE.md` - Complete deployment steps
- `SETUP.md` - Initial setup and configuration
- `QUICK_REFERENCE.md` - Quick reference guide
- `TESTING.md` - Testing procedures
- `DYNAMODB_SETUP.md` - DynamoDB logging setup

## Security Best Practices

- ✅ Separate IAM roles per Lambda function
- ✅ Least privilege permissions
- ✅ No hardcoded credentials
- ✅ CORS properly configured
- ✅ Public S3 bucket only for static assets
- ✅ API Gateway with proper error handling

## Viewing Logs

### Python Script
```bash
python3 scripts/view_dynamodb_logs.py
python3 scripts/view_dynamodb_logs.py --user user@example.com
python3 scripts/view_dynamodb_logs.py --status PENDING
```

### Export to CSV
```bash
python3 scripts/export_to_csv.py output.csv
```

### AWS Console
Navigate to DynamoDB → Tables → EC2ApprovalRequests → Explore items

## Future Enhancements

- [ ] Cognito authentication
- [ ] Multiple instance types
- [ ] RDS and S3 provisioning
- [ ] Cost estimation
- [ ] Slack/Teams integration
- [ ] Admin dashboard

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.
