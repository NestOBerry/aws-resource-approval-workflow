import boto3

ec2 = boto3.client("ec2")

def lambda_handler(event, context):
    """
    Launch EC2 with optional private IP and EBS configuration.
    If not provided, AWS will auto-assign.
    """
    params = event["params"]
    
    # Build RunInstances parameters
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
    
    # Add PrivateIpAddress only if provided
    private_ip = params.get("PrivateIpAddress", "").strip()
    if private_ip and private_ip != "null" and private_ip != "None":
        run_params["PrivateIpAddress"] = private_ip
    
    # Add BlockDeviceMappings only if EBS config is provided
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
            # If conversion fails, skip EBS config (use AMI default)
            pass
    
    # Launch EC2 instance
    response = ec2.run_instances(**run_params)
    
    # Extract only JSON-serializable data
    instance = response["Instances"][0]
    
    return {
        "Instances": [{
            "InstanceId": instance["InstanceId"],
            "InstanceType": instance["InstanceType"],
            "State": instance["State"]["Name"],
            "PrivateIpAddress": instance.get("PrivateIpAddress", ""),
            "SubnetId": instance["SubnetId"],
            "ImageId": instance["ImageId"]
        }]
    }
