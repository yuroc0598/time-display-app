async function updateTime() {
    try {
        const response = await fetch('/api/time');
        const data = await response.json();
        document.getElementById('time-display').textContent = data.current_time;
    } catch (error) {
        document.getElementById('time-display').textContent = 'Error loading time';
    }
}

// Update time on page load
updateTime();

// Auto-refresh every second for realtime updates
setInterval(updateTime, 1000);