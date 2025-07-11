# Analytics Insights Feature Documentation

## Overview
The Analytics Insights feature provides comprehensive analysis of property price influences and geographic price patterns using machine learning and data visualization.

## Features

### 1. Feature Importance Analysis
- **Purpose**: Shows which property features most significantly influence property prices
- **Model Support**: Works with tree-based models (Random Forest, Gradient Boosting) and linear models
- **Visualization**: Interactive bar chart showing top 10 most important features
- **Details**: Complete ranking of all 26 features with importance scores and percentages

### 2. Geographic Price Analysis
- **Cities Analysis**: Average property prices across major Canadian cities
- **Provincial Analysis**: Price comparisons by province
- **Property Type Analysis**: Average prices by property type (Detached, Condo, etc.)
- **Postal Zone Analysis**: Price patterns by postal code zones (first 3 characters)

### 3. Interactive Visualizations
- **Charts**: Bar charts, doughnut charts, and responsive data tables
- **Data Tables**: Detailed breakdowns with price ranges and property counts
- **Export Functionality**: Ability to export charts and data (placeholder for implementation)

## Navigation

### Main Analytics Dashboard
- **URL**: `/dashboard/analytics`
- **Features**:
  - Overview metrics
  - Investment opportunities
  - Risk analysis
  - ROI projections
  - Quick access to deep insights

### Analytics Insights Subpage
- **URL**: `/dashboard/analytics/insights`
- **Features**:
  - Feature importance plots
  - Geographic price analysis
  - Interactive charts and tables
  - Detailed data breakdowns

## Technical Implementation

### Backend Methods

#### `get_feature_importance_analysis()`
```python
# Returns feature importance data from ML model
{
    'success': True,
    'all_features': [...],  # All 26 features with scores
    'top_features': [...],  # Top 10 features
    'model_type': 'RandomForestRegressor',
    'total_features': 26
}
```

#### `get_price_analytics_by_location()`
```python
# Returns comprehensive price data by location
{
    'success': True,
    'data': {
        'cities': [...],        # City price data
        'provinces': [...],     # Province price data
        'property_types': [...], # Type price data
        'zones': [...]          # Postal zone price data
    },
    'summary': {...}            # Summary statistics
}
```

#### `get_neighbourhood_price_analysis(city)`
```python
# Returns neighbourhood-level analysis for specific city
{
    'success': True,
    'neighbourhoods': [...],
    'filtered_city': 'Toronto',
    'total_neighbourhoods': 25
}
```

### Frontend Components

#### Charts Used
- **Chart.js**: For interactive data visualizations
- **Bar Charts**: Feature importance, city prices, provincial prices
- **Doughnut Chart**: Property type distribution
- **Responsive Design**: Charts adapt to different screen sizes

#### Styling
- **Bootstrap 5**: Responsive grid and components
- **Custom CSS**: Gradient backgrounds, card animations, hover effects
- **Font Awesome**: Icons for enhanced visual appeal

## Data Requirements

### Database Tables
- **Property**: Main property data with prices, locations, features
- **Fields Used**:
  - `sold_price`: For price calculations
  - `city`, `province`: For geographic analysis
  - `property_type`: For type analysis
  - `postal_code`: For zone analysis
  - `sqft`, `bedrooms`, `bathrooms`: For feature analysis

### ML Model Requirements
- **Model Types**: Support for tree-based and linear models
- **Features**: 26-feature array as defined in ML service
- **Artifacts**: Model files and feature column definitions

## Error Handling

### Common Scenarios
1. **No Model Loaded**: Graceful degradation with informative message
2. **Insufficient Data**: Minimum thresholds for meaningful analysis
3. **Database Errors**: Fallback to cached or demo data
4. **Template Errors**: Error states with user-friendly messages

### Fallback Strategies
- Demo data when real data unavailable
- Cached results for performance
- Progressive enhancement for features

## Future Enhancements

### Planned Features
1. **Interactive Filters**: Filter by date range, price range, property type
2. **Real-time Updates**: Live data refresh capabilities
3. **Advanced Analytics**: Trend analysis, seasonal patterns
4. **Export Functionality**: PDF reports, Excel exports
5. **Personalization**: User-specific insights and recommendations

### Performance Optimizations
1. **Caching**: Redis caching for expensive calculations
2. **Pagination**: For large datasets
3. **Lazy Loading**: Load charts on demand
4. **Background Processing**: Async data processing

## Usage Examples

### Accessing Analytics
1. Navigate to main site
2. Click "Analytics" dropdown in navigation
3. Select "Advanced Analytics" or "Deep Insights"
4. Explore different visualizations and data

### Interpreting Results
- **Feature Importance**: Higher percentages indicate stronger price influence
- **Geographic Analysis**: Compare prices across different locations
- **Property Types**: Understand market segments
- **Postal Zones**: Identify high-value areas

## Configuration

### Environment Variables
- Database connection for property data
- Model paths for ML analysis
- Chart.js CDN for visualizations

### Dependencies
- Flask for backend routing
- SQLAlchemy for database queries
- Chart.js for frontend charts
- Bootstrap for responsive design
