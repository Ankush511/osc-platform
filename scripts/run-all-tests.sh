#!/bin/bash

# Comprehensive test runner script
# Runs all tests and generates coverage reports

set -e

echo "=========================================="
echo "Running Comprehensive Test Suite"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
BACKEND_STATUS=0
FRONTEND_STATUS=0
E2E_STATUS=0

# Backend Tests
echo ""
echo "${YELLOW}[1/3] Running Backend Tests...${NC}"
echo "=========================================="
cd backend

if pytest --cov=app --cov-report=term-missing --cov-report=html -v; then
    echo "${GREEN}✓ Backend tests passed${NC}"
else
    echo "${RED}✗ Backend tests failed${NC}"
    BACKEND_STATUS=1
fi

cd ..

# Frontend Tests
echo ""
echo "${YELLOW}[2/3] Running Frontend Tests...${NC}"
echo "=========================================="
cd frontend

if npm test -- --coverage; then
    echo "${GREEN}✓ Frontend tests passed${NC}"
else
    echo "${RED}✗ Frontend tests failed${NC}"
    FRONTEND_STATUS=1
fi

# E2E Tests (optional, requires servers running)
echo ""
echo "${YELLOW}[3/3] Running E2E Tests...${NC}"
echo "=========================================="
echo "Note: E2E tests require backend and frontend servers to be running"
echo "Skipping E2E tests in this script. Run manually with: npm run test:e2e"
E2E_STATUS=0

cd ..

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="

if [ $BACKEND_STATUS -eq 0 ]; then
    echo "${GREEN}✓ Backend: PASSED${NC}"
else
    echo "${RED}✗ Backend: FAILED${NC}"
fi

if [ $FRONTEND_STATUS -eq 0 ]; then
    echo "${GREEN}✓ Frontend: PASSED${NC}"
else
    echo "${RED}✗ Frontend: FAILED${NC}"
fi

echo "${YELLOW}⊘ E2E: SKIPPED (run manually)${NC}"

echo ""
echo "Coverage Reports:"
echo "  Backend:  backend/htmlcov/index.html"
echo "  Frontend: frontend/coverage/index.html"

# Exit with error if any tests failed
if [ $BACKEND_STATUS -ne 0 ] || [ $FRONTEND_STATUS -ne 0 ]; then
    echo ""
    echo "${RED}Some tests failed. Please fix before committing.${NC}"
    exit 1
else
    echo ""
    echo "${GREEN}All tests passed! ✓${NC}"
    exit 0
fi
