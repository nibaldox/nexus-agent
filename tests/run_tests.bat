@echo off
REM Test runner script for Developer Agent (Windows)

echo ======================================
echo Nexus Developer Agent - Test Suite
echo ======================================
echo.

REM Check if Docker is running
echo Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)
echo [OK] Docker is running

REM Check if sandbox image exists
echo Checking for nexus-sandbox image...
docker images | findstr "nexus-sandbox" >nul
if errorlevel 1 (
    echo [WARN] nexus-sandbox image not found. Building...
    docker build -t nexus-sandbox:latest ./sandbox
    if errorlevel 1 (
        echo [ERROR] Failed to build sandbox image
        exit /b 1
    )
)
echo [OK] Sandbox image found

REM Install test dependencies
echo Installing test dependencies...
.venv\Scripts\pip install -q -r tests/requirements.txt
echo [OK] Dependencies installed

echo.
echo Running tests...
echo ======================================
echo.

REM Run quick tests
echo 1. Running quick tests (excluding slow)...
.venv\Scripts\pytest tests/test_developer_agent.py -v -m "not slow" --tb=short
set QUICK_RESULT=%errorlevel%

echo.
echo 2. Running security tests...
.venv\Scripts\pytest tests/test_developer_agent.py -v -k "security" --tb=short
set SECURITY_RESULT=%errorlevel%

REM Optional: Run slow tests if --full flag provided
if "%1"=="--full" (
    echo.
    echo 3. Running full test suite (including slow tests)...
    .venv\Scripts\pytest tests/test_developer_agent.py -v --tb=short
    set FULL_RESULT=%errorlevel%
)

REM Summary
echo.
echo ======================================
echo Test Summary
echo ======================================

if %QUICK_RESULT%==0 (
    echo [OK] Quick tests: PASSED
) else (
    echo [FAIL] Quick tests: FAILED
)

if %SECURITY_RESULT%==0 (
    echo [OK] Security tests: PASSED
) else (
    echo [FAIL] Security tests: FAILED
)

if "%1"=="--full" (
    if %FULL_RESULT%==0 (
        echo [OK] Full test suite: PASSED
    ) else (
        echo [FAIL] Full test suite: FAILED
    )
)

echo.

REM Exit with failure if any test suite failed
if not %QUICK_RESULT%==0 exit /b 1
if not %SECURITY_RESULT%==0 exit /b 1
if "%1"=="--full" if not %FULL_RESULT%==0 exit /b 1

echo [SUCCESS] All tests passed!
exit /b 0
