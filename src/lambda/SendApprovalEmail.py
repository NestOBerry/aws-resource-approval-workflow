"""
Lambda Function: SendApprovalEmail
Purpose: Sends approval request email to approver with approve/reject links
Trigger: Step Functions (waitForTaskToken)
"""

import os
import boto3
import urllib.parse

ses = boto3.client("ses")
FROM_EMAIL = os.environ["FROM_EMAIL"]
APPROVAL_BASE_URL = os.environ["APPROVAL_BASE_URL"].rstrip("/")

def lambda_handler(event, context):
    """
    Sends approval email to approver with EC2 request details and action links.
    
    Args:
        event: Contains taskToken and request details from Step Functions
        context: Lambda context object
        
    Returns:
        Status indicating email was sent
        
    Environment Variables:
        FROM_EMAIL: SES verified sender email address
        APPROVAL_BASE_URL: Base URL for approval API Gateway endpoint
    """
    task_token = event["taskToken"]
    req = event["request"]
    
    # Build approval/reject URLs with task token
    token_q = urllib.parse.quote(task_token, safe="")
    approve_url = f"{APPROVAL_BASE_URL}/approval?action=approve&token={token_q}"
    reject_url  = f"{APPROVAL_BASE_URL}/approval?action=reject&token={token_q}"
    
    # Get resolved AMI info
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
    
    # Send email via SES
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={"ToAddresses": [req.get("approverEmail", FROM_EMAIL)]},
        Message={
            "Subject": {"Data": subject}, 
            "Body": {"Text": {"Data": body}}
        }
    )
    
    return {"status": "EMAIL_SENT"}
