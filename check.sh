#!/bin/bash
set -e

echo "🔍 Running linting checks..."
uv run ruff check backend/

echo "✨ Running code formatting..."
uv run ruff format backend/

echo "🧪 Running tests..."
cd backend && uv run pytest -v && cd ..

echo "🐳 Testing Docker build..."
docker build -t time-app-test .

echo "✅ All checks passed! Ready to push to GitHub."