# WebSocket Video Streaming Authentication Updates

## Overview

The WebSocket video streaming endpoint has been updated to require JWT authentication. The authenticated user's ID is now automatically used as the client identifier, ensuring secure and personalized connections.

## Changes Made

### 1. Backend Changes (`backend/app/api/routes/streaming.py`)

#### Added Authentication Function
- Created `get_current_user_ws()` function to authenticate WebSocket connections
- Validates JWT tokens passed as query parameters
- Verifies user existence and active status
- Raises appropriate exceptions for invalid tokens or inactive users

#### Updated WebSocket Endpoint
- **Old**: `/ws/video/{client_id}` - client_id as path parameter
- **New**: `/ws/video?token=YOUR_JWT_TOKEN` - token as query parameter

#### Key Features
- Authentication happens before accepting the WebSocket connection
- User ID is automatically extracted from the JWT token
- Connection is rejected with code 1008 (Policy Violation) if authentication fails
- Connection confirmation includes user email for verification
- All functionality remains the same after authentication

#### New Imports Added
```python
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
```

### 2. Frontend Changes (`beta-frontend/app/pages/camera.py`)

#### Added Authentication UI
- JWT token input field (password-protected)
- Information banner explaining authentication requirement
- Updated WebSocket URL field (removed client_id from default)

#### Updated JavaScript Client
- Token validation before connection attempt
- Automatic URL construction with token query parameter
- User-friendly error messages for missing token
- Updated connection instructions in console log

#### Enhanced Documentation
- Step-by-step authentication instructions
- curl example for obtaining JWT token
- Updated technical details section
- Comprehensive troubleshooting guide

## Authentication Flow

```
1. User logs in → GET /api/v1/login/access-token
   ↓
2. Receives JWT access token
   ↓
3. Opens WebSocket connection with token
   ws://localhost:8000/api/v1/ws/video?token=JWT_TOKEN
   ↓
4. Server validates token
   ↓
5. Server extracts user ID from token
   ↓
6. Connection established with user ID as client_id
   ↓
7. Video streaming begins
```

## Security Benefits

1. **User Identification**: Each connection is tied to a specific authenticated user
2. **Token Validation**: JWT tokens are validated for signature, expiration, and user status
3. **Access Control**: Only active users with valid tokens can connect
4. **Audit Trail**: All connections are logged with user identification
5. **Session Management**: Token expiration naturally limits connection lifetime

## API Usage Examples

### 1. Obtain JWT Token

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your-password"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Connect to WebSocket

**JavaScript:**
```javascript
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/video?token=${encodeURIComponent(token)}`);

ws.onopen = () => {
    console.log('Connected successfully');
};

ws.onmessage = (event) => {
    if (event.data instanceof Blob) {
        // Handle video frame
        const img = document.getElementById('video-frame');
        img.src = URL.createObjectURL(event.data);
    } else {
        // Handle JSON message
        const data = JSON.parse(event.data);
        console.log('Received:', data);
    }
};
```

### 3. Connection Response

When successfully connected, the server sends:
```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "user-uuid-here",
  "user_email": "user@example.com",
  "message": "WebSocket connection established for video streaming - User: user@example.com"
}
```

## Migration Guide

### For Existing Clients

If you have existing WebSocket clients, update them as follows:

**Before:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/video/client123');
```

**After:**
```javascript
const token = await getJWTToken(); // Get token from your auth system
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/video?token=${encodeURIComponent(token)}`);
```

### Error Handling

Add proper error handling for authentication failures:

```javascript
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
    if (event.code === 1008) {
        console.error('Authentication failed. Please check your token.');
        // Redirect to login or refresh token
    }
};
```

## Testing

### Using Streamlit Interface

1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Start the Streamlit frontend:
   ```bash
   cd beta-frontend
   streamlit run app/main.py
   ```

3. Navigate to the Camera page
4. Use the API docs at `http://localhost:8000/docs` to login and get a token
5. Paste the token in the Streamlit interface
6. Click "Connect" to establish authenticated connection

### Using API Documentation

1. Go to `http://localhost:8000/docs`
2. Click "Authorize" and enter your credentials
3. Navigate to the WebSocket endpoints section
4. Use the interactive client to test the connection

## Troubleshooting

### Connection Rejected (Code 1008)
**Cause**: Invalid or expired token
**Solution**: Obtain a fresh token from the login endpoint

### "Authentication Required" Message
**Cause**: No token provided
**Solution**: Enter your JWT token before clicking "Connect"

### "Token validation failed"
**Cause**: Token format is incorrect or corrupted
**Solution**: Verify the token is complete and not truncated

### "User not found" or "Inactive user"
**Cause**: User account doesn't exist or is deactivated
**Solution**: Contact administrator to activate account

## Configuration

### Token Expiration

Token expiration is controlled in `backend/app/core/config.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Default: 60 minutes
```

### Secret Key

Ensure a secure secret key is set in your environment:
```bash
export SECRET_KEY="your-secure-secret-key-here"
```

## Backward Compatibility

⚠️ **Breaking Change**: The old endpoint `/ws/video/{client_id}` is no longer available. All clients must be updated to use the new authenticated endpoint.

## Future Enhancements

Potential improvements for consideration:

1. **Refresh Token Support**: Automatically refresh expired tokens
2. **Role-Based Access**: Different streaming capabilities based on user roles
3. **Connection Limits**: Limit simultaneous connections per user
4. **Rate Limiting**: Per-user rate limiting for frame uploads
5. **Session Recording**: Audit log of all video streaming sessions

## References

- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [JWT Authentication](https://jwt.io/)
- [OAuth2 with Password Flow](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

## Support

For issues or questions:
- Check server logs for detailed error messages
- Verify token validity using `/api/v1/login/test-token` endpoint
- Ensure user account is active in the database

