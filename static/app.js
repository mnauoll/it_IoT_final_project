const API_BASE_URL = window.location.origin;

let historyChart = null;

document.addEventListener('DOMContentLoaded', function() {
    setupTabs();
    loadDevices();
    populateDeviceSelects();
});

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            button.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

async function apiRequest(endpoint, options = {}) {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Request error');
        }

        return await response.json();
    } catch (error) {
        showError(error.message);
        throw error;
    } finally {
        hideLoading();
    }
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

async function loadDevices() {
    try {
        const data = await apiRequest('/api/devices');
        displayDevices(data.devices);
        populateDeviceSelects(data.devices);
    } catch (error) {
        console.error('Error loading devices:', error);
    }
}

function displayDevices(devices) {
    const container = document.getElementById('devices-list');
    
    if (!devices || devices.length === 0) {
        container.innerHTML = '<p>No devices found</p>';
        return;
    }

    container.innerHTML = devices.map(device => `
        <div class="device-card">
            <h3>${device.name || device.device_id}</h3>
            <div class="device-info"><strong>ID:</strong> ${device.device_id}</div>
            <div class="device-info">
                <strong>Location:</strong> 
                ${device.location?.latitude || 'N/A'}, ${device.location?.longitude || 'N/A'}
            </div>
            <div class="device-info">
                <strong>Registered:</strong> 
                ${new Date(device.registered_at).toLocaleString('en-US')}
            </div>
            ${device.last_reading ? `
                <div class="device-info">
                    <strong>Last Reading:</strong> 
                    ${new Date(device.last_reading).toLocaleString('en-US')}
                </div>
            ` : ''}
            <span class="device-status ${device.status || 'offline'}">
                ${device.status === 'online' ? 'Online' : 'Offline'}
            </span>
        </div>
    `).join('');
}

function populateDeviceSelects(devices = null) {
    const selects = ['current-device', 'history-device', 'analytics-device', 'irrigation-device'];
    
    if (!devices) {
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            select.innerHTML = '<option value="">Loading...</option>';
        });
        return;
    }

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = devices.map(device => 
            `<option value="${device.device_id}">${device.name || device.device_id}</option>`
        ).join('');
        
        if (devices.length > 0 && !select.value) {
            select.value = devices[0].device_id;
        }
    });
}

async function loadCurrentData() {
    const deviceId = document.getElementById('current-device').value;
    if (!deviceId) {
        showError('Please select a device');
        return;
    }

    try {
        const data = await apiRequest(`/api/devices/${deviceId}/current`);
        displayCurrentData(data);
    } catch (error) {
        console.error('Error loading current data:', error);
    }
}

function displayCurrentData(data) {
    const container = document.getElementById('current-data');
    
    const timestamp = new Date(data.timestamp).toLocaleString('en-US');
    
    container.innerHTML = `
        <div class="sensor-card">
            <h3>Temperature</h3>
            <div class="sensor-value">${data.temperature?.toFixed(1) || 'N/A'}</div>
            <div class="sensor-unit">°C</div>
        </div>
        <div class="sensor-card">
            <h3>Humidity</h3>
            <div class="sensor-value">${data.humidity?.toFixed(1) || 'N/A'}</div>
            <div class="sensor-unit">%</div>
        </div>
        <div class="sensor-card">
            <h3>Rainfall</h3>
            <div class="sensor-value">${data.rainfall?.toFixed(1) || 'N/A'}</div>
            <div class="sensor-unit">mm/h</div>
        </div>
        <div class="sensor-card">
            <h3>Soil Moisture</h3>
            <div class="sensor-value">${data.soil_moisture?.toFixed(1) || 'N/A'}</div>
            <div class="sensor-unit">%</div>
        </div>
        <div class="sensor-card">
            <h3>Wind Speed</h3>
            <div class="sensor-value">${data.wind_speed?.toFixed(1) || 'N/A'}</div>
            <div class="sensor-unit">km/h</div>
        </div>
        <div class="sensor-card">
            <h3>Measurement Time</h3>
            <div class="sensor-value" style="font-size: 1.2em;">${timestamp}</div>
        </div>
    `;
}

async function loadHistory() {
    const deviceId = document.getElementById('history-device').value;
    const limit = parseInt(document.getElementById('history-limit').value) || 20;
    
    if (!deviceId) {
        showError('Please select a device');
        return;
    }

    try {
        const data = await apiRequest(`/api/devices/${deviceId}/history?limit=${limit}`);
        displayHistory(data.readings);
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(readings) {
    if (!readings || readings.length === 0) {
        document.getElementById('history-chart-container').innerHTML = 
            '<p>No historical data found</p>';
        return;
    }

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
                    tension: 0.4
                },
                {
                    label: 'Humidity (%)',
                    data: humidities,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.4
                },
                {
                    label: 'Soil Moisture (%)',
                    data: soilMoistures,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4
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
                    beginAtZero: false
                }
            }
        }
    });
}

async function loadAnalytics() {
    const deviceId = document.getElementById('analytics-device').value;
    const period = document.getElementById('analytics-period').value;
    
    if (!deviceId) {
        showError('Please select a device');
        return;
    }

    try {
        const data = await apiRequest(`/api/analytics/aggregated?device_id=${deviceId}&period=${period}`);
        displayAnalytics(data);
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function displayAnalytics(data) {
    const container = document.getElementById('analytics-data');
    
    container.innerHTML = `
        <div class="analytics-card">
            <h3>Temperature</h3>
            <div class="stat-row">
                <span class="stat-label">Minimum:</span>
                <span class="stat-value">${data.temperature?.min?.toFixed(2) || 'N/A'} °C</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Maximum:</span>
                <span class="stat-value">${data.temperature?.max?.toFixed(2) || 'N/A'} °C</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Average:</span>
                <span class="stat-value">${data.temperature?.avg?.toFixed(2) || 'N/A'} °C</span>
            </div>
        </div>
        <div class="analytics-card">
            <h3>Humidity</h3>
            <div class="stat-row">
                <span class="stat-label">Minimum:</span>
                <span class="stat-value">${data.humidity?.min?.toFixed(2) || 'N/A'} %</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Maximum:</span>
                <span class="stat-value">${data.humidity?.max?.toFixed(2) || 'N/A'} %</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Average:</span>
                <span class="stat-value">${data.humidity?.avg?.toFixed(2) || 'N/A'} %</span>
            </div>
        </div>
        <div class="analytics-card">
            <h3>Rainfall</h3>
            <div class="stat-row">
                <span class="stat-label">Total:</span>
                <span class="stat-value">${data.rainfall?.total?.toFixed(2) || 'N/A'} mm</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Average:</span>
                <span class="stat-value">${data.rainfall?.avg?.toFixed(2) || 'N/A'} mm/h</span>
            </div>
        </div>
        <div class="analytics-card">
            <h3>General Statistics</h3>
            <div class="stat-row">
                <span class="stat-label">Period:</span>
                <span class="stat-value">${data.period || 'N/A'}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Total Readings:</span>
                <span class="stat-value">${data.readings_count || 0}</span>
            </div>
        </div>
    `;
}

async function loadIrrigation() {
    const deviceId = document.getElementById('irrigation-device').value;
    const cropType = document.getElementById('irrigation-crop').value || 'general';
    
    if (!deviceId) {
        showError('Please select a device');
        return;
    }

    try {
        const data = await apiRequest(`/api/analytics/irrigation?device_id=${deviceId}&crop_type=${cropType}`);
        displayIrrigation(data);
    } catch (error) {
        console.error('Error loading recommendations:', error);
    }
}

function displayIrrigation(data) {
    const container = document.getElementById('irrigation-data');
    const conditions = data.current_conditions;
    const needsIrrigation = data.needs_irrigation;
    
    container.innerHTML = `
        <div class="irrigation-card">
            <h3>Current Conditions</h3>
            <div class="stat-row">
                <span class="stat-label">Soil Moisture:</span>
                <span class="stat-value">${conditions.soil_moisture?.toFixed(1) || 'N/A'} %</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Temperature:</span>
                <span class="stat-value">${conditions.temperature?.toFixed(1) || 'N/A'} °C</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Rainfall:</span>
                <span class="stat-value">${conditions.rainfall?.toFixed(1) || 'N/A'} mm/h</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Air Humidity:</span>
                <span class="stat-value">${conditions.humidity?.toFixed(1) || 'N/A'} %</span>
            </div>
            
            <div class="recommendation ${needsIrrigation ? 'irrigation-needed' : 'no-irrigation'}">
                <h4>Recommendation:</h4>
                <p>${data.recommendation || 'No data'}</p>
                ${needsIrrigation ? `
                    <p style="margin-top: 10px; font-weight: bold;">
                        Recommended water amount: ${data.suggested_water_amount_liters?.toFixed(2) || 'N/A'} liters
                    </p>
                ` : ''}
            </div>
        </div>
    `;
}
