# Final Deployment Guide

Complete guide to deploy DynamoDB logging and host the frontend on AWS.

---

## Part 1: Deploy DynamoDB Logging

### Step 1: Create DynamoDB Table

**Option A: Using AWS Console (Recommended)**

1. Go to **AWS Console** → Search "DynamoDB" → Click **DynamoDB**
2. Click **Create table** button
3. Fill in:
   - **Table name**: `EC2ApprovalRequests`
   - **Partition key**: `requestId` (String)
   - **Table settings**: Select **On-demand** (no need to provision capacity)
4. Scroll down to **Secondary indexes** section
5. Click **Create global index**
   - **Partition key**: `requesterEmail` (String)
   - **Sort key**: `timestamp` (Number)
   - **Index name**: `RequesterEmailIndex`
   - **Projected attributes**: All
6. Click **Create index**
7. Scroll to bottom and click **Create table**
8. Wait for table status to become **Active** (30-60 seconds)

**Option B: Using AWS CLI**

```bash
cd aws-ec2-approval-workflow
aws dynamodb create-table --cli-input-json file://dynamodb/table-definition.json --region ap-southeast-5
```

✅ **Table created!**

---

### Step 2: Add DynamoDB Permissions to Lambda Roles

You need to add DynamoDB permissions to the Lambda execution roles.

**For RequestStarter role:**

1. Go to **IAM Console** → **Roles**
2. Search for and click on `LambdaRole-RequestStarter`
3. Click **Add permissions** → **Create inline policy**
4. Click **JSON** tab
5. Paste this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-southeast-5:*:table/EC2ApprovalRequests",
        "arn:aws:dynamodb:ap-southeast-5:*:table/EC2ApprovalRequests/index/*"
      ]
    }
  ]
}
```

6. Click **Next**
7. Name it: `DynamoDBAccessPolicy`
8. Click **Create policy**

✅ **Permissions added!**

---

### Step 3: Update RequestStarter Lambda

1. Go to **Lambda Console**
2. Click on `RequestStarter`
3. Click **Configuration** tab → **Environment variables**
4. Click **Edit**
5. Click **Add environment variable**
   - **Key**: `DYNAMODB_TABLE`
   - **Value**: `EC2ApprovalRequests`
6. Click **Save**

7. Go back to **Code** tab
8. Replace ALL code with the code from: `lambda/RequestStarter.py` (see DYNAMODB_SETUP.md for the updated code)
9. Click **Deploy**

✅ **Lambda updated with DynamoDB logging!**

---

### Step 4: Create UpdateRequestStatus Lambda (Optional)

This Lambda updates the status after approval/rejection.

1. Go to **Lambda Console**
2. Click **Create function**
3. Fill in:
   - **Function name**: `UpdateRequestStatus`
   - **Runtime**: Python 3.12
   - **Execution role**: Use existing role → Select `LambdaRole-RequestStarter`
4. Click **Create function**

5. Click **Configuration** tab → **Environment variables**
6. Click **Edit** → **Add environment variable**
   - **Key**: `DYNAMODB_TABLE`
   - **Value**: `EC2ApprovalRequests`
7. Click **Save**

8. Go to **Code** tab
9. Delete default code and paste code from: `lambda/UpdateRequestStatus.py`
10. Click **Deploy**

✅ **Status updater created!**

---

### Step 5: Test DynamoDB Logging

1. Go to `http://localhost:8080` (your local frontend)
2. Submit a test request
3. Go to **DynamoDB Console**
4. Click on `EC2ApprovalRequests` table
5. Click **Explore table items** tab
6. You should see your request with status "PENDING"!

✅ **DynamoDB logging is working!**

---

## Part 2: Host Frontend on AWS S3 + CloudFront

### Step 1: Create S3 Bucket for Static Website

1. Go to **S3 Console**
2. Click **Create bucket**
3. Fill in:
   - **Bucket name**: `ec2-approval-portal` (must be globally unique, add suffix if needed)
   - **Region**: ap-southeast-5
   - **Block Public Access settings**: UNCHECK "Block all public access"
   - Check the acknowledgment box
4. Scroll down and click **Create bucket**

✅ **Bucket created!**

---

### Step 2: Enable Static Website Hosting

1. Click on your bucket name
2. Go to **Properties** tab
3. Scroll to **Static website hosting** section
4. Click **Edit**
5. Select **Enable**
6. Fill in:
   - **Index document**: `index.html`
   - **Error document**: `index.html`
7. Click **Save changes**
8. Note the **Bucket website endpoint** URL (you'll need this)

✅ **Static hosting enabled!**

---

### Step 3: Add Bucket Policy for Public Access

1. Go to **Permissions** tab
2. Scroll to **Bucket policy** section
3. Click **Edit**
4. Paste this policy (replace `YOUR-BUCKET-NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

5. Click **Save changes**

✅ **Public access configured!**

---

### Step 4: Upload Frontend Files

**Option A: Using AWS Console**

1. Go to **Objects** tab
2. Click **Upload**
3. Click **Add files**
4. Select these files from `frontend/` folder:
   - `index.html`
   - `app.js`
   - `styles.css`
5. Click **Upload**
6. Wait for upload to complete

**Option B: Using AWS CLI**

```bash
cd aws-ec2-approval-workflow/frontend
aws s3 sync . s3://YOUR-BUCKET-NAME/ --region ap-southeast-5
```

✅ **Files uploaded!**

---

### Step 5: Test the Hosted Website

1. Go back to **Properties** tab
2. Scroll to **Static website hosting**
3. Click on the **Bucket website endpoint** URL
4. Your frontend should load!

Example URL: `http://ec2-approval-portal.s3-website.ap-southeast-5.amazonaws.com`

✅ **Website is live!**

---

### Step 6: (Optional) Add CloudFront for HTTPS

If you want HTTPS and better performance:

1. Go to **CloudFront Console**
2. Click **Create distribution**
3. Fill in:
   - **Origin domain**: Select your S3 bucket website endpoint
   - **Viewer protocol policy**: Redirect HTTP to HTTPS
   - **Default root object**: `index.html`
4. Click **Create distribution**
5. Wait 5-10 minutes for deployment
6. Use the CloudFront domain name (e.g., `d1234abcd.cloudfront.net`)

✅ **HTTPS enabled!**

---

## How to View DynamoDB Logs

### Method 1: AWS Console (Easiest)

1. Go to **DynamoDB Console**
2. Click on `EC2ApprovalRequests` table
3. Click **Explore table items** tab
4. You'll see all requests with:
   - Request ID
   - Timestamp
   - Requester email
   - Status (PENDING/APPROVED/REJECTED/EXPIRED)
   - Instance details

**To filter by user:**
1. Click **Query** tab
2. Select index: `RequesterEmailIndex`
3. Enter email address in the partition key field
4. Click **Run**

---

### Method 2: AWS CLI

**Get all requests:**
```bash
aws dynamodb scan \
  --table-name EC2ApprovalRequests \
  --region ap-southeast-5
```

**Get specific request by ID:**
```bash
aws dynamodb get-item \
  --table-name EC2ApprovalRequests \
  --key '{"requestId":{"S":"YOUR_REQUEST_ID"}}' \
  --region ap-southeast-5
```

**Query all requests by a user:**
```bash
aws dynamodb query \
  --table-name EC2ApprovalRequests \
  --index-name RequesterEmailIndex \
  --key-condition-expression "requesterEmail = :email" \
  --expression-attribute-values '{":email":{"S":"user@example.com"}}' \
  --region ap-southeast-5
```

**Get only pending requests:**
```bash
aws dynamodb scan \
  --table-name EC2ApprovalRequests \
  --filter-expression "#status = :status" \
  --expression-attribute-names '{"#status":"status"}' \
  --expression-attribute-values '{":status":{"S":"PENDING"}}' \
  --region ap-southeast-5
```

---

### Method 3: Python Script for Better Formatting

Create a file `view_logs.py`:

```python
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-5')
table = dynamodb.Table('EC2ApprovalRequests')

# Scan all items
response = table.scan()
items = response['Items']

# Sort by timestamp (newest first)
items.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

print(f"\n{'='*100}")
print(f"Total Requests: {len(items)}")
print(f"{'='*100}\n")

for item in items:
    timestamp = datetime.fromtimestamp(item.get('timestamp', 0))
    print(f"Request ID: {item.get('requestId')}")
    print(f"Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Requester: {item.get('requesterEmail')}")
    print(f"Instance: {item.get('instanceName')} ({item.get('instanceType')})")
    print(f"Status: {item.get('status')}")
    if item.get('instanceId'):
        print(f"Instance ID: {item.get('instanceId')}")
    print(f"{'-'*100}\n")
```

Run it:
```bash
python3 view_logs.py
```

---

## What Gets Logged in DynamoDB

Every request logs:
- ✅ **requestId** - Unique UUID
- ✅ **timestamp** - When request was submitted
- ✅ **requesterEmail** - Who requested it
- ✅ **approverEmail** - Who needs to approve
- ✅ **instanceName** - EC2 instance name
- ✅ **instanceType** - t3.micro, etc.
- ✅ **subnetId** - VPC subnet
- ✅ **securityGroupIds** - Security groups
- ✅ **amiId** - AMI ID (if custom)
- ✅ **ebsVolumeSize** - EBS size (if custom)
- ✅ **ebsVolumeType** - EBS type (if custom)
- ✅ **privateIpAddress** - Private IP (if specified)
- ✅ **status** - PENDING → APPROVED/REJECTED/EXPIRED
- ✅ **executionArn** - Step Functions execution
- ✅ **instanceId** - EC2 instance ID (after approval)
- ✅ **approvalTimestamp** - When approved/rejected

---

## Summary

After completing both parts, you'll have:

1. ✅ **DynamoDB table** logging all requests
2. ✅ **Updated Lambda functions** writing to DynamoDB
3. ✅ **Frontend hosted on S3** (publicly accessible)
4. ✅ **Complete audit trail** of all EC2 requests
5. ✅ **Query capabilities** to view logs by user or status

**Your EC2 approval workflow is now production-ready!**
