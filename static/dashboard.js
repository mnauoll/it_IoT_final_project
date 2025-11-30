const API_BASE_URL = 'http://localhost:5000';

async function loadDashboard() {
    await Promise.all([
        loadStats(),
        loadDevices(),
        loadRecentAlerts(),
        loadDeviceStatusTable()
    ]);
}

async function loadStats() {
    try {
        const devicesResponse = await fetch(`${API_BASE_URL}/api/devices`);
        const devicesData = await devicesResponse.json();
        
        const onlineCount = devicesData.devices.filter(d => d.status === 'online').length;
        
        const alertsResponse = await fetch(`${API_BASE_URL}/api/alerts?limit=100`);
        const alertsData = await alertsResponse.json();
        
        const criticalAlerts = alertsData.alerts.filter(a => a.severity === 'critical' || a.severity === 'warning').length;
        
        document.getElementById('total-devices').textContent = devicesData.count;
        document.getElementById('online-devices').textContent = onlineCount;
        document.getElementById('active-alerts').textContent = criticalAlerts;
        document.getElementById('polling-status').textContent = 'Active';
        document.getElementById('last-update').textContent = new Date().toLocaleString();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadDevices() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices`);
        const data = await response.json();
        
        const container = document.getElementById('devices-list');
        container.innerHTML = '';
        
        if (data.devices.length === 0) {
            container.innerHTML = '<p>No devices registered</p>';
            return;
        }
        
        data.devices.forEach(device => {
            const statusClass = device.status === 'online' ? 'status-online' : 'status-offline';
            const deviceDiv = document.createElement('div');
            deviceDiv.style.cssText = 'padding: 10px; border-bottom: 1px solid #eee;';
            deviceDiv.innerHTML = `
                <strong>${device.name || device.device_id}</strong>
                <span class="${statusClass}" style="float: right; padding: 5px 15px; border-radius: 20px; font-size: 0.85em;">${device.status}</span>
                <div style="color: #666; font-size: 0.9em; margin-top: 5px;">${device.device_id}</div>
                <div style="margin-top: 8px;">
                    <a href="/device/${device.device_id}" style="color: #3498db; text-decoration: none; font-weight: bold;">View Details →</a>
                </div>
            `;
            container.appendChild(deviceDiv);
        });
    } catch (error) {
        document.getElementById('devices-list').innerHTML = '<p class="error">Error loading devices</p>';
    }
}

async function loadRecentAlerts() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/alerts?limit=10`);
        const data = await response.json();
        
        const container = document.getElementById('recent-alerts');
        container.innerHTML = '';
        
        if (data.alerts.length === 0) {
            container.innerHTML = '<p style="color: #28a745;">No recent alerts</p>';
            return;
        }
        
        data.alerts.forEach(alert => {
            const alertDiv = document.createElement('div');
            alertDiv.style.cssText = 'padding: 10px; border-left: 4px solid #ccc; margin-bottom: 10px; background: #f8f9fa;';
            
            if (alert.severity === 'critical') {
                alertDiv.style.borderLeftColor = '#dc3545';
                alertDiv.style.background = '#f8d7da';
            } else if (alert.severity === 'warning') {
                alertDiv.style.borderLeftColor = '#ffc107';
                alertDiv.style.background = '#fff3cd';
            }
            
            const time = new Date(alert.timestamp).toLocaleString();
            alertDiv.innerHTML = `
                <strong>${alert.message}</strong>
                <div style="color: #666; font-size: 0.85em; margin-top: 5px;">
                    ${alert.device_id} - ${time}
                </div>
            `;
            container.appendChild(alertDiv);
        });
    } catch (error) {
        document.getElementById('recent-alerts').innerHTML = '<p class="error">Error loading alerts</p>';
    }
}

async function loadDeviceStatusTable() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/devices`);
        const data = await response.json();
        
        let html = '<table><thead><tr><th>Device</th><th>Status</th><th>Last Reading</th><th>Location</th></tr></thead><tbody>';
        
        for (const device of data.devices) {
            const statusResponse = await fetch(`${API_BASE_URL}/api/devices/${device.device_id}/status`);
            const statusData = await statusResponse.json();
            
            const lastSeen = statusData.last_seen ? new Date(statusData.last_seen).toLocaleString() : 'Never';
            const statusClass = statusData.status === 'online' ? 'status-online' : 'status-offline';
            
            html += `<tr>
                <td><a href="/device/${device.device_id}" style="color: #3498db; text-decoration: none; font-weight: bold;">${device.name || device.device_id}</a></td>
                <td><span class="${statusClass}" style="padding: 5px 15px; border-radius: 20px; font-size: 0.85em;">${statusData.status}</span></td>
                <td>${lastSeen}</td>
                <td>${device.location?.latitude || 'N/A'}, ${device.location?.longitude || 'N/A'}</td>
            </tr>`;
        }
        
        html += '</tbody></table>';
        document.getElementById('device-status-table').innerHTML = html;
    } catch (error) {
        document.getElementById('device-status-table').innerHTML = '<p class="error">Error loading device status</p>';
    }
}

window.onload = () => {
    loadDashboard();
    setInterval(loadDashboard, 30000);
};

