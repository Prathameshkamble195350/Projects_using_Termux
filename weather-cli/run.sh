#!/data/data/com.termux/files/usr/bin/bash
set -e

if [ -z "$OWM_API_KEY" ]; then
  echo "❌ OWM_API_KEY not set. Run: export OWM_API_KEY='your_key'"
  exit 1
fi

# deps
pip show requests >/dev/null 2>&1 || pip install --quiet requests

# usage
if [ $# -eq 0 ]; then
  # default city via env or ask for one flag
  if [ -n "$OWM_DEFAULT_CITY" ]; then
    python weather.py -c "$OWM_DEFAULT_CITY" -u metric
  else
    echo "Usage: ./run.sh -c 'City,CC' [-u metric|imperial|standard]"
    exit 2
  fi
else
  python weather.py "$@"
fi
