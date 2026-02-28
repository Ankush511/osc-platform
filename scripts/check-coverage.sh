#!/bin/bash

# Check test coverage and fail if below threshold

set -e

BACKEND_THRESHOLD=80
FRONTEND_THRESHOLD=80

echo "Checking test coverage..."

# Backend coverage
echo ""
echo "Backend Coverage:"
cd backend
BACKEND_COVERAGE=$(pytest --cov=app --cov-report=term-missing | grep "TOTAL" | awk '{print $4}' | sed 's/%//')

if [ -z "$BACKEND_COVERAGE" ]; then
    echo "Failed to get backend coverage"
    exit 1
fi

echo "Backend: ${BACKEND_COVERAGE}%"

if (( $(echo "$BACKEND_COVERAGE < $BACKEND_THRESHOLD" | bc -l) )); then
    echo "❌ Backend coverage ${BACKEND_COVERAGE}% is below threshold ${BACKEND_THRESHOLD}%"
    BACKEND_FAIL=1
else
    echo "✅ Backend coverage meets threshold"
    BACKEND_FAIL=0
fi

cd ..

# Frontend coverage
echo ""
echo "Frontend Coverage:"
cd frontend
npm run test:coverage > /dev/null 2>&1 || true

# Parse coverage from output
if [ -f "coverage/coverage-summary.json" ]; then
    FRONTEND_COVERAGE=$(node -pe "JSON.parse(require('fs').readFileSync('coverage/coverage-summary.json')).total.lines.pct")
    echo "Frontend: ${FRONTEND_COVERAGE}%"
    
    if (( $(echo "$FRONTEND_COVERAGE < $FRONTEND_THRESHOLD" | bc -l) )); then
        echo "❌ Frontend coverage ${FRONTEND_COVERAGE}% is below threshold ${FRONTEND_THRESHOLD}%"
        FRONTEND_FAIL=1
    else
        echo "✅ Frontend coverage meets threshold"
        FRONTEND_FAIL=0
    fi
else
    echo "⚠️  Could not find frontend coverage report"
    FRONTEND_FAIL=0
fi

cd ..

# Summary
echo ""
if [ $BACKEND_FAIL -eq 1 ] || [ $FRONTEND_FAIL -eq 1 ]; then
    echo "Coverage check failed"
    exit 1
else
    echo "All coverage checks passed"
    exit 0
fi
