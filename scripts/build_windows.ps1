Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (Test-Path "neat\Scripts\python.exe") {
    $Python = "neat\Scripts\python.exe"
} elseif (Test-Path ".venv\Scripts\python.exe") {
    $Python = ".venv\Scripts\python.exe"
} else {
    $Python = "python"
}

& $Python -m PyInstaller `
    --name Neatify `
    --windowed `
    --clean `
    --noconfirm `
    --add-data "assets;assets" `
    gui.py

function Get-SignTool {
    $SignTool = Get-Command "signtool.exe" -ErrorAction SilentlyContinue

    if ($null -ne $SignTool) {
        return $SignTool.Source
    }

    $KitRoots = @(
        "${env:ProgramFiles(x86)}\Windows Kits\10\bin",
        "${env:ProgramFiles}\Windows Kits\10\bin"
    )

    foreach ($Root in $KitRoots) {
        if (-not (Test-Path $Root)) {
            continue
        }

        $Candidates = Get-ChildItem -Path $Root -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*\x64\signtool.exe" } |
            Sort-Object FullName -Descending

        if ($Candidates.Count -gt 0) {
            return $Candidates[0].FullName
        }
    }

    return $null
}

function Sign-FileIfConfigured {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath
    )

    if ([string]::IsNullOrWhiteSpace($env:WINDOWS_CERT_PATH)) {
        Write-Host "Skipping Windows code signing. Set WINDOWS_CERT_PATH and WINDOWS_CERT_PASSWORD to sign."
        return
    }

    $SignToolPath = Get-SignTool

    if ($null -eq $SignToolPath) {
        throw "signtool.exe was not found. Install the Windows SDK to sign Windows builds."
    }

    Write-Host "Signing $FilePath"
    & $SignToolPath sign `
        /fd SHA256 `
        /td SHA256 `
        /tr "http://timestamp.digicert.com" `
        /f "$env:WINDOWS_CERT_PATH" `
        /p "$env:WINDOWS_CERT_PASSWORD" `
        "$FilePath"
}

New-Item -ItemType Directory -Force -Path "release" | Out-Null

Sign-FileIfConfigured "dist\Neatify\Neatify.exe"

$InnoCompiler = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue

if ($null -eq $InnoCompiler) {
    $CommonInnoPaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    )

    foreach ($InnoPath in $CommonInnoPaths) {
        if (Test-Path $InnoPath) {
            $InnoCompiler = @{ Source = $InnoPath }
            break
        }
    }
}

if ($null -ne $InnoCompiler) {
    & $InnoCompiler.Source "scripts\Neatify.iss"
    Sign-FileIfConfigured "release\Neatify-Windows-Setup.exe"
    Write-Host "Created release\Neatify-Windows-Setup.exe"
} else {
    $ZipPath = "release\Neatify-Windows.zip"

    if (Test-Path $ZipPath) {
        Remove-Item $ZipPath
    }

    Compress-Archive -Path "dist\Neatify\*" -DestinationPath $ZipPath
    Write-Host "Created release\Neatify-Windows.zip"
    Write-Host "Install Inno Setup to create a one-click .exe installer."
}
