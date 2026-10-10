$script:Canvas = [System.Drawing.ColorTranslator]::FromHtml('#080A0F')
$script:Surface = [System.Drawing.ColorTranslator]::FromHtml('#11151E')
$script:SurfaceRaised = [System.Drawing.ColorTranslator]::FromHtml('#1A2030')
$script:BorderColor = [System.Drawing.ColorTranslator]::FromHtml('#272D3A')
$script:TextColor = [System.Drawing.ColorTranslator]::FromHtml('#F5F7FA')
$script:MutedText = [System.Drawing.ColorTranslator]::FromHtml('#A0A8B8')
$script:DisabledText = [System.Drawing.ColorTranslator]::FromHtml('#929AAA')
$script:Mint = [System.Drawing.ColorTranslator]::FromHtml('#9BE0B5')
$script:BlueAccent = [System.Drawing.ColorTranslator]::FromHtml('#8BA8FF')
$script:WarningColor = [System.Drawing.ColorTranslator]::FromHtml('#F2C879')
$script:ErrorColor = [System.Drawing.ColorTranslator]::FromHtml('#FF9292')
$script:FontCollection = New-Object System.Drawing.Text.PrivateFontCollection
$fontPath = Join-Path $PSScriptRoot 'Assets\Inter.ttf'
if (Test-Path -LiteralPath $fontPath -PathType Leaf) {
    $script:FontCollection.AddFontFile($fontPath)
    $fontFamily = $script:FontCollection.Families[0]
}
else {
    $fontFamily = New-Object System.Drawing.FontFamily('Segoe UI')
}
$script:BodyFont = [System.Drawing.Font]::new($fontFamily, 9, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Point)
$script:EmphasisFont = [System.Drawing.Font]::new($fontFamily, 9, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
$script:HeadingFont = [System.Drawing.Font]::new($fontFamily, 18, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
$script:SmallFont = [System.Drawing.Font]::new($fontFamily, 8, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Point)

function New-BrandMarkBitmap {
    $bitmap = New-Object System.Drawing.Bitmap(64, 64)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $orbit = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#B8C9E4'), 1.8)
    $meridian = New-Object System.Drawing.Pen($script:BlueAccent, 1.4)
    $corePen = New-Object System.Drawing.Pen($script:TextColor, 1.8)
    $coreBrush = New-Object System.Drawing.SolidBrush($script:Surface)
    $centerBrush = New-Object System.Drawing.SolidBrush($script:TextColor)
    $star = New-Object System.Drawing.Drawing2D.GraphicsPath
    try {
        $graphics.DrawArc($orbit, 8, 8, 48, 48, 40, 310)
        $graphics.TranslateTransform(32, 32)
        $graphics.RotateTransform(-42)
        $graphics.DrawEllipse($meridian, -26, -10.5, 52, 21)
        $graphics.ResetTransform()
        $star.AddBezier(32, 15, 35, 26, 38, 29, 49, 32)
        $star.AddBezier(49, 32, 38, 35, 35, 38, 32, 49)
        $star.AddBezier(32, 49, 29, 38, 26, 35, 15, 32)
        $star.AddBezier(15, 32, 26, 29, 29, 26, 32, 15)
        $graphics.FillPath($coreBrush, $star)
        $graphics.DrawPath($corePen, $star)
        $graphics.FillEllipse($centerBrush, 28.7, 28.7, 6.6, 6.6)
        $orbitDot = New-Object System.Drawing.SolidBrush($script:BlueAccent)
        try { $graphics.FillEllipse($orbitDot, 50.3, 17.4, 4.8, 4.8) }
        finally { $orbitDot.Dispose() }
        return $bitmap
    }
    catch {
        $bitmap.Dispose()
        throw
    }
    finally {
        $graphics.Dispose()
        $orbit.Dispose()
        $meridian.Dispose()
        $corePen.Dispose()
        $coreBrush.Dispose()
        $centerBrush.Dispose()
        $star.Dispose()
    }
}
$script:BrandMark = New-BrandMarkBitmap

if ([System.Windows.Forms.SystemInformation]::HighContrast) {
    $script:Canvas = [System.Drawing.SystemColors]::Window
    $script:Surface = [System.Drawing.SystemColors]::Control
    $script:SurfaceRaised = [System.Drawing.SystemColors]::Control
    $script:BorderColor = [System.Drawing.SystemColors]::WindowText
    $script:TextColor = [System.Drawing.SystemColors]::WindowText
    $script:MutedText = [System.Drawing.SystemColors]::WindowText
    $script:Mint = [System.Drawing.SystemColors]::Highlight
}

function Set-DarkWindowChrome([System.Windows.Forms.Form]$Window) {
    if ([System.Windows.Forms.SystemInformation]::HighContrast) { return }
    if (-not ('AetherionWindowChrome' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class AetherionWindowChrome
{
    [DllImport("dwmapi.dll", PreserveSig = true)]
    private static extern int DwmSetWindowAttribute(
        IntPtr hwnd, int attribute, ref int value, int valueSize);

    public static void UseDarkTitleBar(IntPtr hwnd)
    {
        int value = 1;
        if (DwmSetWindowAttribute(hwnd, 20, ref value, sizeof(int)) != 0)
            DwmSetWindowAttribute(hwnd, 19, ref value, sizeof(int));
    }

    public static void UseMicaBackdrop(IntPtr hwnd)
    {
        int value = 2;
        DwmSetWindowAttribute(hwnd, 38, ref value, sizeof(int));
    }
}
'@
    }
    [AetherionWindowChrome]::UseDarkTitleBar($Window.Handle)
    if ([Environment]::OSVersion.Version.Build -ge 22621) {
        [AetherionWindowChrome]::UseMicaBackdrop($Window.Handle)
    }
}

function Set-FormBase([System.Windows.Forms.Form]$Window, [string]$Title, [bool]$Resizable = $false) {
    $Window.Text = $Title
    $Window.BackColor = $script:Canvas
    $Window.ForeColor = $script:TextColor
    $Window.Font = $script:BodyFont
    $Window.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::Font
    $Window.KeyPreview = $true
    $Window.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterParent
    if (-not $Resizable) {
        $Window.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
        $Window.MaximizeBox = $false
        $Window.MinimizeBox = $false
    }
    $onShown = { Set-DarkWindowChrome $Window }.GetNewClosure()
    $Window.Add_Shown($onShown)
}

function Set-Style($Control, [bool]$IsButton = $false) {
    $Control.BackColor = $script:SurfaceRaised
    $Control.ForeColor = $script:TextColor
    $Control.Font = $script:BodyFont
    if ($Control -is [System.Windows.Forms.Label]) {
        $Control.UseMnemonic = $false
    }
    if ($Control -is [System.Windows.Forms.TextBox]) {
        $Control.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
    }
    if ($Control -is [System.Windows.Forms.ComboBox]) {
        $Control.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
    }
    if ($IsButton) {
        $Control.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
        $Control.FlatAppearance.BorderColor = $script:BorderColor
        $Control.FlatAppearance.BorderSize = 1
        $Control.FlatAppearance.MouseOverBackColor = $script:SurfaceRaised
        $Control.FlatAppearance.MouseDownBackColor = [System.Drawing.ColorTranslator]::FromHtml('#304164')
        $Control.UseVisualStyleBackColor = $false
        $Control.Height = 36
        $Control.Cursor = [System.Windows.Forms.Cursors]::Hand
    }
}

function Add-Label($Parent, [string]$Text, [int]$X, [int]$Y, [int]$Width = 600, [int]$Height = 22, [bool]$Accent = $false) {
    $label = New-Object System.Windows.Forms.Label
    $label.Text = $Text
    $label.Location = New-Object System.Drawing.Point($X, $Y)
    $label.Size = New-Object System.Drawing.Size($Width, $Height)
    $label.ForeColor = if ($Accent) { $script:BlueAccent } else { $script:TextColor }
    $label.Font = if ($Accent) { $script:EmphasisFont } else { $script:BodyFont }
    $label.UseMnemonic = $false
    $label.AutoEllipsis = $true
    if ($Parent -isnot [System.Windows.Forms.TableLayoutPanel]) {
        $Parent.Controls.Add($label)
    }
    return $label
}

function Add-TextBox($Parent, [int]$X, [int]$Y, [int]$Width, [string]$Value = '') {
    $box = New-Object System.Windows.Forms.TextBox
    $box.Location = New-Object System.Drawing.Point($X, $Y)
    $box.Size = New-Object System.Drawing.Size($Width, 30)
    $box.Text = $Value
    $box.AccessibleRole = [System.Windows.Forms.AccessibleRole]::Text
    Set-Style $box
    if ($Parent -isnot [System.Windows.Forms.TableLayoutPanel]) {
        $Parent.Controls.Add($box)
    }
    return $box
}

function Add-Button($Parent, [string]$Text, [int]$X, [int]$Y, [int]$Width = 140) {
    $button = New-Object System.Windows.Forms.Button
    $button.Text = $Text
    $button.Location = New-Object System.Drawing.Point($X, $Y)
    $button.Size = New-Object System.Drawing.Size($Width, 36)
    $button.AccessibleName = $Text
    Set-Style $button $true
    if ($Parent -isnot [System.Windows.Forms.TableLayoutPanel]) {
        $Parent.Controls.Add($button)
    }
    return $button
}

function New-LayoutPanel([System.Windows.Forms.Control]$Parent, [bool]$Table = $false) {
    if ($Table) {
        $panel = New-Object System.Windows.Forms.TableLayoutPanel
        $panel.GrowStyle = [System.Windows.Forms.TableLayoutPanelGrowStyle]::FixedSize
    }
    else {
        $panel = New-Object System.Windows.Forms.Panel
    }
    $panel.Margin = New-Object System.Windows.Forms.Padding(0)
    $Parent.Controls.Add($panel)
    return $panel
}

function Show-ServerSettingsDialog {
    $dialog = New-Object System.Windows.Forms.Form
    Set-FormBase $dialog 'License service settings'
    $dialog.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterParent
    $dialog.Size = New-Object System.Drawing.Size(680, 430)
    $dialog.Padding = New-Object System.Windows.Forms.Padding(26)

    $heading = Add-Label $dialog 'Service settings' 26 22 570 30
    $heading.Font = $script:HeadingFont
    $description = Add-Label $dialog 'Connect this manager to the service used by Aetherion clients.' 27 56 590 24
    $description.ForeColor = $script:MutedText

    Add-Label $dialog 'SERVICE URL' 27 104 560 18 $true | Out-Null
    $urlBox = Add-TextBox $dialog 27 127 606 $script:ManagerSettings.server_url
    $urlBox.Anchor = 'Top,Left,Right'
    $urlBox.AccessibleName = 'License service URL'
    Add-Label $dialog 'ADMINISTRATOR TOKEN' 27 177 560 18 $true | Out-Null
    $tokenBox = Add-TextBox $dialog 27 200 606 $script:ManagerSettings.admin_token
    $tokenBox.UseSystemPasswordChar = $true
    $tokenBox.Anchor = 'Top,Left,Right'
    $tokenBox.AccessibleName = 'Administrator token'

    $status = Add-Label $dialog 'The token is encrypted for this Windows account.' 27 252 606 52
    $status.ForeColor = $script:MutedText
    $status.Anchor = 'Bottom,Left,Right'
    $save = Add-Button $dialog 'Save and connect' 27 342 164
    $save.Anchor = 'Bottom,Left'
    $close = Add-Button $dialog 'Close' 511 342 122
    $close.Anchor = 'Bottom,Right'
    $close.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $dialog.CancelButton = $close

    $save.Add_Click({
        $save.Enabled = $false
        $status.Text = 'Saving settings and verifying the service...'
        $status.ForeColor = $script:MutedText
        $dialog.UseWaitCursor = $true
        $dialog.Refresh()
        try {
            Save-ManagerSettings $urlBox.Text $tokenBox.Text
            $null = Invoke-LicenseService 'GET' '/v1/admin/users'
            $script:SettingsLoadError = $null
            $status.Text = 'Connected. The administrator token was verified.'
            $status.ForeColor = $script:Mint
            Update-IssueReadiness
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
        }
        finally {
            $dialog.UseWaitCursor = $false
            $save.Enabled = $true
        }
    })
    [void]$dialog.ShowDialog($script:MainForm)
    $dialog.Dispose()
}

function Show-SyncExistingLicenseDialog {
    $dialog = New-Object System.Windows.Forms.Form
    Set-FormBase $dialog 'Register an existing license' $true
    $dialog.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterParent
    $dialog.Size = New-Object System.Drawing.Size(720, 500)
    $dialog.MinimumSize = New-Object System.Drawing.Size(620, 430)
    $dialog.Padding = New-Object System.Windows.Forms.Padding(24)

    $heading = Add-Label $dialog 'Sync an existing license' 24 20 630 30
    $heading.Font = $script:HeadingFont
    $description = Add-Label $dialog 'Paste a complete AETH1 key. The service verifies its signature; the private signing key stays on this device.' 25 55 640 40
    $description.ForeColor = $script:MutedText

    Add-Label $dialog 'LICENSE KEY' 25 108 600 18 $true | Out-Null
    $licenseBox = New-Object System.Windows.Forms.TextBox
    $licenseBox.Location = New-Object System.Drawing.Point(25, 132)
    $licenseBox.Size = New-Object System.Drawing.Size(646, 204)
    $licenseBox.Multiline = $true
    $licenseBox.ScrollBars = [System.Windows.Forms.ScrollBars]::None
    $licenseBox.WordWrap = $true
    $licenseBox.Font = New-Object System.Drawing.Font('Consolas', 9)
    $licenseBox.Anchor = 'Top,Bottom,Left,Right'
    $licenseBox.AccessibleName = 'Existing license key'
    Set-Style $licenseBox
    $dialog.Controls.Add($licenseBox)

    $status = Add-Label $dialog 'The key remains device-bound and can only be claimed once.' 25 349 646 46
    $status.ForeColor = $script:MutedText
    $status.Anchor = 'Bottom,Left,Right'
    $sync = Add-Button $dialog 'Verify and sync' 25 408 150
    $sync.Anchor = 'Bottom,Left'
    $close = Add-Button $dialog 'Close' 549 408 122
    $close.Anchor = 'Bottom,Right'
    $close.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $dialog.CancelButton = $close

    $sync.Add_Click({
        $sync.Enabled = $false
        $dialog.UseWaitCursor = $true
        try {
            $value = $licenseBox.Text.Trim()
            if (-not $value) { throw 'Paste the complete license key first.' }
            $status.Text = 'Verifying the license with the service...'
            $status.ForeColor = $script:MutedText
            $dialog.Refresh()
            $result = Invoke-LicenseService 'POST' '/v1/admin/licenses' @{ license_key = $value }
            $state = if ($result.claimed) { 'This license is already claimed by an account.' } else { 'License verified and ready for account registration.' }
            $status.Text = "$state License ID: $($result.license_id)"
            $status.ForeColor = $script:Mint
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
        }
        finally {
            $dialog.UseWaitCursor = $false
            $sync.Enabled = $true
        }
    })
    [void]$dialog.ShowDialog($script:MainForm)
    $dialog.Dispose()
}

function Set-AccountsGridStyle([System.Windows.Forms.DataGridView]$Grid) {
    $Grid.ReadOnly = $true
    $Grid.AllowUserToAddRows = $false
    $Grid.AllowUserToDeleteRows = $false
    $Grid.AllowUserToResizeRows = $false
    $Grid.MultiSelect = $false
    $Grid.SelectionMode = [System.Windows.Forms.DataGridViewSelectionMode]::FullRowSelect
    $Grid.AutoSizeColumnsMode = [System.Windows.Forms.DataGridViewAutoSizeColumnsMode]::Fill
    $Grid.BackgroundColor = $script:Surface
    $Grid.GridColor = $script:BorderColor
    $Grid.BorderStyle = [System.Windows.Forms.BorderStyle]::None
    $Grid.RowHeadersVisible = $false
    $Grid.EnableHeadersVisualStyles = $false
    $Grid.ColumnHeadersBorderStyle = [System.Windows.Forms.DataGridViewHeaderBorderStyle]::Single
    $Grid.RowHeadersBorderStyle = [System.Windows.Forms.DataGridViewHeaderBorderStyle]::Single
    $Grid.CellBorderStyle = [System.Windows.Forms.DataGridViewCellBorderStyle]::SingleHorizontal
    $Grid.ColumnHeadersHeight = 38
    $Grid.RowTemplate.Height = 40
    $Grid.Font = $script:BodyFont
    $Grid.ColumnHeadersDefaultCellStyle.BackColor = $script:SurfaceRaised
    $Grid.ColumnHeadersDefaultCellStyle.ForeColor = $script:TextColor
    $Grid.ColumnHeadersDefaultCellStyle.SelectionBackColor = $script:SurfaceRaised
    $Grid.ColumnHeadersDefaultCellStyle.SelectionForeColor = $script:TextColor
    $Grid.ColumnHeadersDefaultCellStyle.Font = $script:EmphasisFont
    $Grid.DefaultCellStyle.BackColor = $script:Surface
    $Grid.DefaultCellStyle.ForeColor = $script:TextColor
    $Grid.DefaultCellStyle.SelectionBackColor = [System.Drawing.ColorTranslator]::FromHtml('#304164')
    $Grid.DefaultCellStyle.SelectionForeColor = $script:TextColor
    $Grid.DefaultCellStyle.Padding = New-Object System.Windows.Forms.Padding(6, 0, 6, 0)
    $Grid.AlternatingRowsDefaultCellStyle.BackColor = [System.Drawing.ColorTranslator]::FromHtml('#151B26')
}

function Get-UserOnlineState {
    param([object]$User)
    # Only the authenticated server observation proves recent connectivity.
    if ($null -eq $User -or -not $User.PSObject.Properties['online'] -or $User.online -isnot [bool]) { return 'Unknown' }
    if ($User.online) { return 'Online' }
    return 'Offline'
}

function Invoke-UserAdminAction {
    param(
        [int]$UserId,
        [string]$Operation,
        [hashtable]$Body = @{}
    )
    $candidates = switch ($Operation) {
        'temporary-password' {
            @("/v1/admin/users/$UserId/temporary-password")
        }
        'set-password' {
            @("/v1/admin/users/$UserId/password")
        }
        'unlink-device' {
            @("/v1/admin/users/$UserId/unlink-device")
        }
        default { @() }
    }
    foreach ($candidate in $candidates) {
        try {
            return Invoke-LicenseService 'POST' $candidate $Body
        }
        catch {
            $errorText = $_.Exception.Message
            throw
        }
    }
    throw "The service does not expose the $Operation endpoint for this account."
}

function Show-AccountPasswordDialog([System.Windows.Forms.Form]$Owner, [int]$UserId, [string]$Username) {
    $passwordDialog = New-Object System.Windows.Forms.Form
    Set-FormBase $passwordDialog 'Reset account password'
    $passwordDialog.Size = New-Object System.Drawing.Size(590, 410)
    $passwordDialog.Padding = New-Object System.Windows.Forms.Padding(24)

    $heading = Add-Label $passwordDialog "Password for $Username" 24 20 520 28
    $heading.Font = $script:HeadingFont
    $description = Add-Label $passwordDialog 'Passwords are stored as Argon2id hashes and cannot be viewed. Set a replacement or generate a one-time temporary password.' 24 56 520 52
    $description.ForeColor = $script:MutedText
    Add-Label $passwordDialog 'NEW PASSWORD (MINIMUM 12 CHARACTERS)' 24 120 520 20 $true | Out-Null
    $passwordBox = Add-TextBox $passwordDialog 24 144 520 ''
    $passwordBox.UseSystemPasswordChar = $true
    $confirmBox = Add-TextBox $passwordDialog 24 194 520 ''
    $confirmBox.UseSystemPasswordChar = $true
    $confirmLabel = Add-Label $passwordDialog 'CONFIRM PASSWORD' 24 170 520 20
    $status = Add-Label $passwordDialog 'Any replacement must be changed at the next online sign-in. Previously issued offline access may remain usable for up to seven days.' 24 244 520 48
    $status.ForeColor = $script:MutedText
    $setButton = Add-Button $passwordDialog 'Set password' 24 300 132
    $temporaryButton = Add-Button $passwordDialog 'Generate temporary' 168 300 166
    $copyButton = Add-Button $passwordDialog 'Copy password' 346 300 132
    $copyButton.Enabled = $false
    $closeButton = Add-Button $passwordDialog 'Close' 24 350 100
    $closeButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $passwordDialog.CancelButton = $closeButton

    $showPassword = {
        param([string]$Password, [string]$Message)
        $passwordBox.Text = $Password
        $passwordBox.UseSystemPasswordChar = $false
        $passwordBox.ReadOnly = $true
        $confirmBox.Clear()
        $confirmBox.Enabled = $false
        $confirmLabel.Enabled = $false
        $setButton.Enabled = $false
        $temporaryButton.Enabled = $false
        $copyButton.Enabled = $true
        $status.Text = $Message
        $status.ForeColor = $script:Mint
    }.GetNewClosure()

    $setButton.Add_Click({
        $password = $passwordBox.Text
        if ($password.Length -lt 12 -or $password.Length -gt 128) {
            $status.Text = 'Use a password between 12 and 128 characters.'
            $status.ForeColor = $script:WarningColor
            return
        }
        if ($password -cne $confirmBox.Text) {
            $status.Text = 'The password confirmation does not match.'
            $status.ForeColor = $script:WarningColor
            return
        }
        try {
            $setButton.Enabled = $false
            $temporaryButton.Enabled = $false
            $status.Text = 'Updating password securely...'
            $passwordDialog.UseWaitCursor = $true
            $null = Invoke-UserAdminAction -UserId $UserId -Operation 'set-password' -Body @{ password = $password }
            & $showPassword $password 'Password updated. Deliver it securely; the user must replace it at their next online sign-in. Offline access may remain for up to seven days.'
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
            $setButton.Enabled = $true
            $temporaryButton.Enabled = $true
        }
        finally {
            $passwordDialog.UseWaitCursor = $false
        }
    }.GetNewClosure())
    $temporaryButton.Add_Click({
        try {
            $setButton.Enabled = $false
            $temporaryButton.Enabled = $false
            $status.Text = 'Generating a one-time password...'
            $passwordDialog.UseWaitCursor = $true
            $result = Invoke-UserAdminAction -UserId $UserId -Operation 'temporary-password' -Body @{}
            if ([string]::IsNullOrWhiteSpace([string]$result.temporary_password)) {
                throw 'The service did not return a temporary password.'
            }
            & $showPassword ([string]$result.temporary_password) 'Temporary password shown once. Share it securely; the user must replace it at their next online sign-in. Offline access may remain for up to seven days.'
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
            $setButton.Enabled = $true
            $temporaryButton.Enabled = $true
        }
        finally {
            $passwordDialog.UseWaitCursor = $false
        }
    }.GetNewClosure())
    $copyButton.Add_Click({
        try {
            [System.Windows.Forms.Clipboard]::SetText($passwordBox.Text)
            $status.Text = 'Password copied. Clear your clipboard after sharing it securely.'
            $status.ForeColor = $script:Mint
        }
        catch {
            $status.Text = "Could not copy the password: $($_.Exception.Message)"
            $status.ForeColor = $script:ErrorColor
        }
    }.GetNewClosure())

    [void]$passwordDialog.ShowDialog($Owner)
    $passwordDialog.Dispose()
}

function Show-AccountManager {
    $dialog = New-Object System.Windows.Forms.Form
    Set-FormBase $dialog 'Customer accounts' $true
    $dialog.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterParent
    $accountWidth = [Math]::Min(1240, [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea.Width - 40)
    $accountHeight = [Math]::Min(780, [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea.Height - 20)
    $minimumWidth = [Math]::Min(960, [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea.Width - 40)
    $minimumHeight = [Math]::Min(600, [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea.Height - 40)
    $dialog.Size = New-Object System.Drawing.Size($accountWidth, $accountHeight)
    $dialog.MinimumSize = New-Object System.Drawing.Size($minimumWidth, $minimumHeight)

    $outer = New-Object System.Windows.Forms.Panel
    $outer.Dock = [System.Windows.Forms.DockStyle]::Fill
    $outer.AutoScroll = $true
    $outer.Padding = New-Object System.Windows.Forms.Padding(20)
    $dialog.Controls.Add($outer)

    $layout = New-Object System.Windows.Forms.TableLayoutPanel
    $layout.Dock = [System.Windows.Forms.DockStyle]::Top
    $layout.ColumnCount = 1
    $layout.RowCount = 7
    $layout.Padding = New-Object System.Windows.Forms.Padding(0)
    $layout.Margin = New-Object System.Windows.Forms.Padding(0)
    $layout.MinimumSize = New-Object Drawing.Size(880, 600)
    $layout.Height = [Math]::Max(600, $outer.ClientSize.Height - 40)
    $outer.Add_Resize({ $layout.Height = [Math]::Max(600, $outer.ClientSize.Height - 40) })
    foreach ($height in @(58, 78, -1, 116, 88, 88, 44)) {
        $style = if ($height -eq -1) {
            New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Percent, 100)
        }
        else {
            New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, $height)
        }
        [void]$layout.RowStyles.Add($style)
    }
    [void]$layout.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 100)))
    $outer.Controls.Add($layout)

    $header = New-Object System.Windows.Forms.TableLayoutPanel
    $header.Dock = [System.Windows.Forms.DockStyle]::Fill
    $header.ColumnCount = 2
    $header.RowCount = 1
    [void]$header.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 100)))
    [void]$header.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 310)))
    $headerLeft = New-Object System.Windows.Forms.Panel
    $headerLeft.Dock = [System.Windows.Forms.DockStyle]::Fill
    $heading = Add-Label $headerLeft 'Customer accounts' 0 0 540 30
    $heading.Font = $script:HeadingFont
    $subtitle = Add-Label $headerLeft 'Accounts, connection status and subscription control.' 1 32 590 22
    $subtitle.ForeColor = $script:MutedText
    $header.Controls.Add($headerLeft, 0, 0)
    $headerActions = New-Object System.Windows.Forms.FlowLayoutPanel
    $headerActions.Dock = [System.Windows.Forms.DockStyle]::Fill
    $headerActions.FlowDirection = [System.Windows.Forms.FlowDirection]::RightToLeft
    $headerActions.WrapContents = $false
    $headerActions.Padding = New-Object System.Windows.Forms.Padding(0, 5, 0, 0)
    $headerActions.Margin = New-Object System.Windows.Forms.Padding(0)
    $refresh = Add-Button $headerActions 'Refresh list' 0 0 124
    $autoRefresh = New-Object System.Windows.Forms.CheckBox
    $autoRefresh.Text = 'Live status (30s)'
    $autoRefresh.AccessibleName = 'Refresh connection status every thirty seconds'
    $autoRefresh.Size = New-Object Drawing.Size(150, 34)
    $autoRefresh.Checked = $true
    $autoRefresh.ForeColor = $script:MutedText
    $headerActions.Controls.Add($autoRefresh)
    $header.Controls.Add($headerActions, 1, 0)
    [void]$layout.Controls.Add($header, 0, 0)

    $searchRow = New-Object System.Windows.Forms.TableLayoutPanel
    $searchRow.Dock = [System.Windows.Forms.DockStyle]::Fill
    $searchRow.ColumnCount = 2
    $searchRow.RowCount = 1
    [void]$searchRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 48)))
    [void]$searchRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 52)))
    $searchCell = New-Object System.Windows.Forms.Panel
    $searchCell.Dock = [System.Windows.Forms.DockStyle]::Fill
    $searchHint = Add-Label $searchCell 'Search by username or Device ID' 0 1 360 17
    $searchHint.ForeColor = $script:MutedText
    $search = Add-TextBox $searchCell 0 22 360 ''
    $search.Anchor = 'Top,Left,Right'
    $search.AccessibleName = 'Search by username or Device ID'
    $summary = Add-Label $searchRow 'Loading accounts...' 0 10 500 28
    $presenceFilter = New-Object System.Windows.Forms.ComboBox
    $presenceFilter.DropDownStyle = 'DropDownList'
    $presenceFilter.Location = New-Object Drawing.Point(380, 22)
    $presenceFilter.Size = New-Object Drawing.Size(140, 30)
    $presenceFilter.AccessibleName = 'Filter by connection status'
    Set-Style $presenceFilter
    [void]$presenceFilter.Items.AddRange(@('All connections', 'Online', 'Offline', 'Unknown'))
    $presenceFilter.SelectedIndex = 0
    $search.Width = 360
    $search.Anchor = 'Top,Left'
    $searchRow.ColumnStyles[0].Width = 58
    $searchRow.ColumnStyles[1].Width = 42
    $searchCell.Controls.Add($presenceFilter)
    $summary.TextAlign = [System.Drawing.ContentAlignment]::MiddleRight
    $summary.ForeColor = $script:MutedText
    $summary.Dock = [System.Windows.Forms.DockStyle]::Fill
    [void]$searchRow.Controls.Add($searchCell, 0, 0)
    [void]$searchRow.Controls.Add($summary, 1, 0)
    [void]$layout.Controls.Add($searchRow, 0, 1)

    $gridHost = New-Object System.Windows.Forms.Panel
    $gridHost.Dock = [System.Windows.Forms.DockStyle]::Fill
    $gridHost.BackColor = $script:Surface
    $grid = New-Object System.Windows.Forms.DataGridView
    $grid.Dock = [System.Windows.Forms.DockStyle]::Fill
    Set-AccountsGridStyle $grid
    foreach ($columnSpec in @(
        @('id', 'ID'),
        @('username', 'Account'),
        @('active', 'Access'),
        @('online', 'Connection'),
        @('plan', 'Plan'),
        @('plan_key', 'PLAN KEY'),
        @('expires_at', 'Expires'),
        @('days_remaining', 'Days left'),
        @('machine_id', 'Device ID'),
        @('password_change_required', 'PASSWORD CHANGE'),
        @('last_login_at', 'Last contact')
    )) {
        $column = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
        $column.Name = $columnSpec[0]
        $column.HeaderText = $columnSpec[1]
        $column.SortMode = [System.Windows.Forms.DataGridViewColumnSortMode]::NotSortable
        [void]$grid.Columns.Add($column)
    }
    $grid.Columns['id'].Visible = $false
    $grid.Columns['plan_key'].Visible = $false
    $grid.Columns['password_change_required'].Visible = $false
    $grid.Columns['username'].FillWeight = 130
    $grid.Columns['active'].FillWeight = 78
    $grid.Columns['online'].FillWeight = 78
    $grid.Columns['plan'].FillWeight = 94
    $grid.Columns['expires_at'].FillWeight = 100
    $grid.Columns['days_remaining'].FillWeight = 75
    $grid.Columns['machine_id'].Visible = $false
    $grid.Columns['last_login_at'].FillWeight = 132
    [void]$gridHost.Controls.Add($grid)
    $emptyState = Add-Label $gridHost 'No accounts yet. Sync a license before the first client registers.' 24 0 700 50
    $emptyState.Dock = [System.Windows.Forms.DockStyle]::Fill
    $emptyState.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $emptyState.ForeColor = $script:MutedText
    $emptyState.BackColor = $script:Surface
    $emptyState.Visible = $false
    [void]$layout.Controls.Add($gridHost, 0, 2)

    $selectionPanel = New-Object System.Windows.Forms.Panel
    $selectionPanel.Dock = [System.Windows.Forms.DockStyle]::Fill
    $selectionPanel.BackColor = $script:SurfaceRaised
    $selectionPanel.Padding = New-Object System.Windows.Forms.Padding(12, 6, 12, 4)
    $selectionTitle = Add-Label $selectionPanel 'Select an account' 12 5 400 20 $true
    $selectionDetail = Add-Label $selectionPanel 'Choose a row above to review its access and plan.' 12 27 1000 23
    $selectionDetail.ForeColor = $script:MutedText
    $selectionActions = New-Object System.Windows.Forms.FlowLayoutPanel
    $selectionActions.Dock = [System.Windows.Forms.DockStyle]::Bottom
    $selectionActions.FlowDirection = [System.Windows.Forms.FlowDirection]::LeftToRight
    $selectionActions.WrapContents = $false
    $selectionActions.Height = 54
    $selectionActions.Padding = New-Object System.Windows.Forms.Padding(8, 6, 0, 4)
    $selectionActions.Margin = New-Object System.Windows.Forms.Padding(0)
    $selectionActions.BackColor = $script:SurfaceRaised
    $resetPassword = Add-Button $selectionActions 'Reset password' 0 0 142
    $resetPassword.Enabled = $false
    $unlinkDevice = Add-Button $selectionActions 'Unlink device' 0 0 132
    $unlinkDevice.Enabled = $false
    $selectionPanel.Controls.Add($selectionActions)
    [void]$layout.Controls.Add($selectionPanel, 0, 3)

    $planRow = New-Object System.Windows.Forms.TableLayoutPanel
    $planRow.Dock = [System.Windows.Forms.DockStyle]::Fill
    $planRow.ColumnCount = 4
    $planRow.RowCount = 2
    [void]$planRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 194)))
    [void]$planRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 98)))
    [void]$planRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 100)))
    [void]$planRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 142)))
    [void]$planRow.RowStyles.Add((New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 24)))
    [void]$planRow.RowStyles.Add((New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Percent, 100)))
    $planHeading = Add-Label $planRow 'New plan' 0 1 180 20 $true
    $planDaysHeading = Add-Label $planRow 'Days' 0 1 90 20
    $planHint = Add-Label $planRow 'The selected plan replaces the current term. Suspension status is unchanged.' 0 1 520 34
    $planHint.ForeColor = $script:MutedText
    $newPlan = New-Object System.Windows.Forms.ComboBox
    $newPlan.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
    $newPlan.Dock = [System.Windows.Forms.DockStyle]::Fill
    $newPlan.Margin = New-Object System.Windows.Forms.Padding(0, 0, 12, 6)
    Set-Style $newPlan
    [void]$newPlan.Items.Add('Trial (7 days)')
    [void]$newPlan.Items.Add('Custom duration')
    [void]$newPlan.Items.Add('Unlimited')
    $newPlan.SelectedIndex = 1
    $planDays = New-Object System.Windows.Forms.NumericUpDown
    $planDays.Minimum = 1
    $planDays.Maximum = 3650
    $planDays.Value = 30
    $planDays.Dock = [System.Windows.Forms.DockStyle]::Fill
    $planDays.Margin = New-Object System.Windows.Forms.Padding(0, 0, 12, 6)
    Set-Style $planDays
    $applyPlan = Add-Button $planRow 'Apply plan' 0 0 132
    $applyPlan.Dock = [System.Windows.Forms.DockStyle]::Fill
    $applyPlan.Margin = New-Object System.Windows.Forms.Padding(0, 0, 0, 6)
    $applyPlan.Enabled = $false
    foreach ($control in @($newPlan, $planDays, $applyPlan)) { $control.Enabled = $false }
    [void]$planRow.Controls.Add($planHeading, 0, 0)
    [void]$planRow.Controls.Add($planDaysHeading, 1, 0)
    [void]$planRow.Controls.Add($planHint, 2, 0)
    [void]$planRow.Controls.Add($newPlan, 0, 1)
    [void]$planRow.Controls.Add($planDays, 1, 1)
    [void]$planRow.Controls.Add($applyPlan, 3, 1)
    [void]$layout.Controls.Add($planRow, 0, 4)

    $renewRow = New-Object System.Windows.Forms.TableLayoutPanel
    $renewRow.Dock = [System.Windows.Forms.DockStyle]::Fill
    $renewRow.ColumnCount = 4
    $renewRow.RowCount = 2
    [void]$renewRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 112)))
    [void]$renewRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 184)))
    [void]$renewRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 164)))
    [void]$renewRow.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 100)))
    [void]$renewRow.RowStyles.Add((New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 24)))
    [void]$renewRow.RowStyles.Add((New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Percent, 100)))
    $renewDaysHeading = Add-Label $renewRow 'Add days' 0 1 100 20
    $renewHeading = Add-Label $renewRow 'Renewal' 0 1 170 20 $true
    $accessHeading = Add-Label $renewRow 'Account access' 0 1 150 20
    $statusHeading = Add-Label $renewRow 'Feedback' 0 1 100 20
    $amount = New-Object System.Windows.Forms.NumericUpDown
    $amount.Minimum = 1
    $amount.Maximum = 3650
    $amount.Value = 30
    $amount.Dock = [System.Windows.Forms.DockStyle]::Fill
    $amount.Margin = New-Object System.Windows.Forms.Padding(0, 0, 12, 6)
    Set-Style $amount
    $renew = Add-Button $renewRow 'Extend and reactivate' 0 0 170
    $renew.Dock = [System.Windows.Forms.DockStyle]::Fill
    $renew.Margin = New-Object System.Windows.Forms.Padding(0, 0, 12, 6)
    $renew.Enabled = $false
    $toggle = Add-Button $renewRow 'Disable account' 0 0 150
    $toggle.Dock = [System.Windows.Forms.DockStyle]::Fill
    $toggle.Margin = New-Object System.Windows.Forms.Padding(0, 0, 12, 6)
    $toggle.Enabled = $false
    $status = Add-Label $renewRow 'Select an account to manage its plan or access.' 0 1 360 36
    $status.Dock = [System.Windows.Forms.DockStyle]::Fill
    $status.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
    $status.ForeColor = $script:MutedText
    [void]$renewRow.Controls.Add($renewDaysHeading, 0, 0)
    [void]$renewRow.Controls.Add($renewHeading, 1, 0)
    [void]$renewRow.Controls.Add($accessHeading, 2, 0)
    [void]$renewRow.Controls.Add($statusHeading, 3, 0)
    [void]$renewRow.Controls.Add($amount, 0, 1)
    [void]$renewRow.Controls.Add($renew, 1, 1)
    [void]$renewRow.Controls.Add($toggle, 2, 1)
    [void]$renewRow.Controls.Add($status, 3, 1)
    [void]$layout.Controls.Add($renewRow, 0, 5)

    $footer = Add-Label $layout 'Refresh the list to check recent connections.' 0 0 1000 24
    $footer.ForeColor = $script:MutedText
    [void]$layout.Controls.Add($footer, 0, 6)

    $currentUsers = @()
    $newPlan.Add_SelectedIndexChanged({
        $planDays.Enabled = ($newPlan.SelectedIndex -eq 1 -and $grid.SelectedRows.Count -gt 0)
        switch ($newPlan.SelectedIndex) {
            0 { $planHint.Text = 'Replace the current term with 7 days from today. Account access is unchanged.' }
            1 { $planHint.Text = 'Replace the current term with the selected number of days from today.' }
            2 { $planHint.Text = 'Remove the expiration date. Account access is unchanged.' }
        }
    })
    $applyFilter = {
        $needle = $search.Text.Trim()
        $visibleCount = 0
        foreach ($row in $grid.Rows) {
            $matchesSearch = -not $needle -or
                ([string]$row.Cells['username'].Value).IndexOf($needle, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
                ([string]$row.Cells['machine_id'].Value).IndexOf($needle, [StringComparison]::OrdinalIgnoreCase) -ge 0
            $matchesPresence = $presenceFilter.SelectedIndex -eq 0 -or ([string]$row.Cells['online'].Value -eq [string]$presenceFilter.SelectedItem)
            if ($row.Selected -and -not ($matchesSearch -and $matchesPresence)) { $row.Selected = $false }
            if ($grid.CurrentRow -eq $row -and -not ($matchesSearch -and $matchesPresence)) { $grid.CurrentCell = $null }
            $row.Visible = ($matchesSearch -and $matchesPresence)
            if ($row.Visible) { $visibleCount++ }
        }
        $emptyState.Visible = ($visibleCount -eq 0)
        if ($grid.Rows.Count -eq 0) {
            $emptyState.Text = 'No accounts yet. Sync a license before the first client registers.'
        }
        elseif ($visibleCount -eq 0) {
            $emptyState.Text = 'No accounts match these filters.'
        }
    }
    $search.Add_TextChanged($applyFilter)
    $presenceFilter.Add_SelectedIndexChanged($applyFilter)
    $grid.Add_CellFormatting({
        $eventArgs = $_
        if ($eventArgs.ColumnIndex -eq $grid.Columns['active'].Index) {
            if ([string]$eventArgs.Value -eq 'Enabled') {
                $eventArgs.CellStyle.ForeColor = $script:Mint
            }
            else {
                $eventArgs.CellStyle.ForeColor = $script:WarningColor
            }
        }
        elseif ($eventArgs.ColumnIndex -eq $grid.Columns['online'].Index) {
            $state = [string]$eventArgs.Value
            switch ($state) {
                'Online' { $eventArgs.CellStyle.ForeColor = $script:Mint }
                'Recently active' { $eventArgs.CellStyle.ForeColor = $script:BlueAccent }
                'Offline' { $eventArgs.CellStyle.ForeColor = $script:MutedText }
                default { $eventArgs.CellStyle.ForeColor = $script:WarningColor }
            }
        }
    })
    $grid.Add_SelectionChanged({
        if ($grid.SelectedRows.Count -eq 0) {
            $selectionTitle.Text = 'Select an account'
            $selectionDetail.Text = 'Choose a row above to review its access and plan.'
            $applyPlan.Enabled = $false
            $newPlan.Enabled = $false
            $planDays.Enabled = $false
            $renew.Enabled = $false
            $toggle.Enabled = $false
            $resetPassword.Enabled = $false
            $unlinkDevice.Enabled = $false
            return
        }
        $row = $grid.SelectedRows[0]
        $username = [string]$row.Cells['username'].Value
        $statusValue = [string]$row.Cells['active'].Value
        $onlineValue = [string]$row.Cells['online'].Value
        $planValue = [string]$row.Cells['plan_key'].Value
        $planName = [string]$row.Cells['plan'].Value
        $expiryValue = [string]$row.Cells['expires_at'].Value
        $passwordState = if ($row.Cells['password_change_required'].Value) { '   |   Password change required' } else { '' }
        $selectionTitle.Text = $username
        $selectionDetail.Text = "$statusValue   |   $onlineValue   |   $planName   |   Expires $expiryValue$passwordState"
        switch ($planValue) {
            'trial' { $newPlan.SelectedIndex = 0 }
            'duration' { $newPlan.SelectedIndex = 1 }
            'unlimited' { $newPlan.SelectedIndex = 2 }
        }
        $applyPlan.Enabled = $true
        $newPlan.Enabled = $true
        $planDays.Enabled = ($newPlan.SelectedIndex -eq 1)
        $renew.Enabled = ($planValue -ne 'unlimited')
        $toggle.Text = if ($statusValue -eq 'Enabled') { 'Disable account' } else { 'Enable account' }
        $toggle.Enabled = $true
        $resetPassword.Enabled = $true
        $unlinkDevice.Enabled = -not [string]::IsNullOrWhiteSpace([string]$row.Cells['machine_id'].Value)
    })
    $refreshGrid = {
        $refresh.Enabled = $false
        $dialog.UseWaitCursor = $true
        $status.Text = 'Loading accounts...'
        $status.ForeColor = $script:MutedText
        $dialog.Refresh()
        try {
            $result = Invoke-LicenseService 'GET' '/v1/admin/users'
            $currentUsers = @($result.users)
            $grid.Rows.Clear()
            foreach ($user in $currentUsers) {
                $active = if ($user.active -and $user.license_enabled) { 'Enabled' } else { 'Disabled' }
                $onlineState = Get-UserOnlineState $user
                $planName = switch ($user.plan) {
                    'trial' { 'Trial' }
                    'duration' { 'Custom duration' }
                    'unlimited' { 'Unlimited' }
                    default { [string]$user.plan }
                }
                $expiry = if ($user.expires_at) { ([DateTime]::Parse($user.expires_at)).ToLocalTime().ToString('yyyy-MM-dd') } else { 'No expiry' }
                $daysLeft = if ($null -eq $user.days_remaining) { 'Unlimited' } else { [string]$user.days_remaining }
                $last = if ($user.last_seen_at) { ([DateTime]::Parse($user.last_seen_at)).ToLocalTime().ToString('yyyy-MM-dd HH:mm') } else { 'Never' }
                [void]$grid.Rows.Add([string]$user.id, $user.username, $active, $onlineState, $planName, $user.plan, $expiry, $daysLeft, $user.machine_id, [bool]$user.password_change_required, $last)
            }
            $grid.ClearSelection()
            $grid.CurrentCell = $null
            $total = $currentUsers.Count
            $activeCount = @($currentUsers | Where-Object { $_.active -and $_.license_enabled }).Count
            $onlineCount = @($currentUsers | Where-Object { (Get-UserOnlineState $_) -eq 'Online' }).Count
            $offlineCount = @($currentUsers | Where-Object { (Get-UserOnlineState $_) -eq 'Offline' }).Count
            $unknownCount = $total - $onlineCount - $offlineCount
            $summary.Text = "$total accounts   |   $onlineCount online   |   $offlineCount offline   |   $unknownCount unknown"
            $footer.Text = if ($result.presence_window_seconds) { "Online: authenticated contact within $([int]$result.presence_window_seconds / 60) minutes. Offline may include clients using saved access. Refreshed $([DateTime]::Now.ToString('HH:mm:ss'))." } else { 'Presence unavailable: update the license service. Account controls remain available.' }
            $emptyState.Visible = ($total -eq 0)
            $emptyState.Text = 'No accounts yet. Sync a license before the first client registers.'
            $status.Text = 'Select an account to manage its plan or access.'
            & $applyFilter
            $status.ForeColor = $script:MutedText
        }
        catch {
            foreach ($row in $grid.Rows) { $row.Cells['online'].Value = 'Unknown' }
            $summary.Text = 'Connection status unavailable'
            & $applyFilter
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
            if ($grid.Rows.Count -eq 0) {
                $emptyState.Text = 'Accounts could not be loaded. Check service settings and refresh.'
                $emptyState.Visible = $true
            }
        }
        finally {
            $dialog.UseWaitCursor = $false
            $refresh.Enabled = $true
        }
    }
    $refresh.Add_Click($refreshGrid)
    # Update presence only so an administrator's selected plan and duration survive polling.
    $presenceTimer = New-Object System.Windows.Forms.Timer
    $presenceTimer.Interval = 30000
    $presenceTimer.Add_Tick({
        if (-not $autoRefresh.Checked -or -not $refresh.Enabled -or -not $dialog.ContainsFocus) { return }
        $presenceTimer.Stop()
        try {
            $result = Invoke-LicenseService 'GET' '/v1/admin/users'
            foreach ($row in $grid.Rows) {
                $user = @($result.users | Where-Object { [string]$_.id -eq [string]$row.Cells['id'].Value }) | Select-Object -First 1
                $row.Cells['online'].Value = Get-UserOnlineState $user
                if ($user.last_seen_at) { $row.Cells['last_login_at'].Value = ([DateTime]::Parse($user.last_seen_at)).ToLocalTime().ToString('yyyy-MM-dd HH:mm') }
            }
            $onlineCount = @($result.users | Where-Object { (Get-UserOnlineState $_) -eq 'Online' }).Count
            $offlineCount = @($result.users | Where-Object { (Get-UserOnlineState $_) -eq 'Offline' }).Count
            $unknownCount = @($result.users).Count - $onlineCount - $offlineCount
            $summary.Text = "$(@($result.users).Count) accounts   |   $onlineCount online   |   $offlineCount offline   |   $unknownCount unknown"
            $footer.Text = if ($result.presence_window_seconds) { "Online: contact within 6 minutes. Connection status refreshes every 30 seconds. Updated $([DateTime]::Now.ToString('HH:mm:ss'))." } else { 'Presence unavailable: update the license service.' }
            & $applyFilter
        } catch {
            foreach ($row in $grid.Rows) { $row.Cells['online'].Value = 'Unknown' }
            $summary.Text = 'Connection status unavailable'
            $footer.Text = 'Connection status could not be refreshed. Check service settings and refresh the list.'
            & $applyFilter
        } finally { $presenceTimer.Start() }
    })
    $dialog.Add_Shown({ $presenceTimer.Start() })
    $dialog.Add_FormClosed({ $presenceTimer.Stop(); $presenceTimer.Dispose() })
    $resetPassword.Add_Click({
        if ($grid.SelectedRows.Count -eq 0) { $status.Text = 'Select an account first.'; $status.ForeColor = $script:WarningColor; return }
        $row = $grid.SelectedRows[0]
        $id = [int]$row.Cells['id'].Value
        $username = [string]$row.Cells['username'].Value
        Show-AccountPasswordDialog -Owner $dialog -UserId $id -Username $username
        & $refreshGrid
    })
    $unlinkDevice.Add_Click({
        if ($grid.SelectedRows.Count -eq 0) { $status.Text = 'Select an account first.'; $status.ForeColor = $script:WarningColor; return }
        $row = $grid.SelectedRows[0]
        $id = [int]$row.Cells['id'].Value
        $username = [string]$row.Cells['username'].Value
        $deviceId = [string]$row.Cells['machine_id'].Value
        $confirm = [System.Windows.Forms.MessageBox]::Show(
            $dialog,
            "Unlink $username from device $deviceId? Their active sessions will be revoked. The next successful sign-in will bind the account to that device. Previously issued offline access on the old device may remain usable for up to seven days.",
            'Unlink account from device',
            [System.Windows.Forms.MessageBoxButtons]::OKCancel,
            [System.Windows.Forms.MessageBoxIcon]::Warning
        )
        if ($confirm -ne [System.Windows.Forms.DialogResult]::OK) { return }
        try {
            $null = Invoke-UserAdminAction -UserId $id -Operation 'unlink-device' -Body @{}
            & $refreshGrid
            $status.Text = "$username is unlinked. Its next successful sign-in will bind the new device."
            $status.ForeColor = $script:Mint
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
        }
    })
    $applyPlan.Add_Click({
        if ($grid.SelectedRows.Count -eq 0) { $status.Text = 'Select an account first.'; $status.ForeColor = $script:WarningColor; return }
        $selected = @('trial', 'duration', 'unlimited')[$newPlan.SelectedIndex]
        $username = [string]$grid.SelectedRows[0].Cells['username'].Value
        $termText = if ($selected -eq 'trial') { '7 days from today' } elseif ($selected -eq 'duration') { "$($planDays.Value) days from today" } else { 'no expiration date (Unlimited)' }
        $confirm = [System.Windows.Forms.MessageBox]::Show(
            $dialog,
            "Change $username to $($newPlan.SelectedItem)?`r`nThe new term will be $termText.`r`nThis does not change whether the account is enabled.",
            'Confirm plan change',
            [System.Windows.Forms.MessageBoxButtons]::OKCancel,
            [System.Windows.Forms.MessageBoxIcon]::Question
        )
        if ($confirm -ne [System.Windows.Forms.DialogResult]::OK) { return }
        try {
            $id = [int]$grid.SelectedRows[0].Cells['id'].Value
            $body = @{ plan = $selected }
            if ($selected -eq 'duration') { $body.days = [int]$planDays.Value }
            $changed = Invoke-LicenseService 'PATCH' "/v1/admin/users/$id/plan" $body
            & $refreshGrid
            $expiryText = if ($changed.expires_at) { ([DateTime]::Parse($changed.expires_at)).ToLocalTime().ToString('yyyy-MM-dd') } else { 'no expiration' }
            $status.Text = "$username changed to $($changed.plan). New expiration: $expiryText. Account enabled state was not changed."
            $status.ForeColor = $script:Mint
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
        }
    })
    $renew.Add_Click({
        if ($grid.SelectedRows.Count -eq 0) { $status.Text = 'Select an account first.'; $status.ForeColor = $script:WarningColor; return }
        try {
            $id = [int]$grid.SelectedRows[0].Cells['id'].Value
            $result = Invoke-LicenseService 'POST' "/v1/admin/users/$id/renew" @{ days = [int]$amount.Value }
            & $refreshGrid
            $status.Text = "Added $($result.days_added) day(s) to $($result.username). Expires $($result.expires_at)."
            $status.ForeColor = $script:Mint
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
        }
    })
    $toggle.Add_Click({
        if ($grid.SelectedRows.Count -eq 0) { $status.Text = 'Select an account first.'; $status.ForeColor = $script:WarningColor; return }
        try {
            $row = $grid.SelectedRows[0]
            $id = [int]$row.Cells['id'].Value
            $path = if ($row.Cells['active'].Value -eq 'Enabled') { "/v1/admin/users/$id/disable" } else { "/v1/admin/users/$id/enable" }
            $null = Invoke-LicenseService 'POST' $path @{}
            & $refreshGrid
            $status.Text = if ($path -like '*/disable') { 'Account disabled; active sessions revoked.' } else { 'Account enabled.' }
            $status.ForeColor = $script:Mint
        }
        catch {
            $status.Text = $_.Exception.Message
            $status.ForeColor = $script:ErrorColor
        }
    })
    $dialog.Add_Shown($refreshGrid)
    [void]$dialog.ShowDialog($script:MainForm)
    $dialog.Dispose()
}

$script:AuthorityReady = $false
$script:AuthorityError = $null
$script:IssuanceBusy = $false

function Update-IssueReadiness {
    $deviceReady = $script:DeviceInput.Text.Trim() -match '^[A-Fa-f0-9]{32}$'
    $serviceReady = -not [string]::IsNullOrWhiteSpace($script:ManagerSettings.server_url) -and
        -not [string]::IsNullOrWhiteSpace($script:ManagerSettings.admin_token)
    $script:AuthorityState.Text = if ($script:AuthorityReady) { 'Ready' } else { 'Not configured' }
    $script:AuthorityState.ForeColor = if ($script:AuthorityReady) { $script:Mint } else { $script:WarningColor }
    if ($script:AuthorityError) {
        $script:AuthorityState.Text = 'Unable to verify'
        $script:AuthorityState.ForeColor = $script:ErrorColor
        $script:AuthorityDetail.Text = $script:AuthorityError
    }
    else {
        $script:AuthorityDetail.Text = if ($script:AuthorityReady) { 'Protected for this Windows account' } else { 'Create the signing authority once' }
    }
    $script:ServiceState.Text = if ($serviceReady) { 'Configured' } else { 'Needs setup' }
    $script:ServiceState.ForeColor = if ($serviceReady) { $script:Mint } else { $script:WarningColor }
    $script:ServiceBadge.Text = if ($serviceReady) { 'LICENSE SERVICE CONFIGURED' } else { 'Service setup required' }
    $script:ServiceBadge.ForeColor = if ($serviceReady) { $script:Mint } else { $script:WarningColor }
    if ($script:SettingsLoadError) {
        $script:ServiceState.Text = 'Unable to decrypt settings'
        $script:ServiceState.ForeColor = $script:ErrorColor
        $script:ServiceDetail.Text = $script:SettingsLoadError
    }
    else {
        $script:ServiceDetail.Text = if ($serviceReady) { $script:ManagerSettings.server_url } else { 'Set the service URL and administrator token' }
    }
    $script:DeviceState.Text = if ($deviceReady) { 'Valid device ID' } else { 'Enter 32 hexadecimal characters' }
    $script:DeviceState.ForeColor = if ($deviceReady) { $script:Mint } else { $script:MutedText }
    $missingSteps = @()
    if (-not $deviceReady) { $missingSteps += 'a valid Device ID' }
    if (-not $serviceReady) { $missingSteps += 'Service settings' }
    if (-not $script:AuthorityReady) {
        $missingSteps += if ($script:AuthorityError) { 'a valid signing authority' } else { 'signing authority setup' }
    }
    $issuanceReady = $missingSteps.Count -eq 0
    $script:IssueDescription.Text = if ($issuanceReady) {
        'Ready to issue. Choose a plan, then generate and sync the device-bound key.'
    }
    else {
        'To issue a key, complete: ' + ($missingSteps -join ', ') + '.'
    }
    $script:AuthorityButton.Visible = -not $script:AuthorityReady
    $script:IssueGenerate.Enabled = -not $script:IssuanceBusy
    $script:IssueGenerate.Text = if ($issuanceReady) { 'Generate and sync' } else { 'Complete setup to issue' }
    $script:IssueGenerate.BackColor = if ($issuanceReady) { $script:BlueAccent } else { $script:WarningColor }
    $script:IssueGenerate.ForeColor = $script:Canvas
    $script:IssueGenerate.AccessibleDescription = $script:IssueDescription.Text
    $hasKey = -not [string]::IsNullOrWhiteSpace($script:KeyOutput.Text)
    $script:IssueCopy.Visible = $hasKey
    $script:IssueCopy.Enabled = $hasKey
    $script:KeyEmptyState.Visible = -not $hasKey
}

function Refresh-IssueAuthority {
    $script:AuthorityReady = $false
    $script:AuthorityError = $null
    if (Test-Path -LiteralPath $script:KeyPath) {
        try {
            $rsa = Get-PrivateRsa
            $rsa.Dispose()
            $script:AuthorityReady = $true
        }
        catch {
            $script:AuthorityError = $_.Exception.Message
        }
    }
    Update-IssueReadiness
}

function Clear-IssuedKey {
    if (-not [string]::IsNullOrWhiteSpace($script:KeyOutput.Text)) {
        $script:KeyOutput.Clear()
        $script:KeyStatus.Text = 'Issuance details changed. Generate a new key before copying.'
        $script:KeyStatus.ForeColor = $script:WarningColor
    }
    Update-IssueReadiness
}

$script:MainForm = New-Object System.Windows.Forms.Form
Set-FormBase $script:MainForm 'Aetherion License Manager' $true
$workingArea = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$initialWidth = [Math]::Min(1160, $workingArea.Width - 40)
$initialHeight = [Math]::Min(720, $workingArea.Height - 20)
$minimumWidth = [Math]::Min(960, $workingArea.Width - 40)
$minimumHeight = [Math]::Min(650, $workingArea.Height - 40)
$script:MainForm.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
$script:MainForm.Size = New-Object System.Drawing.Size($initialWidth, $initialHeight)
$script:MainForm.MinimumSize = New-Object System.Drawing.Size($minimumWidth, $minimumHeight)
$script:MainForm.Location = New-Object System.Drawing.Point(
    ($workingArea.Left + [int](($workingArea.Width - $initialWidth) / 2)),
    ($workingArea.Top + [int](($workingArea.Height - $initialHeight) / 2))
)

$header = New-Object System.Windows.Forms.TableLayoutPanel
$header.Dock = [System.Windows.Forms.DockStyle]::Top
$header.Height = 78
$header.Padding = New-Object System.Windows.Forms.Padding(24, 12, 24, 8)
$header.Margin = New-Object System.Windows.Forms.Padding(0)
$header.BackColor = $script:Surface
$header.ColumnCount = 2
$header.RowCount = 1
[void]$header.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 58)))
[void]$header.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 42)))
$brandPanel = New-Object System.Windows.Forms.Panel
$brandPanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$mark = New-Object System.Windows.Forms.PictureBox
$mark.Image = $script:BrandMark
$mark.Location = New-Object System.Drawing.Point(0, 4)
$mark.Size = New-Object System.Drawing.Size(42, 42)
$mark.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom
$mark.AccessibleName = 'Aetherion orbital star'
$brandPanel.Controls.Add($mark)
$brand = Add-Label $brandPanel 'AETHERION' 54 1 280 26 $true
$brand.Font = New-Object System.Drawing.Font($fontFamily, 14, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Point)
$brandSub = Add-Label $brandPanel 'BEYOND THE KNOWN.' 55 31 280 18
$brandSub.ForeColor = $script:MutedText
$brandSub.Font = $script:SmallFont
[void]$header.Controls.Add($brandPanel, 0, 0)
$headerActions = New-Object System.Windows.Forms.FlowLayoutPanel
$headerActions.Dock = [System.Windows.Forms.DockStyle]::Fill
$headerActions.FlowDirection = [System.Windows.Forms.FlowDirection]::RightToLeft
$headerActions.WrapContents = $false
$headerActions.Padding = New-Object System.Windows.Forms.Padding(0, 8, 0, 0)
$headerActions.Margin = New-Object System.Windows.Forms.Padding(0)
$accounts = Add-Button $headerActions 'Manage accounts' 0 0 154
$settings = Add-Button $headerActions 'Service settings' 0 0 146
[void]$header.Controls.Add($headerActions, 1, 0)
$script:MainForm.Controls.Add($header)

$workspace = New-Object System.Windows.Forms.Panel
$workspace.Dock = [System.Windows.Forms.DockStyle]::Fill
$workspace.Padding = New-Object System.Windows.Forms.Padding(18)
$workspace.BackColor = $script:Canvas
$script:MainForm.Controls.Add($workspace)
$workspace.BringToFront()

$body = New-Object System.Windows.Forms.TableLayoutPanel
$body.ColumnCount = 2
$body.RowCount = 1
$body.Padding = New-Object System.Windows.Forms.Padding(0)
$body.Margin = New-Object System.Windows.Forms.Padding(0)
$body.Anchor = 'Top,Left'
[void]$body.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Absolute, 260)))
[void]$body.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 100)))
[void]$body.RowStyles.Add((New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Percent, 100)))
$workspace.Controls.Add($body)

$updateMainLayout = {
    $availableWidth = [Math]::Max(1, $workspace.ClientSize.Width)
    $availableHeight = [Math]::Max(1, $workspace.ClientSize.Height)
    $bodyWidth = [Math]::Min(1520, $availableWidth)
    $body.Location = New-Object System.Drawing.Point([int](($availableWidth - $bodyWidth) / 2), 0)
    $body.Size = New-Object System.Drawing.Size($bodyWidth, $availableHeight)
}
$workspace.Add_Resize($updateMainLayout)
$script:MainForm.Add_Shown($updateMainLayout)

$setupPanel = New-Object System.Windows.Forms.Panel
$setupPanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$setupPanel.BackColor = $script:Surface
$setupPanel.Padding = New-Object System.Windows.Forms.Padding(16)
[void]$body.Controls.Add($setupPanel, 0, 0)
$setupTitle = Add-Label $setupPanel 'Client project' 18 18 224 26
$setupTitle.Font = $script:EmphasisFont
Add-Label $setupPanel 'Project folder' 18 64 224 18 $true | Out-Null
$rootBox = Add-TextBox $setupPanel 18 87 224 $script:Root
$rootBox.Anchor = 'Top,Left,Right'
$rootBox.AccessibleName = 'Aetherion client project folder'
$toolTip = New-Object System.Windows.Forms.ToolTip
$toolTip.SetToolTip($rootBox, $script:Root)
$browse = Add-Button $setupPanel 'Browse for project' 18 126 224
$browse.Anchor = 'Top,Left,Right'
$script:AuthorityState = Add-Label $setupPanel 'Not configured' 18 194 224 22 $true
$script:AuthorityDetail = Add-Label $setupPanel 'Create the signing authority once' 18 219 224 40
$script:AuthorityDetail.ForeColor = $script:MutedText
$setup = Add-Button $setupPanel 'Create authority' 18 266 224
$setup.Anchor = 'Top,Left,Right'
$servicePanel = New-Object System.Windows.Forms.Panel
$servicePanel.Location = New-Object System.Drawing.Point(18, 320)
$servicePanel.Size = New-Object System.Drawing.Size(224, 168)
$servicePanel.Anchor = 'Top,Left,Right'
$servicePanel.Margin = New-Object System.Windows.Forms.Padding(0)
$setupPanel.Controls.Add($servicePanel)
$divider = New-Object System.Windows.Forms.Label
$divider.BackColor = $script:BorderColor
$divider.Location = New-Object System.Drawing.Point(0, 0)
$divider.Size = New-Object System.Drawing.Size(224, 1)
$divider.Anchor = 'Top,Left,Right'
$servicePanel.Controls.Add($divider)
$serviceHeading = Add-Label $servicePanel 'License service' 0 18 224 24
$serviceHeading.Font = $script:EmphasisFont
$script:ServiceState = Add-Label $servicePanel 'Needs setup' 0 48 224 22 $true
$script:ServiceDetail = Add-Label $servicePanel 'Set the service URL and administrator token' 0 72 224 40
$script:ServiceDetail.ForeColor = $script:MutedText
$script:ServiceDetail.AutoEllipsis = $true
$settingsInline = Add-Button $servicePanel 'Open service settings' 0 122 224
$settingsInline.Anchor = 'Bottom,Left,Right'
$settingsInline.Margin = New-Object System.Windows.Forms.Padding(0, 0, 0, 8)
$script:AuthorityButton = $null
$script:AuthorityButton = $setup

$issuePanel = New-Object System.Windows.Forms.Panel
$issuePanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$issuePanel.BackColor = $script:Canvas
$issuePanel.Padding = New-Object System.Windows.Forms.Padding(32, 20, 24, 16)
[void]$body.Controls.Add($issuePanel, 1, 0)

$issueLayout = New-Object System.Windows.Forms.TableLayoutPanel
$issueLayout.Dock = [System.Windows.Forms.DockStyle]::Fill
$issueLayout.ColumnCount = 1
$issueLayout.RowCount = 7
$issueLayout.Padding = New-Object System.Windows.Forms.Padding(0)
$issueLayout.Margin = New-Object System.Windows.Forms.Padding(0)
foreach ($rowStyle in @(
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 70)),
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 76)),
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 76)),
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 48)),
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 26)),
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Percent, 100)),
    (New-Object System.Windows.Forms.RowStyle([System.Windows.Forms.SizeType]::Absolute, 48))
)) { [void]$issueLayout.RowStyles.Add($rowStyle) }
[void]$issueLayout.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 100)))
$issuePanel.Controls.Add($issueLayout)

$issueHeader = New-Object System.Windows.Forms.Panel
$issueHeader.Dock = [System.Windows.Forms.DockStyle]::Fill
$issueHeader.Margin = New-Object System.Windows.Forms.Padding(0)
$issueHeading = Add-Label $issueHeader 'Issue a license' 0 0 600 34
$issueHeading.Font = $script:HeadingFont
$script:IssueDescription = Add-Label $issueHeader "Signed on this device and bound to the customer's Device ID." 1 36 600 22
$script:IssueDescription.Anchor = 'Top,Left,Right'
$script:IssueDescription.ForeColor = $script:MutedText
$script:IssueDescription.AutoEllipsis = $true
$script:ServiceBadge = Add-Label $issueHeader 'LICENSE SERVICE' 0 8 220 24 $true
$script:ServiceBadge.Location = New-Object System.Drawing.Point(540, 8)
$script:ServiceBadge.BackColor = $script:SurfaceRaised
$script:ServiceBadge.Padding = New-Object System.Windows.Forms.Padding(8, 2, 8, 2)
$serviceBadgeLayout = {
    $script:ServiceBadge.Visible = $issueHeader.ClientSize.Width -ge 760
    if ($script:ServiceBadge.Visible) {
        $script:ServiceBadge.Left = $issueHeader.ClientSize.Width - $script:ServiceBadge.Width
    }
}.GetNewClosure()
$issueHeader.Add_Resize($serviceBadgeLayout)
$script:ServiceBadge.TextAlign = [System.Drawing.ContentAlignment]::MiddleRight
$script:ServiceBadge.Font = $script:SmallFont
[void]$issueLayout.Controls.Add($issueHeader, 0, 0)

$devicePanel = New-Object System.Windows.Forms.Panel
$devicePanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$devicePanel.Margin = New-Object System.Windows.Forms.Padding(0)
Add-Label $devicePanel 'Device ID' 0 3 300 18 $true | Out-Null
$script:DeviceInput = Add-TextBox $devicePanel 0 27 600 ''
$script:DeviceInput.Anchor = 'Top,Left,Right'
$script:DeviceInput.AccessibleName = 'Customer device ID'
$script:DeviceInput.MaxLength = 32
$deviceToolTip = New-Object System.Windows.Forms.ToolTip
$deviceToolTip.SetToolTip($script:DeviceInput, 'Enter the 32-character hexadecimal Device ID from Aetherion Client.')
$script:DeviceState = Add-Label $devicePanel 'Enter 32 hexadecimal characters' 0 57 600 18
$script:DeviceState.ForeColor = $script:MutedText
[void]$issueLayout.Controls.Add($devicePanel, 0, 1)

$options = New-Object System.Windows.Forms.TableLayoutPanel
$options.Dock = [System.Windows.Forms.DockStyle]::Fill
$options.ColumnCount = 3
$options.RowCount = 1
$options.Padding = New-Object System.Windows.Forms.Padding(0)
$options.Margin = New-Object System.Windows.Forms.Padding(0)
[void]$options.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 43)))
[void]$options.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 36)))
[void]$options.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle([System.Windows.Forms.SizeType]::Percent, 21)))
$licenseePanel = New-Object System.Windows.Forms.Panel
$licenseePanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$licenseePanel.Padding = New-Object System.Windows.Forms.Padding(0, 0, 12, 0)
Add-Label $licenseePanel 'Licensed to (optional)' 0 3 280 18 $true | Out-Null
$licensedTo = Add-TextBox $licenseePanel 0 27 250 ''
$licensedTo.Anchor = 'Top,Left,Right'
$licensedTo.AccessibleName = 'Licensee name, optional'
[void]$options.Controls.Add($licenseePanel, 0, 0)
$planPanel = New-Object System.Windows.Forms.Panel
$planPanel.Dock = [System.Windows.Forms.DockStyle]::Fill
$planPanel.Padding = New-Object System.Windows.Forms.Padding(0, 0, 12, 0)
Add-Label $planPanel 'Plan' 0 3 180 18 $true | Out-Null
$plan = New-Object System.Windows.Forms.ComboBox
$plan.Location = New-Object System.Drawing.Point(0, 27)
$plan.Size = New-Object System.Drawing.Size(180, 30)
$plan.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
$plan.Anchor = 'Top,Left,Right'
$plan.AccessibleName = 'License plan'
Set-Style $plan
[void]$plan.Items.Add('Trial (7 days)')
[void]$plan.Items.Add('Custom duration')
[void]$plan.Items.Add('Unlimited')
$plan.SelectedIndex = 0
[void]$planPanel.Controls.Add($plan)
[void]$options.Controls.Add($planPanel, 1, 0)
$daysPanel = New-Object System.Windows.Forms.Panel
$daysPanel.Dock = [System.Windows.Forms.DockStyle]::Fill
Add-Label $daysPanel 'Days' 0 3 110 18 $true | Out-Null
$days = New-Object System.Windows.Forms.NumericUpDown
$days.Location = New-Object System.Drawing.Point(0, 27)
$days.Size = New-Object System.Drawing.Size(110, 30)
$days.Minimum = 1
$days.Maximum = 3650
$days.Value = 30
$days.Anchor = 'Top,Left,Right'
$days.AccessibleName = 'Custom license duration in days'
Set-Style $days
[void]$daysPanel.Controls.Add($days)
[void]$options.Controls.Add($daysPanel, 2, 0)
$plan.Add_SelectedIndexChanged({ $days.Enabled = ($plan.SelectedIndex -eq 1) })
[void]$issueLayout.Controls.Add($options, 0, 2)

$actionRow = New-Object System.Windows.Forms.FlowLayoutPanel
$actionRow.Dock = [System.Windows.Forms.DockStyle]::Fill
$actionRow.FlowDirection = [System.Windows.Forms.FlowDirection]::LeftToRight
$actionRow.WrapContents = $false
$actionRow.Margin = New-Object System.Windows.Forms.Padding(0)
$actionRow.Padding = New-Object System.Windows.Forms.Padding(0, 4, 0, 0)
$script:IssueGenerate = Add-Button $actionRow 'Generate and sync' 0 0 170
$script:IssueGenerate.Font = $script:EmphasisFont
$script:IssueGenerate.BackColor = $script:SurfaceRaised
$script:IssueGenerate.ForeColor = $script:DisabledText
$script:IssueCopy = Add-Button $actionRow 'Copy key' 0 0 108
$script:IssueCopy.Enabled = $false
$syncExisting = Add-Button $actionRow 'Sync existing key' 0 0 148
$syncExisting.Add_Click({ Show-SyncExistingLicenseDialog })
[void]$issueLayout.Controls.Add($actionRow, 0, 3)

$outputHeading = Add-Label $issueLayout 'Issued license key' 0 1 360 20 $true
[void]$issueLayout.Controls.Add($outputHeading, 0, 4)
$keyContainer = New-Object System.Windows.Forms.Panel
$keyContainer.Dock = [System.Windows.Forms.DockStyle]::Fill
$keyContainer.Margin = New-Object System.Windows.Forms.Padding(0)
$keyContainer.BackColor = $script:SurfaceRaised
$keyContainer.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
$script:KeyOutput = New-Object System.Windows.Forms.TextBox
$script:KeyOutput.Multiline = $true
$script:KeyOutput.ScrollBars = [System.Windows.Forms.ScrollBars]::None
$script:KeyOutput.WordWrap = $true
$script:KeyOutput.ReadOnly = $true
$script:KeyOutput.Font = New-Object System.Drawing.Font('Consolas', 9)
$script:KeyOutput.Dock = [System.Windows.Forms.DockStyle]::Fill
$script:KeyOutput.Margin = New-Object System.Windows.Forms.Padding(0)
$script:KeyOutput.AccessibleName = 'Generated license key'
Set-Style $script:KeyOutput
$script:KeyOutput.BorderStyle = [System.Windows.Forms.BorderStyle]::None
[void]$keyContainer.Controls.Add($script:KeyOutput)
$script:KeyEmptyState = New-Object System.Windows.Forms.Label
$script:KeyEmptyState.Text = 'A signed license key will appear here after generation.'
$script:KeyEmptyState.Dock = [System.Windows.Forms.DockStyle]::Fill
$script:KeyEmptyState.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$script:KeyEmptyState.ForeColor = $script:MutedText
$script:KeyEmptyState.BackColor = $script:SurfaceRaised
$script:KeyEmptyState.Font = $script:BodyFont
$script:KeyEmptyState.AccessibleName = 'No license key generated'
[void]$keyContainer.Controls.Add($script:KeyEmptyState)
$script:KeyEmptyState.BringToFront()
[void]$issueLayout.Controls.Add($keyContainer, 0, 5)
$script:KeyStatus = Add-Label $issueLayout 'The key appears here after it has been signed and synced.' 0 0 800 42
$script:KeyStatus.ForeColor = $script:MutedText
$script:KeyStatus.Dock = [System.Windows.Forms.DockStyle]::Fill
$script:KeyStatus.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
[void]$issueLayout.Controls.Add($script:KeyStatus, 0, 6)

$script:DeviceInput.Add_TextChanged({ Clear-IssuedKey })
$script:KeyOutput.Add_TextChanged({ Update-IssueReadiness })
$licensedTo.Add_TextChanged({ Clear-IssuedKey })
$plan.Add_SelectedIndexChanged({ Clear-IssuedKey })
$days.Add_ValueChanged({ Clear-IssuedKey })
$rootBox.Add_TextChanged({
    $script:Root = $rootBox.Text.Trim()
    $toolTip.SetToolTip($rootBox, $script:Root)
    if ([string]::IsNullOrWhiteSpace($script:Root)) {
        $script:LicenseSource = $null
    }
    else {
        $script:LicenseSource = Join-Path $script:Root 'src\local_ai_benchmark\client\licensing.py'
    }
    Clear-IssuedKey
    Refresh-IssueAuthority
})
$browse.Add_Click({
    $folderPicker = New-Object System.Windows.Forms.FolderBrowserDialog
    $folderPicker.SelectedPath = $rootBox.Text
    $folderPicker.Description = 'Select the Aetherion client project folder.'
    if ($folderPicker.ShowDialog($script:MainForm) -eq [System.Windows.Forms.DialogResult]::OK) {
        $rootBox.Text = $folderPicker.SelectedPath
    }
    $folderPicker.Dispose()
})
$setup.Add_Click({
    $setup.Enabled = $false
    try {
        $script:KeyStatus.Text = Initialize-Authority
        $script:KeyStatus.ForeColor = $script:Mint
        Refresh-IssueAuthority
    }
    catch {
        $script:AuthorityError = $_.Exception.Message
        $script:KeyStatus.Text = $_.Exception.Message
        $script:KeyStatus.ForeColor = $script:ErrorColor
        Update-IssueReadiness
    }
    finally {
        $setup.Enabled = -not $script:AuthorityReady
    }
})
$settings.Add_Click({ Show-ServerSettingsDialog })
$settingsInline.Add_Click({ Show-ServerSettingsDialog })
$accounts.Add_Click({ Show-AccountManager })
$script:IssueGenerate.Add_Click({
    $deviceReady = $script:DeviceInput.Text.Trim() -match '^[A-Fa-f0-9]{32}$'
    $serviceReady = -not [string]::IsNullOrWhiteSpace($script:ManagerSettings.server_url) -and
        -not [string]::IsNullOrWhiteSpace($script:ManagerSettings.admin_token)
    if (-not $deviceReady) {
        $script:KeyStatus.Text = 'Enter the 32-character hexadecimal Device ID from Aetherion Client.'
        $script:KeyStatus.ForeColor = $script:WarningColor
        [void]$script:DeviceInput.Focus()
        return
    }
    if (-not $script:AuthorityReady) {
        $script:KeyStatus.Text = if ($script:AuthorityError) { $script:AuthorityError } else { 'Create the signing authority before issuing a key.' }
        $script:KeyStatus.ForeColor = if ($script:AuthorityError) { $script:ErrorColor } else { $script:WarningColor }
        [void]$setup.Focus()
        return
    }
    if (-not $serviceReady) {
        $script:KeyStatus.Text = if ($script:SettingsLoadError) { $script:SettingsLoadError } else { 'Open Service settings and connect with the administrator token.' }
        $script:KeyStatus.ForeColor = if ($script:SettingsLoadError) { $script:ErrorColor } else { $script:WarningColor }
        [void]$settings.Focus()
        return
    }
    $script:IssuanceBusy = $true
    Update-IssueReadiness
    $script:MainForm.UseWaitCursor = $true
    $script:KeyStatus.Text = 'Signing and syncing the license...'
    $script:KeyStatus.ForeColor = $script:MutedText
    $script:MainForm.Refresh()
    try {
        $selected = @('trial', 'duration', 'unlimited')[$plan.SelectedIndex]
        $generated = New-AetherionKey $script:DeviceInput.Text.Trim() $selected ([int]$days.Value) $licensedTo.Text
        $null = Invoke-LicenseService 'POST' '/v1/admin/licenses' @{ license_key = $generated }
        $script:KeyOutput.Text = $generated
        $script:KeyStatus.Text = 'License issued and synced. This key can be claimed once by its assigned device.'
        $script:KeyStatus.ForeColor = $script:Mint
    }
    catch {
        $script:KeyOutput.Clear()
        $script:KeyStatus.Text = $_.Exception.Message
        $script:KeyStatus.ForeColor = $script:ErrorColor
    }
    finally {
        $script:IssuanceBusy = $false
        $script:MainForm.UseWaitCursor = $false
        Update-IssueReadiness
    }
})
$script:IssueCopy.Add_Click({
    try {
        [Windows.Forms.Clipboard]::SetText($script:KeyOutput.Text)
        $script:KeyStatus.Text = 'License key copied to the clipboard.'
        $script:KeyStatus.ForeColor = $script:Mint
    }
    catch {
        $script:KeyStatus.Text = "Could not copy the key: $($_.Exception.Message)"
        $script:KeyStatus.ForeColor = $script:ErrorColor
    }
})
$script:MainForm.Add_Shown({
    $days.Enabled = $false
    $setup.Enabled = $true
    Refresh-IssueAuthority
    Update-IssueReadiness
    [void]$script:DeviceInput.Focus()
})
[void]$script:MainForm.ShowDialog()
$script:MainForm.Dispose()
