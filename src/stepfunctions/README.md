# Step Functions State Machine

## EC2ApprovalDemo

Orchestrates the EC2 approval workflow with the following states:

1. **ResolveAMI**: Fetches latest AL2023 AMI or uses provided AMI
2. **SendApprovalEmailAndWait**: Sends email and waits for callback (4h timeout)
3. **LaunchEC2**: Provisions EC2 instance with specified parameters
4. **NotifyRequesterApproved**: Sends success notification
5. **NotifyRequesterRejected**: Sends rejection notification
6. **NotifyRequesterExpired**: Sends timeout notification

## Error Handling

- `RejectedByApprover`: Caught and routes to rejection notification
- `States.Timeout`: Caught after 4 hours and routes to expiration notification

## Deployment

Use `EC2ApprovalDemo-UPDATED.json` for the latest version with all features.
