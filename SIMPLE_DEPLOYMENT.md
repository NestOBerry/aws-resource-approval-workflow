# Simple Deployment Guide - t3.micro Only

This is a simplified deployment for POC using only t3.micro with Golden AMI.

---

## Current Status
- ✅ CORS enabled on API Gateway
- ✅ Frontend working at http://localhost:8080
- ✅ RequestStarter updated with CORS headers

---

## STEP 4: Create Lambda - ResolveAMI

### 4.1 Create Function
1. Go to **Lambda Console**
2. Click **Create function**
3. Fill in:
   - **Function name**: `ResolveAMI`
   - **Runtime**: Python 3.12
   - **Execution role**: Use existing role (same as RequestStarter)
4. Click **Create function**

### 4.2 Add Code
Delete default code and paste:

```python
import boto3

ec2 = boto3.client("ec2")

# Golden AMI for t3.micro (customer's approved AMI)
GOLDEN_AMI = "ami-077dbbb6eecc8ae69"

def lambda_handler(event, context):
    """
    Resolves AMI based on:
    1. User-provided AMI (if specified)
    2. Golden AMI for t3.micro (default)
    """
    ami_id = event.get("amiId")
    
    # If user provided AMI, use it
    if ami_id:
        return {
            "amiId": ami_id,
            "source": "user-provided"
        }
    
    # Use golden AMI for t3.micro
    return {
        "amiId": GOLDEN_AMI,
        "source": "golden-ami",
        "description": "Approved Golden AMI for t3.micro"
    }
```

Click **Deploy**

### 4.3 Update Timeout
1. Click **Configuration** tab
2. Click **General configuration**
3. Click **Edit**
4. Change timeout to **30 seconds**
5. Click **Save**

**✅ STEP 4 Complete!**

---

## STEP 5: Create Lambda - LaunchEC2

### 5.1 Create Function
1. Go to **Lambda Console**
2. Click **Create function**
3. Fill in:
   - **Function name**: `LaunchEC2`
   - **Runtime**: Python 3.12
   - **Execution role**: Use existing role
4. Click **Create function**

### 5.2 Add Code
Delete default code and paste:

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
                "Tags": [{"Key": "Name", "Value": params["InstanceName"]}]
            }
        ]
    }
    
    # Add PrivateIpAddress if provided
    private_ip = params.get("PrivateIpAddress", "").strip()
    if private_ip and private_ip != "null":
        run_params["PrivateIpAddress"] = private_ip
    
    # Add EBS config if provided
    ebs_size = params.get("EbsVolumeSize", "").strip()
    ebs_type = params.get("EbsVolumeType", "").strip()
    
    if ebs_size and ebs_size != "null":
        try:
            volume_size = int(ebs_size)
            volume_type = ebs_type if ebs_type and ebs_type != "null" else "gp3"
            
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

Click **Deploy**

### 5.3 Update Timeout
1. Click **Configuration** tab
2. Click **General configuration**
3. Click **Edit**
4. Change timeout to **60 seconds**
5. Click **Save**

**✅ STEP 5 Complete!**

---

## Next Steps

After creating these 2 Lambda functions, you need to:
1. Update SendApprovalEmail (STEP 6)
2. Update SendRequesterNotification (STEP 7)
3. Update Step Functions state machine (STEP 8)

**Ready to continue?**
