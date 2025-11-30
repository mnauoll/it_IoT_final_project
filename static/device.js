const API_BASE_URL = window.location.origin;

let deviceId = null;
let historyChart = null;

function getDeviceIdFromUrl() {
    const path = window.location.pathname;
    const match = path.match(/\/device\/([^\/]+)/);
    return match ? match[1] : null;
}

async function loadAllData() {
    deviceId = getDeviceIdFromUrl();
    if (!deviceId) {
        showError('Device ID not found in URL');
        return;
    }

    try {
        await Promise.all([
            loadDeviceInfo(),
            loadCurrentData(),
            loadAlerts(),
            loadIrrigationRecommendation(),
            loadHistory()
        ]);
    } catch (error) {
        showError('Failed to load device data');
    }
}

async function loadDeviceInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}`);
        if (!response.ok) {
            throw new Error('Device not found');
        }
        
        const device = await response.json();
        
        document.getElementById('device-name').textContent = device.name || device.device_id;
        document.getElementById('device-id').textContent = `ID: ${device.device_id}`;
        
        const statusBadge = document.getElementById('device-status');
        statusBadge.textContent = device.status || 'unknown';
        statusBadge.className = `status-badge ${device.status === 'online' ? 'status-online' : 'status-offline'}`;
        
        const location = device.location;
        if (location) {
            document.getElementById('device-location').textContent = 
                `Location: ${location.latitude}, ${location.longitude}`;
        }
    } catch (error) {
        showError('Error loading device information');
    }
}

async function loadCurrentData() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/current`);
        if (!response.ok) {
            throw new Error('No data available');
        }
        
        const data = await response.json();
        
        document.getElementById('sensor-temperature').textContent = 
            data.temperature !== undefined ? data.temperature.toFixed(1) : '-';
        document.getElementById('sensor-humidity').textContent = 
            data.humidity !== undefined ? data.humidity.toFixed(1) : '-';
        document.getElementById('sensor-rainfall').textContent = 
            data.rainfall !== undefined ? data.rainfall.toFixed(1) : '-';
        document.getElementById('sensor-soil').textContent = 
            data.soil_moisture !== undefined ? data.soil_moisture.toFixed(1) : '-';
        document.getElementById('sensor-wind').textContent = 
            data.wind_speed !== undefined ? data.wind_speed.toFixed(1) : '-';
        document.getElementById('sensor-timestamp').textContent = 
            new Date(data.timestamp).toLocaleString('en-US');
    } catch (error) {
        showError('Error loading current sensor data');
    }
}

async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/alerts?limit=20`);
        if (!response.ok) {
            document.getElementById('alerts-list').innerHTML = '<p>No alerts available</p>';
            return;
        }
        
        const data = await response.json();
        
        if (data.alerts.length === 0) {
            document.getElementById('alerts-list').innerHTML = 
                '<p style="color: #28a745;">✓ No active alerts. All conditions are normal.</p>';
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
            const time = new Date(alert.timestamp).toLocaleString('en-US');
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

async function loadIrrigationRecommendation() {
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
                <div class="stat-row">
                    <span class="stat-label">Current Soil Moisture:</span>
                    <span class="stat-value">${data.current_conditions?.soil_moisture || 'N/A'}%</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Temperature:</span>
                    <span class="stat-value">${data.current_conditions?.temperature || 'N/A'}°C</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Rainfall:</span>
                    <span class="stat-value">${data.current_conditions?.rainfall || 'N/A'} mm/h</span>
                </div>
            </div>
        `;
    } catch (error) {
        document.getElementById('irrigation-recommendation').innerHTML = '<p class="error">Error loading recommendation</p>';
    }
}

async function loadHistory() {
    const limit = parseInt(document.getElementById('history-limit').value) || 20;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices/${deviceId}/history?limit=${limit}`);
        if (!response.ok) {
            document.getElementById('readings-table').innerHTML = '<p>No historical data available</p>';
            return;
        }
        
        const data = await response.json();
        
        if (data.readings.length === 0) {
            document.getElementById('readings-table').innerHTML = '<p>No historical data available</p>';
            if (historyChart) {
                historyChart.destroy();
                historyChart = null;
            }
            return;
        }
        
        const readings = data.readings.slice().reverse();
        
        updateHistoryChart(readings);
        updateReadingsTable(readings);
    } catch (error) {
        document.getElementById('readings-table').innerHTML = '<p class="error">Error loading history</p>';
    }
}

function updateHistoryChart(readings) {
    const ctx = document.getElementById('history-chart').getContext('2d');
    
    const labels = readings.map(r => new Date(r.timestamp).toLocaleString('en-US'));
    const temperatures = readings.map(r => r.temperature);
    const humidities = readings.map(r => r.humidity);
    const soilMoistures = readings.map(r => r.soil_moisture);
    
    if (historyChart) {
        historyChart.destroy();
    }
    
    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatures,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Humidity (%)',
                    data: humidities,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Soil Moisture (%)',
                    data: soilMoistures,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Historical Sensor Data'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: false
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: false,
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

function updateReadingsTable(readings) {
    let html = '<table class="readings-table">';
    html += '<thead><tr>';
    html += '<th>Time</th>';
    html += '<th>Temperature</th>';
    html += '<th>Humidity</th>';
    html += '<th>Rainfall</th>';
    html += '<th>Soil Moisture</th>';
    html += '<th>Wind Speed</th>';
    html += '</tr></thead><tbody>';
    
    readings.forEach(reading => {
        const time = new Date(reading.timestamp).toLocaleString('en-US');
        html += `<tr>
            <td>${time}</td>
            <td>${reading.temperature?.toFixed(1) || 'N/A'}°C</td>
            <td>${reading.humidity?.toFixed(1) || 'N/A'}%</td>
            <td>${reading.rainfall?.toFixed(1) || '0'} mm/h</td>
            <td>${reading.soil_moisture?.toFixed(1) || 'N/A'}%</td>
            <td>${reading.wind_speed?.toFixed(1) || 'N/A'} km/h</td>
        </tr>`;
    });
    
    html += '</tbody></table>';
    document.getElementById('readings-table').innerHTML = html;
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
    loadAllData();
    setInterval(() => {
        loadCurrentData();
        loadAlerts();
    }, 30000);
};

