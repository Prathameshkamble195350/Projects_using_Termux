import os
from stegcheck.steg import compute_hash, _pack_message, _unpack_message, embed_png, extract_png, embed_wav, extract_wav
from PIL import Image
import wave

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "samples")
COVER_PNG = os.path.join(SAMPLES, "cover.png")
COVER_WAV = os.path.join(SAMPLES, "cover.wav")


def make_sample_png():
    img = Image.new("RGBA", (200, 200), color=(120, 200, 150, 255))
    img.save(COVER_PNG)


def make_sample_wav():
    # create a tiny wav: 1 second mono 16-bit 44100 Hz
    import array
    framerate = 44100
    nframes = framerate
    samples = array.array('h', [0] * nframes)
    with wave.open(COVER_WAV, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(samples.tobytes())


def test_pack_unpack_message():
    d = {"alg":"sha256","filename":"x.txt","hash":"abc"}
    raw = _pack_message(d)
    got = _unpack_message(raw)
    assert got == d


def test_png_embed_extract(tmp_path):
    os.makedirs(SAMPLES, exist_ok=True)
    make_sample_png()
    target = tmp_path / "t.txt"
    target.write_text("hello")
    out = tmp_path / "out.png"
    h = compute_hash(str(target))
    meta = {"alg":"sha256","filename":"t.txt","hash":h}
    embed_png(COVER_PNG, str(out), meta)
    extracted = extract_png(str(out))
    assert extracted["hash"] == h


def test_wav_embed_extract(tmp_path):
    os.makedirs(SAMPLES, exist_ok=True)
    make_sample_wav()
    target = tmp_path / "t2.txt"
    target.write_text("data")
    out = tmp_path / "out.wav"
    h = compute_hash(str(target))
    meta = {"alg":"sha256","filename":"t2.txt","hash":h}
    embed_wav(COVER_WAV, str(out), meta)
    extracted = extract_wav(str(out))
    assert extracted["hash"] == h
