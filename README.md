# AWS Resource Approval Workflow

A serverless approval workflow for AWS resource provisioning using AWS Step Functions, Lambda, and API Gateway.

> **Note**: This is a completed proof-of-concept project and is no longer actively maintained. Feel free to fork and adapt for your own use.

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

### Currently Implemented (MVP)
- **EC2 Instances**: Full support with optional EBS and network configuration
  - Instance type: t3.micro
  - OS: Amazon Linux 2023 (via Golden AMI)
  - Optional: Custom EBS volume size/type
  - Optional: Private IP address assignment

### Extensible For (See [CUSTOMIZATION.md](docs/CUSTOMIZATION.md))
- **Multiple Instance Types**: t3.small, t3.medium, etc.
- **Windows OS**: Windows Server support
- **RDS Databases**: MySQL, PostgreSQL provisioning
- **S3 Buckets**: Bucket creation with policies
- **Cognito Auth**: User authentication
- **Cost Estimation**: Pre-approval cost calculation
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
   cd aws-resource-approval-workflow
   cp infrastructure/config.template.json config.json
   # Edit config.json with your values
   ```

2. **Deploy**
   Follow the step-by-step guide in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

3. **Test**
   - Open the S3-hosted website
   - Submit a test EC2 request
   - Check email for approval link
   - Verify resource launches

## Configuration

See [docs/SETUP.md](docs/SETUP.md) for detailed configuration instructions.

Key configuration items:
- AWS region and account
- Resource naming prefix
- API Gateway endpoints
- Golden AMI ID
- SES email addresses

## Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Complete deployment guide |
| [SETUP.md](docs/SETUP.md) | Initial configuration |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture overview |
| [TESTING.md](docs/TESTING.md) | Testing procedures |
| [CUSTOMIZATION.md](docs/CUSTOMIZATION.md) | Extension and customization guide |
| [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | Quick command reference |

## Project Structure

```
aws-resource-approval-workflow/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── CONTRIBUTING.md              # Contribution guidelines
├── requirements.txt             # Python dependencies
│
├── docs/                        # Documentation
│   ├── DEPLOYMENT.md           # Deployment guide
│   ├── ARCHITECTURE.md         # Architecture overview
│   ├── SETUP.md                # Initial setup
│   ├── TESTING.md              # Testing guide
│   ├── CUSTOMIZATION.md        # Extension guide
│   └── QUICK_REFERENCE.md      # Quick reference
│
├── src/                         # Source code
│   ├── lambda/                 # Lambda functions
│   │   ├── RequestStarter.py
│   │   ├── SendApprovalEmail.py
│   │   ├── ApprovalHandler.py
│   │   ├── LaunchEC2.py
│   │   ├── SendRequesterNotification.py
│   │   └── UpdateRequestStatus.py
│   ├── frontend/               # Web UI
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   └── stepfunctions/          # Step Functions definitions
│       └── EC2ApprovalDemo-SIMPLE.json
│
├── infrastructure/              # Infrastructure definitions
│   ├── dynamodb/               # DynamoDB table definition
│   └── config.template.json    # Configuration template
│
└── scripts/                     # Utility scripts
    ├── export_to_csv.py        # Export logs to CSV
    └── view_dynamodb_logs.py   # View logs in terminal
```

## Security Best Practices

- ✅ Separate IAM roles per Lambda function
- ✅ Least privilege permissions
- ✅ No hardcoded credentials
- ✅ CORS properly configured
- ✅ Public S3 bucket only for static assets
- ✅ API Gateway with proper error handling

## Viewing Logs

### Install Dependencies
```bash
pip install -r requirements.txt
```

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

See [docs/CUSTOMIZATION.md](docs/CUSTOMIZATION.md) for detailed extension guides:

- [ ] Cognito authentication
- [ ] Multiple instance types (t3.small, t3.medium, etc.)
- [ ] Windows OS support
- [ ] RDS database provisioning
- [ ] S3 bucket provisioning
- [ ] Cost estimation before approval
- [ ] Slack/Teams notifications
- [ ] Admin dashboard
- [ ] Request history view
- [ ] Multi-region support

## License

MIT License - See [LICENSE](LICENSE) file for details. Feel free to use and modify for your own projects.

## Project Status

⚠️ **This project is archived and not actively maintained.**

This was developed as a proof-of-concept for AWS resource approval workflows. The code is provided as-is for educational and reference purposes. You're welcome to:
- Fork and adapt for your own use
- Learn from the implementation
- Use as a starting point for your own projects

## Support

- 📖 [Documentation](docs/DEPLOYMENT.md)
- 💡 For questions, feel free to open an issue (responses may be delayed)

## Acknowledgments

Built with AWS serverless technologies:
- AWS Lambda
- AWS Step Functions
- Amazon API Gateway
- Amazon DynamoDB
- Amazon SES
- Amazon S3
