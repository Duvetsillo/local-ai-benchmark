$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$projectFile = Join-Path $projectRoot 'Launcher\Launcher.csproj'
$publishDirectory = Join-Path $projectRoot 'Launcher\publish'
$installerDefinition = Join-Path $PSScriptRoot 'Aetherion-License-Manager.iss'
$outputDirectory = Join-Path $projectRoot 'dist'

$compilerCandidates = @(
    (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 7\ISCC.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 7\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 7\ISCC.exe')
)
$compiler = Get-Command 'ISCC.exe' -ErrorAction SilentlyContinue
if ($compiler) {
    $compilerPath = $compiler.Source
}
else {
    $compilerPath = $compilerCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if (-not $compilerPath) {
    throw 'Inno Setup is required to create the installer. Install it from https://jrsoftware.org/isdl.php and run this script again.'
}

$dotnetCandidates = @(
    (Join-Path $env:USERPROFILE '.dotnet\dotnet.exe'),
    (Get-Command 'dotnet.exe' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
)
$dotnetPath = $null
foreach ($candidate in $dotnetCandidates) {
    if (-not $candidate -or -not (Test-Path $candidate -PathType Leaf)) {
        continue
    }

    $availableSdks = & $candidate --list-sdks
    if ($LASTEXITCODE -eq 0 -and ($availableSdks | Where-Object { $_ -match '^8\.' })) {
        $dotnetPath = $candidate
        break
    }
}
if (-not $dotnetPath) {
    throw '.NET SDK 8 is required to build the launcher.'
}

& $dotnetPath publish $projectFile -c Release -r win-x64 --self-contained false -p:UseAppHost=true -o $publishDirectory
if ($LASTEXITCODE -ne 0) {
    throw "Launcher publish failed with exit code $LASTEXITCODE."
}

$launcherFiles = @(
    'Aetherion-License-Manager.exe',
    'Aetherion-License-Manager.dll',
    'Aetherion-License-Manager.deps.json',
    'Aetherion-License-Manager.runtimeconfig.json'
)
foreach ($name in $launcherFiles) {
    $builtFile = Join-Path $publishDirectory $name
    if (-not (Test-Path $builtFile -PathType Leaf)) {
        throw "Published launcher output is missing: $builtFile"
    }
    Copy-Item -LiteralPath $builtFile -Destination (Join-Path $projectRoot $name) -Force
    $builtHash = (Get-FileHash -LiteralPath $builtFile -Algorithm SHA256).Hash
    $rootHash = (Get-FileHash -LiteralPath (Join-Path $projectRoot $name) -Algorithm SHA256).Hash
    if ($builtHash -ne $rootHash) {
        throw "The current launcher output was not copied correctly: $name"
    }
}

$requiredFiles = @(
    (Join-Path $projectRoot 'Aetherion-License-Manager.exe'),
    (Join-Path $projectRoot 'Aetherion-License-Manager.ps1'),
    (Join-Path $projectRoot 'Aetherion-License-Manager.UI.ps1'),
    (Join-Path $projectRoot 'Assets\Inter.ttf'),
    (Join-Path $projectRoot 'Assets\Inter-OFL.txt')
)
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file -PathType Leaf)) {
        throw "Required installer input is missing: $file"
    }
}

New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
& $compilerPath $installerDefinition
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup compilation failed with exit code $LASTEXITCODE."
}

$installerPath = Join-Path $outputDirectory 'Aetherion-License-Manager-Setup.exe'
if (-not (Test-Path $installerPath -PathType Leaf)) {
    throw "Inno Setup did not create the expected installer: $installerPath"
}

Write-Output "Installer created: $installerPath"
