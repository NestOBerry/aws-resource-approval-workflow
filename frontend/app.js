// Configuration - Update this with your API Gateway endpoint
const API_CONFIG = {
    endpoint: 'https://YOUR_API_GATEWAY_ID.execute-api.ap-southeast-5.amazonaws.com/request',
    getHeaders: () => {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // TODO: Add Cognito JWT token when authentication is implemented
        // const token = localStorage.getItem('idToken');
        // if (token) {
        //     headers['Authorization'] = `Bearer ${token}`;
        // }
        
        return headers;
    }
};

// Form submission handler
document.getElementById('ec2RequestForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const responseMessage = document.getElementById('responseMessage');
    
    // Disable submit button
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    // Clear previous messages
    responseMessage.className = 'response-message';
    responseMessage.style.display = 'none';
    
    try {
        // Gather form data
        const ebsVolumeSizeValue = document.getElementById('ebsVolumeSize').value.trim();
        const ebsVolumeTypeValue = document.getElementById('ebsVolumeType').value.trim();
        const privateIpValue = document.getElementById('privateIpAddress').value.trim();
        
        const formData = {
            requesterEmail: document.getElementById('requesterEmail').value.trim(),
            approverEmail: document.getElementById('approverEmail').value.trim(),
            instanceName: document.getElementById('instanceName').value.trim(),
            instanceType: document.getElementById('instanceType').value,
            ebsVolumeSize: ebsVolumeSizeValue ? parseInt(ebsVolumeSizeValue) : null,
            ebsVolumeType: ebsVolumeTypeValue || null,
            privateIpAddress: privateIpValue || null,
            subnetId: document.getElementById('subnetId').value.trim(),
            securityGroupIds: document.getElementById('securityGroupIds').value
                .split(',')
                .map(id => id.trim())
                .filter(id => id.length > 0),
            amiId: document.getElementById('amiId').value.trim() || null
        };
        
        // Validate security group IDs
        if (formData.securityGroupIds.length === 0) {
            throw new Error('At least one security group ID is required');
        }
        
        // Validate IP address format (only if provided)
        if (formData.privateIpAddress && !isValidIPAddress(formData.privateIpAddress)) {
            throw new Error('Invalid IP address format');
        }
        
        console.log('Submitting request:', formData);
        
        // Make API call
        const response = await fetch(API_CONFIG.endpoint, {
            method: 'POST',
            headers: API_CONFIG.getHeaders(),
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('success', `
                ✅ Request submitted successfully!<br>
                <strong>Execution ARN:</strong> ${result.executionArn || 'N/A'}<br>
                An approval email has been sent to the approver.
            `);
            
            // Don't auto-reset form - let user see the success message
            // User can manually click "Clear Form" button if needed
        } else {
            throw new Error(result.message || 'Failed to submit request');
        }
        
    } catch (error) {
        console.error('Error submitting request:', error);
        showMessage('error', `
            ❌ Error: ${error.message}<br>
            Please check your input and try again.
        `);
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Request';
    }
});

// Helper function to validate IP address
function isValidIPAddress(ip) {
    const pattern = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return pattern.test(ip);
}

// Helper function to show messages
function showMessage(type, message) {
    const responseMessage = document.getElementById('responseMessage');
    responseMessage.className = `response-message ${type}`;
    responseMessage.innerHTML = message;
    responseMessage.style.display = 'block';
    
    // Scroll to message
    responseMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Form reset handler
document.getElementById('ec2RequestForm').addEventListener('reset', () => {
    const responseMessage = document.getElementById('responseMessage');
    responseMessage.className = 'response-message';
    responseMessage.style.display = 'none';
});

// TODO: Cognito Authentication Integration
// This section will be implemented when Cognito is ready
/*
async function initializeCognito() {
    // Initialize AWS Cognito
    // Check if user is already logged in
    // Show login/logout UI
}

async function login(username, password) {
    // Authenticate with Cognito
    // Store JWT tokens in localStorage
    // Update UI
}

async function logout() {
    // Clear tokens
    // Redirect to login
}

// Call on page load
// initializeCognito();
*/
