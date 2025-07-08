import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Application startup time for health checks
app.startup_time = time.time()


@app.get("/api/time")
async def get_current_time():
    """Get current time in multiple timezones for world clock display"""
    timezones = {
        "New York": "America/New_York",
        "London": "Europe/London",
        "Tokyo": "Asia/Tokyo",
        "Sydney": "Australia/Sydney",
        "Los Angeles": "America/Los_Angeles",
        "Dubai": "Asia/Dubai"
    }
    
    world_times = {}
    for city, tz in timezones.items():
        try:
            local_time = datetime.now(ZoneInfo(tz))
            world_times[city] = {
                "time": local_time.strftime("%H:%M:%S"),
                "date": local_time.strftime("%Y-%m-%d"),
                "timezone": tz,
                "offset": local_time.strftime("%z")
            }
        except Exception:
            world_times[city] = {
                "time": "--:--:--",
                "date": "-------",
                "timezone": tz,
                "offset": "N/A"
            }
    
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "world_times": world_times
    }


@app.get("/")
async def read_root():
    return FileResponse("../frontend/index.html")


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for Kubernetes liveness probes"""
    try:
        # Check if the application has been running for at least 1 second
        uptime = time.time() - app.startup_time

        # Check if static files directory exists (handle test environment)
        static_dir_exists = (
            Path("../frontend/static").exists() or Path("frontend/static").exists()
        )

        # Check if main HTML file exists (handle test environment)
        html_file_exists = (
            Path("../frontend/index.html").exists()
            or Path("frontend/index.html").exists()
        )

        # Basic time API functionality test
        current_time = datetime.now()

        health_status = {
            "status": "healthy",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "timestamp": current_time.isoformat(),
            "uptime_seconds": round(uptime, 2),
            "checks": {
                "static_files": static_dir_exists,
                "html_file": html_file_exists,
                "time_service": True,
                "uptime_check": uptime > 1,
            },
        }

        # If any critical check fails, return unhealthy status
        if not all([static_dir_exists, html_file_exists, uptime > 1]):
            health_status["status"] = "unhealthy"
            raise HTTPException(status_code=503, detail=health_status)

        return health_status

    except Exception as e:
        error_response = {
            "status": "unhealthy",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
        raise HTTPException(status_code=503, detail=error_response) from None


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probes"""
    try:
        # Check if the application is ready to serve traffic
        uptime = time.time() - app.startup_time

        # Check if static files are accessible (handle test environment)
        static_dir_exists = (
            Path("../frontend/static").exists() or Path("frontend/static").exists()
        )
        html_file_exists = (
            Path("../frontend/index.html").exists()
            or Path("frontend/index.html").exists()
        )

        # Test the time API functionality
        try:
            test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            time_api_working = bool(test_time)
        except Exception:
            time_api_working = False

        readiness_status = {
            "status": "ready",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": round(uptime, 2),
            "checks": {
                "static_files": static_dir_exists,
                "html_file": html_file_exists,
                "time_api": time_api_working,
                "minimum_uptime": uptime > 0.5,
            },
        }

        # Application is ready if all checks pass
        if not all(
            [static_dir_exists, html_file_exists, time_api_working, uptime > 0.5]
        ):
            readiness_status["status"] = "not_ready"
            raise HTTPException(status_code=503, detail=readiness_status)

        return readiness_status

    except Exception as e:
        error_response = {
            "status": "not_ready",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
        raise HTTPException(status_code=503, detail=error_response) from None


@app.get("/metrics")
async def metrics():
    """Enhanced metrics endpoint for Prometheus"""
    uptime = time.time() - app.startup_time
    return {
        "time_app_requests_total": 1,
        "time_app_health": 1,
        "time_app_uptime_seconds": round(uptime, 2),
        "time_app_ready": 1,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)
