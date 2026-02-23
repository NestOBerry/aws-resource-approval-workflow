# DynamoDB Request Logging

## Table: EC2ApprovalRequests

Stores all EC2 provisioning requests with their lifecycle status.

### Schema

**Primary Key:**
- `requestId` (String) - Unique identifier (UUID)

**Attributes:**
- `timestamp` (Number) - Unix timestamp
- `requesterEmail` (String) - Email of requester
- `approverEmail` (String) - Email of approver
- `instanceName` (String) - Name of EC2 instance
- `instanceType` (String) - EC2 instance type
- `subnetId` (String) - VPC subnet ID
- `securityGroupIds` (List) - Security group IDs
- `amiId` (String) - AMI ID (null if auto-resolved)
- `ebsVolumeSize` (Number) - EBS volume size in GB (null if default)
- `ebsVolumeType` (String) - EBS volume type (null if default)
- `privateIpAddress` (String) - Private IP (null if auto-assigned)
- `status` (String) - Current status: PENDING | APPROVED | REJECTED | EXPIRED
- `executionArn` (String) - Step Functions execution ARN
- `instanceId` (String) - EC2 instance ID (after approval)
- `resolvedAmiId` (String) - Actual AMI used (after resolution)
- `approvalTimestamp` (Number) - When approved/rejected
- `expirationTime` (Number) - TTL for auto-cleanup (optional)

**Global Secondary Index:**
- `RequesterEmailIndex` - Query by requester email + timestamp

### Create Table

```bash
aws dynamodb create-table --cli-input-json file://dynamodb/table-definition.json
```

Or use the AWS Console (see STEP_BY_STEP_DEPLOYMENT.md)

### Query Examples

**Get all requests by a user:**
```bash
aws dynamodb query \
  --table-name EC2ApprovalRequests \
  --index-name RequesterEmailIndex \
  --key-condition-expression "requesterEmail = :email" \
  --expression-attribute-values '{":email":{"S":"user@example.com"}}'
```

**Get request by ID:**
```bash
aws dynamodb get-item \
  --table-name EC2ApprovalRequests \
  --key '{"requestId":{"S":"YOUR_REQUEST_ID"}}'
```

**Scan all pending requests:**
```bash
aws dynamodb scan \
  --table-name EC2ApprovalRequests \
  --filter-expression "status = :status" \
  --expression-attribute-values '{":status":{"S":"PENDING"}}'
```
