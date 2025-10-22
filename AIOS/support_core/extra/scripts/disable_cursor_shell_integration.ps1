# Disable Cursor's shell integration to fix input() issues
# Run this in PowerShell to disable Rich integration

Write-Host "Disabling Cursor shell integration..." -ForegroundColor Yellow

# Set environment variables to disable Rich integration
$env:RICH_SHELL_INTEGRATION = "false"
$env:RICH_FORCE_TERMINAL = "false"
$env:RICH_DISABLE_CONSOLE = "true"
$env:RICH_DISABLE_SHELL_INTEGRATION = "true"

# Disable Cursor's shell integration
$env:VSCODE_SHELL_INTEGRATION = "false"
$env:CURSOR_SHELL_INTEGRATION = "false"

Write-Host "Environment variables set:" -ForegroundColor Green
Write-Host "  RICH_SHELL_INTEGRATION = $env:RICH_SHELL_INTEGRATION"
Write-Host "  RICH_FORCE_TERMINAL = $env:RICH_FORCE_TERMINAL"
Write-Host "  RICH_DISABLE_CONSOLE = $env:RICH_DISABLE_CONSOLE"
Write-Host "  RICH_DISABLE_SHELL_INTEGRATION = $env:RICH_DISABLE_SHELL_INTEGRATION"

Write-Host "`nTesting Python input()..." -ForegroundColor Yellow
python -c "
import sys
print(f'stdin.isatty(): {sys.stdin.isatty()}')
print(f'stdout.isatty(): {sys.stdout.isatty()}')
print(f'stderr.isatty(): {sys.stderr.isatty()}')
try:
    user_input = input('Enter something: ')
    print(f'SUCCESS! You entered: {user_input}')
except EOFError as e:
    print(f'EOF Error: {e}')
    print('Input still not working - need to disable at Cursor level')
except Exception as e:
    print(f'Other error: {e}')
"

Write-Host "`nTo permanently fix this:" -ForegroundColor Cyan
Write-Host "1. Add these to your PowerShell profile"
Write-Host "2. Or disable Rich: pip uninstall rich"
Write-Host "3. Or use external terminal outside Cursor"
