# Step-by-Step AWS Deployment Guide

Follow these steps in order. Don't skip any step!

---

## STEP 1: Fix API Gateway CORS (Do This First!)

### 1.1 Open API Gateway Console
1. Go to AWS Console → Search "API Gateway"
2. Click on **API Gateway**
3. You should see your API with ID: `YOUR_API_GATEWAY_ID`
4. Click on it

### 1.2 Check API Type
Look at the top of the page. Does it say:
- **"HTTP API"** or
- **"REST API"**

**Write down which type you have.**

---

### If you have HTTP API:

#### 1.3a Enable CORS (HTTP API)
1. In the left sidebar, click **CORS**
2. Click **Configure**
3. Fill in these values:
   - **Access control allow origins**: `*`
   - **Access control allow methods**: Check `POST` and `OPTIONS`
   - **Access control allow headers**: `Content-Type`
   - **Access control max age**: `300` (optional)
4. Click **Save**
5. You should see "CORS configuration updated successfully"

#### 1.4a Deploy API
1. In the left sidebar, click **Stages**
2. Click on your stage (probably `$default` or `prod`)
3. Click **Deploy** button at the top
4. Wait for "Deployment successful" message

**✅ CORS is now fixed! Skip to STEP 2.**

---

### If you have REST API:

#### 1.3b Enable CORS (REST API)
1. In the left sidebar, click **Resources**
2. Find `/request` in the resource tree
3. Click on `/request` to select it
4. Click **Actions** dropdown → Select **Enable CORS**
5. A dialog appears with these settings:
   - **Access-Control-Allow-Origin**: `'*'` (with quotes)
   - **Access-Control-Allow-Headers**: `'Content-Type'`
   - **Access-Control-Allow-Methods**: Check `POST` and `OPTIONS`
6. Click **Enable CORS and replace existing CORS headers**
7. Click **Yes, replace existing values** in the confirmation dialog
8. Wait for green checkmarks to appear

#### 1.4b Deploy API
1. Click **Actions** dropdown → Select **Deploy API**
2. Select your **Deployment stage** (probably `prod` or `default`)
3. Click **Deploy**
4. You should see "Successfully deployed API"

**✅ CORS is now fixed! Continue to STEP 2.**

---

## STEP 2: Update Lambda - RequestStarter (with OPTIONS handling)

### 2.1 Open Lambda Console
1. Go to AWS Console → Search "Lambda"
2. Click on **Lambda**
3. Find function: `RequestStarter`
4. Click on it

### 2.2 Update Code
1. Scroll down to the **Code** section
2. You should see the code editor
3. **Delete all existing code**
4. **Copy and paste this new code:**

```python
import os
import json
import boto3

sfn = boto3.client("stepfunctions")
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
    
    out = sfn.start_execution(
        stateMachineArn=ARN, 
        input=json.dumps(body)
    )
    
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
            "executionArn": out["executionArn"]
        })
    }
```

5. Click **Deploy** (orange button at top right)
6. Wait for "Successfully updated the function RequestStarter" message

**✅ Step 2 complete!**

---

## STEP 3: Test Frontend (Should Work Now!)

### 3.1 Test in Browser
1. Go back to `http://localhost:8080`
2. Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows) to hard refresh
3. Fill in the form:
   - **Your Email**: your-email@example.com
   - **Instance Name**: test-instance
   - **Instance Type**: t2.micro
   - **Subnet ID**: (use a real subnet ID from your VPC)
   - **Security Group IDs**: (use a real security group ID)
   - Leave **AMI ID**, **EBS**, **Private IP** blank
4. Click **Submit Request**

### 3.2 Expected Result
You should see:
- ✅ Green success message: "Request submitted successfully!"
- ✅ Shows execution ARN
- ✅ No CORS error

### 3.3 If Still Failing
1. Open DevTools (F12)
2. Go to **Network** tab
3. Submit form again
4. Take a screenshot of the network requests
5. Tell me what you see

**✅ If it works, continue to STEP 4!**

---

## STEP 4: Create New Lambda - ResolveAMI

### 4.1 Create Function
1. Go to **Lambda Console**
2. Click **Create function**
3. Select **Author from scratch**
4. Fill in:
   - **Function name**: `ResolveAMI`
   - **Runtime**: Python 3.12
   - **Architecture**: x86_64
   - **Execution role**: Use existing role (select the same role as RequestStarter)
5. Click **Create function**

### 4.2 Add Code
1. Scroll to **Code source**
2. Delete the default code
3. Paste this code:

```python
import boto3

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    ami_id = event.get("amiId")
    
    if ami_id:
        return {
            "amiId": ami_id,
            "source": "user-provided"
        }
    
    response = ec2.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "name", "Values": ["al2023-ami-*-x86_64"]},
            {"Name": "state", "Values": ["available"]},
            {"Name": "architecture", "Values": ["x86_64"]},
            {"Name": "root-device-type", "Values": ["ebs"]}
        ]
    )
    
    if not response["Images"]:
        raise Exception("No Amazon Linux 2023 AMI found")
    
    images = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)
    latest_ami = images[0]
    
    return {
        "amiId": latest_ami["ImageId"],
        "source": "latest-al2023",
        "name": latest_ami["Name"],
        "creationDate": latest_ami["CreationDate"]
    }
```

4. Click **Deploy**
5. Wait for success message

### 4.3 Update Timeout
1. Click **Configuration** tab
2. Click **General configuration** in left sidebar
3. Click **Edit**
4. Change **Timeout** to `30 seconds`
5. Click **Save**

**✅ Step 4 complete!**

---

## STEP 5: Create New Lambda - LaunchEC2

### 5.1 Create Function
1. Go to **Lambda Console**
2. Click **Create function**
3. Select **Author from scratch**
4. Fill in:
   - **Function name**: `LaunchEC2`
   - **Runtime**: Python 3.12
   - **Architecture**: x86_64
   - **Execution role**: Use existing role (same as before)
5. Click **Create function**

### 5.2 Add Code
1. Scroll to **Code source**
2. Delete the default code
3. Paste this code:

```python
import boto3

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    params = event["params"]
    
    run_params = {
        "ImageId": params["ImageId"],
        "InstanceType": params["InstanceType"],
        "MinCount": params["MinCount"],
        "MaxCount": params["MaxCount"],
        "SubnetId": params["SubnetId"],
        "SecurityGroupIds": params["SecurityGroupIds"],
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": params["InstanceName"]
                    }
                ]
            }
        ]
    }
    
    private_ip = params.get("PrivateIpAddress", "").strip()
    if private_ip and private_ip != "null" and private_ip != "None":
        run_params["PrivateIpAddress"] = private_ip
    
    ebs_size = params.get("EbsVolumeSize", "").strip()
    ebs_type = params.get("EbsVolumeType", "").strip()
    
    if ebs_size and ebs_size != "null" and ebs_size != "None":
        try:
            volume_size = int(ebs_size)
            volume_type = ebs_type if ebs_type and ebs_type != "null" else "gp3"
            
            run_params["BlockDeviceMappings"] = [
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "VolumeSize": volume_size,
                        "VolumeType": volume_type,
                        "DeleteOnTermination": True
                    }
                }
            ]
        except (ValueError, TypeError):
            pass
    
    response = ec2.run_instances(**run_params)
    
    return {
        "Instances": response["Instances"]
    }
```

4. Click **Deploy**

### 5.3 Update Timeout
1. Click **Configuration** tab
2. Click **General configuration**
3. Click **Edit**
4. Change **Timeout** to `60 seconds`
5. Click **Save**

**✅ Step 5 complete!**

---

## STEP 6: Update Lambda - SendApprovalEmail

### 6.1 Open Function
1. Go to **Lambda Console**
2. Find function: `SendApprovalEmail`
3. Click on it

### 6.2 Update Code
1. Scroll to **Code source**
2. Delete all existing code
3. Paste this new code:

```python
import os
import boto3
import urllib.parse

ses = boto3.client("ses")
FROM_EMAIL = os.environ["FROM_EMAIL"]
APPROVAL_BASE_URL = os.environ["APPROVAL_BASE_URL"].rstrip("/")

def lambda_handler(event, context):
    task_token = event["taskToken"]
    req = event["request"]
    
    token_q = urllib.parse.quote(task_token, safe="")
    approve_url = f"{APPROVAL_BASE_URL}/approval?action=approve&token={token_q}"
    reject_url  = f"{APPROVAL_BASE_URL}/approval?action=reject&token={token_q}"
    
    resolved_ami = req.get("resolvedAmi", {})
    ami_id = resolved_ami.get("amiId", req.get("amiId", "N/A"))
    ami_source = resolved_ami.get("amiSource", "user-provided")
    
    subject = f"[Approval Required] EC2 launch: {req.get('instanceName','demo')} ({req['instanceType']})"
    
    body = f"""Hi,

An EC2 launch request is pending your approval.

=== Request Details ===
Requester: {req.get('requesterEmail', 'N/A')}
Instance Name: {req.get('instanceName', 'N/A')}
Instance Type: {req['instanceType']}

=== Network Configuration ===
Subnet ID: {req['subnetId']}
Private IP: {req.get('privateIpAddress') or 'Auto-assigned'}
Security Groups: {req['securityGroupIds']}

=== Storage Configuration ===
EBS Volume Size: {req.get('ebsVolumeSize') or 'AMI default'} GB
EBS Volume Type: {req.get('ebsVolumeType') or 'AMI default'}

=== AMI ===
AMI ID: {ami_id}
Source: {ami_source}

=== Actions ===
Approve: {approve_url}
Reject:  {reject_url}

This request will expire in 4 hours.
"""
    
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [req.get("approverEmail", FROM_EMAIL)]},
        Message={
            "Subject": {"Data": subject}, 
            "Body": {"Text": {"Data": body}}
        }
    )
    
    return {"status": "EMAIL_SENT"}
```

4. Click **Deploy**
5. Wait for success message

**✅ Step 6 complete!**

---

## STEP 7: Update Lambda - SendRequesterNotification

### 7.1 Open Function
1. Go to **Lambda Console**
2. Find function: `SendRequesterNotification`
3. Click on it

### 7.2 Update Code
1. Scroll to **Code source**
2. Delete all existing code
3. Paste this new code:

```python
import os
import boto3

ses = boto3.client("ses")
FROM_EMAIL = os.environ["FROM_EMAIL"]

def lambda_handler(event, context):
    requester_email = event["requesterEmail"]
    decision = event.get("decision", "UNKNOWN")
    reason = event.get("reason", "")
    instance_id = event.get("instanceId", "")
    instance_type = event.get("instanceType", "")
    instance_name = event.get("instanceName", "")
    ami_id = event.get("amiId", "")
    ami_source = event.get("amiSource", "")
    ebs_volume_size = event.get("ebsVolumeSize", "")
    ebs_volume_type = event.get("ebsVolumeType", "")
    private_ip = event.get("privateIpAddress", "")
    
    subject = f"[Request {decision}] {instance_name or 'EC2 Provisioning'}"
    
    lines = [f"Decision: {decision}"]
    
    if reason:
        lines.append(f"Reason: {reason}")
    
    lines.append("\n=== Instance Details ===")
    if instance_name:
        lines.append(f"Instance Name: {instance_name}")
    if instance_type:
        lines.append(f"Instance Type: {instance_type}")
    if instance_id:
        lines.append(f"Instance ID: {instance_id}")
    
    if ami_id:
        lines.append(f"\n=== AMI ===")
        lines.append(f"AMI ID: {ami_id}")
        if ami_source:
            lines.append(f"Source: {ami_source}")
    
    if ebs_volume_size or ebs_volume_type:
        lines.append(f"\n=== Storage ===")
        if ebs_volume_size:
            lines.append(f"EBS Volume Size: {ebs_volume_size} GB")
        if ebs_volume_type:
            lines.append(f"EBS Volume Type: {ebs_volume_type}")
    
    if private_ip:
        lines.append(f"\n=== Network ===")
        lines.append(f"Private IP: {private_ip}")
    
    body = "\n".join(lines)
    
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [requester_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )
    
    return {"status": "SENT", "to": requester_email, "decision": decision}
```

4. Click **Deploy**
5. Wait for success message

**✅ Step 7 complete!**

---

## STEP 8: Update Step Functions State Machine

### 8.1 Open Step Functions Console
1. Go to AWS Console → Search "Step Functions"
2. Click on **Step Functions**
3. Find state machine: `EC2ApprovalDemo`
4. Click on it

### 8.2 Update Definition
1. Click **Edit** button at the top right
2. Click **Next** (skip the first page)
3. You should see the **Definition** editor
4. **Delete all existing JSON**
5. **Copy the entire JSON from the file I'll show you next**

**✅ Ready for the JSON? Reply "ready" and I'll give you the complete Step Functions definition.**

---

## STEP 9: Final Testing

After all updates:
1. Go to `http://localhost:8080`
2. Hard refresh (`Cmd+Shift+R`)
3. Submit a test request
4. Check your email for approval
5. Click approve
6. Verify EC2 instance is created

**✅ All done!**
