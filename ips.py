# ips.py
import argparse
import logging
import time
from netfilterqueue import NetfilterQueue
from scapy.all import IP
from detector import Detector
import os
from scapy.all import rdpcap

LOGFILE = "/tmp/light_ips.log"

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

detector = Detector()

def process_nfq_packet(nfpacket):
    try:
        raw = nfpacket.get_payload()
        pkt = IP(raw)
    except Exception as e:
        # Can't parse; accept so we don't kill connectivity
        nfpacket.accept()
        return

    src = pkt[IP].src
    drop, reason = detector.inspect_packet(pkt)
    if drop:
        # log and drop
        logging.info(f"DROP src={src} reason={reason} proto={pkt.proto} summary={pkt.summary()}")
        with open(LOGFILE, "a") as f:
            f.write(f"{time.time()},{src},{reason},{pkt.summary()}\n")
        nfpacket.drop()
    else:
        nfpacket.accept()

def run_nfqueue(queue_num=1):
    nfqueue = NetfilterQueue()
    try:
        nfqueue.bind(queue_num, process_nfq_packet)
        logging.info("Bound to NFQUEUE; waiting for packets (Ctrl-C to stop)")
        nfqueue.run()
    except KeyboardInterrupt:
        logging.info("Stopping NFQUEUE")
    finally:
        nfqueue.unbind()

def pci_process_pcap(path):
    logging.info(f"Processing pcap offline: {path}")
    pkts = rdpcap(path)
    for p in pkts:
        if IP in p:
            drop, reason = detector.inspect_packet(p)
            line = f"{time.time()},{p[IP].src},{reason},{p.summary()}\n"
            with open(LOGFILE, "a") as f:
                f.write(line)
            print(line.strip())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", help="Process an offline pcap and exit")
    parser.add_argument("--queue", type=int, default=1, help="NFQUEUE number")
    args = parser.parse_args()
    # ensure log exists
    open(LOGFILE, "a").close()

    if args.pcap:
        pci_process_pcap(args.pcap)
    else:
        run_nfqueue(args.queue)

if __name__ == "__main__":
    main()
