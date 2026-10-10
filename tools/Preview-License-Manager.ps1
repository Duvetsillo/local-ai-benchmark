param([string]$OutputDirectory = (Join-Path $PSScriptRoot '..\docs\license-manager\captures'))
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Security
[Windows.Forms.Application]::EnableVisualStyles()
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$script:Root = 'Aetherion project'
$script:LicenseSource = 'preview-only-no-source'
$script:KeyPath = 'preview-only-no-key'
$script:ManagerSettings = @{ server_url = ''; admin_token = '' }
$script:DefaultServiceUrl = ''
$script:Canvas = [Drawing.Color]::Black
$script:Surface = [Drawing.Color]::Black
$script:TextColor = [Drawing.Color]::White
$script:Mint = [Drawing.Color]::LightGreen
$tokens = $null; $parseErrors = $null
$ast = [Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot 'Aetherion-License-Manager.ps1'), [ref]$tokens, [ref]$parseErrors)
if ($parseErrors) { throw 'Main script parse failed.' }
foreach ($node in $ast.EndBlock.Statements) {
    if ($node -is [Management.Automation.Language.FunctionDefinitionAst]) { Invoke-Expression $node.Extent.Text }
}
function Invoke-LicenseService {
    param($Method, $Path, $Body)
    if ($Method -ne 'GET' -or $Path -ne '/v1/admin/users') { throw 'Preview forbids account mutations and network access.' }
    $now = [DateTime]::UtcNow
    $users = @()
    foreach ($spec in @(@('demo-studio', 'unlimited', $true, $true), @('demo-research', 'duration', $false, $true), @('demo-trial', 'trial', $false, $true), @('demo-paused', 'duration', $false, $false))) {
        $users += [pscustomobject]@{ id = $users.Count + 1; username = $spec[0]; plan = $spec[1]; online = $spec[2]; active = $spec[3]; license_enabled = $spec[3]; expires_at = $(if ($spec[1] -eq 'unlimited') { $null } else { $now.AddDays($(if ($spec[1] -eq 'trial') { 7 } else { 30 })).ToString('o') }); days_remaining = $(if ($spec[1] -eq 'unlimited') { $null } else { $(if ($spec[1] -eq 'trial') { 7 } else { 30 }) }); machine_id = ''; password_change_required = $false; last_seen_at = $now.AddMinutes($(if ($spec[2]) { -1 } else { -25 })).ToString('o') }
    }
    return [pscustomobject]@{ users = $users; presence_window_seconds = 360 }
}
function Save-Preview($Window, $Name) {
    $Window.PerformLayout()
    [Windows.Forms.Application]::DoEvents()
    $bitmap = New-Object Drawing.Bitmap($Window.Width, $Window.Height)
    try {
        $Window.DrawToBitmap($bitmap, (New-Object Drawing.Rectangle(0, 0, $bitmap.Width, $bitmap.Height)))
        $bitmap.Save((Join-Path $OutputDirectory "$Name.png"), [Drawing.Imaging.ImageFormat]::Png)
    } finally { $bitmap.Dispose() }
}
$ui = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Aetherion-License-Manager.UI.ps1') -Raw
$ui = $ui.Replace('$PSScriptRoot', "'$PSScriptRoot'")
# Build the real UI without opening a window or touching the owner's settings.
$ui = $ui.Replace('[void]$script:MainForm.ShowDialog()', '').Replace('$script:MainForm.Dispose()', '')
$ui = $ui.Replace('[void]$dialog.ShowDialog($script:MainForm)', @'
    $dialog.StartPosition = 'Manual'
    $dialog.Location = New-Object Drawing.Point(-3000, -3000)
    $dialog.Show()
    [Windows.Forms.Application]::DoEvents()
    & $refreshGrid
    $grid.Rows[0].Selected = $true
    if (-not $newPlan.Enabled -or -not $applyPlan.Enabled) { throw 'Selecting an account must enable its plan editor.' }
    Save-Preview $dialog 'aetherion-license-accounts'
    $newPlan.SelectedIndex = 1
    $planDays.Value = 45
    if (-not $planDays.Enabled) { throw 'Custom plans must enable duration editing.' }
    Save-Preview $dialog 'aetherion-license-plans'
    $presenceFilter.SelectedIndex = 2
    if (@($grid.Rows | Where-Object Visible).Count -ne 3) { throw 'Offline filter failed.' }
    if ($grid.SelectedRows.Count -ne 0 -or $applyPlan.Enabled -or $newPlan.Enabled) { throw 'Filtering must clear hidden selection and disable mutations.' }
    $search.Text = 'demo-research'
    if (@($grid.Rows | Where-Object Visible).Count -ne 1) { throw 'Combined search filter failed.' }
    $dialog.Size = $dialog.MinimumSize
    Save-Preview $dialog 'aetherion-license-compact'
'@)
Invoke-Expression $ui
function Refresh-IssueAuthority { $script:AuthorityReady = $false; $script:AuthorityError = 'Preview: no credentials loaded.' }
$script:MainForm.StartPosition = 'Manual'
$script:MainForm.Location = New-Object Drawing.Point(-3000, -3000)
$script:MainForm.Show()
[Windows.Forms.Application]::DoEvents()
Save-Preview $script:MainForm 'aetherion-license-manager'
Show-AccountManager
$script:MainForm.Dispose()
Write-Output 'Four sanitized UI captures generated; filters verified. No credentials or network used.'
