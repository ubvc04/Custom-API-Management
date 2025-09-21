# API Documentation

## Base URL
```
Production: https://your-domain.com
Development: http://localhost:5000
```

## Authentication

All API endpoints require authentication via API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: YOUR_API_KEY" https://your-domain.com/api/endpoint
```

## Rate Limits

- **Default**: 1000 requests per minute per API key
- **Authentication endpoints**: 10 requests per minute per IP
- **Rate limit headers** are included in all responses:
  ```
  X-RateLimit-Limit: 1000
  X-RateLimit-Remaining: 999
  X-RateLimit-Reset: 1640995200
  ```

## Response Format

All API responses follow this format:

### Success Response
```json
{
  "success": true,
  "message": "Request successful",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized (Invalid API Key) |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## Endpoints

### 1. API Status

Check if the API is operational.

**Endpoint:** `GET /api/status`

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "API is operational",
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 2. Test Endpoint

Simple test endpoint to verify API key authentication.

**Endpoint:** `GET /api/test`

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "API test successful",
  "data": {
    "timestamp": "2024-01-01T12:00:00Z",
    "api_key_valid": true
  }
}
```

### 3. User Information

Get information about the authenticated user.

**Endpoint:** `GET /api/user_info`

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "User information retrieved",
  "data": {
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T10:00:00Z",
    "api_keys_count": 3,
    "total_requests": 1250
  }
}
```

### 4. Sample Data

Get sample data for testing purposes.

**Endpoint:** `GET /api/data`

**Authentication:** Required

**Response:**
```json
{
  "success": true,
  "message": "Sample data retrieved",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Sample Item 1",
        "value": 100,
        "category": "electronics"
      },
      {
        "id": 2,
        "name": "Sample Item 2",
        "value": 250,
        "category": "books"
      }
    ],
    "total": 2
  }
}
```

### 5. Weather Data

Get sample weather data.

**Endpoint:** `GET /api/weather`

**Query Parameters:**
- `city` (optional): City name for weather data

**Authentication:** Required

**Example Request:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://your-domain.com/api/weather?city=London"
```

**Response:**
```json
{
  "success": true,
  "message": "Weather data retrieved",
  "data": {
    "city": "London",
    "temperature": 15,
    "humidity": 65,
    "description": "Partly cloudy",
    "wind_speed": 10,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 6. Random Quotes

Get random inspirational quotes.

**Endpoint:** `GET /api/quotes`

**Query Parameters:**
- `count` (optional): Number of quotes to return (default: 1, max: 10)

**Authentication:** Required

**Example Request:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://your-domain.com/api/quotes?count=3"
```

**Response:**
```json
{
  "success": true,
  "message": "Quotes retrieved",
  "data": {
    "quotes": [
      {
        "text": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs"
      },
      {
        "text": "Innovation distinguishes between a leader and a follower.",
        "author": "Steve Jobs"
      }
    ],
    "count": 2
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_API_KEY` | API key is invalid or expired |
| `API_KEY_INACTIVE` | API key is not active |
| `API_KEY_EXPIRED` | API key has expired |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INVALID_REQUEST` | Request format is invalid |
| `MISSING_PARAMETER` | Required parameter is missing |
| `INTERNAL_ERROR` | Server error occurred |

## Example Usage

### Python
```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://your-domain.com"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Test API connection
response = requests.get(f"{BASE_URL}/api/test", headers=headers)
print(response.json())

# Get user information
response = requests.get(f"{BASE_URL}/api/user_info", headers=headers)
user_data = response.json()["data"]
print(f"Username: {user_data['username']}")

# Get weather data
response = requests.get(
    f"{BASE_URL}/api/weather", 
    headers=headers,
    params={"city": "New York"}
)
weather = response.json()["data"]
print(f"Temperature in {weather['city']}: {weather['temperature']}°C")
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://your-domain.com';

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  }
});

// Test API connection
async function testAPI() {
  try {
    const response = await client.get('/api/test');
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

// Get sample data
async function getData() {
  try {
    const response = await client.get('/api/data');
    const items = response.data.data.items;
    console.log(`Retrieved ${items.length} items`);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}

testAPI();
getData();
```

### cURL Examples

**Test Connection:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     https://your-domain.com/api/test
```

**Get User Info:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     https://your-domain.com/api/user_info
```

**Get Weather Data:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://your-domain.com/api/weather?city=Tokyo"
```

**Get Multiple Quotes:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
     "https://your-domain.com/api/quotes?count=5"
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Per API Key**: 1000 requests per minute
- **Per IP (authentication)**: 10 requests per minute
- **Headers included in response**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining in current window
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

### Handling Rate Limits

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response:

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

**Best Practices:**
- Implement exponential backoff
- Cache responses when possible
- Monitor rate limit headers
- Use multiple API keys for higher throughput

## Security

### API Key Security
- Store API keys securely (environment variables, secrets manager)
- Never expose API keys in client-side code
- Regenerate keys regularly
- Use different keys for different environments

### Request Security
- Always use HTTPS in production
- Validate all input parameters
- Monitor for unusual usage patterns
- Implement request signing for sensitive operations

## WebHooks (Future Feature)

Coming soon: WebHook support for real-time notifications.

## SDK Libraries

Official SDK libraries coming soon for:
- Python
- Node.js
- PHP
- Java
- Go

## Support

For API support:
- Check the status page: `/api/status`
- Review rate limit headers
- Check authentication credentials
- Verify endpoint URLs

For technical issues, contact support or open an issue in the repository.

## Changelog

### Version 1.0.0
- Initial API release
- Basic authentication endpoints
- Sample data endpoints
- Rate limiting implementation
- Comprehensive error handling