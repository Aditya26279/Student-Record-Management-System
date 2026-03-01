@echo off
REM ════════════════════════════════════════════════════════════════
REM  Student Record Management System — Windows Launcher
REM  Usage:
REM    run.bat           → launch the CLI
REM    run.bat test      → run all tests
REM    run.bat test unit → run unit tests only
REM    run.bat build-c   → compile C data structures
REM ════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM ── Load .env if it exists ────────────────────────────────────────────────
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        if not "%%A"=="" if not "%%A:~0,1%"=="#" (
            set %%A=%%B
        )
    )
    echo [INFO] Loaded .env
)

REM ── Default DB password prompt if not set ────────────────────────────────
if "%DB_PASSWORD%"=="" (
    set /p DB_PASSWORD="Enter DB password: "
)

REM ── Dispatch ─────────────────────────────────────────────────────────────
if "%1"=="test" (
    if "%2"=="unit" (
        echo [INFO] Running unit tests ^(no DB required^)...
        python -m pytest tests/unit/ -m unit
    ) else if "%2"=="integration" (
        echo [INFO] Running integration tests ^(requires DB^)...
        python -m pytest tests/integration/ -m integration
    ) else (
        echo [INFO] Running full test suite...
        python -m pytest tests/
    )
    goto :eof
)

if "%1"=="build-c" (
    echo [INFO] Building C modules...
    cd c_modules
    make
    cd ..
    goto :eof
)

if "%1"=="test-c" (
    echo [INFO] Running C test harness...
    cd c_modules
    make run
    cd ..
    goto :eof
)

if "%1"=="coverage" (
    echo [INFO] Running tests with coverage...
    python -m pytest tests/ --cov=student_management --cov-report=html --cov-report=term
    echo [INFO] HTML report → htmlcov\index.html
    goto :eof
)

REM ── Default: launch CLI ───────────────────────────────────────────────────
echo.
python main.py
