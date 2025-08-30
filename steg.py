#!/usr/bin/env python3
"""stegcheck.steg - embed/extract hashes into/from PNG and WAV using LSB steganography."""
import os, json, hashlib
from PIL import Image
import wave

MAGIC = b"STEGv1\x00"  # 7 bytes magic

# ------------------ Helpers ------------------

def compute_hash(path: str, algo: str = "sha256") -> str:
    """Compute hex digest of a file using sha256 or sha3_256."""
    if algo.lower() not in ("sha256", "sha3_256"):
        raise ValueError("Unsupported algorithm: choose sha256 or sha3_256")
    h = hashlib.sha256() if algo.lower() == "sha256" else hashlib.sha3_256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _pack_message(data: dict) -> bytes:
    payload = json.dumps(data, separators=(",", ":")).encode("utf-8")
    return MAGIC + len(payload).to_bytes(4, "big") + payload


def _unpack_message(raw: bytes) -> dict:
    if not raw.startswith(MAGIC):
        raise ValueError("Magic header not found")
    length = int.from_bytes(raw[len(MAGIC):len(MAGIC)+4], "big")
    payload = raw[len(MAGIC)+4:len(MAGIC)+4+length]
    return json.loads(payload.decode("utf-8"))


def _bytes_to_bits(b: bytes):
    for byte in b:
        for i in range(8):
            yield (byte >> (7 - i)) & 1


def _bits_to_bytes(bits):
    b = bytearray()
    accum = 0
    cnt = 0
    for bit in bits:
        accum = (accum << 1) | (bit & 1)
        cnt += 1
        if cnt == 8:
            b.append(accum)
            accum = 0
            cnt = 0
    return bytes(b)

# ------------------ PNG (Pillow) ------------------

def embed_png(cover_path: str, out_path: str, data: dict):
    msg = _pack_message(data)
    bits = list(_bytes_to_bits(msg))

    img = Image.open(cover_path).convert("RGBA")
    pixels = list(img.getdata())  # list of (r,g,b,a)
    capacity = len(pixels) * 3
    if len(bits) > capacity:
        raise ValueError(f"Cover image too small: need {len(bits)} bits, capacity {capacity}")

    out_pixels = []
    bit_iter = iter(bits)

    for px in pixels:
        r, g, b, a = px
        new_r = (r & ~1) | (next(bit_iter, 0))
        new_g = (g & ~1) | (next(bit_iter, 0))
        new_b = (b & ~1) | (next(bit_iter, 0))
        out_pixels.append((new_r, new_g, new_b, a))

    # If bits were exhausted earlier, remaining next() will use default 0 (no change)
    img2 = Image.new(img.mode, img.size)
    img2.putdata(out_pixels)
    img2.save(out_path, "PNG")
    return out_path


def extract_png(cover_path: str) -> dict:
    img = Image.open(cover_path).convert("RGBA")
    pixels = list(img.getdata())
    bits = []
    for r, g, b, a in pixels:
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)

    # reconstruct bytes until we can parse magic and length
    # first need at least (len(MAGIC)+4) bytes = header_bytes
    header_bits_needed = (len(MAGIC) + 4) * 8
    header_bytes = _bits_to_bytes(bits[:header_bits_needed])
    if not header_bytes.startswith(MAGIC):
        raise ValueError("No STEG message found")
    payload_len = int.from_bytes(header_bytes[len(MAGIC):len(MAGIC)+4], "big")
    total_bits = (len(MAGIC) + 4 + payload_len) * 8
    if total_bits > len(bits):
        raise ValueError("Incomplete message in cover file")
    full_bytes = _bits_to_bytes(bits[:total_bits])
    return _unpack_message(full_bytes)

# ------------------ WAV (wave module) ------------------

def embed_wav(cover_path: str, out_path: str, data: dict):
    msg = _pack_message(data)
    bits = list(_bytes_to_bits(msg))

    with wave.open(cover_path, "rb") as wf:
        params = wf.getparams()
        frames = bytearray(wf.readframes(wf.getnframes()))

    capacity = len(frames)  # one bit per frame byte
    if len(bits) > capacity:
        raise ValueError(f"Cover wav too small: need {len(bits)} bits, capacity {capacity}")

    # modify LSB of each byte
    for i, b in enumerate(bits):
        frames[i] = (frames[i] & ~1) | b

    with wave.open(out_path, "wb") as wf:
        wf.setparams(params)
        wf.writeframes(bytes(frames))
    return out_path


def extract_wav(cover_path: str) -> dict:
    with wave.open(cover_path, "rb") as wf:
        frames = bytearray(wf.readframes(wf.getnframes()))

    bits = [b & 1 for b in frames]

    header_bits_needed = (len(MAGIC) + 4) * 8
    header_bytes = _bits_to_bytes(bits[:header_bits_needed])
    if not header_bytes.startswith(MAGIC):
        raise ValueError("No STEG message found in WAV")
    payload_len = int.from_bytes(header_bytes[len(MAGIC):len(MAGIC)+4], "big")
    total_bits = (len(MAGIC) + 4 + payload_len) * 8
    if total_bits > len(bits):
        raise ValueError("Incomplete message in WAV cover")
    full_bytes = _bits_to_bytes(bits[:total_bits])
    return _unpack_message(full_bytes)
