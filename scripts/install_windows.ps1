$ErrorActionPreference = "Stop"

$rootDir = Resolve-Path "${PSScriptRoot}\.."
$workDir = Join-Path $rootDir ".build"
$qtDir = Join-Path $workDir "qt5"
$pyqtDir = Join-Path $workDir "pyqt5"
$pyqtWebEngineDir = Join-Path $workDir "pyqtwebengine"
$qtInstallDir = Join-Path $workDir "qt-install"

New-Item -ItemType Directory -Force -Path $workDir | Out-Null

Write-Host "Borgor Browser - Windows setup for PyQtWebEngine with proprietary codecs"
Write-Host "This script builds QtWebEngine with proprietary codecs enabled and then builds"
Write-Host "PyQt5 + PyQtWebEngine against that Qt build."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required on PATH"
}

if (-not (Test-Path $qtDir)) {
  Write-Host ":: Cloning Qt5"
  git clone https://code.qt.io/qt/qt5.git $qtDir
  Push-Location $qtDir
  git checkout 5.15.2
  .\init-repository --module-subset=qtbase,qtdeclarative,qtwebengine,qtwebchannel,qtwebsockets,qttools
  Pop-Location
}

Write-Host ":: Configuring Qt with proprietary codecs"
Push-Location $qtDir
.\configure.bat -opensource -confirm-license -release -nomake examples -nomake tests `
  -prefix $qtInstallDir -webengine-proprietary-codecs -webengine-ffmpeg
jom
jom install
Pop-Location

Write-Host ":: Setting up Python virtual environment"
python -m venv (Join-Path $workDir "venv")
& (Join-Path $workDir "venv\Scripts\activate.ps1")

pip install --upgrade pip setuptools wheel sip

if (-not (Test-Path $pyqtDir)) {
  Write-Host ":: Cloning PyQt5"
  git clone https://github.com/baoboa/pyqt5.git $pyqtDir
}

if (-not (Test-Path $pyqtWebEngineDir)) {
  Write-Host ":: Cloning PyQtWebEngine"
  git clone https://github.com/baoboa/pyqtwebengine.git $pyqtWebEngineDir
}

Write-Host ":: Building PyQt5"
Push-Location $pyqtDir
python configure.py --qmake (Join-Path $qtInstallDir "bin\qmake.exe") --confirm-license
jom
jom install
Pop-Location

Write-Host ":: Building PyQtWebEngine"
Push-Location $pyqtWebEngineDir
python configure.py --qmake (Join-Path $qtInstallDir "bin\qmake.exe") --confirm-license
jom
jom install
Pop-Location

Write-Host ":: Done. Activate the venv and run: python browser.py"
