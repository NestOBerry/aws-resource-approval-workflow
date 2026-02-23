"""
Lambda Function: RequestStarter
Purpose: Receives EC2 provisioning requests from API Gateway and starts Step Functions workflow
Trigger: API Gateway POST /request
"""

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
    """
    Starts the EC2 approval workflow Step Functions execution.
    
    Args:
        event: API Gateway event containing request body with EC2 parameters
        context: Lambda context object
        
    Returns:
        API Gateway response with execution ARN
        
    Environment Variables:
        STATE_MACHINE_ARN: ARN of the Step Functions state machine
        DYNAMODB_TABLE: DynamoDB table name for logging (default: EC2ApprovalRequests)
    """
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
    readable_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
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
                "requestDate": readable_date,
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
                "expirationTime": timestamp + (4 * 3600)  # 4 hours TTL
            }
        )
    except Exception as e:
        print(f"Failed to log to DynamoDB: {str(e)}")
        # Don't fail the request if logging fails
    
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

