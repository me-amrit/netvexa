# NETVEXA Authentication & Authorization Guide

## Overview

The NETVEXA platform uses a dual authentication system supporting both JWT tokens for web applications and API keys for programmatic access (e.g., WordPress plugin).

## Authentication Methods

### 1. JWT Token Authentication

Used for web dashboard and interactive applications.

#### Registration
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "company_name": "My Company"
}
```

Response:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "company_name": "My Company",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=SecurePassword123!
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Using JWT Token
Include the access token in the Authorization header:
```bash
Authorization: Bearer eyJ...
```

#### Refresh Token
```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### 2. API Key Authentication

Used for WordPress plugin and other integrations.

#### Create API Key
```bash
POST /api/auth/api-keys?name=WordPress%20Plugin
Authorization: Bearer {jwt_token}
```

Response:
```json
{
  "id": "uuid",
  "name": "WordPress Plugin",
  "key": "nv_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456",
  "created_at": "2024-01-01T00:00:00"
}
```

**Important**: The API key is only shown once. Store it securely.

#### Using API Key
Include the API key in the Authorization header:
```bash
Authorization: Bearer nv_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456
```

## Protected Endpoints

All endpoints except the following require authentication:
- `GET /` (health check)
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/agents/{agent_id}/config` (public for chat widget)
- `GET /static/*` (static files)

## Agent Management

### Create Agent
```bash
POST /api/agents/
Authorization: Bearer {token_or_api_key}
Content-Type: application/json

{
  "name": "Customer Support Agent",
  "personality": {
    "tone": "professional",
    "language": "en",
    "response_style": "concise"
  },
  "welcome_message": "Hello! How can I help you today?"
}
```

### List Agents
```bash
GET /api/agents/
Authorization: Bearer {token_or_api_key}
```

### Get Agent
```bash
GET /api/agents/{agent_id}
Authorization: Bearer {token_or_api_key}
```

### Update Agent
```bash
PUT /api/agents/{agent_id}
Authorization: Bearer {token_or_api_key}
Content-Type: application/json

{
  "name": "Updated Agent Name",
  "personality": {
    "tone": "friendly"
  }
}
```

### Delete Agent
```bash
DELETE /api/agents/{agent_id}
Authorization: Bearer {token_or_api_key}
```

## Security Best Practices

1. **Password Requirements**
   - Minimum 8 characters
   - Include uppercase, lowercase, numbers, and special characters
   - Avoid common passwords

2. **Token Management**
   - Access tokens expire in 30 minutes
   - Refresh tokens expire in 7 days
   - Store tokens securely (never in localStorage for sensitive apps)

3. **API Key Security**
   - Limit API keys to specific use cases
   - Rotate keys periodically
   - Monitor usage through last_used_at timestamp
   - Maximum 5 active keys per user

4. **HTTPS Only**
   - Always use HTTPS in production
   - Never send credentials over unencrypted connections

## Testing Authentication

Use the provided test script:
```bash
cd backend
python test_auth.py
```

This will:
1. Register a test user
2. Login and get JWT tokens
3. Create an API key
4. Create an agent
5. Test both authentication methods

## WordPress Plugin Integration

The WordPress plugin uses API key authentication:

1. User creates an API key in the NETVEXA dashboard
2. User enters the API key in WordPress admin settings
3. Plugin uses the API key for all backend requests

Example WordPress request:
```php
$response = wp_remote_post($api_url . '/api/agents/', array(
    'headers' => array(
        'Authorization' => 'Bearer ' . $api_key,
        'Content-Type' => 'application/json'
    ),
    'body' => json_encode($agent_data)
));
```

## Error Handling

### Common Authentication Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 401 | Invalid credentials | Check email/password or API key |
| 403 | User account disabled | Contact support |
| 422 | Validation error | Check request format |
| 429 | Rate limited | Wait before retrying |

### Token Expiration

When an access token expires:
1. Use the refresh token to get a new access token
2. If refresh token is expired, user must login again
3. API keys don't expire but can be revoked

## Multi-Tenant Architecture

- Each user has isolated data
- Agents belong to specific users
- API keys are user-specific
- No cross-tenant data access

## Future Enhancements

1. **OAuth2 Social Login** (Phase 2)
   - Google, Microsoft, LinkedIn

2. **Two-Factor Authentication** (Phase 2)
   - TOTP support
   - SMS backup codes

3. **Role-Based Access Control** (Phase 3)
   - Team management
   - Permission levels

4. **SSO Support** (Phase 3)
   - SAML 2.0
   - OpenID Connect