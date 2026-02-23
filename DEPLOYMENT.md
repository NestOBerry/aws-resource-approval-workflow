# Deployment Guide

## Prerequisites
- AWS CLI configured
- AWS account with appropriate permissions
- SES verified email addresses
- Python 3.12

## Step-by-Step Deployment

### 1. Create IAM Roles

#### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "states:StartExecution",
        "states:SendTaskSuccess",
        "states:SendTaskFailure",
        "ses:SendEmail",
        "ec2:RunInstances",
        "ec2:DescribeImages",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. Deploy Lambda Functions

```bash
cd lambda
for func in *.py; do
  zip ${func%.py}.zip $func
  aws lambda create-function \
    --function-name ${func%.py} \
    --runtime python3.12 \
    --role arn:aws:iam::ACCOUNT_ID:role/LambdaRole \
    --handler ${func%.py}.lambda_handler \
    --zip-file fileb://${func%.py}.zip
done
```

### 3. Set Environment Variables

```bash
# RequestStarter
aws lambda update-function-configuration \
  --function-name RequestStarter \
  --environment Variables={STATE_MACHINE_ARN=arn:aws:states:REGION:ACCOUNT:stateMachine:EC2ApprovalDemo}

# SendApprovalEmail
aws lambda update-function-configuration \
  --function-name SendApprovalEmail \
  --environment Variables={FROM_EMAIL=noreply@company.com,APPROVAL_BASE_URL=https://API_ID.execute-api.REGION.amazonaws.com}

# SendRequesterNotification
aws lambda update-function-configuration \
  --function-name SendRequesterNotification \
  --environment Variables={FROM_EMAIL=noreply@company.com}
```

### 4. Deploy Step Functions

```bash
aws stepfunctions create-state-machine \
  --name EC2ApprovalDemo \
  --definition file://stepfunctions/EC2ApprovalDemo-UPDATED.json \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/StepFunctionsRole
```

### 5. Deploy Frontend

```bash
aws s3 mb s3://ec2-request-portal
aws s3 sync frontend/ s3://ec2-request-portal/
aws s3 website s3://ec2-request-portal/ --index-document index.html
```
