# AWS EC2 Approval Workflow - Project Structure

```
aws-ec2-approval-workflow/
├── README.md                           # Main project documentation
├── DEPLOYMENT.md                       # Deployment guide
├── .gitignore                          # Git ignore rules
├── PROJECT_STRUCTURE.md                # This file
│
├── lambda/                             # Lambda function code
│   ├── RequestStarter.py           # Initiates Step Functions workflow
│   ├── ResolveAMI.py               # Resolves latest AL2023 AMI
│   ├── SendApprovalEmail.py        # Sends approval email
│   ├── LaunchEC2.py                # Launches EC2 instance
│   ├── SendRequesterNotification.py # Notifies requester
│   └── ApprovalHandler.py          # Handles approve/reject actions
│
├── stepfunctions/                      # Step Functions definitions
│   ├── EC2ApprovalDemo-UPDATED.json # State machine definition
│   └── README.md                       # Step Functions documentation
│
└── frontend/                           # Web frontend
    ├── index.html                      # Main HTML page
    ├── app.js                          # JavaScript logic
    ├── styles.css                      # Styling
    └── README.md                       # Frontend documentation

## Component Overview

### Lambda Functions (6 total)
- **RequestStarter**: Entry point from API Gateway
- **ResolveAMI**: Fetches latest AMI or uses provided one
- **SendApprovalEmail**: Sends email with approve/reject links
- **LaunchEC2**: Provisions EC2 with optional parameters
- **SendRequesterNotification**: Sends outcome notification
- **ApprovalHandler**: Processes email link clicks

### Step Functions (1 state machine)
- **EC2ApprovalDemo**: Orchestrates the entire workflow

### Frontend (3 files)
- Simple HTML/CSS/JS portal for request submission
- Ready for S3 + CloudFront deployment
- Cognito-ready for future authentication

## Quick Start

1. Review `README.md` for architecture overview
2. Follow `DEPLOYMENT.md` for step-by-step deployment
3. Update API endpoint in `frontend/app.js`
4. Deploy Lambda functions and Step Functions
5. Upload frontend to S3

## Git Repository

Ready to push to GitHub:
```bash
cd aws-ec2-approval-workflow
git init
git add .
git commit -m "Initial commit: AWS EC2 approval workflow"
git remote add origin <your-repo-url>
git push -u origin main
```
