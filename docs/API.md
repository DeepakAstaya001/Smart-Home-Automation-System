# Smart Home Automation API Documentation

## Overview

The Smart Home API provides comprehensive control over all system components including devices, security, energy management, and user administration. The API follows RESTful principles and supports both HTTP requests and real-time WebSocket connections.

## Base URL

```
Production: https://api.smarthome-system.com/v1
Development: http://localhost:3000/api/v1
```

## Authentication

### API Key Authentication

Include your API key in the header:

```http
Authorization: Bearer your-api-key-here
Content-Type: application/json
```

### JWT Authentication

For user-specific operations:

```http
Authorization: Bearer your-jwt-token
Content-Type: application/json
```

## Device Management

### Get All Devices

```http
GET /devices
```

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "id": "living_room_light_1",
      "name": "Living Room Main Light",
      "type": "light",
      "room": "living_room",
      "status": "on",
      "properties": {
        "brightness": 80,
        "color": "#ffffff",
        "power_consumption": 60
      },
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Control Device

```http
POST /devices/{device_id}/control
```

**Request Body:**
```json
{
  "action": "turn_on",
  "properties": {
    "brightness": 70,
    "color": "#ff0000"
  }
}
```

**Response:**
```json
{
  "success": true,
  "device_id": "living_room_light_1",
  "status": "on",
  "message": "Device controlled successfully"
}
```

### Get Device Status

```http
GET /devices/{device_id}/status
```

### Update Device Settings

```http
PUT /devices/{device_id}/settings
```

## Room Management

### Get All Rooms

```http
GET /rooms
```

### Control Room Devices

```http
POST /rooms/{room_id}/control
```

**Request Body:**
```json
{
  "action": "turn_off_all_lights",
  "scene": "movie_mode"
}
```

## Security System

### Get Security Status

```http
GET /security/status
```

**Response:**
```json
{
  "success": true,
  "system_status": "armed",
  "cameras": [
    {
      "id": "front_door_cam",
      "status": "online",
      "recording": true,
      "motion_detected": false
    }
  ],
  "sensors": [
    {
      "id": "front_door_sensor",
      "type": "door",
      "status": "closed"
    }
  ],
  "alerts": []
}
```

### Arm/Disarm Security

```http
POST /security/arm
POST /security/disarm
```

**Request Body:**
```json
{
  "mode": "away",
  "user_id": "user123",
  "pin": "1234"
}
```

### Get Security Events

```http
GET /security/events?limit=50&offset=0
```

### Camera Controls

```http
GET /security/cameras
GET /security/cameras/{camera_id}/stream
POST /security/cameras/{camera_id}/record
```

## Energy Management

### Get Energy Consumption

```http
GET /energy/consumption?period=day&room=living_room
```

**Response:**
```json
{
  "success": true,
  "period": "day",
  "total_consumption": 25.6,
  "cost": 3.84,
  "devices": [
    {
      "device_id": "living_room_light_1",
      "consumption": 1.44,
      "percentage": 5.6
    }
  ],
  "hourly_data": [
    {
      "hour": "00:00",
      "consumption": 0.8,
      "cost": 0.12
    }
  ]
}
```

### Get Energy Reports

```http
GET /energy/reports?type=monthly
```

### Energy Optimization

```http
POST /energy/optimize
```

**Request Body:**
```json
{
  "target_reduction": 20,
  "priority_devices": ["ac", "heating"],
  "exclude_devices": ["security_system"]
}
```

### Energy Predictions

```http
GET /energy/predictions?days=7
```

## Voice Control

### Process Voice Command

```http
POST /voice/command
```

**Request Body:**
```json
{
  "command": "turn on living room lights",
  "language": "en",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "success": true,
  "interpreted_command": "turn_on_lights",
  "target_devices": ["living_room_light_1"],
  "response": "Living room lights turned on",
  "confidence": 0.95
}
```

### Get Voice Commands History

```http
GET /voice/history?user_id=user123&limit=20
```

### Add Custom Voice Command

```http
POST /voice/commands/custom
```

## User Management

### User Registration

```http
POST /users/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "role": "family"
}
```

### User Authentication

```http
POST /users/login
```

### Get User Profile

```http
GET /users/profile
```

### Update User Settings

```http
PUT /users/settings
```

## Automation & Scenes

### Get All Scenes

```http
GET /scenes
```

### Create Scene

```http
POST /scenes
```

**Request Body:**
```json
{
  "name": "Movie Night",
  "description": "Dim lights and close curtains",
  "actions": [
    {
      "device_id": "living_room_light_1",
      "action": "set_brightness",
      "value": 20
    },
    {
      "device_id": "curtains_motor",
      "action": "close"
    }
  ]
}
```

### Activate Scene

```http
POST /scenes/{scene_id}/activate
```

### Get Automation Rules

```http
GET /automation/rules
```

### Create Automation Rule

```http
POST /automation/rules
```

## System Management

### Get System Status

```http
GET /system/status
```

**Response:**
```json
{
  "success": true,
  "status": "online",
  "uptime": 86400,
  "version": "1.0.0",
  "components": {
    "database": "connected",
    "mqtt": "connected",
    "voice_service": "running",
    "security_service": "running",
    "energy_service": "running"
  },
  "statistics": {
    "total_devices": 25,
    "active_devices": 18,
    "total_users": 4,
    "active_sessions": 2
  }
}
```

### System Configuration

```http
GET /system/config
PUT /system/config
```

### System Logs

```http
GET /system/logs?level=error&limit=100
```

## WebSocket Events

### Connection

```javascript
const socket = io('http://localhost:3000');

socket.on('connect', () => {
  console.log('Connected to Smart Home System');
});
```

### Device Status Updates

```javascript
socket.on('device_status_changed', (data) => {
  console.log('Device Update:', {
    device_id: data.device_id,
    status: data.status,
    properties: data.properties,
    timestamp: data.timestamp
  });
});
```

### Security Alerts

```javascript
socket.on('security_alert', (data) => {
  console.log('Security Alert:', {
    type: data.type,
    severity: data.severity,
    location: data.location,
    description: data.description,
    timestamp: data.timestamp
  });
});
```

### Energy Updates

```javascript
socket.on('energy_update', (data) => {
  console.log('Energy Update:', {
    current_usage: data.current_usage,
    cost_per_hour: data.cost_per_hour,
    prediction: data.prediction
  });
});
```

### Voice Command Results

```javascript
socket.on('voice_command_processed', (data) => {
  console.log('Voice Command:', {
    command: data.command,
    result: data.result,
    devices_affected: data.devices_affected
  });
});
```

## MQTT Topics

### Device Control

```
# Send commands
smarthome/devices/{room}/{device}/command

# Receive status updates
smarthome/devices/{room}/{device}/status

# Example
smarthome/devices/living_room/light_1/command
```

**Payload Example:**
```json
{
  "action": "turn_on",
  "properties": {
    "brightness": 80
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Security Events

```
smarthome/security/alerts
smarthome/security/cameras/{camera_id}/motion
smarthome/security/sensors/{sensor_id}/triggered
smarthome/security/access/door/{door_id}
```

### Energy Management

```
smarthome/energy/consumption
smarthome/energy/optimization/result
smarthome/energy/alerts/peak_usage
```

### System Events

```
smarthome/system/status
smarthome/system/errors
smarthome/system/maintenance
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Rate Limited
- `500` - Internal Server Error

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "The specified device was not found",
    "details": {
      "device_id": "invalid_device_123"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

- `INVALID_API_KEY` - API key is missing or invalid
- `DEVICE_NOT_FOUND` - Device ID does not exist
- `DEVICE_OFFLINE` - Device is not responding
- `INVALID_COMMAND` - Command not supported by device
- `SECURITY_VIOLATION` - Unauthorized access attempt
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `SYSTEM_MAINTENANCE` - System is under maintenance

## Rate Limiting

### Limits

- **Free Tier**: 1000 requests/hour
- **Pro Tier**: 10000 requests/hour
- **Enterprise**: Unlimited

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## SDK Examples

### Python SDK

```python
from smarthome_sdk import SmartHomeClient

client = SmartHomeClient(api_key='your-api-key')

# Control device
result = client.devices.control('living_room_light_1', {
    'action': 'turn_on',
    'brightness': 80
})

# Get energy consumption
consumption = client.energy.get_consumption(period='day')

# Arm security system
client.security.arm(mode='away', pin='1234')
```

### JavaScript SDK

```javascript
import { SmartHomeClient } from 'smarthome-sdk';

const client = new SmartHomeClient({
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:3000/api/v1'
});

// Control device
const result = await client.devices.control('living_room_light_1', {
  action: 'turn_on',
  brightness: 80
});

// Listen for real-time updates
client.on('device_status_changed', (data) => {
  console.log('Device updated:', data);
});
```

### Flutter/Dart SDK

```dart
import 'package:smarthome_sdk/smarthome_sdk.dart';

final client = SmartHomeClient(
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:3000/api/v1',
);

// Control device
final result = await client.devices.control(
  'living_room_light_1',
  DeviceCommand(
    action: 'turn_on',
    properties: {'brightness': 80},
  ),
);

// Get security status
final securityStatus = await client.security.getStatus();
```

## Testing

### API Testing with curl

```bash
# Get all devices
curl -X GET "http://localhost:3000/api/v1/devices" \
  -H "Authorization: Bearer your-api-key"

# Control device
curl -X POST "http://localhost:3000/api/v1/devices/living_room_light_1/control" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"action":"turn_on","properties":{"brightness":80}}'

# Get energy consumption
curl -X GET "http://localhost:3000/api/v1/energy/consumption?period=day" \
  -H "Authorization: Bearer your-api-key"
```

### Postman Collection

A complete Postman collection is available at:
`docs/postman/SmartHome_API.postman_collection.json`

## Webhooks

### Setting Up Webhooks

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["device_status_changed", "security_alert"],
  "secret": "webhook_secret"
}
```

### Webhook Payload

```json
{
  "event": "security_alert",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "type": "motion_detected",
    "camera_id": "front_door_cam",
    "confidence": 0.95
  },
  "signature": "sha256=..."
}
```

## API Versioning

The API uses URL versioning:

- `/api/v1/` - Current stable version
- `/api/v2/` - Next version (when available)

### Deprecation Policy

- 6 months notice before deprecation
- Backward compatibility maintained
- Migration guides provided

## Support

### Documentation

- **API Reference**: https://docs.smarthome-system.com/api
- **SDK Documentation**: https://docs.smarthome-system.com/sdk
- **Tutorials**: https://docs.smarthome-system.com/tutorials

### Community

- **GitHub Issues**: https://github.com/yourusername/advanced-smart-home/issues
- **Discord**: https://discord.gg/smarthome
- **Forum**: https://forum.smarthome-system.com

### Professional Support

- **Email**: api-support@smarthome-system.com
- **Priority Support**: Available for Enterprise customers
- **Custom Integration**: Professional services available