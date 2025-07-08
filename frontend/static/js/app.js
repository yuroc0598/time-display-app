async function updateTime() {
    try {
        const response = await fetch('/api/time');
        const data = await response.json();
        
        // Update main time display
        document.getElementById('time-display').textContent = `Los Angeles Time: ${data.current_time}`;
        
        // Update world clock
        const worldClockDiv = document.getElementById('world-clock');
        if (data.world_times) {
            let worldClockHTML = '<h2>World Clock</h2><div class="timezone-grid">';
            
            for (const [city, timeInfo] of Object.entries(data.world_times)) {
                worldClockHTML += `
                    <div class="timezone-card">
                        <h3>${city}</h3>
                        <div class="time">${timeInfo.time}</div>
                        <div class="date">${timeInfo.date}</div>
                        <div class="offset">UTC${timeInfo.offset}</div>
                    </div>
                `;
            }
            
            worldClockHTML += '</div>';
            worldClockDiv.innerHTML = worldClockHTML;
        }
    } catch (error) {
        document.getElementById('time-display').textContent = 'Error loading time';
        document.getElementById('world-clock').innerHTML = '<p>Error loading world clock</p>';
    }
}

// Update time on page load
updateTime();

// Auto-refresh every second for realtime updates
setInterval(updateTime, 1000);