# Business Context - AgriWeather IoT Platform

## Architecture Diagrams

The AgriWeather platform architecture is documented using C4 model diagrams:

### System Context Diagram
![System Context Diagram](../source/images/system-context-diagram.png)

### Container Diagram
![Container Diagram](../source/images/conteiner-diagram.png)

## Executive Summary

AgriWeather is an innovative IoT-based weather monitoring platform designed specifically for agricultural applications. The platform provides real-time weather data collection, storage, and analysis to help farmers and agricultural professionals make informed decisions about crop planning, irrigation scheduling, and overall farm management.

## Problem Statement

Modern agriculture faces significant challenges related to weather unpredictability and climate change. Farmers often lack access to:
- Real-time, localized weather data for their specific fields
- Historical weather patterns for long-term planning
- Actionable insights for irrigation and crop management
- Cost-effective weather monitoring solutions

These gaps lead to:
- Inefficient water usage and increased costs
- Suboptimal crop yields
- Difficulty in planning planting and harvesting schedules
- Reactive rather than proactive farm management

## Solution Overview

AgriWeather provides a cloud-connected IoT solution that:
1. Deploys IoT weather sensors (or simulators) in agricultural fields
2. Collects real-time environmental data (temperature, humidity, rainfall, soil moisture, wind speed, etc.)
3. Stores data securely in cloud storage (Azure Blob Storage)
4. Processes and analyzes data through a backend REST API
5. Provides CLI (Command-Line Interface) for platform management and data access
6. Exposes data via REST API for integration with mobile apps, dashboards, and third-party systems
7. Includes comprehensive Postman collection for API testing and integration

## Target Users & Stakeholders

### Primary Users
- **Small to Medium Farm Owners**: Need affordable weather monitoring for better decision-making
- **Agricultural Consultants**: Require accurate data to advise multiple clients
- **Crop Managers**: Need real-time data for irrigation and crop protection decisions

### Secondary Users
- **Agricultural Researchers**: Use historical data for studies and trend analysis
- **Insurance Companies**: Utilize weather data for crop insurance assessments
- **Government Agricultural Departments**: Monitor regional agricultural conditions

## Use Cases

### UC-01: Real-Time Weather Monitoring
**Actor**: Farmer  
**Description**: Monitor current weather conditions at specific field locations  
**Preconditions**: IoT device deployed and connected to cloud  
**Flow**:
1. IoT device collects environmental data every 5-15 minutes
2. Data is transmitted to cloud storage
3. Backend processes and validates data
4. User accesses current readings via CLI or REST API
5. System displays temperature, humidity, rainfall, wind speed, soil moisture

**Postconditions**: Current weather data is available and stored  
**Business Value**: Enables immediate response to changing conditions

### UC-02: Irrigation Scheduling
**Actor**: Crop Manager  
**Description**: Determine optimal irrigation schedule based on weather data and forecasts  
**Preconditions**: Historical and current weather data available  
**Flow**:
1. User requests irrigation recommendations via API
2. System analyzes current soil moisture levels
3. System evaluates recent rainfall data
4. System considers weather forecast
5. Backend calculates water requirements
6. System provides irrigation schedule recommendation

**Postconditions**: Irrigation plan is generated  
**Business Value**: Reduces water waste by 20-30%, optimizes crop health

### UC-03: Crop Planning
**Actor**: Farm Owner  
**Description**: Plan planting schedules based on historical weather patterns  
**Preconditions**: At least one season of historical data  
**Flow**:
1. User queries historical weather data for specific time periods
2. Backend retrieves data from cloud storage
3. System analyzes temperature patterns, frost dates, rainfall distribution
4. User compares current year trends with historical averages
5. User makes informed decisions about planting dates

**Postconditions**: Data-driven planting schedule created  
**Business Value**: Increases crop success rate, reduces weather-related losses

### UC-04: Frost Alert System
**Actor**: Farmer  
**Description**: Receive alerts when frost conditions are detected or predicted  
**Preconditions**: IoT device monitoring temperature  
**Flow**:
1. IoT device detects temperature dropping below threshold
2. Data transmitted to backend in real-time
3. Backend evaluates frost risk conditions
4. System triggers alert via API
5. Farmer receives notification to take protective measures

**Postconditions**: Alert logged and delivered  
**Business Value**: Prevents crop damage, enables timely protective actions

### UC-05: Historical Data Analysis
**Actor**: Agricultural Consultant  
**Description**: Analyze weather trends over multiple seasons  
**Preconditions**: Multi-season data stored in cloud  
**Flow**:
1. User requests historical data via REST API
2. Backend queries cloud storage for specified date ranges
3. System aggregates and formats data
4. User receives data for analysis
5. Consultant identifies patterns and trends

**Postconditions**: Historical report generated  
**Business Value**: Supports strategic planning and client advisory services

### UC-06: Device Health Monitoring
**Actor**: System Administrator  
**Description**: Monitor IoT device connectivity and data quality  
**Preconditions**: IoT devices registered in system  
**Flow**:
1. Backend tracks last transmission time for each device
2. System validates data quality and sensor readings
3. Admin queries device status via CLI or API
4. System reports device health metrics
5. Admin identifies and addresses connectivity issues

**Postconditions**: Device status report available  
**Business Value**: Ensures data reliability and system uptime

### UC-07: CLI-Based Data Query
**Actor**: Farmer  
**Description**: Quick access to weather data via command-line interface  
**Preconditions**: CLI tool installed, device registered  
**Flow**:
1. User opens terminal/command prompt
2. User executes CLI command with device ID or location
3. CLI connects to REST API backend
4. System retrieves latest weather data
5. CLI displays formatted weather information (temperature, humidity, etc.)
6. User can optionally export data to file

**Postconditions**: Weather data displayed in terminal  
**Business Value**: Fast, scriptable access to data without web browser

## User Stories

### Epic 1: Weather Data Collection

**US-01**: As a farmer, I want my IoT device to automatically collect temperature data every 15 minutes so that I have accurate real-time information about my field conditions.  
**Acceptance Criteria**:
- Device reads temperature sensor every 15 minutes
- Data includes timestamp and device ID
- Readings are accurate within ±0.5°C
- Data is transmitted to cloud within 1 minute of collection

**US-02**: As a crop manager, I want to monitor soil moisture levels so that I can determine when irrigation is needed.  
**Acceptance Criteria**:
- Device measures soil moisture percentage
- Data updates every 30 minutes
- Historical moisture trends are accessible via API
- Moisture readings trigger alerts at defined thresholds

**US-03**: As an agricultural consultant, I want to access rainfall data so that I can advise clients on water management.  
**Acceptance Criteria**:
- System records rainfall amounts in mm
- Daily, weekly, and monthly totals are calculated
- Data is accessible via REST API
- Rainfall data can be filtered by date range and location

### Epic 2: Data Storage & Retrieval

**US-04**: As a developer, I want all weather data stored in cloud storage so that it's secure, scalable, and accessible.  
**Acceptance Criteria**:
- Data is stored in Azure Blob Storage
- Data is organized by date and device ID
- Storage supports at least 2 years of historical data
- Data retrieval latency is under 2 seconds

**US-05**: As a researcher, I want to query historical weather data by date range so that I can perform seasonal analysis.  
**Acceptance Criteria**:
- REST API supports date range queries
- Results returned in JSON format
- API supports filtering by data type (temperature, humidity, etc.)
- Maximum query range is 1 year

### Epic 3: API & Integration

**US-06**: As a third-party developer, I want a REST API to retrieve current weather conditions so that I can integrate data into my mobile app.  
**Acceptance Criteria**:
- GET endpoint returns latest readings for specified device
- Response includes all sensor data types
- API uses standard HTTP status codes
- Postman collection includes example requests

**US-07**: As a developer, I want API endpoints to retrieve aggregated data so that I can analyze daily/weekly averages.  
**Acceptance Criteria**:
- API supports aggregation by hour, day, week, month
- Endpoints return min, max, and average values
- Response time is under 3 seconds
- API supports multiple device queries
- All endpoints documented in Postman collection

**US-07b**: As a farmer, I want to use a CLI tool to query my field's current weather so that I can quickly check conditions without complex tools.  
**Acceptance Criteria**:
- CLI command returns current weather in readable format
- Supports filtering by device ID or location
- Returns data in under 3 seconds
- Displays all sensor readings (temperature, humidity, etc.)

### Epic 4: Alerts & Notifications

**US-08**: As a farmer, I want to receive alerts when temperature drops below freezing so that I can protect my crops from frost damage.  
**Acceptance Criteria**:
- System monitors temperature thresholds
- Alerts triggered when temperature < 0°C
- Alert includes timestamp and current temperature
- Alert data accessible via API

**US-09**: As a system administrator, I want to be notified when a device stops sending data so that I can troubleshoot connectivity issues.  
**Acceptance Criteria**:
- System detects when device hasn't transmitted in 1 hour
- Admin receives device offline notification
- Device status is queryable via API
- Notification includes device ID and last transmission time

### Epic 5: Irrigation Management

**US-10**: As a crop manager, I want irrigation recommendations based on weather data so that I can optimize water usage.  
**Acceptance Criteria**:
- System analyzes soil moisture, temperature, and rainfall
- API endpoint provides irrigation schedule recommendations
- Recommendations consider crop type and growth stage
- System calculates estimated water requirements
- CLI command available for quick recommendations

**US-11**: As a farm owner, I want to track water savings from data-driven irrigation so that I can measure ROI.  
**Acceptance Criteria**:
- System logs irrigation events
- API provides water usage reports
- Comparison with baseline/traditional irrigation methods
- Reports show cost savings
- Reports accessible via CLI and API

### Epic 6: CLI & Developer Tools

**US-12**: As a system administrator, I want a CLI tool to manage IoT devices so that I can register, configure, and monitor devices efficiently.  
**Acceptance Criteria**:
- CLI supports device registration and removal
- Device configuration can be updated via CLI
- Device status and health viewable in CLI
- Commands follow standard CLI conventions

**US-13**: As a developer, I want a Postman collection with all API endpoints so that I can quickly test and understand the API.  
**Acceptance Criteria**:
- Collection includes all REST API endpoints
- Example requests and responses included
- Environment variables configured for easy testing
- Collection organized by functional area
- Authentication examples included

## Value Proposition

### For Farmers
- **Reduce Water Costs**: 20-30% reduction in irrigation water usage
- **Increase Yields**: 10-15% improvement through optimized growing conditions
- **Save Time**: Automated monitoring eliminates manual weather checking
- **Reduce Risk**: Early warning alerts prevent weather-related crop damage

### For Agricultural Consultants
- **Data-Driven Advice**: Provide recommendations based on actual field data
- **Client Retention**: Offer value-added services through technology
- **Scalability**: Monitor multiple client locations from single platform
- **Professional Credibility**: Leverage IoT technology for competitive advantage

### For Researchers
- **Quality Data**: Access to verified, real-time agricultural weather data
- **Long-Term Trends**: Multi-season datasets for climate studies
- **Spatial Analysis**: Compare data across different geographical locations
- **Research Efficiency**: API access enables automated data collection

## Success Metrics

### Technical Metrics
- **Device Uptime**: >99% connectivity and data transmission
- **API Reliability**: 99.9% availability
- **Data Accuracy**: Sensor readings within manufacturer specifications
- **Response Time**: API queries return within 3 seconds

### Business Metrics
- **User Adoption**: 100 active devices within first 6 months
- **Customer Satisfaction**: >4.5/5 rating
- **Water Savings**: Average 25% reduction in irrigation water usage
- **ROI Period**: Users achieve positive ROI within 1 growing season

### Agricultural Impact Metrics
- **Yield Improvement**: Average 12% increase in crop yields
- **Cost Reduction**: 15-20% reduction in water and labor costs
- **Risk Mitigation**: 50% reduction in weather-related crop losses
- **Decision Speed**: Reduce time from data collection to action by 80%

## Technical Architecture

### Platform Components

1. **IoT Device Simulator**
   - Simulates weather sensors (temperature, humidity, rainfall, soil moisture, wind speed)
   - Sends data via MQTT protocol to cloud
   - Configurable data generation intervals

2. **Cloud Infrastructure (Azure)**
   - Azure IoT Hub for device connectivity
   - Azure Blob Storage for data persistence
   - Azure Functions for data processing (optional)

3. **REST API Backend**
   - Python-based (Flask/FastAPI)
   - Endpoints for data retrieval, device management, analytics
   - JWT/API key authentication
   - JSON response format

4. **CLI Tool**
   - Python-based command-line interface
   - Commands for data query, device management, reports
   - Cross-platform (Windows, Linux, macOS)
   - Config file support for credentials

5. **Postman Collection**
   - Complete API endpoint coverage
   - Example requests/responses
   - Environment variables setup
   - Testing scenarios

### Example CLI Commands
```
# Get current weather for device
agriweather get-current --device-id DEVICE001

# Get historical data
agriweather get-history --device-id DEVICE001 --from 2025-10-01 --to 2025-10-29

# Register new device
agriweather register-device --name "Field A Sensor" --location "40.7128,-74.0060"

# Get irrigation recommendation
agriweather recommend-irrigation --device-id DEVICE001 --crop-type wheat

# List all devices
agriweather list-devices
```

### Example API Endpoints
```
GET    /api/devices                    # List all devices
GET    /api/devices/{id}/current       # Current readings
GET    /api/devices/{id}/history       # Historical data
POST   /api/devices                    # Register device
GET    /api/analytics/irrigation       # Irrigation recommendations
GET    /api/analytics/aggregated       # Aggregated data (daily/weekly/monthly)
GET    /api/health                     # System health check
```

## Future Enhancements

1. **Machine Learning Integration**: Predictive analytics for weather forecasting and crop recommendations
2. **Multi-Sensor Support**: Expand to include soil pH, nutrient levels, and pest detection
3. **Web Dashboard**: Optional web interface for visualization
4. **Mobile Applications**: Native iOS/Android apps for farmers
5. **Integration Capabilities**: Connect with existing farm management systems
6. **Automated Actions**: Trigger irrigation systems automatically based on sensor data
7. **Community Features**: Share weather data and insights with neighboring farms

---

**Document Version**: 1.0  
**Last Updated**: October 29, 2025  
**Project**: AgriWeather IoT Platform  
**Course**: IoT & Cloud Computing

