#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "📦 Installing requirements..."
pip install -r requirements.txt --quiet

echo "🚀 Running System Info Tool..."
python system_info.py
