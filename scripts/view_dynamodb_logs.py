#!/usr/bin/env python3
"""
View EC2 Approval Request Logs from DynamoDB
Usage: python3 view_dynamodb_logs.py [--user EMAIL] [--status STATUS]
"""

import boto3
import argparse
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-5')
table = dynamodb.Table('EC2ApprovalRequests')

def decimal_to_int(obj):
    """Convert Decimal to int for display"""
    if isinstance(obj, Decimal):
        return int(obj)
    return obj

def format_timestamp(ts):
    """Format Unix timestamp to readable date"""
    if ts:
        return datetime.fromtimestamp(decimal_to_int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    return 'N/A'

def view_all_requests():
    """View all requests"""
    response = table.scan()
    items = response['Items']
    
    # Sort by timestamp (newest first)
    items.sort(key=lambda x: decimal_to_int(x.get('timestamp', 0)), reverse=True)
    
    print(f"\n{'='*120}")
    print(f"EC2 APPROVAL REQUESTS - Total: {len(items)}")
    print(f"{'='*120}\n")
    
    for item in items:
        print_request(item)

def view_by_user(email):
    """View requests by specific user"""
    response = table.query(
        IndexName='RequesterEmailIndex',
        KeyConditionExpression='requesterEmail = :email',
        ExpressionAttributeValues={':email': email}
    )
    
    items = response['Items']
    items.sort(key=lambda x: decimal_to_int(x.get('timestamp', 0)), reverse=True)
    
    print(f"\n{'='*120}")
    print(f"REQUESTS BY {email} - Total: {len(items)}")
    print(f"{'='*120}\n")
    
    for item in items:
        print_request(item)

def view_by_status(status):
    """View requests by status"""
    response = table.scan(
        FilterExpression='#status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': status.upper()}
    )
    
    items = response['Items']
    items.sort(key=lambda x: decimal_to_int(x.get('timestamp', 0)), reverse=True)
    
    print(f"\n{'='*120}")
    print(f"{status.upper()} REQUESTS - Total: {len(items)}")
    print(f"{'='*120}\n")
    
    for item in items:
        print_request(item)

def print_request(item):
    """Print a single request in formatted way"""
    status = item.get('status', 'UNKNOWN')
    status_emoji = {
        'PENDING': '⏳',
        'APPROVED': '✅',
        'REJECTED': '❌',
        'EXPIRED': '⏰'
    }.get(status, '❓')
    
    print(f"{status_emoji} REQUEST DETAILS")
    print(f"{'='*80}")
    
    # Request Information
    print(f"\n📋 REQUEST INFO:")
    print(f"   Request ID: {item.get('requestId')}")
    print(f"   Submitted: {format_timestamp(item.get('timestamp'))}")
    print(f"   Status: {status}")
    
    # Requester Information
    print(f"\n👤 REQUESTER:")
    print(f"   Email: {item.get('requesterEmail')}")
    
    # Instance Details
    print(f"\n💻 INSTANCE DETAILS:")
    print(f"   Name: {item.get('instanceName')}")
    print(f"   Type: {item.get('instanceType')}")
    print(f"   Subnet: {item.get('subnetId')}")
    print(f"   Security Groups: {', '.join(item.get('securityGroupIds', []))}")
    
    # Optional Configuration
    if item.get('amiId'):
        print(f"   AMI: {item.get('amiId')}")
    if item.get('ebsVolumeSize'):
        print(f"   EBS: {decimal_to_int(item.get('ebsVolumeSize'))} GB ({item.get('ebsVolumeType', 'default')})")
    if item.get('privateIpAddress'):
        print(f"   Private IP: {item.get('privateIpAddress')}")
    
    # Approval Information
    print(f"\n✍️  APPROVAL INFO:")
    print(f"   Approver Email: {item.get('approverEmail', 'N/A')}")
    if item.get('approvalTimestamp'):
        print(f"   Decision Time: {format_timestamp(item.get('approvalTimestamp'))}")
    if item.get('instanceId'):
        print(f"   Instance ID: {item.get('instanceId')}")
    
    # Technical Details
    print(f"\n🔧 TECHNICAL:")
    print(f"   Execution ARN: {item.get('executionArn', 'N/A')[:60]}...")
    
    print(f"\n{'-'*80}\n")

def main():
    parser = argparse.ArgumentParser(description='View EC2 Approval Request Logs')
    parser.add_argument('--user', help='Filter by requester email')
    parser.add_argument('--status', help='Filter by status (PENDING/APPROVED/REJECTED/EXPIRED)')
    
    args = parser.parse_args()
    
    try:
        if args.user:
            view_by_user(args.user)
        elif args.status:
            view_by_status(args.status)
        else:
            view_all_requests()
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure:")
        print("1. DynamoDB table 'EC2ApprovalRequests' exists")
        print("2. You have AWS credentials configured")
        print("3. You have permissions to read from DynamoDB")

if __name__ == '__main__':
    main()
