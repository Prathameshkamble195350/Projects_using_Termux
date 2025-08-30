# detector.py
import time
from collections import defaultdict, deque
import re
from scapy.all import IP, TCP, ICMP, Raw

class Detector:
    def __init__(self,
                 icmp_threshold=30, icmp_window=10,
                 syn_threshold=60, syn_window=10,
                 scan_port_threshold=12, scan_window=5,
                 block_duration=300):
        # sliding windows per src IP (timestamps or port sets)
        self.icmp_times = defaultdict(deque)   # src_ip -> deque of timestamps
        self.syn_times = defaultdict(deque)
        self.port_hits = defaultdict(deque)    # store (timestamp, port)
        self.blocked = {}  # ip -> expiry_time (unix ts)

        self.icmp_threshold = icmp_threshold
        self.icmp_window = icmp_window

        self.syn_threshold = syn_threshold
        self.syn_window = syn_window

        self.scan_port_threshold = scan_port_threshold
        self.scan_window = scan_window

        self.block_duration = block_duration

        # simple SQLi/payload regex (improvable)
        sqli_patterns = [
            r"(?i)\bunion\b.*\bselect\b",
            r"(?i)'\s*or\s*'1'='1",
            r"(?i)\bselect\b.*\bfrom\b",
            r"(?i)drop\s+table",
            r"(?i)insert\s+into",
            r"(?i)--\s", r";\s*--"
        ]
        self.sqli_re = re.compile("|".join(sqli_patterns))

    def is_blocked(self, src_ip, now=None):
        now = now or time.time()
        if src_ip in self.blocked and self.blocked[src_ip] > now:
            return True
        # cleanup if expired
        if src_ip in self.blocked and self.blocked[src_ip] <= now:
            del self.blocked[src_ip]
        return False

    def block_ip(self, src_ip, now=None):
        now = now or time.time()
        self.blocked[src_ip] = now + self.block_duration

    def _cleanup_deque(self, dq, window, now):
        # pop left while too old
        while dq and dq[0] < now - window:
            dq.popleft()

    def inspect_packet(self, pkt):  # pkt is a scapy packet
        now = time.time()
        if IP not in pkt:
            return False, "non-ip"  # accept non-IP by default

        ip = pkt[IP]
        src = ip.src

        if self.is_blocked(src, now):
            return True, "blocked-list"

        # ICMP flood detection
        if ICMP in pkt:
            dq = self.icmp_times[src]
            dq.append(now)
            self._cleanup_deque(dq, self.icmp_window, now)
            if len(dq) > self.icmp_threshold:
                self.block_ip(src, now)
                return True, "icmp-flood"

        # TCP-related rules
        if TCP in pkt:
            tcp = pkt[TCP]
            flags = tcp.flags

            # SYN flood detection: SYN flag set, no ACK
            if flags & 0x02 and not (flags & 0x10):  # SYN and not ACK
                dq = self.syn_times[src]
                dq.append(now)
                self._cleanup_deque(dq, self.syn_window, now)
                if len(dq) > self.syn_threshold:
                    self.block_ip(src, now)
                    return True, "syn-flood"

                # port-scan detection: many distinct ports in a sliding window
                self.port_hits[src].append((now, tcp.dport))
                # remove old
                ph = self.port_hits[src]
                # filter only within window
                ph = deque([(t,p) for (t,p) in ph if t >= now - self.scan_window])
                self.port_hits[src] = ph
                ports = {p for (t,p) in ph}
                if len(ports) >= self.scan_port_threshold:
                    self.block_ip(src, now)
                    return True, "port-scan"

            # HTTP payload scanning / SQLi patterns
            if Raw in tcp and (tcp.dport in (80,8080) or tcp.sport in (80,8080) or b"HTTP" in bytes(tcp.payload)[:8]):
                # try to decode safely
                try:
                    payload = bytes(tcp.payload).decode('utf-8', errors='ignore')
                except Exception:
                    payload = ""
                if self.sqli_re.search(payload):
                    self.block_ip(src, now)
                    return True, "sqli-payload"

            # detect unusual TCP flags (NULL/FIN/XMAS scans)
            # NULL -> flags == 0; FIN -> flags == 0x01; XMAS -> FIN+PSH+URG (0x29)
            if int(flags) == 0:
                # null scan
                self.block_ip(src, now)
                return True, "null-scan"
            if int(flags) & 0x01 and not (int(flags) & 0x02):
                # FIN without SYN -> suspicious
                self.block_ip(src, now)
                return True, "fin-scan"

        return False, "ok"
