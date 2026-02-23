# DeepFaceLive on macOS

Steps to run [DeepFaceLive](https://github.com/iperov/DeepFaceLive) on Mac (CPU only; no CUDA/DirectX).

## 1. Get the repo

**Option A – Download ZIP (recommended if clone fails)**  
- Open https://github.com/iperov/DeepFaceLive  
- Click **Code** → **Download ZIP**  
- Unzip and rename the folder to `DeepFaceLive`  
- Move it to `/Applications/face-live/DeepFaceLive`

**Option B – Git clone**  
```bash
cd /Applications/face-live
git config --global http.postBuffer 524288000
git clone --depth 1 https://github.com/iperov/DeepFaceLive.git
```

## 2. Python 3.9

DeepFaceLive is known to work with Python 3.9. Use a dedicated env:

```bash
brew install python@3.9
/usr/local/opt/python@3.9/bin/python3.9 -m venv /Applications/face-live/DeepFaceLive_venv
source /Applications/face-live/DeepFaceLive_venv/bin/activate
```

(On Apple Silicon use `brew --prefix python@3.9` for the path.)

## 3. Install dependencies

From the DeepFaceLive repo, install whatever the project uses (e.g. PyQt, OpenCV, ONNX Runtime). If there is a `requirements.txt`:

```bash
cd /Applications/face-live/DeepFaceLive
pip install -r requirements.txt
```

If there is no requirements file, try:

```bash
pip install opencv-python numpy onnxruntime PyQt5
```

Install any other deps the app or docs mention.

## 4. Apply macOS patches

From the `face-live` project root:

```bash
cd /Applications/face-live
chmod +x DeepFaceLive_macOS/apply_patches.sh
./DeepFaceLive_macOS/apply_patches.sh
```

This updates CameraSource (and any other patched files) so camera and timer behavior are correct on macOS.

## 5. Workspace and DFM models

DeepFaceLive needs **trained face models (`.dfm`)** in a userdata directory. The run script uses the shared **workspace**:

- **`workspace/dfm_models/*.dfm`** – place your exported DFM models here (from DeepFaceLab `exportdfm`).
- After training in DeepFaceLab, run `exportdfm`, then copy `workspace/model/*.dfm` → `workspace/dfm_models/`. See `DeepFaceLab/TRAIN_MAC.md` for the full pipeline.

## 6. Run with CPU (no CUDA)

```bash
cd /Applications/face-live/DeepFaceLive
source /Applications/face-live/DeepFaceLive_venv/bin/activate  # or your venv
python main.py run DeepFaceLive --no-cuda --userdata-dir /Applications/face-live/workspace
```

Or use the helper script (sets workspace as userdata automatically):

```bash
/Applications/face-live/DeepFaceLive_macOS/run_deepfacelive_mac.sh
```

## Notes

- **Performance:** Running with `--no-cuda` uses CPU only; it can be slow on Mac.
- **Camera:** The app uses OpenCV’s default camera API on Mac (CAP_ANY). Grant **Terminal** (or your IDE) camera access in **System Settings → Privacy & Security → Camera**.
- **GUI:** The app uses Qt; it should run on macOS. If you see “platform not supported” or missing DLLs, those are likely Windows-only paths that would need extra patching.
- **Repo archived:** The project was [archived in Nov 2024](https://github.com/iperov/DeepFaceLive); no new releases, but the code can still be cloned and run.
