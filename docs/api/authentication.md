# Authentication API

## Overview

The Falcon Vision authentication system provides secure user management and JWT-based authentication for API access.

## Authentication Flow

### 1. User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false
}
```

### 2. User Login
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 3. Token Refresh
```http
POST /api/v1/auth/refresh
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
- `email` (string, required): User email address
- `password` (string, required): User password (min 8 characters)
- `full_name` (string, required): User's full name

**Response:**
- `201 Created`: User successfully created
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Email already exists

#### POST /api/v1/auth/login
Authenticate user and return access token.

**Request Body:**
- `username` (string, required): User email
- `password` (string, required): User password

**Response:**
- `200 OK`: Authentication successful
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Missing required fields

#### POST /api/v1/auth/logout
Logout user and invalidate token.

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
- `200 OK`: Logout successful
- `401 Unauthorized`: Invalid token

#### GET /api/v1/auth/me
Get current user information.

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### User Management Endpoints

#### GET /api/v1/users
Get list of users (admin only).

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records (default: 100)

**Response:**
```json
{
  "users": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "is_verified": true
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

#### PUT /api/v1/users/{user_id}
Update user information (admin only).

**Headers:**
- `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "is_active": true,
  "is_verified": true
}
```

**Response:**
- `200 OK`: User updated successfully
- `404 Not Found`: User not found
- `403 Forbidden`: Insufficient permissions

## Security Features

### JWT Token Configuration
- **Algorithm**: HS256
- **Expiration**: 1 hour (configurable)
- **Refresh Token**: 7 days
- **Secret Key**: Environment variable

### Password Security
- **Hashing**: bcrypt with salt rounds
- **Minimum Length**: 8 characters
- **Complexity**: Not enforced (can be configured)

### CORS Configuration
- **Allowed Origins**: Configurable
- **Allowed Methods**: GET, POST, PUT, DELETE
- **Allowed Headers**: Authorization, Content-Type
- **Credentials**: Supported

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "User not found"
}
```

## Rate Limiting

### Login Attempts
- **Max Attempts**: 5 per minute per IP
- **Lockout Duration**: 15 minutes
- **Reset**: Automatic after lockout period

### API Requests
- **Rate Limit**: 100 requests per minute per user
- **Burst Limit**: 10 requests per second
- **Headers**: Rate limit information included in response

## Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Password Hashing
PASSWORD_HASH_ROUNDS=12

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=10
```

## Testing

### Test Authentication
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"

# Get user info
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```
