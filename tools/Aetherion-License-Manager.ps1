Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Security
[System.Windows.Forms.Application]::EnableVisualStyles()

$script:Root = 'C:\Users\Dayve\Desktop\Carpetas\Local_AI_Benchmark'
$script:LicenseSource = Join-Path $script:Root 'src\local_ai_benchmark\client\licensing.py'
$script:KeyPath = Join-Path $env:LOCALAPPDATA 'Aetherion\licensing\signing_key.dpapi'
$script:ManagerSettingsPath = Join-Path $env:LOCALAPPDATA 'Aetherion\licensing\manager-settings.dpapi'
$script:Mint = [System.Drawing.Color]::FromArgb(91, 226, 194)
$script:Surface = [System.Drawing.Color]::FromArgb(25, 34, 45)
$script:Canvas = [System.Drawing.Color]::FromArgb(13, 18, 26)
$script:TextColor = [System.Drawing.Color]::FromArgb(230, 237, 245)
$script:DefaultServiceUrl = 'https://aetherionlbs.duckdns.org'
$script:ManagerSettings = @{ server_url = $script:DefaultServiceUrl; admin_token = '' }

function Read-ManagerSettings {
    if (-not (Test-Path -LiteralPath $script:ManagerSettingsPath)) { return @{ server_url = $script:DefaultServiceUrl; admin_token = '' } }
    try {
        $protected = [IO.File]::ReadAllBytes($script:ManagerSettingsPath)
        $plain = [Security.Cryptography.ProtectedData]::Unprotect($protected, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
        $settings = [Text.Encoding]::UTF8.GetString($plain) | ConvertFrom-Json
        [Array]::Clear($plain, 0, $plain.Length)
        $savedUrl = [string]$settings.server_url
        if ([string]::IsNullOrWhiteSpace($savedUrl)) { $savedUrl = $script:DefaultServiceUrl }
        $savedToken = [string]$settings.admin_token
        if ($null -ne $savedToken) { $savedToken = $savedToken.Trim() }
        return @{ server_url = $savedUrl.Trim().TrimEnd('/'); admin_token = $savedToken }
    } catch { throw 'No se pudo descifrar la configuración del administrador. Verifica que la abras con la misma cuenta de Windows.' }
}
function Save-ManagerSettings([string]$ServerUrl, [string]$AdminToken) {
    if ([string]::IsNullOrWhiteSpace($ServerUrl)) { throw 'La URL del servicio no puede quedar vacía.' }
    $url = $ServerUrl.Trim().TrimEnd('/')
    $parsed = $null
    if (-not [Uri]::TryCreate($url, [UriKind]::Absolute, [ref]$parsed)) { throw 'La URL del servicio no es válida.' }
    $loopback = $parsed.Host -in @('localhost','127.0.0.1','::1')
    if ($parsed.Scheme -ne 'https' -and -not ($parsed.Scheme -eq 'http' -and $loopback)) { throw 'Usa HTTPS para el servidor; HTTP solo se permite en localhost.' }
    if ([string]::IsNullOrWhiteSpace($AdminToken)) { throw 'El token de administrador no puede quedar vacío.' }
    $token = $AdminToken.Trim()
    if ($token.Length -lt 32) { throw 'El token de administrador debe tener por lo menos 32 caracteres.' }
    $script:ManagerSettings = @{ server_url = $url; admin_token = $token }
    $plain = [Text.Encoding]::UTF8.GetBytes(($script:ManagerSettings | ConvertTo-Json -Compress))
    $protected = [Security.Cryptography.ProtectedData]::Protect($plain, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
    $directory = Split-Path -Parent $script:ManagerSettingsPath
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
    [IO.File]::WriteAllBytes($script:ManagerSettingsPath, $protected)
    [Array]::Clear($plain, 0, $plain.Length)
}
function Invoke-LicenseService([string]$Method, [string]$Path, $Body = $null) {
    if (-not $script:ManagerSettings.server_url -or -not $script:ManagerSettings.admin_token) { throw 'Abre Server settings y configura la URL y el token de administrador del VPS.' }
    $headers = @{ Authorization = "Bearer $($script:ManagerSettings.admin_token)"; Accept = 'application/json' }
    $params = @{ Uri = ($script:ManagerSettings.server_url.TrimEnd('/') + $Path); Method = $Method; Headers = $headers; TimeoutSec = 15 }
    if ($null -ne $Body) { $params.ContentType = 'application/json'; $params.Body = $Body | ConvertTo-Json -Compress -Depth 8 }
    try { return Invoke-RestMethod @params }
    catch {
        $detail = $_.ErrorDetails.Message
        if (-not $detail) { $detail = $_.Exception.Message }
        throw "License service: $detail"
    }
}
function Show-ServerSettingsDialog {
    $dialog = New-Object System.Windows.Forms.Form
    $dialog.Text = 'License Service Settings'; $dialog.StartPosition = 'CenterParent'; $dialog.Size = New-Object System.Drawing.Size(600, 290); $dialog.BackColor = $script:Canvas; $dialog.ForeColor = $script:TextColor
    Add-Label $dialog 'LICENSE SERVICE URL' 24 24 500 20 $true | Out-Null
    $urlBox = Add-TextBox $dialog 24 48 535 $script:ManagerSettings.server_url
    Add-Label $dialog 'ADMINISTRATOR TOKEN' 24 94 500 20 $true | Out-Null
    $tokenBox = Add-TextBox $dialog 24 118 535 $script:ManagerSettings.admin_token; $tokenBox.UseSystemPasswordChar = $true
    $status = Add-Label $dialog 'Use the same URL configured for Aetherion clients. The token is encrypted for this Windows account.' 24 157 535 45
    $save = Add-Button $dialog 'Save and connect' 24 215 160
    $save.Add_Click({
        try {
            Save-ManagerSettings $urlBox.Text $tokenBox.Text
            $null = Invoke-LicenseService 'GET' '/v1/admin/users'
            $status.Text = 'Connected; administrator token verified.'; $status.ForeColor = $script:Mint; Update-IssueReadiness
        } catch { $status.Text = $_.Exception.Message; $status.ForeColor = [Drawing.Color]::Salmon }
    })
    [void]$dialog.ShowDialog($form)
}
function Show-SyncExistingLicenseDialog {
    $dialog = New-Object System.Windows.Forms.Form
    $dialog.Text = 'Register Existing License'; $dialog.StartPosition = 'CenterParent'; $dialog.Size = New-Object System.Drawing.Size(650, 360); $dialog.BackColor = $script:Canvas; $dialog.ForeColor = $script:TextColor
    Add-Label $dialog 'SYNC A PREVIOUSLY ISSUED LICENSE' 22 18 570 26 $true | Out-Null
    Add-Label $dialog 'Paste the complete AETH1 key. It will be verified and registered; the private signing key is not sent.' 22 52 590 42 | Out-Null
    $licenseBox = New-Object System.Windows.Forms.TextBox; $licenseBox.Location = New-Object Drawing.Point(22, 102); $licenseBox.Size = New-Object Drawing.Size(590, 125); $licenseBox.Multiline = $true; $licenseBox.ScrollBars = 'Vertical'; $licenseBox.Font = New-Object System.Drawing.Font('Consolas', 9); Set-Style $licenseBox; $dialog.Controls.Add($licenseBox)
    $status = Add-Label $dialog 'The key remains device-bound and can only be claimed once.' 22 238 590 38
    $sync = Add-Button $dialog 'Verify and sync license' 22 286 190
    $sync.Add_Click({
        try {
            $value = $licenseBox.Text.Trim()
            if (-not $value) { throw 'Paste the complete license key first.' }
            $result = Invoke-LicenseService 'POST' '/v1/admin/licenses' @{ license_key = $value }
            $state = if ($result.claimed) { 'This license is already claimed by an account.' } else { 'License verified and ready for account registration.' }
            $status.Text = "$state License ID: $($result.license_id)"; $status.ForeColor = $script:Mint
        } catch { $status.Text = $_.Exception.Message; $status.ForeColor = [Drawing.Color]::Salmon }
    })
    [void]$dialog.ShowDialog($form)
}
function Show-AccountManager {
    $dialog = New-Object System.Windows.Forms.Form
    $dialog.Text = 'Aetherion Accounts'; $dialog.StartPosition = 'CenterParent'; $dialog.Size = New-Object System.Drawing.Size(1180, 760); $dialog.MinimumSize = New-Object System.Drawing.Size(1060, 680); $dialog.BackColor = $script:Canvas; $dialog.ForeColor = $script:TextColor
    $heading = Add-Label $dialog 'Customer accounts' 24 18 570 34 $true
    $heading.Font = New-Object System.Drawing.Font('Segoe UI Semibold', 16)
    $subtitle = Add-Label $dialog 'Review access, adjust plans, and manage renewals.' 26 51 650 22
    $subtitle.ForeColor = [Drawing.Color]::FromArgb(172, 189, 207)
    $reload = Add-Button $dialog 'Refresh list' 1030 22 120
    $reload.Anchor = 'Top,Right'
    Add-Label $dialog 'SEARCH' 24 82 80 18 $true | Out-Null
    $search = Add-TextBox $dialog 24 103 390 ''
    Add-Label $dialog 'Filter by username or Device ID' 428 107 300 22 | Out-Null
    $summary = Add-Label $dialog 'Loading accounts...' 735 106 415 22
    $summary.Anchor = 'Top,Right'
    $summary.TextAlign = 'MiddleRight'
    $grid = New-Object System.Windows.Forms.DataGridView
    $grid.Location = New-Object Drawing.Point(24, 140); $grid.Size = New-Object Drawing.Size(1126, 322); $grid.Anchor = 'Top,Bottom,Left,Right'
    $grid.ReadOnly = $true; $grid.AllowUserToAddRows = $false; $grid.AllowUserToDeleteRows = $false; $grid.MultiSelect = $false; $grid.SelectionMode = 'FullRowSelect'; $grid.AutoSizeColumnsMode = 'Fill'; $grid.BackgroundColor = $script:Surface; $grid.GridColor = [Drawing.Color]::FromArgb(54,72,91); $grid.BorderStyle = 'None'; $grid.RowHeadersVisible = $false
    $grid.EnableHeadersVisualStyles = $false; $grid.ColumnHeadersDefaultCellStyle.BackColor = $script:Surface; $grid.ColumnHeadersDefaultCellStyle.ForeColor = $script:Mint; $grid.DefaultCellStyle.BackColor = $script:Canvas; $grid.DefaultCellStyle.ForeColor = $script:TextColor; $grid.DefaultCellStyle.SelectionBackColor = [Drawing.Color]::FromArgb(42,61,77); $grid.DefaultCellStyle.SelectionForeColor = $script:TextColor
    $grid.ColumnHeadersHeight = 34
    $grid.RowTemplate.Height = 30
    foreach($col in @(@('id','ID'),@('username','USERNAME'),@('active','STATUS'),@('plan','PLAN'),@('plan_key','PLAN KEY'),@('expires_at','EXPIRES'),@('days_remaining','DAYS LEFT'),@('machine_id','DEVICE ID'),@('last_login_at','LAST SIGN-IN'))){
        $column = New-Object System.Windows.Forms.DataGridViewTextBoxColumn; $column.Name=$col[0]; $column.HeaderText=$col[1]; $column.SortMode='NotSortable'; [void]$grid.Columns.Add($column)
    }
    $grid.Columns['id'].Visible = $false
    $grid.Columns['plan_key'].Visible = $false
    $grid.Columns['username'].FillWeight = 140
    $grid.Columns['active'].FillWeight = 85
    $grid.Columns['plan'].FillWeight = 100
    $grid.Columns['expires_at'].FillWeight = 105
    $grid.Columns['days_remaining'].FillWeight = 75
    $grid.Columns['machine_id'].FillWeight = 190
    $grid.Columns['last_login_at'].FillWeight = 140
    $dialog.Controls.Add($grid)
    $emptyState = Add-Label $dialog 'No accounts yet. Sync a license before the first client registers.' 80 267 1014 48
    $emptyState.TextAlign = 'MiddleCenter'
    $emptyState.ForeColor = [Drawing.Color]::FromArgb(172, 189, 207)
    $emptyState.BackColor = $script:Surface
    $emptyState.Visible = $false
    $selectionPanel = New-Object System.Windows.Forms.Panel
    $selectionPanel.Location = New-Object Drawing.Point(24, 478); $selectionPanel.Size = New-Object Drawing.Size(1126, 54); $selectionPanel.Anchor = 'Bottom,Left,Right'; $selectionPanel.BackColor = $script:Surface
    $dialog.Controls.Add($selectionPanel)
    $selectionTitle = Add-Label $selectionPanel 'SELECT AN ACCOUNT' 14 6 230 18 $true
    $selectionDetail = Add-Label $selectionPanel 'Choose a row above to see account details and enable actions.' 14 25 1080 22
    $selectionDetail.ForeColor = [Drawing.Color]::FromArgb(172, 189, 207)

    $planHeading = Add-Label $dialog 'CHANGE PLAN' 24 546 210 19 $true
    $planHeading.Anchor = 'Bottom,Left'
    $newPlan = New-Object System.Windows.Forms.ComboBox
    $newPlan.Location = New-Object Drawing.Point(24, 569); $newPlan.Size = New-Object Drawing.Size(220, 30); $newPlan.DropDownStyle = 'DropDownList'; Set-Style $newPlan
    $newPlan.Anchor = 'Bottom,Left'
    [void]$newPlan.Items.Add('Trial · 7 days')
    [void]$newPlan.Items.Add('Custom duration')
    [void]$newPlan.Items.Add('Unlimited')
    $newPlan.SelectedIndex = 1
    $dialog.Controls.Add($newPlan)
    $planDaysHeading = Add-Label $dialog 'DAYS' 262 546 90 19 $true
    $planDaysHeading.Anchor = 'Bottom,Left'
    $planDays = New-Object System.Windows.Forms.NumericUpDown
    $planDays.Location = New-Object Drawing.Point(262, 569); $planDays.Size = New-Object Drawing.Size(100, 30); $planDays.Minimum = 1; $planDays.Maximum = 3650; $planDays.Value = 30; Set-Style $planDays
    $planDays.Anchor = 'Bottom,Left'
    $dialog.Controls.Add($planDays)
    $planHint = Add-Label $dialog 'The new term starts today. Changing the plan does not lift a suspension.' 380 573 490 25
    $planHint.ForeColor = [Drawing.Color]::FromArgb(172, 189, 207)
    $planHint.Anchor = 'Bottom,Left'
    $applyPlan = Add-Button $dialog 'Apply plan' 960 567 190
    $applyPlan.Anchor = 'Bottom,Right'
    $applyPlan.Enabled = $false
    $applyPlan.BackColor = $script:Surface
    $applyPlan.ForeColor = [Drawing.Color]::FromArgb(145, 160, 176)

    $line = New-Object System.Windows.Forms.Label
    $line.BackColor = [Drawing.Color]::FromArgb(54,72,91); $line.Location = New-Object Drawing.Point(24, 615); $line.Size = New-Object Drawing.Size(1126, 1); $line.Anchor = 'Bottom,Left,Right'
    $dialog.Controls.Add($line)
    $renewalHeading = Add-Label $dialog 'RENEWAL' 24 627 120 18 $true
    $renewalHeading.Anchor = 'Bottom,Left'
    $renewalDaysHeading = Add-Label $dialog 'ADD DAYS' 24 649 90 18
    $renewalDaysHeading.Anchor = 'Bottom,Left'
    $amount = New-Object System.Windows.Forms.NumericUpDown
    $amount.Location=New-Object Drawing.Point(24, 670); $amount.Size=New-Object Drawing.Size(100, 30); $amount.Minimum=1; $amount.Maximum=3650; $amount.Value=30; $amount.Anchor='Bottom,Left'; Set-Style $amount; $dialog.Controls.Add($amount)
    $renew = Add-Button $dialog 'Extend & reactivate' 142 668 180
    $renew.Anchor = 'Bottom,Left'
    $renew.Enabled = $false
    $toggle = Add-Button $dialog 'Disable account' 338 668 155
    $toggle.Anchor = 'Bottom,Left'
    $toggle.Enabled = $false
    $status = Add-Label $dialog 'Select an account to manage its plan or access.' 520 672 630 28
    $status.Anchor = 'Bottom,Left,Right'
    $currentUsers = @()
    $newPlan.Add_SelectedIndexChanged({
        $planDays.Enabled = ($newPlan.SelectedIndex -eq 1)
        switch ($newPlan.SelectedIndex) {
            0 { $planHint.Text = 'Replace the current term with 7 days starting today.' }
            1 { $planHint.Text = 'Replace the current term with the selected number of days from today.' }
            2 { $planHint.Text = 'Remove the expiration date. The account suspension state is unchanged.' }
        }
    })
    $search.Add_TextChanged({
        $needle = $search.Text.Trim()
        $visibleCount = 0
        foreach ($row in $grid.Rows) {
            $matchesSearch = -not $needle -or
                ([string]$row.Cells['username'].Value).IndexOf($needle, [StringComparison]::OrdinalIgnoreCase) -ge 0 -or
                ([string]$row.Cells['machine_id'].Value).IndexOf($needle, [StringComparison]::OrdinalIgnoreCase) -ge 0
            $row.Visible = $matchesSearch
            if ($matchesSearch) { $visibleCount++ }
        }
        $emptyState.Visible = ($visibleCount -eq 0)
        if ($emptyState.Visible -and $grid.Rows.Count -gt 0) { $emptyState.Text = 'No accounts match that username or Device ID.' }
        elseif ($grid.Rows.Count -eq 0) { $emptyState.Text = 'No accounts yet. Sync a license before the first client registers.' }
    })
    $grid.Add_SelectionChanged({
        if ($grid.SelectedRows.Count -eq 0) {
            $selectionTitle.Text = 'SELECT AN ACCOUNT'
            $selectionDetail.Text = 'Choose a row above to see account details and enable actions.'
            $applyPlan.Enabled = $false; $renew.Enabled = $false; $toggle.Enabled = $false
            $applyPlan.BackColor = $script:Surface
            $applyPlan.ForeColor = [Drawing.Color]::FromArgb(145, 160, 176)
            return
        }
        $row = $grid.SelectedRows[0]
        $username = [string]$row.Cells['username'].Value
        $statusValue = [string]$row.Cells['active'].Value
        $planValue = [string]$row.Cells['plan_key'].Value
        $planName = [string]$row.Cells['plan'].Value
        $expiryValue = [string]$row.Cells['expires_at'].Value
        $selectionTitle.Text = "SELECTED  /  $username"
        $selectionDetail.Text = "$statusValue  ·  Current plan: $planName  ·  Expires: $expiryValue"
        switch ($planValue) {
            'trial' { $newPlan.SelectedIndex = 0 }
            'duration' { $newPlan.SelectedIndex = 1 }
            'unlimited' { $newPlan.SelectedIndex = 2 }
        }
        $applyPlan.Enabled = $true
        $applyPlan.BackColor = $script:Mint
        $applyPlan.ForeColor = $script:Canvas
        $renew.Enabled = ($planValue -ne 'unlimited')
        $toggle.Text = if ($statusValue -eq 'ACTIVE') { 'Disable account' } else { 'Enable account' }
        $toggle.Enabled = $true
    })
    $refreshGrid = {
        try {
            $result = Invoke-LicenseService 'GET' '/v1/admin/users'
            $currentUsers = @($result.users)
            $grid.Rows.Clear()
            foreach($user in $currentUsers){
                $active = if($user.active -and $user.license_enabled){'ACTIVE'}else{'DISABLED'}
                $planName = switch ($user.plan) { 'trial' { 'Trial' } 'duration' { 'Custom duration' } 'unlimited' { 'Unlimited' } default { [string]$user.plan } }
                $expiry = if($user.expires_at){([DateTime]::Parse($user.expires_at)).ToLocalTime().ToString('yyyy-MM-dd')}else{'Unlimited'}
                $daysLeft = if($null -eq $user.days_remaining){'∞'}else{[string]$user.days_remaining}
                $last = if($user.last_login_at){([DateTime]::Parse($user.last_login_at)).ToLocalTime().ToString('yyyy-MM-dd HH:mm')}else{'Never'}
                [void]$grid.Rows.Add([string]$user.id,$user.username,$active,$planName,$user.plan,$expiry,$daysLeft,$user.machine_id,$last)
            }
            $grid.ClearSelection()
            $grid.CurrentCell = $null
            $total = $currentUsers.Count
            $activeCount = @($currentUsers | Where-Object { $_.active -and $_.license_enabled }).Count
            $summary.Text = "$total accounts   ·   $activeCount active   ·   $($total - $activeCount) disabled"
            $emptyState.Visible = ($total -eq 0)
            $emptyState.Text = 'No accounts yet. Sync a license before the first client registers.'
            $status.Text = 'Select an account to manage its plan or access.'; $status.ForeColor = $script:TextColor
        } catch { $status.Text=$_.Exception.Message; $status.ForeColor=[Drawing.Color]::Salmon }
    }
    $reload.Add_Click($refreshGrid)
    $applyPlan.Add_Click({
        if ($grid.SelectedRows.Count -eq 0) { $status.Text = 'Select an account first.'; return }
        $selected = @('trial','duration','unlimited')[$newPlan.SelectedIndex]
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
        } catch { $status.Text=$_.Exception.Message; $status.ForeColor=[Drawing.Color]::Salmon }
    })
    $renew.Add_Click({
        if($grid.SelectedRows.Count -eq 0){$status.Text='Select an account first.';return}
        try{$id=[int]$grid.SelectedRows[0].Cells['id'].Value;$result=Invoke-LicenseService 'POST' "/v1/admin/users/$id/renew" @{days=[int]$amount.Value};& $refreshGrid;$status.Text="Added $($result.days_added) day(s) to $($result.username). Expires $($result.expires_at).";$status.ForeColor=$script:Mint}catch{$status.Text=$_.Exception.Message;$status.ForeColor=[Drawing.Color]::Salmon}
    })
    $toggle.Add_Click({
        if($grid.SelectedRows.Count -eq 0){$status.Text='Select an account first.';return}
        try{$row=$grid.SelectedRows[0];$id=[int]$row.Cells['id'].Value;$path=if($row.Cells['active'].Value -eq 'ACTIVE'){"/v1/admin/users/$id/disable"}else{"/v1/admin/users/$id/enable"};$null=Invoke-LicenseService 'POST' $path @{};& $refreshGrid;$status.Text=if($path -like '*/disable'){'Account disabled; active sessions revoked.'}else{'Account enabled.'};$status.ForeColor=$script:Mint}catch{$status.Text=$_.Exception.Message;$status.ForeColor=[Drawing.Color]::Salmon}
    })
    $dialog.Add_Shown($refreshGrid)
    [void]$dialog.ShowDialog($form)
}
try {
    $script:ManagerSettings = Read-ManagerSettings
    $script:SettingsLoadError = $null
} catch {
    $script:SettingsLoadError = $_.Exception.Message
}

function Set-Style($control, [bool]$isButton = $false) {
    $control.BackColor = $script:Surface
    $control.ForeColor = $script:TextColor
    $control.Font = New-Object System.Drawing.Font('Segoe UI', 9)
    if ($isButton) { $control.FlatStyle = 'Flat'; $control.FlatAppearance.BorderColor = [System.Drawing.Color]::FromArgb(54, 72, 91); $control.Height = 34 }
}
function Add-Label($parent, [string]$text, [int]$x, [int]$y, [int]$width = 600, [int]$height = 22, [bool]$accent = $false) {
    $label = New-Object System.Windows.Forms.Label
    $label.Text = $text; $label.Location = New-Object System.Drawing.Point($x, $y)
    $label.Size = New-Object System.Drawing.Size($width, $height)
    $label.ForeColor = if ($accent) { $script:Mint } else { $script:TextColor }
    $label.Font = New-Object System.Drawing.Font('Segoe UI', $(if ($accent) { 9 } else { 9 }), $(if ($accent) { [System.Drawing.FontStyle]::Bold } else { [System.Drawing.FontStyle]::Regular }))
    $parent.Controls.Add($label); return $label
}
function Add-TextBox($parent, [int]$x, [int]$y, [int]$width, [string]$value = '') {
    $box = New-Object System.Windows.Forms.TextBox
    $box.Location = New-Object System.Drawing.Point($x, $y); $box.Size = New-Object System.Drawing.Size($width, 28)
    $box.Text = $value; Set-Style $box; $parent.Controls.Add($box); return $box
}
function Add-Button($parent, [string]$text, [int]$x, [int]$y, [int]$width = 140) {
    $button = New-Object System.Windows.Forms.Button
    $button.Text = $text; $button.Location = New-Object System.Drawing.Point($x, $y); $button.Size = New-Object System.Drawing.Size($width, 34)
    Set-Style $button $true; $parent.Controls.Add($button); return $button
}
function Get-SourcePublicKey {
    if (-not (Test-Path -LiteralPath $script:LicenseSource)) { throw "No se encuentra licensing.py: $script:LicenseSource" }
    $source = [IO.File]::ReadAllText($script:LicenseSource)
    $match = [regex]::Match($source, '(?m)^PUBLIC_KEY_N = "([0-9a-fA-F]*)"$')
    if (-not $match.Success) { throw 'No encuentro la constante PUBLIC_KEY_N en licensing.py.' }
    return @{ Source = $source; Match = $match }
}
function Initialize-Authority {
    $sourceInfo = Get-SourcePublicKey
    if ($sourceInfo.Match.Groups[1].Value) { throw 'La autoridad ya se configuró en este cliente. No se puede reemplazar aquí porque invalidaría las licencias existentes.' }
    if (Test-Path -LiteralPath $script:KeyPath) { throw 'Ya existe una clave privada del generador, pero el cliente no muestra una clave pública. Comprueba el origen del proyecto antes de continuar.' }
    $directory = Split-Path -Parent $script:KeyPath
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
    $rsa = [System.Security.Cryptography.RSACng]::new(2048)
    try {
        $parameters = $rsa.ExportParameters($true)
        $xml = $rsa.ToXmlString($true)
        $plain = [Text.Encoding]::UTF8.GetBytes($xml)
        $protected = [Security.Cryptography.ProtectedData]::Protect($plain, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
        [IO.File]::WriteAllBytes($script:KeyPath, $protected)
        $modulus = ([BitConverter]::ToString($parameters.Modulus)).Replace('-', '').TrimStart('0').ToLowerInvariant()
        if (-not $modulus) { throw 'No se pudo leer el módulo de la clave pública.' }
        $publicLine = [regex]::new('(?m)^PUBLIC_KEY_N = ""$')
        $updated = $publicLine.Replace($sourceInfo.Source, "PUBLIC_KEY_N = `"$modulus`"", 1)
        if ($updated -eq $sourceInfo.Source) { throw 'No se pudo configurar la clave pública en el proyecto.' }
        [IO.File]::WriteAllText($script:LicenseSource, $updated, (New-Object Text.UTF8Encoding($false)))
        return 'Autoridad creada. La clave privada quedó protegida para este usuario de Windows. Ahora hay que reconstruir el cliente Aetherion para incluir la clave pública.'
    } finally { $rsa.Dispose() }
}
function Get-PrivateRsa {
    if (-not (Test-Path -LiteralPath $script:KeyPath)) { throw 'Primero usa «Crear autoridad». Esta acción se realiza una sola vez.' }
    $protected = [IO.File]::ReadAllBytes($script:KeyPath)
    $plain = [Security.Cryptography.ProtectedData]::Unprotect($protected, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
    $rsa = [System.Security.Cryptography.RSACng]::new()
    $rsa.FromXmlString([Text.Encoding]::UTF8.GetString($plain))
    [Array]::Clear($plain, 0, $plain.Length)
    $sourceInfo = Get-SourcePublicKey
    $modulus = ([BitConverter]::ToString($rsa.ExportParameters($false).Modulus)).Replace('-', '').TrimStart('0').ToLowerInvariant()
    if ($sourceInfo.Match.Groups[1].Value.ToLowerInvariant() -ne $modulus) { $rsa.Dispose(); throw 'La clave privada no corresponde a la clave pública del código fuente seleccionado.' }
    return $rsa
}
function ConvertTo-Base64Url([byte[]]$Bytes) { return [Convert]::ToBase64String($Bytes).TrimEnd('=').Replace('+','-').Replace('/','_') }
function New-AetherionKey([string]$MachineId, [string]$Plan, [int]$Days, [string]$LicensedTo) {
    if ($MachineId -notmatch '^[A-Fa-f0-9]{32}$') { throw 'El ID de equipo debe tener 32 caracteres hexadecimales. Cópialo desde la pantalla de activación.' }
    if ($Plan -eq 'duration' -and ($Days -lt 1 -or $Days -gt 3650)) { throw 'La duración personalizada debe estar entre 1 y 3650 días.' }
    $now = [DateTime]::UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", [Globalization.CultureInfo]::InvariantCulture)
    $expires = if ($Plan -eq 'unlimited') { $null } else { [DateTime]::UtcNow.AddDays($(if ($Plan -eq 'trial') { 7 } else { $Days })).ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", [Globalization.CultureInfo]::InvariantCulture) }
    $payload = [ordered]@{ version = 1; license_id = [guid]::NewGuid().ToString('N'); plan = $Plan; licensed_to = $LicensedTo.Trim(); machine_id = $MachineId.ToUpperInvariant(); issued_at = $now; expires_at = $expires }
    $json = $payload | ConvertTo-Json -Compress -Depth 5
    $payloadBytes = (New-Object Text.UTF8Encoding($false)).GetBytes($json)
    $rsa = Get-PrivateRsa
    try { $signature = $rsa.SignData($payloadBytes, [Security.Cryptography.HashAlgorithmName]::SHA256, [Security.Cryptography.RSASignaturePadding]::Pss) }
    finally { $rsa.Dispose() }
    return 'AETH1.' + (ConvertTo-Base64Url $payloadBytes) + '.' + (ConvertTo-Base64Url $signature)
}

$script:AuthorityReady = $false
function Update-IssueReadiness {
    $deviceReady = $script:IssueDevice.Text.Trim() -match '^[A-Fa-f0-9]{32}$'
    $serviceReady = -not [string]::IsNullOrWhiteSpace($script:ManagerSettings.server_url) -and
        -not [string]::IsNullOrWhiteSpace($script:ManagerSettings.admin_token)
    $authorityText = if ($script:AuthorityReady) { 'Signing authority: ready' } else { 'Signing authority: create or verify' }
    $serviceText = if ($serviceReady) { 'Service: configured' } else { 'Service: configure settings' }
    $deviceText = if ($deviceReady) { 'Device ID: valid' } else { 'Device ID: 32 hex characters required' }
    $script:IssueReadiness.Text = "$authorityText  |  $serviceText  |  $deviceText"
    $script:IssueReadiness.ForeColor = if ($script:AuthorityReady -and $serviceReady -and $deviceReady) {
        $script:Mint
    } else {
        [System.Drawing.Color]::FromArgb(242, 190, 105)
    }
    $issuanceReady = $script:AuthorityReady -and $serviceReady -and $deviceReady
    $script:IssueGenerate.Enabled = $issuanceReady
    if ($issuanceReady) {
        $script:IssueGenerate.BackColor = $script:Mint
        $script:IssueGenerate.ForeColor = $script:Canvas
    } else {
        $script:IssueGenerate.BackColor = [System.Drawing.Color]::FromArgb(43, 55, 68)
        $script:IssueGenerate.ForeColor = [System.Drawing.Color]::FromArgb(145, 160, 176)
    }
    $hasKey = -not [string]::IsNullOrWhiteSpace($script:IssueOutput.Text)
    $script:IssueCopy.Enabled = $hasKey
    $script:IssueCopy.ForeColor = if ($hasKey) { $script:TextColor } else { [System.Drawing.Color]::FromArgb(145, 160, 176) }
}
function Refresh-IssueAuthority {
    $script:AuthorityReady = $false
    if (Test-Path -LiteralPath $script:KeyPath) {
        try {
            $rsa = Get-PrivateRsa
            $rsa.Dispose()
            $script:AuthorityReady = $true
        } catch {
            $script:AuthorityReady = $false
        }
    }
    Update-IssueReadiness
}
function Clear-IssuedKey {
    if (-not [string]::IsNullOrWhiteSpace($script:IssueOutput.Text)) {
        $script:IssueOutput.Clear()
        $script:IssueMessage.Text = 'Issuance details changed. Generate a new key before copying.'
        $script:IssueMessage.ForeColor = $script:TextColor
    }
    Update-IssueReadiness
}
. (Join-Path $PSScriptRoot 'Aetherion-License-Manager.UI.ps1')
