# Daily Audit Automation - Option 3: Smart Hybrid
# Runs silently, only interrupts if issues found, sends toast notification

$logFile = "reports\audit_log_$(Get-Date -Format 'yyyy-MM-dd').txt"
$timestamp = Get-Date -Format "HH:mm:ss"

# Run V3 audit silently, save output
Write-Output "[$timestamp] Starting daily AIOS audit..." | Out-File -FilePath $logFile
py main.py --audit --v3 2>&1 | Out-File -FilePath $logFile -Append

$exitCode = $LASTEXITCODE
$timestamp = Get-Date -Format "HH:mm:ss"

# Function to send Windows notification
function Send-Notification {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Type = "Info"  # Info, Success, Warning, Error
    )
    
    try {
        # Try modern toast first
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        
        $template = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>$Title</text>
            <text>$Message</text>
        </binding>
    </visual>
</toast>
"@
        
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("AIOS Audit").Show($toast)
    }
    catch {
        # Fallback to balloon notification (more reliable)
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        
        # Set icon based on type
        switch ($Type) {
            "Success" { $notify.Icon = [System.Drawing.SystemIcons]::Information }
            "Warning" { $notify.Icon = [System.Drawing.SystemIcons]::Warning }
            "Error"   { $notify.Icon = [System.Drawing.SystemIcons]::Error }
            default   { $notify.Icon = [System.Drawing.SystemIcons]::Information }
        }
        
        $notify.Visible = $true
        $notify.ShowBalloonTip(5000, $Title, $Message, [System.Windows.Forms.ToolTipIcon]::Info)
        
        # Keep alive for display
        Start-Sleep -Seconds 6
        $notify.Dispose()
    }
}

# Analyze results and take action
if ($exitCode -eq 0) {
    # SUCCESS - Audit passed
    Write-Output "[$timestamp] Audit PASSED - No issues found" | Out-File -FilePath $logFile -Append
    
    # Send success notification (silent, informational)
    Send-Notification -Title "AIOS Audit Passed" -Message "All systems nominal. Dashboard updated." -Type "Success"
    
    # Don't open dashboard - available at reports\dashboard.html anytime
    
} else {
    # ISSUES FOUND - Get attention
    Write-Output "[$timestamp] Audit FAILED - Issues detected (exit code: $exitCode)" | Out-File -FilePath $logFile -Append
    
    # Check if critical issues
    $dashboardContent = Get-Content "reports\dashboard.html" -Raw
    $hasCritical = $dashboardContent -match "CRITICAL" -or $dashboardContent -match "status.*:.*CRITICAL"
    
    if ($hasCritical) {
        # CRITICAL - Open dashboard immediately
        Write-Output "[$timestamp] CRITICAL issues found - opening dashboard" | Out-File -FilePath $logFile -Append
        
        Send-Notification -Title "AIOS Audit: CRITICAL ISSUES" -Message "Critical problems detected. Opening dashboard..." -Type "Error"
        
        Start-Sleep -Seconds 2
        start reports\dashboard.html
        
    } else {
        # WARNING level - Toast only, don't interrupt
        Write-Output "[$timestamp] Warning issues found - toast notification sent" | Out-File -FilePath $logFile -Append
        
        Send-Notification -Title "AIOS Audit: Issues Found" -Message "Non-critical issues detected. Check dashboard when convenient." -Type "Warning"
    }
}

# Log completion
Write-Output "[$timestamp] Audit automation complete" | Out-File -FilePath $logFile -Append

# Exit cleanly (no user interaction needed)
exit 0

