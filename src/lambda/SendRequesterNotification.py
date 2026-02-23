"""
Lambda Function: SendRequesterNotification
Purpose: Notifies requester of approval decision (approved/rejected/expired)
Trigger: Step Functions
"""

import os
import boto3

ses = boto3.client("ses")
FROM_EMAIL = os.environ["FROM_EMAIL"]

def lambda_handler(event, context):
    """
    Sends notification email to requester with decision outcome and instance details.
    
    Args:
        event: Contains decision, requester email, and instance details
        context: Lambda context object
        
    Returns:
        Status with recipient and decision
        
    Environment Variables:
        FROM_EMAIL: SES verified sender email address
    """
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
    
    # Build email body
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
    
    # Send email via SES
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [requester_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}}
        }
    )
    
    return {"status": "SENT", "to": requester_email, "decision": decision}
