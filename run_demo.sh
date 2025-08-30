#!/bin/bash
# Usage: sudo ./run_demo.sh interface
IFACE="$1"
if [ -z "$IFACE" ]; then
  echo "Usage: sudo $0 <interface>"
  exit 1
fi

# NFQUEUE iptables rules (IPv4)
iptables -I INPUT -j NFQUEUE --queue-num 1
iptables -I FORWARD -j NFQUEUE --queue-num 1

echo "Starting ips.py in background (logs -> /tmp/light_ips.log)"
source .venv/bin/activate
python3 ips.py & PID=$!

echo "Replay malicious pcap onto $IFACE (you can change file)"
echo "tcpreplay -i $IFACE syn_flood.pcap"
# You can replace with icmp_flood.pcap or sqli_http.pcap
tcpreplay -i "$IFACE" syn_flood.pcap

sleep 2
echo "IPS log tail:"
tail -n 50 /tmp/light_ips.log

echo "Stopping ips (pid $PID) and clearing iptables rules"
kill $PID
iptables -D INPUT -j NFQUEUE --queue-num 1
iptables -D FORWARD -j NFQUEUE --queue-num 1
