# Customization Guide

This document describes how to extend the MVP beyond its current EC2-only implementation.

## Current MVP Features

The deployed solution includes:
- ✅ EC2 instance provisioning (t3.micro only)
- ✅ Email-based approval workflow
- ✅ DynamoDB request logging
- ✅ Web-based request portal
- ✅ Optional EBS and network configuration
- ✅ Human-readable audit trail

## Extension Ideas

### 1. Add Cognito Authentication

**Current State**: Frontend has TODO markers for Cognito integration

**What to Add**:
1. Create Cognito User Pool
2. Update `frontend/app.js`:
   - Uncomment Cognito sections (lines 127-150)
   - Implement `initializeCognito()`, `login()`, `logout()`
   - Add JWT token to API requests
3. Update API Gateway to validate Cognito tokens
4. Add login/logout UI to `frontend/index.html`

**Benefits**: Secure user authentication, no need to enter email manually

---

### 2. Support Multiple Instance Types

**Current State**: Only t3.micro is available

**What to Add**:
1. Update `frontend/index.html`:
   ```html
   <option value="t3.micro">t3.micro (2 vCPU, 1 GB RAM)</option>
   <option value="t3.small">t3.small (2 vCPU, 2 GB RAM)</option>
   <option value="t3.medium">t3.medium (2 vCPU, 4 GB RAM)</option>
   ```

2. Update Golden AMI if needed for larger instances
3. Consider cost approval thresholds

**Benefits**: More flexibility for different workloads

---

### 3. Add Windows OS Support

**Current State**: Only Linux AMI supported

**What to Add**:
1. Find Windows AMI ID in your region:
   ```bash
   aws ec2 describe-images \
     --owners amazon \
     --filters "Name=name,Values=Windows_Server-2022*" \
     --query 'Images[0].ImageId'
   ```

2. Add OS selector to frontend:
   ```html
   <select id="osType">
     <option value="linux">Amazon Linux 2023</option>
     <option value="windows">Windows Server 2022</option>
   </select>
   ```

3. Update Step Functions to use different AMI based on OS choice

**Benefits**: Support for Windows workloads

---

### 4. Add RDS Database Provisioning

**What to Add**:
1. Create new Lambda function: `LaunchRDS.py`
   ```python
   import boto3
   rds = boto3.client('rds')
   
   def lambda_handler(event, context):
       response = rds.create_db_instance(
           DBInstanceIdentifier=event['dbName'],
           DBInstanceClass=event['dbInstanceClass'],
           Engine=event['engine'],
           MasterUsername=event['masterUsername'],
           MasterUserPassword=event['masterPassword'],
           # ... other parameters
       )
       return response
   ```

2. Add RDS form fields to frontend
3. Update Step Functions to handle RDS requests
4. Add RDS-specific approval logic

**Benefits**: Unified approval workflow for databases

---

### 5. Add S3 Bucket Provisioning

**What to Add**:
1. Create new Lambda function: `CreateS3Bucket.py`
   ```python
   import boto3
   s3 = boto3.client('s3')
   
   def lambda_handler(event, context):
       response = s3.create_bucket(
           Bucket=event['bucketName'],
           CreateBucketConfiguration={
               'LocationConstraint': event['region']
           }
       )
       # Apply bucket policy if provided
       return response
   ```

2. Add S3 form fields to frontend
3. Update Step Functions workflow
4. Add bucket policy templates

**Benefits**: Centralized storage provisioning

---

### 6. Add Cost Estimation

**What to Add**:
1. Create Lambda function: `EstimateCost.py`
   - Use AWS Pricing API
   - Calculate monthly cost estimate
   - Include in approval email

2. Update approval email template to show costs
3. Add cost threshold for auto-approval

**Benefits**: Better cost control and visibility

---

### 7. Add Slack/Teams Notifications

**What to Add**:
1. Create Lambda function: `SendSlackNotification.py`
   ```python
   import requests
   
   def lambda_handler(event, context):
       webhook_url = os.environ['SLACK_WEBHOOK']
       message = {
           "text": f"New EC2 request: {event['instanceName']}"
       }
       requests.post(webhook_url, json=message)
   ```

2. Add Slack webhook URL to environment variables
3. Call from Step Functions after request submission

**Benefits**: Real-time notifications in team channels

---

### 8. Add Admin Dashboard

**What to Add**:
1. Create new frontend page: `admin.html`
2. Add Lambda function: `GetAllRequests.py`
   - Query DynamoDB for all requests
   - Return paginated results
3. Display requests in table with filters
4. Add bulk approval/rejection

**Benefits**: Better visibility and management

---

### 9. Add Request History View

**What to Add**:
1. Update frontend to show user's past requests
2. Query DynamoDB by requester email
3. Show status, timestamps, instance IDs
4. Add "Request Again" button to clone requests

**Benefits**: Better user experience

---

### 10. Multi-Region Support

**What to Add**:
1. Add region selector to frontend
2. Update Lambda functions to use selected region
3. Maintain separate DynamoDB tables per region
4. Update Step Functions to handle region parameter

**Benefits**: Global deployment support

---

## Implementation Priority

### High Value, Low Effort
1. Multiple instance types
2. Windows OS support
3. Cost estimation

### High Value, Medium Effort
4. Cognito authentication
5. Slack/Teams notifications
6. Request history view

### High Value, High Effort
7. RDS provisioning
8. S3 bucket provisioning
9. Admin dashboard
10. Multi-region support

---

## Testing Customizations

When adding features:
1. Test Lambda functions locally first
2. Update Step Functions definition
3. Test end-to-end workflow
4. Update documentation
5. Add error handling
6. Update DynamoDB schema if needed

---

## Need Help?

The current codebase provides a solid foundation. Study the existing Lambda functions and Step Functions workflow to understand the patterns, then extend them for your use case.
