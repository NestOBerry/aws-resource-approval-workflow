"""
Lambda Function: UpdateRequestStatus
Purpose: Updates request status in DynamoDB after approval/rejection/expiration
Trigger: Step Functions (called from notification states)
"""

import os
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DYNAMODB_TABLE", "EC2ApprovalRequests"))

def lambda_handler(event, context):
    """
    Updates the status of a request in DynamoDB.
    
    Args:
        event: Contains requestId, decision, and optional instanceId
        context: Lambda context object
        
    Returns:
        Status update confirmation
        
    Environment Variables:
        DYNAMODB_TABLE: DynamoDB table name (default: EC2ApprovalRequests)
    """
    request_id = event.get("requestId")
    decision = event.get("decision", "UNKNOWN")
    instance_id = event.get("instanceId")
    
    if not request_id:
        print("No requestId provided, skipping DynamoDB update")
        return {"status": "SKIPPED", "reason": "No requestId"}
    
    timestamp = int(datetime.utcnow().timestamp())
    
    # Build update expression
    update_expr = "SET #status = :status, approvalTimestamp = :timestamp"
    expr_attr_names = {"#status": "status"}
    expr_attr_values = {
        ":status": decision,
        ":timestamp": timestamp
    }
    
    # Add instanceId if provided (for approved requests)
    if instance_id:
        update_expr += ", instanceId = :instanceId"
        expr_attr_values[":instanceId"] = instance_id
    
    # Add resolved AMI if provided
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
        
        return {
            "status": "UPDATED",
            "requestId": request_id,
            "decision": decision
        }
    except Exception as e:
        print(f"Failed to update DynamoDB: {str(e)}")
        return {
            "status": "FAILED",
            "error": str(e)
        }
