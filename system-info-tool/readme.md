# 📱 System Info Tool (Termux)

A simple Python script to display **system inform>

## 🔹 Features
- OS, Processor, and Device details
- CPU usage & core count
- Memory (RAM) usage
- Storage usage
- Battery status (via Termux API)
- Local IP address

## 🔹 Requirements
- Termux app
- Python 3
- `psutil` library
- Termux:API (for battery info)

Install requirements:
```bash
pkg update && pkg upgrade -y
pkg install python termux-api -y
pip install -r requirements.txt
