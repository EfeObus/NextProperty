# NextProperty AI - API Documentation

## Table of Contents
- [Overview](#overview)
- [Base URLs](#base-urls)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Main Routes](#main-routes)
- [API Endpoints](#api-endpoints)
- [Dashboard Endpoints](#dashboard-endpoints)
- [Admin Endpoints](#admin-endpoints)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Overview

NextProperty AI is a comprehensive real estate platform providing property listings, AI-powered property valuations, market analysis, and investment insights. This documentation covers all available API endpoints and routes.

**Version**: 1.0.0  
**Base URL**: `http://localhost:5007` (default development)

## Base URLs

- **Development**: `http://localhost:5007`
- **Production**: `https://your-domain.com` (when deployed)

## Authentication

Currently, most endpoints are publicly accessible. Authentication-required endpoints are marked with `` and will return:

```json
{
  "success": false,
  "error": "Authentication required",
  "demo": true
}
```

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "pagination": { ... } // for paginated results
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message description"
}
```

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Internal Server Error |

---

# Main Routes

## Home & Navigation

### `GET /`
**Homepage with featured properties and market overview**

**Response**: Renders `index.html` with:
- `top_properties`: AI-selected undervalued properties (limit: 6)
- `featured_properties`: High-value recent properties (limit: 6)
- `market_stats`: Platform statistics
- `top_cities`: Cities by property count (limit: 8)
- `market_predictions`: AI market predictions

**Market Stats Structure**:
```json
{
  "total_properties": 1250,
  "avg_price": 750000.50,
  "cities_covered": 25,
  "ai_analyzed": 980
}
```

### `GET /properties`
**Property listings with search and filter**

**Query Parameters**:
- `city` (string): Filter by city name
- `type` (string): Filter by property type
- `min_price` (float): Minimum price filter
- `max_price` (float): Maximum price filter
- `bedrooms` (int): Minimum bedrooms
- `bathrooms` (float): Minimum bathrooms
- `page` (int): Page number (default: 1)

**Response**: Renders `properties/list.html` with paginated results

### `GET /property/<listing_id>`
**Individual property details page**

**Parameters**:
- `listing_id`: Unique property identifier

**Response**: Renders `properties/detail.html` with:
- Property details
- AI analysis (if available)
- Nearby properties
- Save/favorite status

### `GET /search`
**Advanced property search page**

**Query Parameters**:
- `location` (string): Search in city/province/postal code
- `property_type` (string): Property type filter
- `min_price` (float): Price range minimum
- `max_price` (float): Price range maximum
- `bedrooms` (int): Bedroom count
- `bathrooms` (float): Bathroom count
- `page` (int): Page number

**Response**: Renders `properties/search.html` with search results

### `GET /mapview`
**Interactive map view of properties**

**Query Parameters**: Same as `/properties`

**Response**: Renders `mapview.html` with:
- Properties with coordinates (max 500)
- Filter options
- Map center coordinates

### `GET /favourites`
**User favorites page (demo mode)**

**Response**: Renders `favourites.html` with demo content

### `GET /predict-price`
**Property price prediction form**

**Response**: Renders `properties/price_prediction_form.html`

### `POST /predict-price`
**Process price prediction**

**Form Data**:
- `bedrooms` (int, required)
- `bathrooms` (float, required)
- `square_feet` (int, required)
- `lot_size` (int, optional)
- `year_built` (int, optional)
- `property_type` (string, required)
- `city` (string, required)
- `province` (string, required)
- `postal_code` (string, optional)

**Response**: Renders `properties/price_prediction.html` with prediction results

### `GET /upload-property`
**Property upload form**

**Response**: Renders `properties/upload_form.html`

### `POST /upload-property`
**Submit new property listing**

**Form Data**:
- `address` (string, required)
- `city` (string, required)
- `province` (string, required)
- `postal_code` (string, optional)
- `property_type` (string, required)
- `bedrooms` (int, required)
- `bathrooms` (float, required)
- `sqft` (int, required)
- `lot_size` (float, optional)
- `year_built` (int, optional)
- `listing_price` (float, required)
- `features` (text, optional)
- `description` (text, optional)

---

# API Endpoints

All API endpoints are prefixed with `/api/`

## Property Data

### `GET /api/properties`
**Get filtered property listings**

**Query Parameters**:
- `city` (string): Filter by city
- `type` (string): Property type filter
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `page` (int): Page number (default: 1)
- `per_page` (int): Results per page (max: 100, default: 20)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "listing_id": "NP12345678",
      "address": "123 Main St",
      "city": "Toronto",
      "province": "ON",
      "property_type": "Detached",
      "bedrooms": 3,
      "bathrooms": 2.5,
      "sqft": 2000,
      "sold_price": 850000,
      "original_price": 900000,
      "latitude": 43.7532,
      "longitude": -79.3832,
      "sold_date": "2024-12-01T00:00:00",
      "ai_valuation": 875000,
      "investment_score": 8.2,
      "risk_assessment": "Low"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1250,
    "pages": 63,
    "has_next": true,
    "has_prev": false
  }
}
```

### `GET /api/properties/<listing_id>`
**Get single property details**

**Response**:
```json
{
  "success": true,
  "data": {
    "listing_id": "NP12345678",
    "address": "123 Main St",
    "city": "Toronto",
    "province": "ON",
    "postal_code": "M5V 3A8",
    "property_type": "Detached",
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft": 2000,
    "lot_size": 0.25,
    "year_built": 2015,
    "sold_price": 850000,
    "original_price": 900000,
    "latitude": 43.7532,
    "longitude": -79.3832,
    "features": "Hardwood floors, granite counters",
    "agent_id": "AG123",
    "sold_date": "2024-12-01T00:00:00",
    "ai_valuation": 875000,
    "investment_score": 8.2,
    "risk_assessment": "Low",
    "market_trend": "Stable"
  }
}
```

### `GET /api/properties/<listing_id>/photos`
**Get property photos**

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "photo_url": "https://example.com/photo1.jpg",
      "photo_type": "exterior",
      "caption": "Front view",
      "order_index": 1
    }
  ]
}
```

### `GET /api/properties/<listing_id>/rooms`
**Get property room details**

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "room_type": "bedroom",
      "level": "main",
      "dimensions": "12x10",
      "features": "Walk-in closet"
    }
  ]
}
```

### `POST /api/properties/<listing_id>/analyze`
**Generate AI analysis for property**

**Response**:
```json
{
  "success": true,
  "data": {
    "listing_id": "NP12345678",
    "analysis": {
      "predicted_price": 875000,
      "confidence": 0.92,
      "confidence_interval": {
        "lower": 825000,
        "upper": 925000
      },
      "investment_score": 8.2,
      "risk_level": "Low",
      "market_trend": "Stable",
      "price_per_sqft": 437.5,
      "comparable_properties": 15,
      "market_position": "Fair Value"
    }
  }
}
```

## Search & Discovery

### `GET /api/search`
**Advanced property search**

**Query Parameters**:
- `q` (string): Text search query
- `city` (string): City filter
- `type` (string): Property type filter
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `bedrooms` (int): Bedroom count
- `bathrooms` (float): Bathroom count
- `page` (int): Page number
- `per_page` (int): Results per page

**Response**: Same format as `/api/properties` with additional `search_params`

### `GET /api/search/geospatial`
**Location-based property search**

**Query Parameters**:
- `lat` (float, required): Latitude
- `lng` (float, required): Longitude
- `radius` (float): Search radius in km (default: 5)

**Response**:
```json
{
  "success": true,
  "data": [...], // property array
  "search_center": {
    "latitude": 43.7532,
    "longitude": -79.3832,
    "radius_km": 5
  }
}
```

### `GET /api/top-deals`
**Get undervalued properties**

**Query Parameters**:
- `limit` (int): Number of deals (max: 50, default: 20)
- `city` (string): City filter
- `type` (string): Property type filter

**Response**:
```json
{
  "success": true,
  "deals": [
    {
      "listing_id": "NP12345678",
      "address": "123 Main St",
      "city": "Toronto",
      "property_type": "Detached",
      "bedrooms": 3,
      "bathrooms": 2.5,
      "sqft": 2000,
      "actual_price": 850000,
      "predicted_price": 920000,
      "value_difference": 70000,
      "value_difference_percent": 8.2,
      "investment_potential": "High",
      "investment_score": 8.2,
      "risk_level": "Low"
    }
  ],
  "count": 15
}
```

## AI & Machine Learning

### `POST /api/property-prediction`
**Predict property price**

**Request Body**:
```json
{
  "bedrooms": 3,
  "bathrooms": 2.5,
  "square_feet": 2000,
  "lot_size": 0.25,
  "year_built": 2015,
  "property_type": "Detached",
  "city": "Toronto",
  "province": "ON",
  "postal_code": "M5V 3A8",
  "dom": 25,
  "taxes": 8000
}
```

**Response**:
```json
{
  "success": true,
  "prediction": {
    "predicted_price": 875000,
    "confidence": 0.92,
    "confidence_interval": {
      "lower": 825000,
      "upper": 925000
    },
    "price_per_sqft": 437.5,
    "market_comparison": "Above Average",
    "factors": {
      "location_impact": 0.15,
      "size_impact": 0.25,
      "age_impact": -0.05,
      "market_impact": 0.10
    }
  }
}
```

### `GET /api/property-prediction/<listing_id>`
**Get AI prediction for existing property**

**Response**: Same format as POST endpoint, with additional `cached` flag

### `POST /api/properties/bulk-analyze`
**Bulk analyze properties for AI predictions**

**Response**:
```json
{
  "success": true,
  "analyzed_count": 85,
  "total_processed": 100
}
```

## Market Data

### `GET /api/market/trends`
**Get market trends and statistics**

**Query Parameters**:
- `city` (string): City filter
- `type` (string): Property type filter
- `months` (int): Historical period (default: 12)

**Response**:
```json
{
  "success": true,
  "data": {
    "price_trends": [
      {
        "month": "2024-01",
        "avg_price": 850000,
        "median_price": 825000,
        "volume": 150
      }
    ],
    "growth_rate": 5.2,
    "market_health": "Strong",
    "inventory_levels": "Balanced"
  }
}
```

### `GET /api/market/economic-indicators`
**Get economic indicators**

**Query Parameters**:
- `source` (string): BOC or STATCAN
- `category` (string): Indicator category
- `limit` (int): Number of indicators (default: 20)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "indicator_code": "CANSIM-10-10-0005",
      "name": "Consumer Price Index",
      "description": "Monthly CPI data",
      "source": "STATCAN",
      "category": "Inflation",
      "latest_value": {
        "value": 3.2,
        "date": "2024-11-01",
        "unit": "Percentage"
      }
    }
  ]
}
```

### `GET /api/market/predictions`
**Get market predictions**

**Query Parameters**:
- `city` (string): City filter
- `type` (string): Property type filter
- `horizon` (int): Prediction horizon in months (default: 6)

**Response**:
```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "month": "2025-01",
        "predicted_avg_price": 890000,
        "confidence": 0.85,
        "trend": "Increasing"
      }
    ],
    "overall_trend": "Bullish",
    "confidence": 0.82
  }
}
```

## Agents

### `GET /api/agents/<agent_id>`
**Get agent details**

**Response**:
```json
{
  "success": true,
  "data": {
    "agent_id": "AG123",
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "+1-416-555-0123",
    "brokerage": "ABC Realty",
    "license_number": "ON123456",
    "specialties": ["Luxury Homes", "First-time Buyers"],
    "years_experience": 8,
    "average_rating": 4.8,
    "total_sales": 150,
    "is_active": true
  }
}
```

### `GET /api/agents/<agent_id>/properties`
**Get agent's property listings**

**Query Parameters**:
- `page` (int): Page number
- `per_page` (int): Results per page

**Response**: Same format as `/api/properties` with pagination

## Statistics

### `GET /api/stats/summary`
**Get platform statistics summary**

**Response**:
```json
{
  "success": true,
  "data": {
    "total_properties": 1250,
    "total_agents": 45,
    "recent_properties": 85,
    "price_statistics": {
      "average_price": 785000,
      "min_price": 200000,
      "max_price": 3500000
    },
    "top_cities": [
      {
        "city": "Toronto",
        "count": 450
      },
      {
        "city": "Vancouver",
        "count": 320
      }
    ]
  }
}
```

## Model Management

### `GET /api/model/status`
**Get current ML model status**

**Response**:
```json
{
  "success": true,
  "model_status": {
    "r2_score": 0.912,
    "rmse": 45000,
    "mae": 32000,
    "mape": 4.2,
    "status": "healthy"
  },
  "metadata": {
    "model_name": "gradient_boost_v2",
    "training_date": "2024-12-01T10:30:00",
    "features_count": 26,
    "training_samples": 85000
  },
  "retrain_recommended": false
}
```

### `GET /api/model/available`
**Get available trained models**

**Response**:
```json
{
  "success": true,
  "available_models": [
    {
      "name": "gradient_boost_v2",
      "r2_score": 0.912,
      "rmse": 45000,
      "training_date": "2024-12-01T10:30:00",
      "is_active": true
    }
  ],
  "comparison": {
    "best_model": "gradient_boost_v2",
    "performance_ranking": [...]
  }
}
```

### `POST /api/model/switch`
**Switch to different model**

**Request Body**:
```json
{
  "model_name": "gradient_boost_v1"
}
```

### `POST /api/model/test`
**Test current model**

**Request Body**:
```json
{
  "features": {
    "bedrooms": 3,
    "bathrooms": 2,
    "square_feet": 2000,
    "property_type": "Detached",
    "city": "Toronto",
    "province": "ON"
  }
}
```

### `GET /api/model/performance-history`
**Get model performance history**

**Response**:
```json
{
  "success": true,
  "performance_data": [
    {
      "model": "gradient_boost_v2",
      "r2_score": 0.912,
      "rmse": 45000,
      "mae": 32000,
      "mape": 4.2,
      "training_time": 120
    }
  ],
  "best_model": "gradient_boost_v2",
  "training_info": {
    "last_training": "2024-12-01T10:30:00",
    "samples_used": 85000,
    "features_engineered": 26
  }
}
```

## Map Data

### `GET /api/properties/map-data`
**Get property data for map display**

**Query Parameters**: Same as `/properties`

**Response**:
```json
{
  "properties": [
    {
      "listing_id": "NP12345678",
      "lat": 43.7532,
      "lng": -79.3832,
      "price": 850000,
      "address": "123 Main St",
      "city": "Toronto",
      "property_type": "Detached",
      "bedrooms": 3,
      "bathrooms": 2.5,
      "sqft": 2000,
      "sold_date": "2024-12-01T00:00:00"
    }
  ],
  "count": 347
}
```

## User Actions (Demo Mode)

### `POST /api/save-property` 
**Save property to user's list (demo)**

**Request Body**:
```json
{
  "listing_id": "NP12345678"
}
```

**Response**:
```json
{
  "message": "Authentication required to save properties",
  "demo": true
}
```

### `POST /api/update-saved-property` 
**Update saved property notes (demo)**

### `GET /api/check-saved-status/<listing_id>` 
**Check if property is saved (demo)**

### `GET /api/saved-property/<saved_id>` 
**Get saved property details (demo)**

---

# Dashboard Endpoints

All dashboard endpoints require authentication (currently in demo mode).

### `GET /dashboard/` 
**Dashboard overview page**

**Response**: Renders `dashboard/overview.html` with:
- User's saved properties count
- Recent market activity
- Preferred cities data
- Market trends
- Investment recommendations
- Economic indicators

### `GET /dashboard/portfolio` 
**User's property portfolio page**

**Response**: Renders `dashboard/portfolio.html` with:
- Saved properties
- Portfolio statistics
- Performance analysis

---

# Admin Endpoints

All admin endpoints are prefixed with `/admin/` and require admin authentication.

### `GET /admin/` 
**Admin dashboard**

**Response**: Renders `admin/dashboard.html` with:
- System statistics
- Model status
- Database health
- Recent activity

### `GET /admin/bulk-operations` 
**Bulk operations management**

**Response**: Renders `admin/bulk_operations.html` with operation status

### `POST /admin/api/bulk-ai-analysis` 
**Generate AI valuations in bulk**

**Request Body**:
```json
{
  "batch_size": 50,
  "force_update": false
}
```

**Response**:
```json
{
  "success": true,
  "message": "Analysis completed",
  "processed": 45,
  "errors": 5
}
```

---

# Rate Limiting

**Enterprise-grade rate limiting is now implemented** to protect against abuse and ensure fair usage:

## Rate Limit Configuration

### Global Limits
- **All endpoints**: 1000 requests per minute per IP address
- **API endpoints**: 100 requests per minute
- **Authentication**: 10 login attempts per minute
- **Property search**: 200 requests per minute
- **ML predictions**: 50 requests per minute
- **File uploads**: 10 uploads per minute

### User-Based Limits
- **Authenticated users**: 2x higher limits
- **Premium users**: 5x higher limits
- **Admin users**: 10x higher limits

### Rate Limit Headers

All responses include rate limit information:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 60
```

### Rate Limit Exceeded Response

When rate limits are exceeded, you'll receive a 429 status code:

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again in 60 seconds.",
  "retry_after": 60,
  "limit": 100,
  "reset_time": "2025-01-01T12:00:00Z"
}
```

### Best Practices

1. **Check rate limit headers** before making requests
2. **Implement exponential backoff** when hitting limits
3. **Space out requests** appropriately
4. **Use caching** to reduce API calls
5. **Batch operations** when possible

### Rate Limit Bypass

For legitimate high-volume applications:
- Contact support for rate limit increases
- Consider premium API access
- Implement proper request queuing

# Caching

Several endpoints use caching with different timeouts:
- Property listings: 5 minutes
- Property details: 10 minutes
- Photos: 1 hour
- Market data: 30 minutes
- Statistics: 30 minutes

# Examples

## Get Properties in Toronto

```bash
curl "http://localhost:5007/api/properties?city=Toronto&per_page=5"
```

## Predict Property Price

```bash
curl -X POST "http://localhost:5007/api/property-prediction" \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 3,
    "bathrooms": 2.5,
    "square_feet": 2000,
    "property_type": "Detached",
    "city": "Toronto",
    "province": "ON"
  }'
```

## Search Properties Near Location

```bash
curl "http://localhost:5007/api/search/geospatial?lat=43.7532&lng=-79.3832&radius=10"
```

## Get Top Investment Deals

```bash
curl "http://localhost:5007/api/top-deals?limit=10&city=Toronto"
```

## Get Market Trends

```bash
curl "http://localhost:5007/api/market/trends?city=Toronto&months=12"
```

---

## Notes

1. **Authentication**: Most endpoints are currently in demo mode. Full authentication will be implemented in future versions.

2. **Data Validation**: All endpoints include proper input validation and error handling.

3. **Performance**: Large datasets are paginated and cached for optimal performance.

4. **AI Features**: Machine learning predictions and analysis are core features of the platform.

5. **Economic Integration**: Real economic indicators are integrated for enhanced market analysis.

6. **Geospatial**: Location-based search and mapping capabilities are fully functional.

This documentation covers all current endpoints and will be updated as new features are added.
