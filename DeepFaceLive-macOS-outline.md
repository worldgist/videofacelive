# DeepFaceLive on macOS – Outline

Summary of what’s in the [DeepFaceLive](https://github.com/iperov/DeepFaceLive) repo and what would be needed to run it on macOS.

---

## What’s in the repo

- **Entry point:** `main.py` – CLI with subcommands:
  - `run DeepFaceLive` – run the main app (`apps.DeepFaceLive.DeepFaceLiveApp`)
  - `dev` – dev tools (split/merge large files, extract FaceSynthetics)
  - `train FaceAligner` – train face aligner model
- **Main app:** `apps/DeepFaceLive/` – real-time face swap / face animator UI.
- **Training:** `apps/trainers/FaceAligner/` – face aligner training.
- **Libraries:** `xlib/` – shared code (app args, OS helpers, etc.).
- **Models / resources:** `modelhub/`, `resources/` – ONNX models and assets.
- **Docs:** `doc/` – Windows setup, streaming, video calls, FAQ.
- **Build:** `build/windows/` (Windows), `build/linux/` (Docker + NVIDIA/CUDA).

**Features:**

- Face swap with DFM models or single photo (Insight).
- Face animator (drive a static face with webcam, similar to Avatarify).
- Designed for streaming and video calls.

---

## Official platform support

| Platform | Support | Notes |
|----------|--------|--------|
| **Windows 10 x64** | ✅ Full | DirectX 12 build; portable release (no install). Recommended: RTX 2070+ or similar. |
| **Linux** | ⚠️ Build only | Docker in `build/linux/`; needs NVIDIA driver 470 + CUDA 11.4. No official “desktop” macOS path. |
| **macOS** | ❌ None | No docs, no build, no release. |

So the repo is **Windows-first**, with a **Linux Docker/CUDA** path; **macOS is not supported**.

---

## Technical dependencies (from code and docs)

- **Python:** 3.9 (newer versions reported incompatible in community).
- **ONNX Runtime:** e.g. 1.8.x; code mentions CUDA (e.g. `CUDA_PATH_V11_2`); `--no-cuda` exists for CPU.
- **GPU:** DirectX 12 on Windows; on Linux, NVIDIA + CUDA 11.4 in Docker.
- **OS layer:** `xlib.os` (process priority, etc.) – may assume Windows/Linux.
- **UI:** Likely a desktop GUI (Windows-oriented); exact stack is in `apps/DeepFaceLive/`.

---

## What would be needed to run on macOS

1. **Clone the repo**  
   Already (or once) cloned under:  
   ` /Applications/face-live/DeepFaceLive/`  
   If not, run:  
   `git clone --depth 1 https://github.com/iperov/DeepFaceLive.git`

2. **Python environment**  
   - Use Python 3.9 (e.g. `pyenv` or `brew install python@3.9`).  
   - Create a venv and install deps (e.g. `pip install -r requirements.txt` if present).

3. **Replace or abstract GPU path**  
   - No DirectX on macOS; no official CUDA.  
   - Options:  
     - **ONNX Runtime** with CoreML or CPU only (if the app supports `--no-cuda` and runs without GPU).  
     - **Metal** via ONNX Runtime or custom ops (would require code changes).  
   - So: either run CPU-only (slow) or port GPU bits to Metal/ONNX-Metal.

4. **OS and UI**  
   - Replace or stub Windows/Linux-only bits in `xlib.os` (e.g. process priority).  
   - If the UI is Windows-specific (e.g. Win32), it would need a macOS alternative (e.g. Qt/Tk or a minimal local web UI).

5. **Camera and I/O**  
   - On macOS, camera/video I/O can be done with OpenCV or AVFoundation; the rest of the pipeline would need to accept frames from that.

6. **Realistic options on a Mac**  
   - **Try CPU-only:** clone, Python 3.9, install deps, run `python main.py run DeepFaceLive --no-cuda` and fix import/OS errors as they appear (no guarantee the app will be usable).  
   - **Use the Windows build elsewhere:** run the official Windows portable build on a Windows or cloud GPU machine and use it for streaming/calls.  
   - **Use what you have on Mac:** keep using **Avatarify** (`python run.py --config avatarify.yaml`) for face-animator style use on macOS.

---

## Quick reference commands (once repo is present)

```bash
cd /Applications/face-live/DeepFaceLive
# Python 3.9 recommended
python main.py run DeepFaceLive --no-cuda
# Optional: set workspace
python main.py run DeepFaceLive --userdata-dir /path/to/data --no-cuda
```

If the clone is not there yet, run from ` /Applications/face-live/`:

```bash
git clone --depth 1 https://github.com/iperov/DeepFaceLive.git
```

### If `git clone` fails (disconnect / early EOF)

The repo is large; the connection may drop. Try in **Terminal.app** (not Cursor):

1. **Larger buffer and retry:**
   ```bash
   cd /Applications/face-live
   rm -rf DeepFaceLive
   git config --global http.postBuffer 524288000
   git clone --depth 1 https://github.com/iperov/DeepFaceLive.git
   ```

2. **Or download as ZIP** (no git history):
   - Open https://github.com/iperov/DeepFaceLive
   - Click **Code** → **Download ZIP**
   - Unzip to `/Applications/face-live/` and rename the folder to `DeepFaceLive`

---

## Summary

- **Repo contents:** Main app in `apps/DeepFaceLive/`, ONNX models, xlib, trainers, Windows/Linux build and docs.  
- **macOS:** Not officially supported; use the **DeepFaceLive_macOS** helper in this project to patch and run on Mac (CPU only).  
- **Practical on Mac:** Use `DeepFaceLive_macOS/README_MAC.md` and `apply_patches.sh` after cloning; run with `--no-cuda`. For a smooth face-animator experience on Mac without DeepFaceLive, Avatarify (`python run.py --config avatarify.yaml`) remains the supported option.
