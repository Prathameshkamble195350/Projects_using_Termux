# tests/test_detector.py
import time
from detector import Detector
from scapy.all import IP, ICMP, TCP, Raw

def test_icmp_flood_detection():
    d = Detector(icmp_threshold=3, icmp_window=2)
    src = "10.0.0.1"
    for _ in range(4):
        pkt = IP(src=src, dst="10.0.0.2")/ICMP()
        drop, reason = d.inspect_packet(pkt)
    assert drop and reason == "icmp-flood"

def test_syn_flood_detection():
    d = Detector(syn_threshold=4, syn_window=2)
    src = "10.0.0.3"
    for _ in range(5):
        pkt = IP(src=src, dst="10.0.0.4")/TCP(sport=1234, dport=80, flags="S")
        drop, reason = d.inspect_packet(pkt)
    assert drop and reason == "syn-flood"

def test_sqli_detection():
    d = Detector()
    src = "10.0.0.8"
    payload = "GET /index.php?id=1 UNION SELECT username FROM users -- HTTP/1.1\r\n"
    pkt = IP(src=src, dst="10.0.0.9")/TCP(sport=1234, dport=80, flags="PA")/Raw(load=payload.encode())
    drop, reason = d.inspect_packet(pkt)
    assert drop and reason == "sqli-payload"
