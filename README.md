<div align="center">

# ⚡ Easy Network Manager

**Modern Windows Process Monitor & Network Firewall Control Room by Kayzit**

[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6?style=flat-square&logo=windows)](https://github.com/ngtien137/easy-network-manager)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![Architecture](https://img.shields.io/badge/architecture-Clean%20%2F%20MVP-20B8F2?style=flat-square)](https://github.com/ngtien137/easy-network-manager)
[![Release](https://img.shields.io/badge/release-v1.0.0-41E6A5?style=flat-square)](https://github.com/ngtien137/easy-network-manager/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg?style=flat-square)](LICENSE)

*A clean, lightweight, open-source Windows task manager and network killswitch that gives you full control over which processes can access the internet.*

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Building from Source](#-building-from-source) • [License](#-license)

</div>

---

## 🌟 Features

### ⚡ 1-Click Network Killswitch
- Block or restore internet access for any application or process instantly.
- Uses native **Windows Defender Firewall** (`netsh advfirewall`) rules with non-destructive atomic inbound/outbound control.
- Rules persist even after closing the app, with an optional **Auto-restore network on exit** safeguard.

### 📊 Task Manager Process Classification
- Groups multi-instance applications (e.g. Google Chrome tabs, Discord workers, VS Code processes) into aggregated root entries.
- Accurately classifies **Interactive Apps** vs **Background Services** using the Windows Desktop Window Station API (`OpenInputDesktop` + `EnumDesktopWindows`).
- Real-time CPU%, RAM usage, and active socket connection counts.

### 📈 Live Telemetry & Socket Observability
- **Throughput Spline Chart**: Real-time download and upload speed graphing drawn with hardware-accelerated Qt painter.
- **Active Sockets Inspector**: Live view of all active TCP/UDP endpoints, local/remote IP addresses, ports, and connection states.
- 1-click socket kill and process firewall blocking directly from the traffic feed.

### 🛡️ Smart Firewall Profiles
- **🎮 Gaming Mode**: Temporarily blocks background downloaders (Windows Update, OneDrive, etc.) to minimize ping latency.
- **💼 Focus Mode**: Blocks distracting communication/entertainment apps (Spotify, Discord, Telegram, Steam).
- **🔒 Strict Privacy**: Blocks all non-system, untrusted background outbound connections.

### 🎨 Fluent Control Room UI
- Modern **Dark / Light theme** based on Windows 11 Fluent Design tokens (`Signal Cyan #20B8F2`, `Emerald Green #41E6A5`, `Ruby Red #FF6868`).
- **Dynamic Bilingual Support (EN · VI)**: Instant 1-click language toggle between English and Vietnamese across the entire application without restarts.
- **Fast Splash Screen & Smooth Loading States**: Instant startup with progress feedback and safe exit cleanup dialogs.
- **System Tray Integration**: Minimize to the Windows notification tray with quick unblock actions.

---

## 🚀 Quick Start

### Option A: Portable Standalone Executable (Recommended)
1. Download the latest `Kayzit_NetManager_Portable.exe` from the [Releases](https://github.com/Kayzit/NetManager/releases) page.
2. Double-click to run!
   * *No Python installation or setup required.*
   * *Automatically requests Administrator privileges when needed to manage firewall rules.*

---

### Option B: Run from Source

#### Prerequisites
- **Windows 10 / 11** (64-bit)
- **Python 3.10+** (Python 3.12 recommended)

#### 1. Clone the repository
```bash
git clone https://github.com/Kayzit/NetManager.git
cd NetManager
```

#### 2. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Run the application
```bash
python main.py
```
*Or double-click `run.bat` in the root folder.*

---

## 🏗️ Architecture & Design Patterns

The project is structured according to **Clean Architecture** and the **Model-View-Presenter (MVP)** pattern, strictly avoiding God Objects.

```
NetworkManager/
├── controllers/          # Presenters / Business Logic Coordinators
│   └── app_controller.py
├── core/                 # Core Domain Models, Interfaces & Services
│   ├── elevation.py      # UAC elevation service
│   ├── firewall_service.py # Atomic Windows Firewall engine
│   ├── i18n.py           # Dynamic EN/VI translation manager
│   ├── interfaces.py     # Pure abstract interfaces
│   ├── models.py         # Type-safe dataclasses
│   └── process_scanner.py# Task Manager process & socket scanner
├── resources/            # Multi-resolution brand icons & assets
│   ├── icon.ico
│   └── icon.png
├── ui/                   # Decoupled GUI Views & Components (PyQt6)
│   ├── components/       # Reusable widgets (Sidebar, Topbar, MetricCard, Chart, Splash)
│   ├── modals/           # Dialogs (ProcessInspector, ExitDialog)
│   ├── views/            # Main tabs (Processes, Traffic, Profiles, Settings)
│   ├── main_window.py    # Master Shell & Navigation host
│   └── theme.py          # Fluent Control Room styling tokens
├── workers/              # Background QThread workers
│   └── monitor_worker.py # Non-blocking asynchronous metrics polling
├── tests/                # Automated unit tests
├── build.bat             # 1-click standalone portable EXE builder
├── main.py               # Application entry point
├── requirements.txt      # Dependency specification
└── version_info.txt      # Windows executable metadata
```

---

## 🛠️ Building from Source

To compile a standalone, zero-dependency portable `.exe`:

```bash
# Option 1: Run the automated build script
build.bat

# Option 2: Run PyInstaller manually
pyinstaller --noconsole --onefile --icon="resources/icon.ico" --add-data="resources;resources" --version-file="version_info.txt" --name="Kayzit_NetManager_Portable" --distpath . --clean main.py
```

The output file `Kayzit_NetManager_Portable.exe` will be generated directly in the root directory.

---

## 🔒 Security & Privacy Notice

- **100% Transparent & Safe**: NetManager is completely open-source and uses standard Windows APIs (`psutil`, `win32gui`, `netsh`).
- **No Kernel Drivers**: Does not install intrusive drivers or third-party background services.
- **Non-Destructive**: All firewall rules created by NetManager are tagged with a `NetManager_` prefix, allowing safe cleanup without affecting your existing Windows Firewall configuration.

---

## 🧪 Running Tests

To run the automated unit test suite:

```bash
python -m unittest discover tests
```

---

## 📄 License

This project is open-source software licensed under the [MIT License](LICENSE).

---

<div align="center">
  <b>Kayzit NetManager</b> — Crafted with ❤️ by Kayzit.
</div>
