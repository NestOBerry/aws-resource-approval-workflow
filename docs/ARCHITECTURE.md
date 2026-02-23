# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER WORKFLOW                                   │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐         ┌─────────────┐         ┌──────────────────┐
    │  User    │────────▶│  Frontend   │────────▶│   API Gateway    │
    │          │         │  (S3/Web)   │         │   (HTTP API)     │
    └──────────┘         └─────────────┘         └────────┬─────────┘
                                                          │
                                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAMBDA FUNCTIONS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │ RequestStarter  │    │ ApprovalHandler │    │ UpdateRequest   │        │
│   │                 │    │                 │    │ Status          │        │
│   │ • Receives      │    │ • Handles       │    │ • Updates       │        │
│   │   requests      │    │   approve/      │    │   DynamoDB      │        │
│   │ • Logs to       │    │   reject        │    │   status        │        │
│   │   DynamoDB      │    │ • Sends task    │    │                 │        │
│   │ • Starts        │    │   token         │    │                 │        │
│   │   workflow      │    │                 │    │                 │        │
│   └────────┬────────┘    └─────────────────┘    └─────────────────┘        │
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │                    STEP FUNCTIONS                                │      │
│   │                                                                  │      │
│   │   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐  │      │
│   │   │ SendApproval  │───▶│   LaunchEC2   │───▶│ SendRequester │  │      │
│   │   │ Email         │    │               │    │ Notification  │  │      │
│   │   │               │    │ • Creates     │    │               │  │      │
│   │   │ • Sends email │    │   EC2         │    │ • Notifies    │  │      │
│   │   │ • Waits for   │    │   instance    │    │   requester   │  │      │
│   │   │   approval    │    │               │    │   of result   │  │      │
│   │   └───────────────┘    └───────────────┘    └───────────────┘  │      │
│   │                                                                  │      │
│   │   Error Paths: Rejected ──▶ NotifyRejected                      │      │
│   │                Timeout  ──▶ NotifyExpired                       │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA STORES                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐              ┌─────────────────┐                      │
│   │    DynamoDB     │              │      SES        │                      │
│   │                 │              │                 │                      │
│   │ • Request logs  │              │ • Approval      │                      │
│   │ • Status        │              │   emails        │                      │
│   │ • Audit trail   │              │ • Notification  │                      │
│   │                 │              │   emails        │                      │
│   └─────────────────┘              └─────────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (S3)
- Static HTML/CSS/JavaScript
- Hosted on S3 with static website hosting
- Optional: CloudFront for HTTPS

### API Gateway
- HTTP API (not REST API)
- Two routes:
  - `POST /request` - Submit new request
  - `GET /approval` - Handle approve/reject clicks
- CORS enabled

### Lambda Functions

| Function | Trigger | Purpose |
|----------|---------|---------|
| RequestStarter | API Gateway POST | Receives requests, logs to DynamoDB, starts Step Functions |
| SendApprovalEmail | Step Functions | Sends approval email with approve/reject links |
| ApprovalHandler | API Gateway GET | Handles approve/reject clicks, sends task token |
| LaunchEC2 | Step Functions | Launches EC2 instance with specified configuration |
| SendRequesterNotification | Step Functions | Notifies requester of decision |
| UpdateRequestStatus | Step Functions | Updates DynamoDB with final status |

### Step Functions
- Orchestrates the approval workflow
- Uses `waitForTaskToken` for human approval
- 4-hour timeout for approval
- Handles: Approved, Rejected, Expired paths

### DynamoDB
- Table: `EC2ApprovalRequests`
- Primary Key: `requestId` (String)
- GSI: `RequesterEmailIndex` (requesterEmail + timestamp)
- Stores complete audit trail

### SES (Simple Email Service)
- Sends approval request emails
- Sends notification emails
- Requires verified email addresses

## Data Flow

### Request Submission
1. User fills form on frontend
2. Frontend POSTs to API Gateway
3. RequestStarter Lambda:
   - Generates unique requestId
   - Logs to DynamoDB (status: PENDING)
   - Starts Step Functions execution
4. Step Functions invokes SendApprovalEmail
5. Approver receives email with links

### Approval Flow
1. Approver clicks Approve/Reject link
2. API Gateway routes to ApprovalHandler
3. ApprovalHandler sends task token to Step Functions
4. Step Functions continues:
   - If Approved: LaunchEC2 → SendNotification → UpdateStatus
   - If Rejected: SendNotification → UpdateStatus
5. DynamoDB updated with final status

### Timeout Flow
1. No response within 4 hours
2. Step Functions catches timeout
3. SendNotification (EXPIRED) → UpdateStatus
4. DynamoDB updated with EXPIRED status

## Security

- IAM roles follow least privilege principle
- Each Lambda has specific permissions only
- No hardcoded credentials
- CORS configured for frontend domain
- SES requires verified email addresses
