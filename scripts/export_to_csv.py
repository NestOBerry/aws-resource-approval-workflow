#!/usr/bin/env python3
"""
Export EC2 Approval Requests to CSV
Usage: python3 export_to_csv.py [output_file.csv]
"""

import boto3
import csv
import sys
import os
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'EC2ApprovalRequests')
REGION = os.environ.get('AWS_REGION', 'ap-southeast-5')

dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def decimal_to_int(obj):
    """Convert Decimal to int"""
    if isinstance(obj, Decimal):
        return int(obj)
    return obj

def format_timestamp(ts):
    """Format Unix timestamp to readable date"""
    if ts:
        return datetime.fromtimestamp(decimal_to_int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    return ''

def export_to_csv(filename='ec2_requests.csv'):
    """Export all requests to CSV"""
    response = table.scan()
    items = response['Items']
    
    # Sort by timestamp (newest first)
    items.sort(key=lambda x: decimal_to_int(x.get('timestamp', 0)), reverse=True)
    
    # Define CSV columns in logical order
    fieldnames = [
        'requestId',
        'requestDate',
        'status',
        'requesterEmail',
        'instanceName',
        'instanceType',
        'subnetId',
        'securityGroupIds',
        'amiId',
        'ebsVolumeSize',
        'ebsVolumeType',
        'privateIpAddress',
        'approverEmail',
        'approvalDate',
        'instanceId',
        'executionArn'
    ]
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in items:
            row = {
                'requestId': item.get('requestId', ''),
                'requestDate': item.get('requestDate', format_timestamp(item.get('timestamp'))),
                'status': item.get('status', ''),
                'requesterEmail': item.get('requesterEmail', ''),
                'instanceName': item.get('instanceName', ''),
                'instanceType': item.get('instanceType', ''),
                'subnetId': item.get('subnetId', ''),
                'securityGroupIds': ', '.join(item.get('securityGroupIds', [])),
                'amiId': item.get('amiId', ''),
                'ebsVolumeSize': decimal_to_int(item.get('ebsVolumeSize')) if item.get('ebsVolumeSize') else '',
                'ebsVolumeType': item.get('ebsVolumeType', ''),
                'privateIpAddress': item.get('privateIpAddress', ''),
                'approverEmail': item.get('approverEmail', ''),
                'approvalDate': item.get('approvalDate', format_timestamp(item.get('approvalTimestamp'))),
                'instanceId': item.get('instanceId', ''),
                'executionArn': item.get('executionArn', '')
            }
            writer.writerow(row)
    
    print(f"✅ Exported {len(items)} requests to {filename}")
    print(f"\nColumns (in order):")
    print("1. Request Info: requestId, requestDate, status")
    print("2. Requester: requesterEmail")
    print("3. Instance: instanceName, instanceType, subnetId, securityGroupIds")
    print("4. Optional Config: amiId, ebsVolumeSize, ebsVolumeType, privateIpAddress")
    print("5. Approval: approverEmail, approvalDate, instanceId")
    print("6. Technical: executionArn")

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else 'ec2_requests.csv'
    
    try:
        export_to_csv(filename)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nMake sure:")
        print(f"1. DynamoDB table '{TABLE_NAME}' exists")
        print("2. You have AWS credentials configured")
        print("3. You have permissions to read from DynamoDB")
        print(f"\nSet DYNAMODB_TABLE environment variable if using a different table name")
