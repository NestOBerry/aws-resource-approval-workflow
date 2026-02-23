# Deployment Steps - From Current to New Version

## Current State
Your AWS has the OLD version without:
- AMI auto-resolution
- Optional EBS configuration
- Optional Private IP

## Deployment Order (IMPORTANT!)

### Step 1: Create New Lambda Functions

#### 1.1 Create ResolveAMI
```bash
cd aws-ec2-approval-workflow/lambda
zip ResolveAMI.zip ResolveAMI.py

aws lambda create-function \
  --function-name ResolveAMI \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_LAMBDA_ROLE \
  --handler ResolveAMI.lambda_handler \
  --zip-file fileb://ResolveAMI.zip \
  --timeout 30
```

#### 1.2 Create LaunchEC2
```bash
zip LaunchEC2.zip LaunchEC2.py

aws lambda create-function \
  --function-name LaunchEC2 \
  --runtime python3.12 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_LAMBDA_ROLE \
  --handler LaunchEC2.lambda_handler \
  --zip-file fileb://LaunchEC2.zip \
  --timeout 60
```

### Step 2: Update Existing Lambda Functions

#### 2.1 Update SendApprovalEmail
```bash
zip SendApprovalEmail.zip SendApprovalEmail.py

aws lambda update-function-code \
  --function-name SendApprovalEmail \
  --zip-file fileb://SendApprovalEmail.zip
```

#### 2.2 Update SendRequesterNotification
```bash
zip SendRequesterNotification.zip SendRequesterNotification.py

aws lambda update-function-code \
  --function-name SendRequesterNotification \
  --zip-file fileb://SendRequesterNotification.zip
```

### Step 3: Update Step Functions State Machine

```bash
cd aws-ec2-approval-workflow/stepfunctions

aws stepfunctions update-state-machine \
  --state-machine-arn arn:aws:states:ap-southeast-5:YOUR_ACCOUNT:stateMachine:EC2ApprovalDemo \
  --definition file://EC2ApprovalDemo-UPDATED.json
```

### Step 4: Test the Updated System

#### Test 1: With all defaults (no AMI, no EBS, no IP)
```bash
curl -X POST https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com/request \
  -H "Content-Type: application/json" \
  -d '{
    "requesterEmail": "your@email.com",
    "approverEmail": "approver@email.com",
    "instanceName": "test-auto-defaults",
    "instanceType": "t2.micro",
    "subnetId": "subnet-YOUR_SUBNET",
    "securityGroupIds": ["sg-YOUR_SG"]
  }'
```

#### Test 2: With custom values
```bash
curl -X POST https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com/request \
  -H "Content-Type: application/json" \
  -d '{
    "requesterEmail": "your@email.com",
    "approverEmail": "approver@email.com",
    "instanceName": "test-custom",
    "instanceType": "t3.small",
    "subnetId": "subnet-YOUR_SUBNET",
    "securityGroupIds": ["sg-YOUR_SG"],
    "amiId": "ami-YOUR_AMI",
    "ebsVolumeSize": 30,
    "ebsVolumeType": "gp3",
    "privateIpAddress": "10.0.1.50"
  }'
```

### Step 5: Deploy Frontend to S3

```bash
cd aws-ec2-approval-workflow/frontend

# Create S3 bucket (if not exists)
aws s3 mb s3://ec2-request-portal-YOUR_NAME

# Upload files
aws s3 cp index.html s3://ec2-request-portal-YOUR_NAME/
aws s3 cp app.js s3://ec2-request-portal-YOUR_NAME/
aws s3 cp styles.css s3://ec2-request-portal-YOUR_NAME/

# Enable static website hosting
aws s3 website s3://ec2-request-portal-YOUR_NAME/ \
  --index-document index.html

# Make files public (or use CloudFront)
aws s3api put-bucket-policy \
  --bucket ec2-request-portal-YOUR_NAME \
  --policy '{
    "Version": "2012-10-17",
    "Statement": [{
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::ec2-request-portal-YOUR_NAME/*"
    }]
  }'
```

## Rollback Plan

If something goes wrong:

### Rollback Step Functions
```bash
# Revert to old definition (you should backup first!)
aws stepfunctions update-state-machine \
  --state-machine-arn arn:aws:states:ap-southeast-5:YOUR_ACCOUNT:stateMachine:EC2ApprovalDemo \
  --definition file://EC2ApprovalDemo-OLD-BACKUP.json
```

### Rollback Lambda Functions
```bash
# List versions
aws lambda list-versions-by-function --function-name SendApprovalEmail

# Revert to previous version
aws lambda update-function-configuration \
  --function-name SendApprovalEmail \
  --revision-id PREVIOUS_REVISION_ID
```

## Verification Checklist

After deployment:
- [ ] All 6 Lambda functions exist
- [ ] Step Functions has 7 states (was 5 before)
- [ ] Test request with no AMI → should use latest AL2023
- [ ] Test request with no EBS → should use AMI default
- [ ] Test request with no IP → should auto-assign
- [ ] Approval email shows new fields
- [ ] Notification email shows new fields
- [ ] Frontend form submits successfully
