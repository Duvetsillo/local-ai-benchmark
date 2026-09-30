Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Security
[System.Windows.Forms.Application]::EnableVisualStyles()

$script:Root = 'C:\Users\Dayve\Desktop\Carpetas\Local_AI_Benchmark'
$script:LicenseSource = Join-Path $script:Root 'src\local_ai_benchmark\client\licensing.py'
$script:KeyPath = Join-Path $env:LOCALAPPDATA 'Aetherion\licensing\signing_key.dpapi'
$script:Mint = [System.Drawing.Color]::FromArgb(91, 226, 194)
$script:Surface = [System.Drawing.Color]::FromArgb(25, 34, 45)
$script:Canvas = [System.Drawing.Color]::FromArgb(13, 18, 26)
$script:TextColor = [System.Drawing.Color]::FromArgb(230, 237, 245)

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

$form = New-Object System.Windows.Forms.Form
$form.Text = 'Aetherion License Manager'; $form.StartPosition = 'CenterScreen'; $form.Size = New-Object System.Drawing.Size(760, 720)
$form.MinimumSize = New-Object System.Drawing.Size(760, 720); $form.BackColor = $script:Canvas; $form.ForeColor = $script:TextColor
$form.Font = New-Object System.Drawing.Font('Segoe UI', 9)
Add-Label $form 'AETHERION' 28 22 300 36 $true | Out-Null
$title = Add-Label $form 'LICENSE MANAGER  /  OFFLINE SIGNING AUTHORITY' 28 56 650 24 $false
$title.ForeColor = [System.Drawing.Color]::FromArgb(153, 176, 198)
$rootBox = Add-TextBox $form 28 105 585 $script:Root
$rootBox.Add_TextChanged({ $script:Root = $rootBox.Text; $script:LicenseSource = Join-Path $script:Root 'src\local_ai_benchmark\client\licensing.py' })
$browse = Add-Button $form 'Browse project' 625 103 105
$browse.Add_Click({ $dialog = New-Object System.Windows.Forms.FolderBrowserDialog; $dialog.SelectedPath = $rootBox.Text; if ($dialog.ShowDialog() -eq 'OK') { $rootBox.Text = $dialog.SelectedPath; $script:Root = $rootBox.Text; $script:LicenseSource = Join-Path $script:Root 'src\local_ai_benchmark\client\licensing.py' } })
$setup = Add-Button $form 'Create authority' 28 148 145
$setup.Add_Click({ try { $message.Text = Initialize-Authority; $message.ForeColor = $script:Mint } catch { $message.Text = $_.Exception.Message; $message.ForeColor = [Drawing.Color]::Salmon } })
$message = Add-Label $form 'Private signing key is protected by Windows for this account.' 187 151 535 38
$line = New-Object System.Windows.Forms.Label; $line.BackColor = [System.Drawing.Color]::FromArgb(54,72,91); $line.Location = New-Object Drawing.Point(28,200); $line.Size = New-Object Drawing.Size(700,1); $form.Controls.Add($line)
Add-Label $form 'ISSUE A DEVICE-BOUND LICENSE' 28 220 500 24 $true | Out-Null
Add-Label $form 'DEVICE ID' 28 258 200 20 | Out-Null
$device = Add-TextBox $form 28 281 700 ''
Add-Label $form 'LICENSED TO (OPTIONAL)' 28 324 250 20 | Out-Null
$licensedTo = Add-TextBox $form 28 347 700 ''
Add-Label $form 'PLAN' 28 390 100 20 | Out-Null
$plan = New-Object System.Windows.Forms.ComboBox; $plan.Location = New-Object Drawing.Point(28,413); $plan.Size = New-Object Drawing.Size(235,28); $plan.DropDownStyle = 'DropDownList'; Set-Style $plan
[void]$plan.Items.Add('Trial · 7 days'); [void]$plan.Items.Add('Custom duration'); [void]$plan.Items.Add('Unlimited'); $plan.SelectedIndex = 0; $form.Controls.Add($plan)
Add-Label $form 'DAYS' 287 390 100 20 | Out-Null
$days = New-Object System.Windows.Forms.NumericUpDown; $days.Location = New-Object Drawing.Point(287,413); $days.Size = New-Object Drawing.Size(120,28); $days.Minimum = 1; $days.Maximum = 3650; $days.Value = 3; Set-Style $days; $form.Controls.Add($days)
$plan.Add_SelectedIndexChanged({ $days.Enabled = ($plan.SelectedIndex -eq 1) })
$generate = Add-Button $form 'Generate license key' 28 462 190
$copy = Add-Button $form 'Copy key' 228 462 120
$key = New-Object System.Windows.Forms.TextBox; $key.Location = New-Object Drawing.Point(28,508); $key.Size = New-Object Drawing.Size(700,100); $key.Multiline = $true; $key.ScrollBars = 'Vertical'; $key.ReadOnly = $true; $key.Font = New-Object System.Drawing.Font('Consolas', 9); Set-Style $key; $form.Controls.Add($key)
$generate.Add_Click({ try { $selected = @('trial','duration','unlimited')[$plan.SelectedIndex]; $key.Text = New-AetherionKey $device.Text $selected ([int]$days.Value) $licensedTo.Text; $message.Text = 'Licencia firmada para un solo equipo. Copia la clave y entrégala al usuario.'; $message.ForeColor = $script:Mint } catch { $message.Text = $_.Exception.Message; $message.ForeColor = [Drawing.Color]::Salmon } })
$copy.Add_Click({ if ($key.Text) { [Windows.Forms.Clipboard]::SetText($key.Text); $message.Text = 'Clave copiada al portapapeles.'; $message.ForeColor = $script:Mint } })
$foot = Add-Label $form 'La clave privada nunca se incluye en el cliente Aetherion. Trial: 7 días. El modo ilimitado no tiene caducidad.' 28 625 700 38
$form.Add_Shown({ $days.Enabled = $false })
[void]$form.ShowDialog()
