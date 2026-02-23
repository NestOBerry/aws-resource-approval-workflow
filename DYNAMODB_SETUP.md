# DynamoDB Setup - Request Logging

## What This Does

Logs every EC2 request with:
- ✅ Who requested it
- ✅ When it was requested
- ✅ What they requested (instance type, AMI, etc.)
- ✅ Current status (PENDING → APPROVED/REJECTED/EXPIRED)
- ✅ Instance ID (after approval)

---

## STEP 1: Create DynamoDB Table

### Option A: AWS Console (Easiest)

1. Go to **AWS Console** → Search "DynamoDB"
2. Click **DynamoDB**
3. Click **Create table** button
4. Fill in:
   - **Table name**: `EC2ApprovalRequests`
   - **Partition key**: `requestId` (String)
   - **Table settings**: Select **On-demand** (pay per request)
5. Scroll down to **Secondary indexes**
6. Click **Create global index**
   - **Partition key**: `requesterEmail` (String)
   - **Sort key**: `timestamp` (Number)
   - **Index name**: `RequesterEmailIndex`
   - **Projected attributes**: All
7. Click **Create index**
8. Scroll to bottom and click **Create table**
9. Wait for table status to become **Active** (30-60 seconds)

### Option B: AWS CLI

```bash
cd aws-ec2-approval-workflow
aws dynamodb create-table --cli-input-json file://dynamodb/table-definition.json
```

**✅ Table created!**

---

## STEP 2: Update Lambda IAM Role

Your Lambda functions need permission to read/write DynamoDB.

### 2.1 Find Your Lambda Execution Role

1. Go to **Lambda Console**
2. Click on `RequestStarter`
3. Click **Configuration** tab
4. Click **Permissions** in left sidebar
5. Under **Execution role**, click the role name (opens IAM)

### 2.2 Add DynamoDB Policy

1. In IAM role page, click **Add permissions** → **Attach policies**
2. Search for: `AmazonDynamoDBFullAccess`
3. Check the box next to it
4. Click **Add permissions**

**Or create a custom policy (more secure):**

1. Click **Add permissions** → **Create inline policy**
2. Click **JSON** tab
3. Paste this:

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
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:ap-southeast-5:*:table/EC2ApprovalRequests",
        "arn:aws:dynamodb:ap-southeast-5:*:table/EC2ApprovalRequests/index/*"
      ]
    }
  ]
}
```

4. Click **Review policy**
5. Name it: `EC2ApprovalDynamoDBAccess`
6. Click **Create policy**

**✅ Permissions added!**

---

## STEP 3: Update Lambda - RequestStarter (with DynamoDB logging)

1. Go to **Lambda Console**
2. Click on `RequestStarter`
3. Scroll to **Code source**
4. **Delete all code**
5. **Paste the new code** (see below)
6. Click **Deploy**

### New Code:

```python
import os
import json
import boto3
import uuid
from datetime import datetime

sfn = boto3.client("stepfunctions")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "EC2ApprovalRequests"))
ARN = os.environ["STATE_MACHINE_ARN"]

def lambda_handler(event, context):
    # Handle OPTIONS preflight request
    if event.get('httpMethod') == 'OPTIONS' or event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": ""
        }
    
    body = json.loads(event.get("body") or "{}")
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    timestamp = int(datetime.utcnow().timestamp())
    
    # Add requestId to the request
    body["requestId"] = request_id
    body["timestamp"] = timestamp
    
    # Start Step Functions execution
    out = sfn.start_execution(
        stateMachineArn=ARN,
        name=f"request-{request_id}",
        input=json.dumps(body)
    )
    
    # Log request to DynamoDB
    try:
        table.put_item(
            Item={
                "requestId": request_id,
                "timestamp": timestamp,
                "requesterEmail": body.get("requesterEmail", "unknown"),
                "approverEmail": body.get("approverEmail", "unknown"),
                "instanceName": body.get("instanceName", ""),
                "instanceType": body.get("instanceType", ""),
                "subnetId": body.get("subnetId", ""),
                "securityGroupIds": body.get("securityGroupIds", []),
                "amiId": body.get("amiId"),
                "ebsVolumeSize": body.get("ebsVolumeSize"),
                "ebsVolumeType": body.get("ebsVolumeType"),
                "privateIpAddress": body.get("privateIpAddress"),
                "status": "PENDING",
                "executionArn": out["executionArn"],
                "expirationTime": timestamp + (4 * 3600)
            }
        )
    except Exception as e:
        print(f"Failed to log to DynamoDB: {str(e)}")
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({
            "message": "Submitted",
            "requestId": request_id,
            "executionArn": out["executionArn"]
        })
    }
```

**✅ Lambda updated!**

---

## STEP 4: Create Lambda - UpdateRequestStatus (Optional but Recommended)

This Lambda updates the request status after approval/rejection.

1. Go to **Lambda Console**
2. Click **Create function**
3. Fill in:
   - **Function name**: `UpdateRequestStatus`
   - **Runtime**: Python 3.12
   - **Execution role**: Use existing role (same as RequestStarter)
4. Click **Create function**
5. Paste this code:

```python
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "EC2ApprovalRequests"))

def lambda_handler(event, context):
    request_id = event.get("requestId")
    decision = event.get("decision", "UNKNOWN")
    instance_id = event.get("instanceId")
    
    if not request_id:
        return {"status": "SKIPPED"}
    
    timestamp = int(datetime.utcnow().timestamp())
    
    update_expr = "SET #status = :status, approvalTimestamp = :timestamp"
    expr_attr_names = {"#status": "status"}
    expr_attr_values = {
        ":status": decision,
        ":timestamp": timestamp
    }
    
    if instance_id:
        update_expr += ", instanceId = :instanceId"
        expr_attr_values[":instanceId"] = instance_id
    
    if event.get("amiId"):
        update_expr += ", resolvedAmiId = :amiId"
        expr_attr_values[":amiId"] = event.get("amiId")
    
    try:
        table.update_item(
            Key={"requestId": request_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values
        )
        return {"status": "UPDATED"}
    except Exception as e:
        print(f"Failed to update: {str(e)}")
        return {"status": "FAILED"}
```

6. Click **Deploy**

**✅ Status updater created!**

---

## STEP 5: Test DynamoDB Logging

1. Go to `http://localhost:8080`
2. Submit a test request
3. Go to **DynamoDB Console**
4. Click on `EC2ApprovalRequests` table
5. Click **Explore table items**
6. You should see your request logged!

**✅ Logging is working!**

---

## View Logged Requests

### In AWS Console:
1. Go to **DynamoDB Console**
2. Click `EC2ApprovalRequests`
3. Click **Explore table items**
4. See all requests with status

### Query by User:
1. Click **Query** tab
2. Select index: `RequesterEmailIndex`
3. Enter email address
4. Click **Run**

### Using AWS CLI:
```bash
# Get all requests
aws dynamodb scan --table-name EC2ApprovalRequests

# Get specific request
aws dynamodb get-item \
  --table-name EC2ApprovalRequests \
  --key '{"requestId":{"S":"YOUR_REQUEST_ID"}}'

# Query by user
aws dynamodb query \
  --table-name EC2ApprovalRequests \
  --index-name RequesterEmailIndex \
  --key-condition-expression "requesterEmail = :email" \
  --expression-attribute-values '{":email":{"S":"user@example.com"}}'
```

---

## What Gets Logged

Every request logs:
- ✅ Request ID (unique)
- ✅ Timestamp
- ✅ Requester email
- ✅ Approver email
- ✅ Instance details (name, type, subnet, security groups)
- ✅ Optional fields (AMI, EBS, Private IP)
- ✅ Status (PENDING → APPROVED/REJECTED/EXPIRED)
- ✅ Execution ARN
- ✅ Instance ID (after approval)

**Perfect for auditing and compliance!**
