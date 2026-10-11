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

New-Item -ItemType Directory -Force -Path "release" | Out-Null

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
