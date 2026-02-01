#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="${ROOT_DIR}/.build"
QT_DIR="${WORK_DIR}/qt5"
PYQT_DIR="${WORK_DIR}/pyqt5"
PYQT_WEBENGINE_DIR="${WORK_DIR}/pyqtwebengine"
QT_INSTALL_DIR="${WORK_DIR}/qt-install"

mkdir -p "${WORK_DIR}"

cat <<'BANNER'
Borgor Browser - Linux setup for PyQtWebEngine with proprietary codecs
This script builds QtWebEngine with proprietary codecs enabled and then builds
PyQt5 + PyQtWebEngine against that Qt build.

Requirements:
  - build tools: gcc/g++, make, ninja (recommended), python3
  - dependencies for QtWebEngine (see Qt docs)
  - plenty of disk space (QtWebEngine builds are large)
BANNER

echo ":: Ensuring build dependencies (Ubuntu/Debian example)"
if command -v apt-get >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y build-essential python3 python3-venv ninja-build git \
    libgl1-mesa-dev libxcb-xinerama0 libxkbcommon-dev libxrender-dev \
    libxrandr-dev libxcomposite-dev libxdamage-dev libxfixes-dev \
    libxi-dev libx11-xcb-dev libxcursor-dev libxext-dev libxss-dev \
    libxtst-dev libnss3-dev libasound2-dev libdbus-1-dev libdrm-dev
fi

if [ ! -d "${QT_DIR}" ]; then
  echo ":: Cloning Qt5"
  git clone https://code.qt.io/qt/qt5.git "${QT_DIR}"
  (
    cd "${QT_DIR}"
    git checkout 5.15.2
    ./init-repository --module-subset=qtbase,qtdeclarative,qtwebengine,qtwebchannel,qtwebsockets,qttools
  )
fi

echo ":: Configuring Qt with proprietary codecs"
(
  cd "${QT_DIR}"
  ./configure \
    -opensource -confirm-license -release -nomake examples -nomake tests \
    -prefix "${QT_INSTALL_DIR}" \
    -webengine-proprietary-codecs -webengine-ffmpeg
  make -j"$(nproc)"
  make install
)

echo ":: Setting up Python virtual environment"
python3 -m venv "${WORK_DIR}/venv"
# shellcheck disable=SC1091
source "${WORK_DIR}/venv/bin/activate"

pip install --upgrade pip setuptools wheel sip

if [ ! -d "${PYQT_DIR}" ]; then
  echo ":: Cloning PyQt5"
  git clone https://github.com/baoboa/pyqt5.git "${PYQT_DIR}"
fi

if [ ! -d "${PYQT_WEBENGINE_DIR}" ]; then
  echo ":: Cloning PyQtWebEngine"
  git clone https://github.com/baoboa/pyqtwebengine.git "${PYQT_WEBENGINE_DIR}"
fi

echo ":: Building PyQt5"
(
  cd "${PYQT_DIR}"
  python3 configure.py --qmake "${QT_INSTALL_DIR}/bin/qmake" --confirm-license
  make -j"$(nproc)"
  make install
)

echo ":: Building PyQtWebEngine"
(
  cd "${PYQT_WEBENGINE_DIR}"
  python3 configure.py --qmake "${QT_INSTALL_DIR}/bin/qmake" --confirm-license
  make -j"$(nproc)"
  make install
)

echo ":: Done. Activate the venv and run: python browser.py"
