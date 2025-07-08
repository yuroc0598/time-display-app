# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a world clock web application with a FastAPI backend and vanilla HTML/CSS/JS frontend. The application displays current time in multiple timezones via REST API and includes health/metrics endpoints for Kubernetes monitoring.

## Development Commands

- **Install dependencies**: `uv sync` (uses uv package manager)
- **Run backend locally**: `cd backend && uv run uvicorn main:app --reload`
- **Run all checks**: `./check.sh` (linting, formatting, tests, Docker build)
- **Lint code**: `uv run ruff check backend/`
- **Format code**: `uv run ruff format backend/`
- **Run tests**: `cd backend && uv run pytest -v`
- **Test Docker build**: `docker build -t time-app-test .`

## Architecture

### Backend Structure
- `backend/main.py`: FastAPI application with endpoints:
  - `/api/time`: Returns current time and world clock data for 6 major cities
  - `/health`: Health check for Kubernetes liveness probes
  - `/ready`: Readiness check for Kubernetes readiness probes
  - `/metrics`: Basic metrics endpoint for Prometheus
  - `/`: Serves the frontend HTML file
- `backend/test_main.py`: Test suite using pytest and FastAPI TestClient
- Static files are served from `../frontend/static/`

### Frontend Structure
- `frontend/index.html`: Main HTML page with world clock display
- `frontend/static/css/style.css`: Modern styling with responsive grid layout
- `frontend/static/js/app.js`: JavaScript for fetching time data and updating world clock display

### Configuration
- Uses `pyproject.toml` for Python dependencies and tool configuration
- Ruff configured for Python 3.12+ with specific linting rules
- Pytest configured to run tests from `backend/` directory

## Deployment

### GitHub Actions CI/CD
- **Development**: Automatic deployment on push to main branch
- **Staging**: Triggered after successful dev deployment
- **Production**: Manual deployment with confirmation required

### GCP Infrastructure
- **Project ID**: `archie-465300`
- **Clusters**: `archie-dev`, `archie-staging`, `archie-production`
- **Domains**: 
  - Dev: `dev.34.120.50.114.nip.io`
  - Staging: `staging.34.49.96.120.nip.io`
  - Production: `prod.34.120.176.88.nip.io`

### Kubernetes
- Uses Kustomize for environment-specific configurations
- Base manifests in `k8s/base/`: deployment, service, HPA, ingress
- Environment overlays in `k8s/dev/`, `k8s/staging/`, `k8s/prod/`
- Monitoring setup with Prometheus and Grafana in `k8s/monitoring/`

### Docker
- Multi-stage build copying frontend and backend
- Runs on port 8000 with uvicorn server
- Uses Python 3.13-slim base image

## World Clock Features

The application displays time for these cities:
- New York (America/New_York)
- London (Europe/London)
- Tokyo (Asia/Tokyo)
- Sydney (Australia/Sydney)
- Los Angeles (America/Los_Angeles)
- Dubai (Asia/Dubai)

Each timezone shows:
- Current time (HH:MM:SS)
- Current date (YYYY-MM-DD)
- UTC offset
- Responsive card layout with hover effects

## Important Notes

- The application expects frontend files to be accessible via relative paths from the backend
- Environment variable `ENVIRONMENT` is used for health checks and metrics
- Use `uv` package manager instead of pip for dependency management
- All Python code should follow ruff formatting and linting rules
- SSL certificates are managed by Google Cloud and use nip.io domains for testing