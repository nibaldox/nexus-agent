#!/bin/bash
# Test runner script for Developer Agent

echo "🧪 Nexus Developer Agent - Test Suite"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if sandbox image exists
echo "Checking for nexus-sandbox image..."
if ! docker images | grep -q "nexus-sandbox"; then
    echo -e "${YELLOW}⚠ nexus-sandbox image not found. Building...${NC}"
    docker build -t nexus-sandbox:latest ./sandbox
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to build sandbox image${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Sandbox image found${NC}"

# Install test dependencies
echo "Installing test dependencies..."
pip install -q -r tests/requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo "Running tests..."
echo "================"

# Run different test suites
echo ""
echo "1️⃣  Running quick tests (excluding slow)..."
pytest tests/test_developer_agent.py -v -m "not slow" --tb=short

QUICK_RESULT=$?

echo ""
echo "2️⃣  Running security tests..."
pytest tests/test_developer_agent.py -v -k "security" --tb=short

SECURITY_RESULT=$?

# Optional: Run slow tests if requested
if [ "$1" == "--full" ]; then
    echo ""
    echo "3️⃣  Running full test suite (including slow tests)..."
    pytest tests/test_developer_agent.py -v --tb=short
    FULL_RESULT=$?
fi

# Summary
echo ""
echo "======================================"
echo "Test Summary"
echo "======================================"

if [ $QUICK_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Quick tests: PASSED${NC}"
else
    echo -e "${RED}✗ Quick tests: FAILED${NC}"
fi

if [ $SECURITY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Security tests: PASSED${NC}"
else
    echo -e "${RED}✗ Security tests: FAILED${NC}"
fi

if [ "$1" == "--full" ]; then
    if [ $FULL_RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ Full test suite: PASSED${NC}"
    else
        echo -e "${RED}✗ Full test suite: FAILED${NC}"
    fi
fi

echo ""

# Exit with failure if any test suite failed
if [ $QUICK_RESULT -ne 0 ] || [ $SECURITY_RESULT -ne 0 ]; then
    exit 1
fi

if [ "$1" == "--full" ] && [ $FULL_RESULT -ne 0 ]; then
    exit 1
fi

echo -e "${GREEN}🎉 All tests passed!${NC}"
exit 0
