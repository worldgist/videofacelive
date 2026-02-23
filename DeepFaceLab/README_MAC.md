# DeepFaceLab on macOS

[DeepFaceLab](https://github.com/iperov/DeepFaceLab) is the leading software for creating deepfakes (face swap, train models, merge). Official releases are **Windows-only**. On Mac you can run from source with **CPU only** (slow; no GPU/CUDA).

## Requirements

- **Python 3.8 or 3.9** (TensorFlow 2.4–2.10 works best with these; 3.10+ may have compatibility issues)
- macOS 10.15+ (Intel or Apple Silicon)

## Install

### 1. Create a dedicated venv (recommended)

```bash
cd /Applications/face-live
# Python 3.9 (if you have it via Homebrew)
/usr/local/opt/python@3.9/bin/python3.9 -m venv DeepFaceLab_venv
source DeepFaceLab_venv/bin/activate
```

On Apple Silicon, use your Python 3.9 path (e.g. `$(brew --prefix python@3.9)/bin/python3.9`).

### 2. Install dependencies

```bash
cd /Applications/face-live/DeepFaceLab
pip install --upgrade pip
pip install -r requirements-mac.txt
```

If you get errors (e.g. TensorFlow or numpy version conflicts), try:

```bash
pip install tensorflow==2.10.0
pip install -r requirements-mac.txt
```

### 3. Run

Use `--cpu-only` for extract, train, and merge. Examples:

```bash
# Extract faces from images
python main.py extract --input-dir /path/to/images --output-dir /path/to/output --detector s3fd --cpu-only

# Sort extracted faces
python main.py sort --input-dir /path/to/output --by hist

# Train (CPU only; very slow)
python main.py train --training-data-src-dir /path/to/src_faces --training-data-dst-dir /path/to/dst_faces --model-dir /path/to/model --model Model_Name --cpu-only

# Merge
python main.py merge --input-dir /path/to/frames --output-dir /path/to/merged --output-mask-dir /path/to/masks --model-dir /path/to/model --model Model_Name --cpu-only
```

List available models:

```bash
ls models/
```

## Notes

- **Performance:** Training and merging on CPU are much slower than on a Windows GPU. For serious use, consider the [Windows release](https://github.com/iperov/DeepFaceLab) or [Google Colab](https://github.com/iperov/DeepFaceLab#requirements-colabtxt).
- **Apple Silicon:** TensorFlow 2.9+ has native M1/M2 support; you may get some speedup with `tensorflow` (no extra flags). For best compatibility, stick to the versions in `requirements-mac.txt`.
- The repo was **archived** (Nov 2024); code is still usable but not actively maintained.
