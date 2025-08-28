#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
import requests
from colorama import Fore, Style, init

init(autoreset=True)

API_URL = "https://api.openweathermap.org/data/2.5/weather"

# --- Banner ---
def banner():
    os.system("clear")
    print(Fore.CYAN + Style.BRIGHT + r"""
 __        __   _                            _     
 \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \
   \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
    \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/
                🌤  Weather CLI Tool
""" + Style.RESET_ALL)
    print(Fore.YELLOW + "="*55 + Style.RESET_ALL)

# --- Format time ---
def fmt_time(ts_utc: int, tz_offset_sec: int) -> str:
    tz = timezone(timedelta(seconds=tz_offset_sec))
    return datetime.fromtimestamp(ts_utc, tz).strftime("%Y-%m-%d %H:%M")

def main():
    banner()
    api_key = os.environ.get("OWM_API_KEY")
    if not api_key:
        print(Fore.RED + "❌ OWM_API_KEY not set. Run: export OWM_API_KEY='your_key'" + Style.RESET_ALL)
        sys.exit(1)

    p = argparse.ArgumentParser(
        description="Weather CLI (OpenWeatherMap)\nExamples:\n"
                    "  python weather.py -c 'Mumbai,IN' -u metric\n"
                    "  python weather.py --lat 19.07 --lon 72.88 -u metric",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    p.add_argument("-c", "--city", help="City name (e.g. 'Pune,IN'). Country code recommended.")
    p.add_argument("--lat", type=float, help="Latitude")
    p.add_argument("--lon", type=float, help="Longitude")
    p.add_argument("-u", "--units", choices=["metric", "imperial", "standard"], default="metric",
                   help="Units: metric(°C,m/s), imperial(°F,mph), standard(K,m/s)")
    args = p.parse_args()

    params = {"appid": api_key, "units": args.units}
    if args.lat is not None and args.lon is not None:
        params.update({"lat": args.lat, "lon": args.lon})
    elif args.city:
        params["q"] = args.city
    else:
        default_city = os.environ.get("OWM_DEFAULT_CITY")
        if default_city:
            params["q"] = default_city
        else:
            print(Fore.RED + "❌ Provide --city 'Name,CC' or --lat/--lon (or set OWM_DEFAULT_CITY)." + Style.RESET_ALL)
            sys.exit(2)

    try:
        r = requests.get(API_URL, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        print(Fore.RED + f"❌ Network error: {e}" + Style.RESET_ALL)
        sys.exit(3)

    if r.status_code != 200:
        msg = data.get("message", "Unknown error")
        print(Fore.RED + f"❌ API error ({r.status_code}): {msg}" + Style.RESET_ALL)
        sys.exit(4)

    # --- Parse weather ---
    name = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    weather_main = (data.get("weather") or [{}])[0].get("main", "N/A")
    weather_desc = (data.get("weather") or [{}])[0].get("description", "N/A").title()
    main_data = data.get("main", {})
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    vis = data.get("visibility", None)
    tz_offset = data.get("timezone", 0)
    updated = data.get("dt", None)
    sunrise = data.get("sys", {}).get("sunrise", None)
    sunset  = data.get("sys", {}).get("sunset", None)

    unit_temp = {"metric": "°C", "imperial": "°F", "standard": "K"}[args.units]
    unit_wind = {"metric": "m/s", "imperial": "mph", "standard": "m/s"}[args.units]

    # --- Display ---
    print(Fore.GREEN + f"\n📍 Location     : {name}, {country}" + Style.RESET_ALL)
    print(Fore.CYAN  + f"☁️  Condition    : {weather_main} ({weather_desc})" + Style.RESET_ALL)
    print(Fore.YELLOW+ f"🌡 Temperature  : {main_data.get('temp', 'N/A')}{unit_temp} "
                       f"(Feels {main_data.get('feels_like', 'N/A')}{unit_temp})" + Style.RESET_ALL)
    print(Fore.MAGENTA+ f"💧 Humidity     : {main_data.get('humidity', 'N/A')}%   "
                        f"Pressure: {main_data.get('pressure', 'N/A')} hPa" + Style.RESET_ALL)
    if 'temp_min' in main_data and 'temp_max' in main_data:
        print(Fore.BLUE + f"🌡 Min/Max      : {main_data['temp_min']}{unit_temp} / {main_data['temp_max']}{unit_temp}" + Style.RESET_ALL)
    print(Fore.CYAN + f"💨 Wind         : {wind.get('speed', 'N/A')} {unit_wind}  Dir: {wind.get('deg', 'N/A')}°" + Style.RESET_ALL)
    print(Fore.CYAN + f"☁️  Clouds       : {clouds.get('all','N/A')}%" + Style.RESET_ALL)
    if vis is not None:
        print(Fore.CYAN + f"👁 Visibility   : {round(vis/1000,1)} km" + Style.RESET_ALL)
    if sunrise:
        print(Fore.YELLOW + f"🌅 Sunrise      : {fmt_time(sunrise, tz_offset)}" + Style.RESET_ALL)
    if sunset:
        print(Fore.RED + f"🌇 Sunset       : {fmt_time(sunset, tz_offset)}" + Style.RESET_ALL)
    if updated:
        print(Fore.WHITE + f"🕒 Updated      : {fmt_time(updated, tz_offset)}" + Style.RESET_ALL)

    print(Fore.YELLOW + "\n====================================================\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
