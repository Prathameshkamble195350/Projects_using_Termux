# generate_pcaps.py
from scapy.all import IP, ICMP, TCP, Ether, wrpcap
import random
import time

def make_normal_pcap(path="normal.pcap"):
    pkts = []
    for i in range(20):
        pkts.append(IP(src="10.0.0.5", dst="10.0.0.10")/ICMP())
    wrpcap(path, pkts)
    print("Wrote", path)

def make_icmp_flood_pcap(path="icmp_flood.pcap"):
    pkts = []
    for i in range(300):
        pkts.append(IP(src="192.168.1.55", dst="192.168.1.100")/ICMP())
    wrpcap(path, pkts)
    print("Wrote", path)

def make_syn_flood_pcap(path="syn_flood.pcap"):
    pkts = []
    for i in range(1000):
        sport = random.randint(1024,65535)
        dport = random.randint(20,1024)
        pkts.append(IP(src="203.0.113.77", dst="203.0.113.5")/TCP(sport=sport, dport=dport, flags="S"))
    wrpcap(path, pkts)
    print("Wrote", path)

def make_sqli_http_pcap(path="sqli_http.pcap"):
    pkts = []
    payload = "GET /index.php?id=1 UNION SELECT username,password FROM users -- HTTP/1.1\r\nHost: example\r\n\r\n"
    for i in range(5):
        pkts.append(IP(src="198.51.100.9", dst="198.51.100.10")/TCP(sport=12345, dport=80, flags="PA")/payload)
    wrpcap(path, pkts)
    print("Wrote", path)

if __name__ == "__main__":
    make_normal_pcap()
    make_icmp_flood_pcap()
    make_syn_flood_pcap()
    make_sqli_http_pcap()
