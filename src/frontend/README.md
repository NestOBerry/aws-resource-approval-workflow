# Frontend - EC2 Request Portal

Simple, responsive web interface for submitting EC2 provisioning requests.

## Files

- `index.html`: Main HTML structure
- `app.js`: Form handling and API integration
- `styles.css`: Responsive styling

## Configuration

Update `API_CONFIG.endpoint` in `app.js` with your API Gateway URL.

## Features

- Form validation
- Optional fields (AMI, EBS, Private IP)
- Error handling
- Success/error messages
- Extensible for Cognito authentication (see ../CUSTOMIZATION.md)

## Local Testing

```bash
python3 -m http.server 8000
```

Open http://localhost:8000

## Deployment

Upload to S3 bucket with static website hosting enabled.
Recommended: Use CloudFront for HTTPS and caching.
