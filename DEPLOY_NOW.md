# Deploy Now - Simplified Guide

Only 4 Lambda functions needed! No ResolveAMI Lambda.

---

## What You Already Have ✅
- RequestStarter (with CORS)
- SendApprovalEmail
- SendRequesterNotification
- ApprovalHandler
- Step Functions state machine

---

## What Needs Updating

### STEP 1: Create Lambda - LaunchEC2 (NEW)

1. Go to **Lambda Console**
2. Click **Create function**
3. Fill in:
   - **Function name**: `LaunchEC2`
   - **Runtime**: Python 3.12
   - **Execution role**: Use existing role (same as RequestStarter)
4. Click **Create function**
5. Delete default code and paste:

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
        "TagSpecifications": [{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": params["InstanceName"]}]
        }]
    }
    
    # Add PrivateIpAddress if provided
    private_ip = params.get("PrivateIpAddress", "").strip()
    if private_ip and private_ip != "null":
        run_params["PrivateIpAddress"] = private_ip
    
    # Add EBS config if provided
    ebs_size = params.get("EbsVolumeSize", "").strip()
    if ebs_size and ebs_size != "null":
        try:
            volume_size = int(ebs_size)
            volume_type = params.get("EbsVolumeType", "gp3").strip() or "gp3"
            
            run_params["BlockDeviceMappings"] = [{
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "VolumeSize": volume_size,
                    "VolumeType": volume_type,
                    "DeleteOnTermination": True
                }
            }]
        except (ValueError, TypeError):
            pass
    
    response = ec2.run_instances(**run_params)
    return {"Instances": response["Instances"]}
```

6. Click **Deploy**
7. Go to **Configuration** → **General configuration** → **Edit**
8. Change timeout to **60 seconds** → **Save**

---

### STEP 2: Update Lambda - SendApprovalEmail

1. Go to **Lambda Console**
2. Click on `SendApprovalEmail`
3. Replace code with:

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
EBS Volume Size: {req.get('ebsVolumeSize') or 'Default'} GB
EBS Volume Type: {req.get('ebsVolumeType') or 'Default'}

=== AMI ===
AMI ID: ami-077dbbb6eecc8ae69 (Golden AMI for t3.micro)

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

---

### STEP 3: Update Lambda - SendRequesterNotification

1. Go to **Lambda Console**
2. Click on `SendRequesterNotification`
3. Replace code with:

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

---

### STEP 4: Update Step Functions

1. Go to **Step Functions Console**
2. Click on `EC2ApprovalDemo`
3. Click **Edit**
4. Click **Next**
5. In the **Definition** editor, **delete all JSON**
6. **Paste the new definition** (see EC2ApprovalDemo-SIMPLE.json file)
7. Click **Next** → **Next** → **Save**

---

## Test Everything

1. Go to `http://localhost:8080`
2. Refresh page (`Cmd+Shift+R`)
3. Fill form (only t3.micro available now)
4. Submit
5. Check email for approval
6. Click approve
7. Check EC2 console for new instance!

---

## Summary

**Total Lambda Functions: 4**
- RequestStarter (existing, updated)
- SendApprovalEmail (existing, updated)
- SendRequesterNotification (existing, updated)
- LaunchEC2 (NEW)
- ApprovalHandler (existing, no changes)

**No ResolveAMI Lambda needed!** AMI is hardcoded in Step Functions.
