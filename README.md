# Grip8a

Repo for our experimental **finger strength & hangboard analytics** project.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Repo Size](https://img.shields.io/github/repo-size/justin-frandsen/Grip8a.svg)](https://github.com/justin-frandsen/Grip8a)
[![Last Commit](https://img.shields.io/github/last-commit/justin-frandsen/Grip8a.svg)](https://github.com/justin-frandsen/Grip8a/commits/main)

Structure:
```
grip8a/
│
├── ble/ # Handles Bluetooth Low Energy communication
│ └── manager.py # BLEManager class + current force value
│ └── config.py # where to enter device name and uuid
├── cli/ # Command-line interfaces for user interaction
│ ├── force_cli.py # Menus for force sensor tools
│ └── maxhang_cli.py # Menus for hangboard tools
│
├── db/ # SQLite database logic
│ ├── force_db.py # Handles force sensor table (readings)
│ ├── maxhang_db.py # Handles hang log table (hangs)
│ └── config.py # Central DB file path shared across modules
│
├── utils/ # Shared utilities and helper functions
│ └── timers.py # Complex timer used for hang protocols
│
├── run.py # Entry point for the entire application
└── README.md
```

## Overview

Grip8a is a system for:

- Logging max hangs  
- Tracking hangboard training progression  
- Collecting real-time **force sensor** data over BLE  
- Storing all data in a local SQLite database  
- Running timers, protocols, and analytics without internet access 

Long term we may package it as a mobile app

## current features

### **Hangboard Tools**
- **Complex Timer** — fully working  
- **Log Max Hang** — fully working  
- **View Logs** — fully working  
- Local SQLite storage

### **Force Sensor Tools**
- **BLE Connection**
- **Live force streaming**
- **Saving readings to DB (`force_readings.db`)**
- **NOT YET TESTED** — requires Micah


## How to run

1. Activate virtual environment
Mac/Linux:
```bash
source .venv/bin/activate
```

Windows:
```powershell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the program
```bash
python run.py
```