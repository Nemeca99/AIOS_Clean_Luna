# Test main.py auto-venv activation
Write-Host "Testing main.py Auto-VEnv Activation" -ForegroundColor Cyan
Write-Host "=" * 60

# Test 1: Check current Python
Write-Host "`n1. System Python (before main.py):" -ForegroundColor Yellow
py -c "import sys; print(f'   Executable: {sys.executable}'); print(f'   In venv: {hasattr(sys, chr(34) + chr(34) + chr(34) + chr(34).join([chr(114), chr(101), chr(97), chr(108), chr(95), chr(112), chr(114), chr(101), chr(102), chr(105
