#!/usr/bin/env python3
import argparse
import os
from .steg import compute_hash, embed_png, extract_png, embed_wav, extract_wav

parser = argparse.ArgumentParser("stegcheck")
sub = parser.add_subparsers(dest="cmd")

# gen-hash
p = sub.add_parser("hash")
p.add_argument("target", help="file to hash")
p.add_argument("--algo", default="sha256", choices=["sha256","sha3_256"])

# embed
p = sub.add_parser("embed")
p.add_argument("target", help="file to hash and embed")
p.add_argument("--cover", required=True, help="cover file (PNG or WAV)")
p.add_argument("--out", required=True, help="output stego file")
p.add_argument("--algo", default="sha256", choices=["sha256","sha3_256"])

# extract
p = sub.add_parser("extract")
p.add_argument("--stego", required=True, help="stego cover (PNG or WAV)")

# verify
p = sub.add_parser("verify")
p.add_argument("target", help="file to verify")
p.add_argument("--stego", required=True, help="stego cover (PNG or WAV) to extract hash from")

args = parser.parse_args()

if args.cmd == "hash":
    print(compute_hash(args.target, args.algo))

elif args.cmd == "embed":
    h = compute_hash(args.target, args.algo)
    meta = {"alg": args.algo, "filename": os.path.basename(args.target), "hash": h}
    ext = args.cover.lower().split('.')[-1]
    if ext == "png":
        embed_png(args.cover, args.out, meta)
    elif ext == "wav":
        embed_wav(args.cover, args.out, meta)
    else:
        raise SystemExit("Unsupported cover format: use PNG or WAV")
    print("Embedded. Output:", args.out)

elif args.cmd == "extract":
    ext = args.stego.lower().split('.')[-1]
    if ext == "png":
        meta = extract_png(args.stego)
    elif ext == "wav":
        meta = extract_wav(args.stego)
    else:
        raise SystemExit("Unsupported stego format: use PNG or WAV")
    print(meta)

elif args.cmd == "verify":
    ext = args.stego.lower().split('.')[-1]
    if ext == "png":
        meta = extract_png(args.stego)
    elif ext == "wav":
        meta = extract_wav(args.stego)
    else:
        raise SystemExit("Unsupported stego format: use PNG or WAV")
    algo = meta.get("alg")
    expected = meta.get("hash")
    cur = compute_hash(args.target, algo)
    if cur == expected:
        print("OK: hashes match")
        print(meta)
    else:
        print("MISMATCH: file has been modified")
        print("expected:", expected)
        print("current :", cur)

else:
    parser.print_help()
