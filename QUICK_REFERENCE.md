# Quick Reference Guide

## Deployment Checklist

### ✅ Core Workflow (Already Done)
- [x] Lambda: RequestStarter
- [x] Lambda: SendApprovalEmail
- [x] Lambda: SendRequesterNotification
- [x] Lambda: LaunchEC2
- [x] Lambda: ApprovalHandler
- [x] Step Functions: EC2ApprovalDemo
- [x] API Gateway: HTTP API with CORS
- [x] Frontend: Running locally on port 8080

### 🔄 Next Steps

#### 1. Deploy DynamoDB Logging
- [ ] Create DynamoDB table `EC2ApprovalRequests`
- [ ] Add DynamoDB permissions to Lambda roles
- [ ] Add environment variable `DYNAMODB_TABLE` to RequestStarter
- [ ] Create UpdateRequestStatus Lambda (optional)
- [ ] Test logging

#### 2. Host Frontend on AWS
- [ ] Create S3 bucket
- [ ] Enable static website hosting
- [ ] Add bucket policy for public access
- [ ] Upload frontend files (index.html, app.js, styles.css)
- [ ] Test hosted website
- [ ] (Optional) Add CloudFront for HTTPS

---

## Important URLs & Resources

### API Endpoints
- **API Gateway**: https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com
- **Request Endpoint**: https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com/request
- **Approval Endpoint**: https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com/approval

### Local Development
- **Frontend**: http://localhost:8080

### AWS Resources
- **Region**: ap-southeast-5
- **Golden AMI**: ami-077dbbb6eecc8ae69 (Amazon Linux 2023)
- **DynamoDB Table**: EC2ApprovalRequests
- **Step Functions**: EC2ApprovalDemo

---

## Lambda Functions Summary

| Function | Purpose | Permissions Needed |
|----------|---------|-------------------|
| RequestStarter | Receives requests, starts workflow | Step Functions, DynamoDB |
| SendApprovalEmail | Sends approval email | SES |
| SendRequesterNotification | Notifies requester | SES |
| LaunchEC2 | Launches EC2 instance | EC2 (RunInstances, CreateTags) |
| ApprovalHandler | Handles approve/reject clicks | Step Functions |
| UpdateRequestStatus | Updates DynamoDB status | DynamoDB |

---

## View DynamoDB Logs

### Using Python Script
```bash
# View all requests
python3 scripts/view_dynamodb_logs.py

# View requests by user
python3 scripts/view_dynamodb_logs.py --user user@example.com

# View pending requests
python3 scripts/view_dynamodb_logs.py --status PENDING
```

### Using AWS Console
1. Go to DynamoDB Console
2. Click `EC2ApprovalRequests` table
3. Click "Explore table items"

### Using AWS CLI
```bash
# All requests
aws dynamodb scan --table-name EC2ApprovalRequests --region ap-southeast-5

# Specific request
aws dynamodb get-item \
  --table-name EC2ApprovalRequests \
  --key '{"requestId":{"S":"REQUEST_ID"}}' \
  --region ap-southeast-5

# By user
aws dynamodb query \
  --table-name EC2ApprovalRequests \
  --index-name RequesterEmailIndex \
  --key-condition-expression "requesterEmail = :email" \
  --expression-attribute-values '{":email":{"S":"user@example.com"}}' \
  --region ap-southeast-5
```

---

## Testing Workflow

### 1. Submit Request
```bash
curl -X POST https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com/request \
  -H "Content-Type: application/json" \
  -d '{
    "requesterEmail": "your@email.com",
    "instanceName": "test-instance",
    "instanceType": "t3.micro",
    "subnetId": "subnet-YOUR_SUBNET",
    "securityGroupIds": ["sg-YOUR_SG"]
  }'
```

### 2. Check Email
- Approver receives email with approve/reject links

### 3. Click Approve
- Instance launches automatically
- Requester receives notification with instance ID

### 4. Verify in AWS
- Check EC2 Console for new instance
- Check DynamoDB for logged request
- Check Step Functions execution

---

## Troubleshooting

### Frontend Issues
- **CORS Error**: Check API Gateway CORS settings
- **Form not submitting**: Check browser console for errors
- **API endpoint wrong**: Update `app.js` with correct endpoint

### Lambda Issues
- **Permission denied**: Check IAM role permissions
- **Timeout**: Increase Lambda timeout in Configuration
- **Environment variable missing**: Add required env vars

### Step Functions Issues
- **Task token error**: Use `$$.Task.Token` (double $$)
- **JSON serialization error**: Return only serializable data from Lambda
- **Execution failed**: Check CloudWatch Logs for each Lambda

### DynamoDB Issues
- **Access denied**: Add DynamoDB permissions to Lambda role
- **Table not found**: Create table first
- **No data**: Check if RequestStarter has DYNAMODB_TABLE env var

---

## File Structure

```
aws-ec2-approval-workflow/
├── frontend/
│   ├── index.html          # Web form
│   ├── app.js              # Frontend logic
│   └── styles.css          # Styling
├── lambda/
│   ├── RequestStarter.py
│   ├── SendApprovalEmail.py
│   ├── SendRequesterNotification.py
│   ├── LaunchEC2.py
│   ├── ApprovalHandler.py
│   └── UpdateRequestStatus.py
├── stepfunctions/
│   └── EC2ApprovalDemo-SIMPLE.json
├── dynamodb/
│   ├── table-definition.json
│   └── README.md
├── scripts/
│   └── view_dynamodb_logs.py
└── FINAL_DEPLOYMENT_GUIDE.md  # Complete deployment steps
```

---

## Next Enhancements

### Phase 1 (Current)
- ✅ Basic approval workflow
- ✅ Email notifications
- ✅ Optional EBS and Private IP
- 🔄 DynamoDB logging
- 🔄 S3 hosted frontend

### Phase 2 (Future)
- [ ] Cognito authentication
- [ ] Multiple instance types
- [ ] Windows OS support (different AMI)
- [ ] RDS provisioning
- [ ] S3 bucket provisioning
- [ ] Cost estimation before approval
- [ ] Slack/Teams notifications
- [ ] Admin dashboard

---

## Support

For detailed deployment steps, see:
- `FINAL_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `DYNAMODB_SETUP.md` - DynamoDB setup details
- `TESTING.md` - Testing procedures
