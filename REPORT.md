Include:

Title, members, environment (Kali version, Python version)

Design & message format (explain MAGIC + length + JSON)

Embedding technique (PNG LSB in RGB channels; WAV LSB in frames)

Capacity & limitations (image size, audio length; cannot reliably embed in lossy formats like JPEG or MP3)

False negatives/positives (explain how an attacker can modify cover to remove hidden data; compressed/resaved images may destroy payload)

Improvements (steganographic transforms, encryption of payload, multi-file embedding, GUI, authenticated encryption)

Demo results & test summary
