/**
 * 🎨 DevPro Team Notification: 
 * TO: Sarah Zoghly (Frontend Developer)
 * PURPOSE: Connects your visual dashboard UI with Maryam's core AI Live Telemetry loop.
 * INSTRUCTION: Include this script into your main HTML dashboard file.
 */

async function updateDashboard() {
    try {
        const response = await fetch('live_status.json');
        const data = await response.json();
        
        const cpuElement = document.getElementById('cpu-gauge');
        if (cpuElement) cpuElement.innerText = `${data.cpu}%`;
        
        const statusLight = document.getElementById('status-light');
        if (statusLight) {
            if (data.status === 'danger') {
                statusLight.style.backgroundColor = 'red';   
                statusLight.innerText = '🔴 DANGER: AI Healing Active';
            } else {
                statusLight.style.backgroundColor = 'green'; 
                statusLight.innerText = '🟢 SYSTEM HEALTHY';
            }
        }
    } catch (error) {
        console.log("Waiting for live AI telemetry pulse stream...");
    }
}

setInterval(updateDashboard, 1000);
