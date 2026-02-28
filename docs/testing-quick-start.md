# Testing Quick Start Guide

Quick reference for running tests in the Open Source Contribution Platform.

## Prerequisites

### Backend
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Frontend
```bash
cd frontend
npm install
npx playwright install  # For E2E tests
```

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_service.py

# Run specific test
pytest tests/test_auth_service.py::TestAuthService::test_create_user

# Run in verbose mode
pytest -v

# Run in parallel (faster)
pytest -n auto
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode (for development)
npm run test:watch

# Run with UI
npm run test:ui

# Run specific test file
npm test IssueCard.test.tsx
```

### E2E Tests

```bash
cd frontend

# Run all E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run in debug mode
npm run test:e2e:debug

# View test report
npm run test:e2e:report

# Run specific test file
npx playwright test e2e/auth.spec.ts

# Run on specific browser
npx playwright test --project=chromium
```

### Load Tests

```bash
cd backend

# Start load test with UI
locust -f locustfile.py --host=http://localhost:8000

# Run headless with 100 users
locust -f locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 5m --headless

# Generate HTML report
locust -f locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 5m \
  --html=load_test_report.html --headless
```

## Quick Commands

### Run All Tests
```bash
# From project root
./scripts/run-all-tests.sh
```

### Check Coverage
```bash
# From project root
./scripts/check-coverage.sh
```

### Pre-commit Checks
```bash
# Backend
cd backend
flake8 app/
mypy app/
pytest

# Frontend
cd frontend
npm run lint
npx tsc --noEmit
npm test
```

## Viewing Coverage Reports

### Backend
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Frontend
```bash
cd frontend
npm run test:coverage
open coverage/index.html
```

## Common Issues

### Backend Tests Fail with Database Errors
```bash
# Reset test database
cd backend
alembic downgrade base
alembic upgrade head
```

### E2E Tests Timeout
Increase timeout in `playwright.config.ts`:
```typescript
timeout: 60000  // 60 seconds
```

### Frontend Tests Fail with Module Errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## CI/CD

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

View results in GitHub Actions tab.

## Coverage Goals

- **Overall**: 80% minimum
- **Critical paths**: 100% (auth, PR validation)

## Need Help?

- Full documentation: [TESTING.md](../TESTING.md)
- Test status: [TEST_STATUS.md](../TEST_STATUS.md)
- Report issues on GitHub

## Test Structure

```
backend/tests/          # Backend unit & integration tests
frontend/src/**/__tests__/  # Frontend component tests
frontend/e2e/           # End-to-end tests
backend/locustfile.py   # Load tests
.github/workflows/ci.yml    # CI/CD pipeline
```

## Tips

1. **Run tests before committing**: Use pre-commit checks
2. **Watch mode for development**: Use `npm run test:watch` or `pytest-watch`
3. **Focus on failing tests**: Use `pytest -x` to stop on first failure
4. **Debug E2E tests**: Use `npm run test:e2e:debug` to step through tests
5. **Check coverage regularly**: Aim to maintain or improve coverage

---

For detailed information, see [TESTING.md](../TESTING.md)
