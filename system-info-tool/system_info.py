import os
import platform
import psutil
import socket
import datetime
import requests

# 🎨 Colors
R = "\033[31m"  # Red
G = "\033[32m"  # Green
Y = "\033[33m"  # Yellow
B = "\033[34m"  # Blue
M = "\033[35m"  # Magenta
C = "\033[36m"  # Cyan
W = "\033[37m"  # White
RESET = "\033[0m"

# 🔥 ASCII Banner
BANNER = f"""
{R}███████╗██╗   ██╗███████╗████████╗
{R}██╔════╝██║   ██║██╔════╝╚══██╔══╝
{Y}███████╗██║   ██║█████╗     ██║   
{Y}╚════██║██║   ██║██╔══╝     ██║   
{G}███████║╚██████╔╝███████╗   ██║   
{G}╚══════╝ ╚═════╝ ╚══════╝   ╚═╝   
{C}       📊 Termux System Info Tool
{RESET}
"""

def get_external_ip():
    try:
        ip = requests.get("https://api64.ipify.org?format=json", timeout=5).json()
        return ip.get("ip", "Unavailable")
    except:
        return "Unavailable"

def main():
    print(BANNER)
    print(f"{M}===== 📡 SYSTEM INFORMATION ====={RESET}\n")

    # OS Info
    print(f"{C}OS:{RESET} {platform.system()}")
    print(f"{C}OS Version:{RESET} {platform.version()}")
    print(f"{C}Release:{RESET} {platform.release()}")
    print(f"{C}Architecture:{RESET} {platform.machine()}")
    print(f"{C}Python Version:{RESET} {platform.python_version()}")

    # Device / User
    user = os.getenv("USER") or "Unknown"
    hostname = socket.gethostname()
    print(f"{C}User:{RESET} {user}")
    print(f"{C}Hostname:{RESET} {hostname}")

    # Date / Time
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{C}Current Time:{RESET} {now}")

    # External IP
    print(f"{C}External IP:{RESET} {get_external_ip()}")

    # Hardware Info
    print(f"{C}CPU Cores:{RESET} {psutil.cpu_count(logical=True)}")
    print(f"{C}Total RAM (MB):{RESET} {psutil.virtual_memory().total / 1024 / 1024:.2f}")
    print(f"{C}Available RAM (MB):{RESET} {psutil.virtual_memory().available / 1024 / 1024:.2f}")
    print(f"{C}Total Disk (GB):{RESET} {psutil.disk_usage('/').total / 1024 / 1024 / 1024:.2f}")
    print(f"{C}Used Disk (GB):{RESET} {psutil.disk_usage('/').used / 1024 / 1024 / 1024:.2f}")

    print(f"\n{M}===================================={RESET}")

if __name__ == "__main__":
    main()
    
