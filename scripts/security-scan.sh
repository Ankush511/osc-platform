#!/bin/bash

# Security vulnerability assessment script
# This script runs various security checks on the application

set -e

echo "=========================================="
echo "Security Vulnerability Assessment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}Error: Must be run from project root${NC}"
    exit 1
fi

echo "1. Checking Python dependencies for known vulnerabilities..."
echo "------------------------------------------------------"
cd backend

# Install safety if not present
pip install safety --quiet

# Check for known vulnerabilities
if safety check --json > /tmp/safety-report.json 2>&1; then
    echo -e "${GREEN}✓ No known vulnerabilities found in Python dependencies${NC}"
else
    echo -e "${YELLOW}⚠ Vulnerabilities found in Python dependencies${NC}"
    cat /tmp/safety-report.json
fi

echo ""
echo "2. Checking for hardcoded secrets..."
echo "------------------------------------------------------"

# Check for potential secrets in code
if command -v grep &> /dev/null; then
    # Look for common secret patterns
    SECRET_PATTERNS=(
        "password\s*=\s*['\"][^'\"]+['\"]"
        "api_key\s*=\s*['\"][^'\"]+['\"]"
        "secret\s*=\s*['\"][^'\"]+['\"]"
        "token\s*=\s*['\"][^'\"]+['\"]"
    )
    
    SECRETS_FOUND=0
    for pattern in "${SECRET_PATTERNS[@]}"; do
        if grep -r -i -E "$pattern" app/ --exclude-dir=__pycache__ --exclude="*.pyc" 2>/dev/null; then
            SECRETS_FOUND=1
        fi
    done
    
    if [ $SECRETS_FOUND -eq 0 ]; then
        echo -e "${GREEN}✓ No obvious hardcoded secrets found${NC}"
    else
        echo -e "${YELLOW}⚠ Potential hardcoded secrets found (review above)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ grep not available, skipping secret scan${NC}"
fi

echo ""
echo "3. Checking for SQL injection vulnerabilities..."
echo "------------------------------------------------------"

# Look for raw SQL queries that might be vulnerable
if grep -r "execute.*%" app/ --exclude-dir=__pycache__ 2>/dev/null; then
    echo -e "${YELLOW}⚠ Potential SQL injection vulnerabilities found${NC}"
else
    echo -e "${GREEN}✓ No obvious SQL injection patterns found${NC}"
fi

echo ""
echo "4. Running security tests..."
echo "------------------------------------------------------"

# Run security-specific tests
if pytest tests/security/ -v 2>&1; then
    echo -e "${GREEN}✓ Security tests passed${NC}"
else
    echo -e "${RED}✗ Security tests failed${NC}"
fi

echo ""
echo "5. Checking security configuration..."
echo "------------------------------------------------------"

# Check if security features are enabled in config
if grep -q "ENABLE_SECURITY_HEADERS.*=.*True" app/core/config.py; then
    echo -e "${GREEN}✓ Security headers enabled${NC}"
else
    echo -e "${YELLOW}⚠ Security headers not explicitly enabled${NC}"
fi

if grep -q "ENABLE_DDOS_PROTECTION.*=.*True" app/core/config.py; then
    echo -e "${GREEN}✓ DDoS protection enabled${NC}"
else
    echo -e "${YELLOW}⚠ DDoS protection not explicitly enabled${NC}"
fi

echo ""
echo "6. Checking for debug mode in production..."
echo "------------------------------------------------------"

if grep -q "DEBUG.*=.*True" .env 2>/dev/null; then
    echo -e "${RED}✗ DEBUG mode is enabled in .env${NC}"
else
    echo -e "${GREEN}✓ DEBUG mode not enabled in .env${NC}"
fi

echo ""
echo "=========================================="
echo "Security Assessment Complete"
echo "=========================================="
echo ""
echo "Recommendations:"
echo "1. Review any warnings above"
echo "2. Keep dependencies up to date"
echo "3. Never commit .env files"
echo "4. Use environment variables for secrets"
echo "5. Enable all security features in production"
echo "6. Regularly run security scans"
echo ""
