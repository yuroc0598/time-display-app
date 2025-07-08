from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

@app.get("/api/time")
async def get_current_time():
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Current Time</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
            .time-display { font-size: 2em; color: #333; margin: 20px; }
        </style>
    </head>
    <body>
        <h1>Current Time Display</h1>
        <div class="time-display" id="time-display">Loading...</div>
        
        <script>
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
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)