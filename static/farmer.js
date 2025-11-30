const API_BASE_URL = 'http://localhost:5000';
let selectedDeviceId = null;

async function loadData() {
    try {
        await loadDevices();
    } catch (error) {
        showError('Failed to connect to API server. Make sure it is running on http://localhost:5000');
    }
}

async function loadDevices() {
    const response = await fetch(`${API_BASE_URL}/api/devices`);
    const data = await response.json();
    
    const container = document.getElementById('devices-container');
    container.innerHTML = '';
    
    if (data.devices.length === 0) {
        container.innerHTML = '<p>No devices registered</p>';
        return;
    }
    
    data.devices.forEach(device => {
        const deviceDiv = document.createElement('div');
        deviceDiv.className = 'device-item';
        deviceDiv.onclick = () => selectDevice(device.device_id);
        
        const statusClass = device.status === 'online' ? 'status-online' : 'status-offline';
        
        deviceDiv.innerHTML = `
            <div class="device-header">
                <span class="device-name">${device.name || device.device_id}</span>
                <span class="device-status ${statusClass}">${device.status || 'unknown'}</span>
            </div>
            <div style="color: #666; font-size: 0.9em;">
                ID: ${device.device_id}<br>
                Location: ${device.location?.latitude || 'N/A'}, ${device.location?.longitude || 'N/A'}
            </div>
            <div style="margin-top: 10px;">
                <a href="/device/${device.device_id}" style="color: #3498db; text-decoration: none; font-weight: bold;">View Details →</a>
            </div>
        `;
        
        container.appendChild(deviceDiv);
    });
    
    if (!selectedDeviceId && data.devices.length > 0) {
        selectDevice(data.devices[0].device_id);
    }
}

async function selectDevice(deviceId) {
    selectedDeviceId = deviceId;
    
    document.querySelectorAll('.device-item').forEach(item => {
        item.classList.remove('active');
    });
    
    document.getElementById('device-details').style.display = 'block';
    
    await Promise.all([
        loadCurrentWeather(deviceId),
        loadAlerts(deviceId),
        loadIrrigationRecommendation(deviceId),
        loadHistory(deviceId)
    ]);
}

async function loadAlerts(deviceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/alerts?limit=10`);
        if (!response.ok) {
            document.getElementById('alerts-list').innerHTML = '<p>No alerts available</p>';
            return;
        }
        
        const data = await response.json();
        
        if (data.alerts.length === 0) {
            document.getElementById('alerts-list').innerHTML = '<p style="color: #28a745;">✓ No active alerts. All conditions are normal.</p>';
            document.getElementById('alert-banner').classList.remove('show');
            return;
        }
        
        const hasCritical = data.has_critical;
        const hasWarnings = data.has_warnings;
        
        if (hasCritical) {
            showAlertBanner('critical', 'Critical alerts detected! Check the alerts section below.');
        } else if (hasWarnings) {
            showAlertBanner('warning', 'Warning alerts detected. Review conditions below.');
        }
        
        let html = '';
        data.alerts.slice().reverse().forEach(alert => {
            const time = new Date(alert.timestamp).toLocaleString();
            html += `
                <div class="alert-item ${alert.severity}">
                    <strong>${alert.message}</strong>
                    <div class="alert-time">${time}</div>
                </div>
            `;
        });
        
        document.getElementById('alerts-list').innerHTML = html;
    } catch (error) {
        document.getElementById('alerts-list').innerHTML = '<p class="error">Error loading alerts</p>';
    }
}

function showAlertBanner(type, message) {
    const banner = document.getElementById('alert-banner');
    banner.className = `alert-banner ${type} show`;
    banner.textContent = message;
}

async function loadCurrentWeather(deviceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/current`);
        if (!response.ok) {
            document.getElementById('current-weather').innerHTML = '<p>No data available</p>';
            return;
        }
        
        const data = await response.json();
        
        document.getElementById('current-weather').innerHTML = `
            <div class="stat">
                <span class="stat-label">Temperature</span>
                <span class="stat-value">${data.temperature || 'N/A'}°C</span>
            </div>
            <div class="stat">
                <span class="stat-label">Humidity</span>
                <span class="stat-value">${data.humidity || 'N/A'}%</span>
            </div>
            <div class="stat">
                <span class="stat-label">Rainfall</span>
                <span class="stat-value">${data.rainfall || 0} mm/h</span>
            </div>
            <div class="stat">
                <span class="stat-label">Last Update</span>
                <span class="stat-value" style="font-size: 0.85em;">${new Date(data.timestamp).toLocaleString()}</span>
            </div>
        `;
        
        document.getElementById('soil-water').innerHTML = `
            <div class="stat">
                <span class="stat-label">Soil Moisture</span>
                <span class="stat-value">${data.soil_moisture || 'N/A'}%</span>
            </div>
            <div class="stat">
                <span class="stat-label">Rainfall Rate</span>
                <span class="stat-value">${data.rainfall || 0} mm/h</span>
            </div>
        `;
        
        document.getElementById('wind-info').innerHTML = `
            <div class="stat">
                <span class="stat-label">Wind Speed</span>
                <span class="stat-value">${data.wind_speed || 'N/A'} km/h</span>
            </div>
        `;
    } catch (error) {
        document.getElementById('current-weather').innerHTML = '<p class="error">Error loading data</p>';
    }
}

async function loadIrrigationRecommendation(deviceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/analytics/irrigation?device_id=${deviceId}&crop_type=general`);
        if (!response.ok) {
            document.getElementById('irrigation-recommendation').innerHTML = '<p>No recommendation available</p>';
            return;
        }
        
        const data = await response.json();
        const needsIrrigation = data.needs_irrigation;
        const className = needsIrrigation ? 'irrigation-recommendation irrigation-needed' : 'irrigation-recommendation';
        
        document.getElementById('irrigation-recommendation').innerHTML = `
            <div class="${className}">
                <strong>${data.recommendation || 'No recommendation'}</strong>
                ${needsIrrigation ? `<br><br>Suggested water amount: ${data.suggested_water_amount_liters || 0} liters` : ''}
            </div>
            <div style="margin-top: 15px;">
                <div class="stat">
                    <span class="stat-label">Current Soil Moisture</span>
                    <span class="stat-value">${data.current_conditions?.soil_moisture || 'N/A'}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Temperature</span>
                    <span class="stat-value">${data.current_conditions?.temperature || 'N/A'}°C</span>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('irrigation-recommendation').innerHTML = '<p class="error">Error loading recommendation</p>';
    }
}

async function loadHistory(deviceId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/history?limit=10`);
        if (!response.ok) {
            document.getElementById('history-chart').innerHTML = '<p>No historical data available</p>';
            return;
        }
        
        const data = await response.json();
        
        if (data.readings.length === 0) {
            document.getElementById('history-chart').innerHTML = '<p>No historical data available</p>';
            return;
        }
        
        let html = '<table style="width: 100%; border-collapse: collapse;">';
        html += '<thead><tr style="background: #f5f5f5;"><th style="padding: 10px; text-align: left;">Time</th><th style="padding: 10px; text-align: left;">Temp</th><th style="padding: 10px; text-align: left;">Humidity</th><th style="padding: 10px; text-align: left;">Rainfall</th><th style="padding: 10px; text-align: left;">Soil</th></tr></thead><tbody>';
        
        data.readings.slice().reverse().forEach(reading => {
            const time = new Date(reading.timestamp).toLocaleString();
            html += `<tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 8px;">${time}</td>
                <td style="padding: 8px;">${reading.temperature}°C</td>
                <td style="padding: 8px;">${reading.humidity}%</td>
                <td style="padding: 8px;">${reading.rainfall} mm/h</td>
                <td style="padding: 8px;">${reading.soil_moisture}%</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        document.getElementById('history-chart').innerHTML = html;
    } catch (error) {
        document.getElementById('history-chart').innerHTML = '<p class="error">Error loading history</p>';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

window.onload = () => {
    loadData();
    setInterval(() => {
        if (selectedDeviceId) {
            loadCurrentWeather(selectedDeviceId);
            loadAlerts(selectedDeviceId);
        }
    }, 30000);
};

