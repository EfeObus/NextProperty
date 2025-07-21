# NextProperty AI - User Guide (v2.8.0)

## Table of Contents
- [Getting Started](#getting-started)
- [API Key System](#api-key-system)
- [Account Management](#account-management)
- [Property Search](#property-search)
- [Property Listings](#property-listings)
- [AI Price Predictions](#ai-price-predictions)
- [Favorites Management](#favorites-management)
- [Dashboard Overview](#dashboard-overview)
- [Market Analysis](#market-analysis)
- [API Usage](#api-usage)
- [Mobile Experience](#mobile-experience)
- [Troubleshooting](#troubleshooting)
- [Frequently Asked Questions](#frequently-asked-questions)

## Getting Started

### Welcome to NextProperty AI v2.8.0

NextProperty AI is an advanced real estate platform that combines traditional property search with cutting-edge artificial intelligence to provide accurate property valuations and market insights. With our new API key system, developers can integrate our AI-powered property analysis into their own applications.

### ✨ New in v2.8.0
- **🔑 5-Tier API Key System**: FREE, BASIC, PREMIUM, ENTERPRISE, and UNLIMITED tiers
- **📊 Developer Analytics**: Real-time usage monitoring and quota management
- **🌍 Geographic Controls**: Canadian province and city-based access management
- **⚡ Advanced Rate Limiting**: Enhanced protection with predictive capabilities
- **🐳 Docker Database**: Production-ready MySQL infrastructure

### Key Features
- **🤖 AI-Powered Analysis**: 88.3% accuracy with 6+ machine learning models
- **🔍 Smart Property Search**: Advanced filters with AI-powered recommendations
- **💰 Instant Valuations**: Real-time property price predictions
- **📈 Market Intelligence**: Live economic data from Bank of Canada & Statistics Canada
- **⭐ Favorites Management**: Save and organize properties of interest
- **🏘️ Professional Network**: Connect with verified real estate agents
- **📱 Mobile-Friendly**: Full functionality on any device
- **🔒 Enterprise Security**: Multi-layer protection with behavioral analysis

### System Requirements
- **Web Browser**: Chrome 70+, Firefox 65+, Safari 12+, Edge 79+
- **Internet Connection**: Broadband recommended for optimal performance
- **JavaScript**: Must be enabled for full functionality
- **Cookies**: Required for authentication and preferences

---

## 🔑 API Key System

### Overview
The API Key system allows developers to access NextProperty AI's powerful property analysis and prediction capabilities programmatically. Choose from 5 tiers based on your needs.

### API Tier Comparison

| Feature | FREE | BASIC | PREMIUM | ENTERPRISE | UNLIMITED |
|---------|------|-------|---------|------------|-----------|
| **Requests/min** | 10 | 60 | 300 | 1,500 | 10,000 |
| **Requests/hour** | 100 | 1,000 | 5,000 | 25,000 | 100,000 |
| **Requests/day** | 1,000 | 10,000 | 50,000 | 250,000 | 1,000,000 |
| **Data Transfer** | 10MB/day | 100MB/day | 1GB/day | 10GB/day | 100GB/day |
| **Compute Time** | 60s/day | 300s/day | 1,800s/day | 7,200s/day | 86,400s/day |
| **Support** | Community | Email | Priority | 24/7 Phone | Dedicated Manager |
| **SLA** | None | 99% | 99.5% | 99.9% | 99.99% |

### Getting Started with API Keys

#### 1. Request API Access
- Contact our team at api@nextproperty.ai
- Specify your use case and expected usage
- Choose appropriate tier based on requirements

#### 2. API Key Format
```
npai_{tier}_{random_string}
Example: npai_premium_k8x9m2n4p7q1w5e8r3t6y0u2i5o9
```

#### 3. API Authentication
```bash
# Include API key in request headers
curl -H "X-API-Key: npai_premium_..." \
     https://nextproperty.ai/api/properties
```

### API Usage Examples

#### Property Search
```python
import requests

headers = {'X-API-Key': 'npai_premium_...'}
params = {
    'city': 'Toronto',
    'min_price': 500000,
    'max_price': 1000000,
    'bedrooms': 3
}

response = requests.get(
    'https://nextproperty.ai/api/properties',
    headers=headers,
    params=params
)

properties = response.json()
```

#### Price Prediction
```python
prediction_data = {
    'sqft': 2000,
    'bedrooms': 3,
    'bathrooms': 2,
    'city': 'Toronto',
    'property_type': 'house'
}

response = requests.post(
    'https://nextproperty.ai/api/predict',
    headers=headers,
    json=prediction_data
)

prediction = response.json()
print(f"Predicted price: ${prediction['price']:,.2f}")
print(f"Confidence: {prediction['confidence']:.1%}")
```

#### Market Analytics
```python
response = requests.get(
    'https://nextproperty.ai/api/market/toronto',
    headers=headers
)

market_data = response.json()
print(f"Average price: ${market_data['avg_price']:,.2f}")
print(f"Market trend: {market_data['trend']}")
```

### API Usage Monitoring

#### Check Your Usage
```python
response = requests.get(
    'https://nextproperty.ai/api/usage',
    headers=headers
)

usage = response.json()
print(f"Requests today: {usage['requests_today']}/{usage['daily_limit']}")
print(f"Data transfer: {usage['data_transfer_mb']:.1f}MB/{usage['data_limit_mb']}MB")
```

#### Rate Limiting Headers
All API responses include rate limiting information:
```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 245
X-RateLimit-Reset: 1642694400
X-RateLimit-Retry-After: 60
```

## Account Management

### Creating an Account

1. **Visit the Registration Page**
   - Click "Sign Up" in the top navigation
   - Or visit `/register` directly

2. **Fill in Your Information**
   ```
   Required Fields:
   - First Name
   - Last Name
   - Email Address
   - Password (minimum 8 characters)
   - Phone Number (optional)
   
   Account Type:
   - Buyer/Investor
   - Property Owner
   - Real Estate Agent
   ```

3. **Email Verification**
   - Check your email for a verification link
   - Click the link to activate your account
   - You can now log in to the platform

### Logging In

1. **Access the Login Page**
   - Click "Login" in the top navigation
   - Enter your email and password
   - Click "Sign In"

2. **Forgot Password**
   - Click "Forgot Password?" on the login page
   - Enter your email address
   - Check your email for reset instructions
   - Follow the link to create a new password

### Profile Management

1. **Access Your Profile**
   - Click your name in the top-right corner
   - Select "Profile" from the dropdown menu

2. **Edit Profile Information**
   ```
   Editable Fields:
   - Personal Information (name, phone, bio)
   - Contact Preferences
   - Notification Settings
   - Profile Picture
   - Investment Preferences
   ```

3. **Account Security**
   - Change password regularly
   - Enable two-factor authentication (recommended)
   - Review login activity
   - Manage connected devices

## Property Search

### Basic Search

1. **Using the Search Bar**
   - Enter a location (city, neighborhood, address)
   - Select property type (house, condo, townhouse)
   - Set price range using the slider
   - Click "Search" to view results

2. **Quick Filters**
   ```
   Available Filters:
   - Price Range: $0 - $5,000,000+
   - Bedrooms: 1-5+
   - Bathrooms: 1-4+
   - Property Type: House, Condo, Townhouse
   - Square Footage: 500-5000+ sq ft
   ```

### Advanced Search

1. **Access Advanced Filters**
   - Click "Advanced Search" below the main search bar
   - Additional filters will expand

2. **Advanced Filter Options**
   ```
   Location Filters:
   - Specific neighborhoods
   - School districts
   - Distance from landmarks
   - Transit accessibility
   
   Property Features:
   - Year built
   - Lot size
   - Garage spaces
   - Basement type
   - Heating/cooling systems
   
   Financial Filters:
   - Property taxes
   - HOA fees
   - Days on market
   - Price per square foot
   ```

3. **Save Search Criteria**
   - Click "Save Search" after setting filters
   - Name your search for easy reference
   - Set up email alerts for new matching properties

### Search Results

1. **Viewing Results**
   - Results display as cards with key information
   - Use list or map view toggle
   - Sort by price, date, size, or AI score

2. **Property Cards Include**
   ```
   Basic Information:
   - Property photos
   - Price and price per sq ft
   - Bedrooms and bathrooms
   - Square footage
   - Address and neighborhood
   
   AI Features:
   - Predicted value range
   - Market trend indicator
   - Investment score
   - Price history
   ```

3. **Map View**
   - Interactive map with property markers
   - Cluster view for dense areas
   - Filter by map boundaries
   - View nearby amenities and schools

## Property Listings

### Viewing Property Details

1. **Property Information Tabs**
   ```
   Overview Tab:
   - Basic property details
   - Property description
   - Key features and amenities
   - Property history
   
   Photos Tab:
   - High-resolution image gallery
   - Virtual tour (if available)
   - Neighborhood photos
   
   Details Tab:
   - Complete property specifications
   - Room-by-room descriptions
   - Appliances and fixtures
   - Lot and building details
   
   Location Tab:
   - Interactive neighborhood map
   - Nearby schools and ratings
   - Local amenities and services
   - Transportation options
   
   Market Analysis Tab:
   - Price history and trends
   - Comparable properties
   - Neighborhood statistics
   - Market predictions
   ```

2. **Contact Information**
   - Listing agent details and contact info
   - Schedule showing button
   - Send message to agent
   - Request more information

### Property Photos and Media

1. **Photo Gallery**
   - High-resolution images
   - Full-screen viewing mode
   - Thumbnail navigation
   - Download individual photos

2. **Virtual Tours**
   - 360-degree room views (when available)
   - Interactive floor plans
   - Video walkthroughs
   - Street view integration

## Price Predictions

### AI-Powered Valuations

1. **Instant Price Estimates**
   - Every property displays an AI-predicted value
   - Confidence rating (High, Medium, Low)
   - Value range with upper and lower bounds
   - Last updated timestamp

2. **Prediction Factors**
   ```
   Our AI considers:
   - Property characteristics (size, age, features)
   - Location factors (neighborhood, schools, amenities)
   - Market conditions (recent sales, inventory, trends)
   - Economic indicators (interest rates, employment, GDP)
   - Seasonal adjustments
   - Local regulations and zoning
   ```

### Custom Valuations

1. **Request Custom Valuation**
   - Click "Get Detailed Valuation" on any property
   - Provide additional property details if needed
   - Receive comprehensive valuation report

2. **Valuation Report Includes**
   ```
   Report Sections:
   - Executive Summary
   - Predicted value with confidence interval
   - Comparable properties analysis
   - Market trends and indicators
   - Risk assessment
   - Investment potential scoring
   - Recommendations
   ```

### Market Predictions

1. **Neighborhood Trends**
   - Average price trends over time
   - Price appreciation forecasts
   - Market velocity indicators
   - Supply and demand analysis

2. **Economic Impact Analysis**
   - Interest rate sensitivity
   - Employment impact on prices
   - Population growth effects
   - Infrastructure development impact

## Favorites Management

### Adding Properties to Favorites

1. **Save Properties**
   - Click the heart icon on any property card
   - Or click "Add to Favorites" on property detail page
   - Properties are instantly saved to your account

2. **Organize Favorites**
   - Create custom lists (e.g., "Top Choices", "Investment Properties")
   - Add notes to each saved property
   - Set reminders for follow-up actions

### Managing Your Favorites

1. **Access Favorites**
   - Click "Favorites" in the main navigation
   - Or access through your dashboard

2. **Favorites Features**
   ```
   Available Actions:
   - View all saved properties
   - Filter by custom lists
   - Sort by date saved, price, or custom order
   - Add personal notes and ratings
   - Share favorite lists with others
   - Export to PDF or spreadsheet
   - Set up price alerts
   ```

3. **Price Alerts**
   - Get notified when prices change
   - Set custom price thresholds
   - Receive weekly market updates for saved properties

## Dashboard Overview

### Personal Dashboard

1. **Dashboard Sections**
   ```
   Main Dashboard Includes:
   - Recent activity summary
   - Saved searches and alerts
   - Favorite properties
   - Market updates for your areas of interest
   - Recommended properties
   - Agent communications
   - Account notifications
   ```

2. **Quick Actions**
   - Start new property search
   - View recent property visits
   - Access saved searches
   - Update profile settings
   - Contact saved agents

### Activity Tracking

1. **Search History**
   - View your recent searches
   - Quickly repeat previous searches
   - See search result statistics
   - Refine past searches with new criteria

2. **Property Views**
   - Track properties you've viewed
   - See viewing timestamps
   - Note any price changes since viewing
   - Quick access to view again

### Notifications and Alerts

1. **Notification Types**
   ```
   You'll receive alerts for:
   - New properties matching saved searches
   - Price changes on favorite properties
   - Market updates for areas of interest
   - Messages from agents
   - Account security notifications
   ```

2. **Notification Preferences**
   - Choose email or in-app notifications
   - Set frequency (immediate, daily, weekly)
   - Customize notification types
   - Manage quiet hours

## Market Analysis

### Market Reports

1. **Neighborhood Reports**
   - Average prices and trends
   - Sales volume and velocity
   - Price per square foot analysis
   - Inventory levels and absorption rates

2. **Economic Indicators**
   ```
   Key Metrics Displayed:
   - Bank of Canada interest rates
   - Employment statistics
   - Population growth data
   - GDP indicators
   - Housing starts and permits
   - Regional economic forecasts
   ```

### Comparative Market Analysis

1. **Property Comparisons**
   - Compare up to 4 properties side-by-side
   - Feature-by-feature comparison
   - Price and value analysis
   - Location scoring comparison

2. **Market Positioning**
   - See how a property compares to neighborhood average
   - Understand pricing relative to similar properties
   - Identify potential value opportunities
   - Assess fair market value

### Investment Analysis

1. **Investment Metrics**
   ```
   For Investment Properties:
   - Cap rate calculations
   - Cash flow projections
   - Appreciation forecasts
   - Rental yield estimates
   - ROI analysis
   - Risk assessment scores
   ```

2. **Market Timing**
   - Best time to buy/sell indicators
   - Seasonal market patterns
   - Economic cycle positioning
   - Interest rate impact analysis

## Mobile Experience

### Mobile App Features

1. **Full Feature Access**
   - All desktop features available on mobile
   - Touch-optimized interface
   - Swipe gestures for photo galleries
   - Location-based search using GPS

2. **Mobile-Specific Features**
   ```
   Mobile Enhancements:
   - GPS-based property discovery
   - Camera integration for property photos
   - Push notifications
   - Offline favorites access
   - Quick dial to agents
   - Share properties via text/social media
   ```

### Mobile Navigation

1. **Bottom Navigation Bar**
   - Search: Access property search
   - Favorites: View saved properties
   - Dashboard: Personal overview
   - Profile: Account settings

2. **Gesture Controls**
   - Swipe left/right on property photos
   - Pull to refresh search results
   - Pinch to zoom on maps
   - Long press for context menus

## Troubleshooting

### Common Issues

1. **Login Problems**
   ```
   If you can't log in:
   - Check email and password spelling
   - Try password reset if forgotten
   - Clear browser cache and cookies
   - Disable browser extensions temporarily
   - Try incognito/private browsing mode
   ```

2. **Search Not Working**
   ```
   If search results don't appear:
   - Check internet connection
   - Try different search terms
   - Clear search filters
   - Refresh the page
   - Try a different browser
   ```

3. **Slow Performance**
   ```
   To improve performance:
   - Close unnecessary browser tabs
   - Clear browser cache
   - Disable heavy browser extensions
   - Check internet speed
   - Try using a different device
   ```

4. **Map Issues**
   ```
   If maps don't load:
   - Check if location services are enabled
   - Refresh the page
   - Try a different browser
   - Clear browser cache
   - Check if ad blockers are interfering
   ```

5. **"Too Many Requests" Error (Error 429)**
   ```
   If you see a "Too Many Requests" message:
   - You've exceeded the rate limit for requests
   - Wait a few minutes before trying again
   - The message will show when you can retry
   - Consider spacing out your requests
   - Contact support if you need higher limits for legitimate use
   ```

   **Rate Limits by Action:**
   - Property searches: 200 requests per minute
   - AI predictions: 50 requests per minute
   - Login attempts: 10 attempts per minute
   - API calls: 100 requests per minute
   - File uploads: 10 uploads per minute

   **Tips to Avoid Rate Limits:**
   - Avoid rapid-fire clicking or refreshing
   - Use search filters to get more specific results
   - Save interesting properties to favorites instead of re-searching
   - If using the API, implement proper delay between requests

### Getting Help

1. **Contact Support**
   ```
   Support Options:
   - Email: support@nextproperty.ai
   - Phone: 1-800-NEXTPROP (1-800-639-8776)
   - Live Chat: Available on website
   - Help Center: Comprehensive FAQ and guides
   ```

2. **Response Times**
   - Live Chat: Immediate during business hours
   - Email: Within 24 hours
   - Phone: Business hours (9 AM - 6 PM EST)

## Frequently Asked Questions

### General Questions

**Q: Is NextProperty AI free to use?**
A: Yes, basic property search and viewing is completely free. Premium features like detailed market reports and investment analysis may require a subscription.

**Q: How accurate are the AI price predictions?**
A: Our AI model typically provides predictions within 5-10% of actual market value. Accuracy varies by location and property type, with confidence ratings provided for each prediction.

**Q: How often is the data updated?**
A: Property listings are updated in real-time. Economic data is refreshed daily. AI model predictions are recalculated when new market data becomes available.

### Account Questions

**Q: Can I change my email address?**
A: Yes, you can update your email address in your profile settings. You'll need to verify the new email address.

**Q: How do I delete my account?**
A: Contact our support team to request account deletion. We'll permanently remove your data within 30 days.

**Q: Can multiple people use the same account?**
A: Accounts are designed for individual use. For team access, contact us about business account options.

### Property Search Questions

**Q: Why don't I see some properties I know are for sale?**
A: We source listings from multiple MLS systems, but some properties may not be included if they're private sales or not yet syndicated to our platform.

**Q: Can I search for sold properties?**
A: Yes, use the "Include Sold" filter to see recently sold properties for market analysis.

**Q: How do I get alerts for new properties?**
A: Save your search criteria and enable email alerts. You'll be notified when new properties match your criteria.

### Technical Questions

**Q: Which browsers are supported?**
A: We support Chrome 70+, Firefox 65+, Safari 12+, and Edge 79+. For the best experience, use the latest browser version.

**Q: Is my personal information secure?**
A: Yes, we use bank-level encryption to protect your data. We never sell personal information to third parties.

**Q: Can I use the platform offline?**
A: Basic favorites viewing is available offline on mobile. All other features require an internet connection.

### AI and Predictions

**Q: How does the AI make price predictions?**
A: Our machine learning model analyzes thousands of factors including property characteristics, location data, market trends, and economic indicators to generate predictions.

**Q: Why do predictions sometimes change?**
A: Predictions update when new market data becomes available or economic conditions change. This ensures you always have the most current valuation.

**Q: Can I request a professional appraisal?**
A: While our AI provides estimates, for legal or lending purposes, you'll need a licensed appraiser. We can connect you with qualified professionals in your area.

---

## Need More Help?

If you can't find the answer to your question in this guide, please don't hesitate to contact our support team:

- **Email**: support@nextproperty.ai
- **Phone**: 1-800-NEXTPROP (1-800-639-8776)
- **Live Chat**: Available on our website during business hours
- **Help Center**: Visit our comprehensive online help center

Our team is committed to helping you make the most of NextProperty AI's powerful features and insights.

---

*Last Updated: January 2024*
*Version: 1.0*
