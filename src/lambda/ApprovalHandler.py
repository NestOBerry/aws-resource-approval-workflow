"""
Lambda Function: ApprovalHandler
Purpose: Handles approval/rejection decisions from email links
Trigger: API Gateway GET /approval
"""

import boto3
import json

sfn = boto3.client("stepfunctions")

def lambda_handler(event, context):
    """
    Processes approval or rejection from email link and sends task token response.
    
    Args:
        event: API Gateway event with query parameters (action, token)
        context: Lambda context object
        
    Returns:
        API Gateway response with success/error message
        
    Query Parameters:
        action: "approve" or "reject"
        token: Step Functions task token from email
    """
    qs = event.get("queryStringParameters") or {}
    action = qs.get("action")
    token = qs.get("token")
    
    # Validate parameters
    if not token or action not in ("approve", "reject"):
        return {
            "statusCode": 400, 
            "body": "Missing or invalid parameters"
        }
    
    # Handle approval
    if action == "approve":
        sfn.send_task_success(
            taskToken=token,
            output=json.dumps({
                "approval": {
                    "decision": "APPROVED", 
                    "approvedBy": "manager"
                }
            })
        )
        return {
            "statusCode": 200, 
            "body": "Approved. You may close this page."
        }
    
    # Handle rejection
    sfn.send_task_failure(
        taskToken=token,
        error="RejectedByApprover",
        cause="Rejected via email link"
    )
    return {
        "statusCode": 200, 
        "body": "Rejected. You may close this page."
    }
