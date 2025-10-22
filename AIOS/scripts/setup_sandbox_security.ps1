#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup OS-level sandbox security for AIOS Auditor
.DESCRIPTION
    Creates AIOSAUDITOR user and configures NTFS ACLs for read-only repo access.
    WARNING: Requires Administrator privileges!
.EXAMPLE
    .\setup_sandbox_security.ps1
#>

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "AIOS SANDBOX OS SECURITY SETUP" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$AuditorUser = "AIOSAUDITOR"
$RepoRoot = "F:\AIOS_Clean"
$SandboxRoot = "$env:TEMP\aios_sandbox"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Auditor User: $AuditorUser"
Write-Host "  Repo Root: $RepoRoot"
Write-Host "  Sandbox Root: $SandboxRoot"
Write-Host ""

# Step 1: Create sandbox directory
Write-Host "[1/4] Creating sandbox directory..." -ForegroundColor Green
if (!(Test-Path $SandboxRoot)) {
    New-Item -ItemType Directory -Path $SandboxRoot -Force | Out-Null
    Write-Host "  Created: $SandboxRoot" -ForegroundColor Gray
} else {
    Write-Host "  Already exists: $SandboxRoot" -ForegroundColor Gray
}

# Step 2: Create auditor user
Write-Host ""
Write-Host "[2/4] Creating auditor user..." -ForegroundColor Green

try {
    # Check if user exists
    $userExists = Get-LocalUser -Name $AuditorUser -ErrorAction SilentlyContinue
    
    if ($userExists) {
        Write-Host "  User $AuditorUser already exists" -ForegroundColor Gray
    } else {
        # Generate random password
        Add-Type -AssemblyName 'System.Web'
        $password = [System.Web.Security.Membership]::GeneratePassword(16, 4)
        $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
        
        # Create user
        New-LocalUser -Name $AuditorUser -Password $securePassword -Description "AIOS Auditor - Low privilege sandbox user" -AccountNeverExpires -PasswordNeverExpires | Out-Null
        
        Write-Host "  Created user: $AuditorUser" -ForegroundColor Gray
        Write-Host "  Password: $password" -ForegroundColor Yellow
        Write-Host "  IMPORTANT: Save this password securely!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ERROR: Could not create user: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Configure NTFS ACLs on repo (read-only)
Write-Host ""
Write-Host "[3/4] Configuring NTFS ACLs on repo (read-only)..." -ForegroundColor Green

try {
    # Grant read & execute
    Write-Host "  Granting read-execute..." -ForegroundColor Gray
    icacls $RepoRoot /grant "${AuditorUser}:(RX)" /t | Out-Null
    
    # Deny write, modify, delete
    Write-Host "  Denying write/modify/delete..." -ForegroundColor Gray
    icacls $RepoRoot /deny "${AuditorUser}:(W,M,DC)" /t | Out-Null
    
    Write-Host "  Repo ACLs configured" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not configure repo ACLs: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Configure NTFS ACLs on sandbox (full control)
Write-Host ""
Write-Host "[4/4] Configuring NTFS ACLs on sandbox (full control)..." -ForegroundColor Green

try {
    # Grant full control with inheritance
    Write-Host "  Granting full control..." -ForegroundColor Gray
    icacls $SandboxRoot /grant "${AuditorUser}:(OI)(CI)(F)" /t | Out-Null
    
    Write-Host "  Sandbox ACLs configured" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Could not configure sandbox ACLs: $_" -ForegroundColor Red
    exit 1
}

# Verification
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "VERIFICATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Test Python security module
Write-Host ""
Write-Host "Running Python security tests..." -ForegroundColor Green
py main_core/audit_core/sandbox_os_security.py

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test the security: py main.py --sandbox-security test"
Write-Host "  2. View status: py main.py --sandbox-security status"
Write-Host "  3. Run auditor as $AuditorUser for real isolation"
Write-Host ""
Write-Host "Security Features Enabled:" -ForegroundColor Yellow
Write-Host "  [x] Read-only repo access for auditor"
Write-Host "  [x] Write-only sandbox access for auditor"
Write-Host "  [x] NTFS enforcement at OS level"
Write-Host "  [x] Path traversal protection"
Write-Host "  [x] Cross-drive protection"
Write-Host ""

