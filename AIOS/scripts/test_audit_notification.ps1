# Test Audit Notification System
# Run this to test the toast notifications without running full audit

Write-Host "Testing AIOS audit notification system..." -ForegroundColor Cyan
Write-Host ""

# Function to send Windows toast notification
function Send-Toast {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Type = "Info"
    )
    
    try {
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
    <actions>
        <action content="View Dashboard" arguments="file:///$($PWD.Path.Replace('\', '/'))/reports/dashboard.html" activationType="protocol"/>
    </actions>
</toast>
"@
        
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($template)
        $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
        
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("AIOS Audit").Show($toast)
        
        Write-Host "Toast sent successfully!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Toast failed: $_" -ForegroundColor Red
        Write-Host "Falling back to balloon notification..." -ForegroundColor Yellow
        
        # Fallback: Use PowerShell balloon notification
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(5000, $Title, $Message, [System.Windows.Forms.ToolTipIcon]::Info)
        
        Start-Sleep -Seconds 6
        $notify.Dispose()
        
        Write-Host "Balloon notification sent!" -ForegroundColor Green
        return $true
    }
}

# Test different notification types
Write-Host "Test 1: Success notification..." -ForegroundColor Yellow
Send-Toast -Title "AIOS Audit Passed" -Message "All systems nominal. Dashboard updated." -Type "Success"
Start-Sleep -Seconds 3

Write-Host "Test 2: Warning notification..." -ForegroundColor Yellow
Send-Toast -Title "AIOS Audit: Issues Found" -Message "Non-critical issues detected. Check dashboard when convenient." -Type "Warning"
Start-Sleep -Seconds 3

Write-Host "Test 3: Critical notification..." -ForegroundColor Yellow
Send-Toast -Title "AIOS Audit: CRITICAL ISSUES" -Message "Critical problems detected. Opening dashboard..." -Type "Error"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Notification tests complete!" -ForegroundColor Green
Write-Host "If you saw 3 notifications, the system is working." -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

