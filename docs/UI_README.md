# AgriWeather Web Interface

## Launch

1. Make sure the API server is running:
   ```powershell
   cd project\it_IoT_final_project
   python src\api_server.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Web Interface Features

### 1. Devices
- View all registered devices
- Information about status, location, and latest readings

### 2. Current Data
- View current readings for selected device
- Display temperature, humidity, rainfall, soil moisture, and wind speed

### 3. History
- Historical data charts
- Configure number of records to display
- Visualization of temperature, humidity, and soil moisture changes

### 4. Analytics
- Statistics for selected period (day/week/month)
- Minimum, maximum, and average values
- Total rainfall

### 5. Irrigation
- Irrigation recommendations based on current conditions
- Information about watering needs
- Recommended water amount

## Technologies

- HTML5
- CSS3 (modern design with gradients)
- JavaScript (ES6+)
- Chart.js for charts
- Flask for API

## File Structure

```
static/
  ├── index.html    # Main page
  ├── style.css     # Styles
  └── app.js        # JavaScript logic
```
