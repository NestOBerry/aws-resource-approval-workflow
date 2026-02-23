# Testing Guide

## Pre-Deployment Checklist

### 1. Update Existing Lambda Functions

**Functions that need updating:**
- ✅ `SendApprovalEmail` - Add new fields to email
- ✅ `SendRequesterNotification` - Add new fields to notification

**New Lambda functions to create:**
- ✅ `ResolveAMI` - Fetch latest AL2023 AMI
- ✅ `LaunchEC2` - Launch EC2 with optional params

**Functions that stay the same:**
- ✅ `RequestStarter` - No changes needed
- ✅ `ApprovalHandler` - No changes needed

### 2. Update Step Functions

Replace the entire state machine definition with `EC2ApprovalDemo-UPDATED.json`

**New states added:**
- `ResolveAMI` - First state (new)
- `PrepareEC2Parameters` - Before LaunchEC2 (new)

### 3. Required IAM Permissions

Ensure Lambda execution role has:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:DescribeImages",
        "ec2:CreateTags",
        "ses:SendEmail",
        "states:StartExecution",
        "states:SendTaskSuccess",
        "states:SendTaskFailure",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Local Frontend Testing

### Step 1: Start Local Server

```bash
cd aws-ec2-approval-workflow/frontend
python3 -m http.server 8000
```

### Step 2: Open Browser

Navigate to: `http://localhost:8000`

### Step 3: Test Form Validation

**Test Case 1: All fields filled**
- Fill all fields including optional ones
- Submit and check browser console for API call

**Test Case 2: Optional fields empty**
- Leave AMI ID blank
- Leave EBS fields blank
- Leave Private IP blank
- Should still submit successfully

**Test Case 3: Invalid inputs**
- Invalid email format
- Invalid IP address format
- Empty required fields
- Should show validation errors

## Integration Testing (After Deployment)

### Test 1: Basic Request (All Defaults)

```bash
curl -X POST https://YOUR_API_GATEWAY/request \
  -H "Content-Type: application/json" \
  -d '{
    "requesterEmail": "your@email.com",
    "approverEmail": "approver@email.com",
    "instanceName": "test-instance",
    "instanceType": "t2.micro",
    "subnetId": "subnet-YOUR_SUBNET",
    "securityGroupIds": ["sg-YOUR_SG"]
  }'
```

**Expected:**
- Returns 200 with executionArn
- Approver receives email
- Email shows "Auto-assigned" for IP
- Email shows "AMI default" for EBS

### Test 2: Request with All Options

```bash
curl -X POST https://YOUR_API_GATEWAY/request \
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

**Expected:**
- Returns 200 with executionArn
- Email shows all custom values

### Test 3: Approval Flow

1. Click "Approve" link in email
2. Should see "Approved. You may close this page."
3. Check Step Functions execution - should be in "LaunchEC2" state
4. Requester receives approval email with instance ID

### Test 4: Rejection Flow

1. Click "Reject" link in email
2. Should see "Rejected. You may close this page."
3. Requester receives rejection email

### Test 5: Timeout Flow

1. Submit request
2. Wait 4+ hours without clicking approve/reject
3. Requester receives expiration email

## Troubleshooting

### Frontend Issues

**Problem**: Form submits but no API call
- Check browser console for errors
- Verify API endpoint URL in `app.js`
- Check CORS configuration on API Gateway

**Problem**: CORS error
- Enable CORS on API Gateway
- Add `Access-Control-Allow-Origin: *` header

### Backend Issues

**Problem**: Step Functions fails at ResolveAMI
- Check Lambda logs for `ResolveAMI`
- Verify IAM permissions for `ec2:DescribeImages`

**Problem**: Step Functions fails at LaunchEC2
- Check Lambda logs for `LaunchEC2`
- Verify subnet ID exists
- Verify security group IDs exist
- Check if private IP is already in use

**Problem**: No approval email received
- Check SES sending limits
- Verify email addresses are verified in SES
- Check Lambda logs for `SendApprovalEmail`

## Monitoring

### CloudWatch Logs

Check logs for each Lambda function:
```bash
aws logs tail /aws/lambda/RequestStarter --follow
aws logs tail /aws/lambda/ResolveAMI --follow
aws logs tail /aws/lambda/LaunchEC2 --follow
```

### Step Functions Execution

```bash
aws stepfunctions list-executions \
  --state-machine-arn arn:aws:states:REGION:ACCOUNT:stateMachine:EC2ApprovalDemo \
  --max-results 10
```
