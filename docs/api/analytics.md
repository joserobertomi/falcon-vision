# Analytics API

## Overview

The Analytics API provides comprehensive data analysis and reporting capabilities for person detection metrics, user activity, and system performance.

## Analytics Endpoints

### GET /api/v1/analytics/overview
Get high-level analytics overview.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `start_date` (string, optional): Start date filter (ISO format)
- `end_date` (string, optional): End date filter (ISO format)
- `user_id` (string, optional): Filter by specific user (admin only)

**Response:**
```json
{
  "summary": {
    "total_detections": 15420,
    "unique_users": 25,
    "active_sessions": 8,
    "average_detection_confidence": 0.87,
    "detection_accuracy": 0.92
  },
  "time_range": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z",
    "period_days": 31
  },
  "trends": {
    "detections_trend": "+15.3%",
    "users_trend": "+8.7%",
    "accuracy_trend": "+2.1%"
  },
  "top_metrics": {
    "peak_detection_hour": 14,
    "most_active_user": "user-uuid",
    "highest_confidence_detection": 0.99
  }
}
```

### GET /api/v1/analytics/detections
Get detailed detection analytics.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `start_date` (string, optional): Start date filter
- `end_date` (string, optional): End date filter
- `group_by` (string, optional): Group by period (hour, day, week, month)
- `user_id` (string, optional): Filter by user
- `confidence_min` (float, optional): Minimum confidence threshold
- `confidence_max` (float, optional): Maximum confidence threshold

**Response:**
```json
{
  "time_series": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "detections": 45,
      "unique_persons": 12,
      "average_confidence": 0.89,
      "processing_time_avg": 0.15
    }
  ],
  "confidence_distribution": {
    "0.9-1.0": 1250,
    "0.8-0.9": 3200,
    "0.7-0.8": 1800,
    "0.6-0.7": 900,
    "0.5-0.6": 500
  },
  "hourly_patterns": {
    "00": 25,
    "01": 15,
    "02": 10,
    "12": 85,
    "13": 95,
    "14": 120,
    "15": 110
  },
  "daily_patterns": {
    "monday": 450,
    "tuesday": 520,
    "wednesday": 480,
    "thursday": 510,
    "friday": 580,
    "saturday": 320,
    "sunday": 280
  }
}
```

### GET /api/v1/analytics/users
Get user activity analytics.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `start_date` (string, optional): Start date filter
- `end_date` (string, optional): End date filter
- `group_by` (string, optional): Group by period

**Response:**
```json
{
  "user_activity": [
    {
      "user_id": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "total_detections": 1250,
      "active_days": 25,
      "last_activity": "2024-01-31T15:30:00Z",
      "average_session_duration": 1800,
      "detection_frequency": 50
    }
  ],
  "activity_summary": {
    "total_active_users": 25,
    "new_users_this_period": 5,
    "average_detections_per_user": 616.8,
    "most_active_user": "user-uuid"
  },
  "retention_metrics": {
    "daily_active_users": 15,
    "weekly_active_users": 22,
    "monthly_active_users": 25,
    "retention_rate_7d": 0.88,
    "retention_rate_30d": 0.76
  }
}
```

### GET /api/v1/analytics/performance
Get system performance analytics.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `start_date` (string, optional): Start date filter
- `end_date` (string, optional): End date filter
- `metric` (string, optional): Specific metric (cpu, memory, gpu, latency)

**Response:**
```json
{
  "system_metrics": {
    "cpu_usage": {
      "average": 45.2,
      "peak": 89.5,
      "current": 52.1
    },
    "memory_usage": {
      "average": "2.1GB",
      "peak": "3.8GB",
      "current": "2.3GB"
    },
    "gpu_usage": {
      "average": 78.5,
      "peak": 95.2,
      "current": 82.1
    }
  },
  "detection_metrics": {
    "average_processing_time": 0.15,
    "fastest_processing_time": 0.08,
    "slowest_processing_time": 0.45,
    "throughput_fps": 6.67,
    "success_rate": 0.98
  },
  "api_metrics": {
    "total_requests": 15420,
    "successful_requests": 15112,
    "failed_requests": 308,
    "average_response_time": 0.25,
    "error_rate": 0.02
  },
  "time_series": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "cpu_usage": 45.2,
      "memory_usage": 2.1,
      "gpu_usage": 78.5,
      "processing_time": 0.15,
      "throughput": 6.67
    }
  ]
}
```

### GET /api/v1/analytics/reports
Generate analytics reports.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `report_type` (string, required): Report type (daily, weekly, monthly, custom)
- `start_date` (string, optional): Start date for custom reports
- `end_date` (string, optional): End date for custom reports
- `format` (string, optional): Report format (json, csv, pdf)

**Response:**
```json
{
  "report_id": "report-uuid",
  "report_type": "weekly",
  "generated_at": "2024-01-31T15:30:00Z",
  "period": {
    "start_date": "2024-01-25T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  },
  "summary": {
    "total_detections": 3250,
    "unique_users": 18,
    "average_confidence": 0.87,
    "system_uptime": 0.99
  },
  "download_url": "/api/v1/analytics/reports/report-uuid/download",
  "expires_at": "2024-02-07T15:30:00Z"
}
```

### GET /api/v1/analytics/reports/{report_id}/download
Download generated report.

**Headers:**
- `Authorization: Bearer <access_token>`

**Path Parameters:**
- `report_id` (string, required): Report UUID

**Response:**
- File download (PDF, CSV, or JSON based on format)

## Real-time Analytics

### WebSocket Analytics Stream
Connect to real-time analytics updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/analytics');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Analytics update:', data);
};
```

**Message Types:**
- `detection_update`: New detection data
- `performance_update`: System performance metrics
- `user_activity`: User activity updates
- `alert`: System alerts and notifications

## Data Export

### GET /api/v1/analytics/export
Export analytics data.

**Headers:**
- `Authorization: Bearer <access_token>`

**Query Parameters:**
- `data_type` (string, required): Data type (detections, users, performance)
- `start_date` (string, optional): Start date filter
- `end_date` (string, optional): End date filter
- `format` (string, optional): Export format (csv, json, xlsx)
- `include_metadata` (boolean, optional): Include metadata

**Response:**
- File download with exported data

## Custom Metrics

### POST /api/v1/analytics/metrics/custom
Create custom analytics metrics.

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "name": "custom_metric",
  "description": "Custom detection metric",
  "query": "SELECT COUNT(*) FROM detections WHERE confidence > 0.8",
  "aggregation": "sum",
  "group_by": "hour"
}
```

**Response:**
```json
{
  "metric_id": "metric-uuid",
  "name": "custom_metric",
  "status": "active",
  "created_at": "2024-01-31T15:30:00Z"
}
```

### GET /api/v1/analytics/metrics/custom/{metric_id}
Get custom metric data.

**Headers:**
- `Authorization: Bearer <access_token>`

**Path Parameters:**
- `metric_id` (string, required): Custom metric UUID

**Response:**
```json
{
  "metric_id": "metric-uuid",
  "name": "custom_metric",
  "data": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "value": 45,
      "group": "00"
    }
  ],
  "aggregation": "sum",
  "group_by": "hour"
}
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid date range. Start date must be before end date"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": "Invalid group_by parameter. Must be one of: hour, day, week, month"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Analytics processing failed",
  "error_code": "ANALYTICS_ERROR"
}
```

## Rate Limiting

### Analytics Requests
- **Rate Limit**: 60 requests per minute per user
- **Burst Limit**: 10 requests per second
- **Report Generation**: 5 reports per hour per user

### Data Export
- **Export Limit**: 10 exports per hour per user
- **Max Data Range**: 90 days per export
- **File Size Limit**: 100MB per export

## Testing

### Test Analytics
```bash
# Get overview
curl -X GET "http://localhost:8000/api/v1/analytics/overview" \
  -H "Authorization: Bearer <access_token>"

# Get detection analytics
curl -X GET "http://localhost:8000/api/v1/analytics/detections?group_by=day" \
  -H "Authorization: Bearer <access_token>"

# Generate report
curl -X GET "http://localhost:8000/api/v1/analytics/reports?report_type=weekly" \
  -H "Authorization: Bearer <access_token>"

# Export data
curl -X GET "http://localhost:8000/api/v1/analytics/export?data_type=detections&format=csv" \
  -H "Authorization: Bearer <access_token>"
```
