# FACE-LIVE setup guide

Get the project running on macOS: video call UI, optional DeepFaceLive face swap, and optional training.

---

## 1. Prerequisites

- **macOS** (tested on recent versions)
- **Python 3.9+** (3.9 or 3.12 typical)
- **Terminal** (or your IDE terminal)

If Python isn’t installed:

```bash
brew install python@3.12
# or: brew install python@3.9
```

---

## 2. Project location

Use your actual project path. In this guide we assume:

```text
/Applications/face-live
```

Replace with your path (e.g. `~/Projects/face-live`) in the commands below.

```bash
cd /Applications/face-live
```

---

## 3. Main environment (call UI + camera)

This is the only env you need for the Zoom-style call UI and webcam.

**Create and activate venv:**

```bash
cd /Applications/face-live
python3 -m venv .venv
source .venv/bin/activate
```

**Install dependencies:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

You should see `(.venv)` in your prompt. Keep this terminal (or re-run `source .venv/bin/activate` when you open a new one).

---

## 4. Config and workspace

**Config** (camera indices for UI) is in `config.json`. Defaults are fine to start:

- `webcam_index`: 0 (built-in camera)
- `deepfacelive_camera_index`: 2 (for when you add a virtual camera later)

**Workspace** is used for training and for DeepFaceLive models. Ensure the folder exists:

```bash
mkdir -p /Applications/face-live/workspace/dfm_models
```

No need to create `src_faces` or `dst_faces` until you’re ready to train.

---

## 5. Verify: camera and UI

**List cameras** (optional; quiets OpenCV probe messages):

```bash
python list_cameras.py
```

You should see something like: `Available camera indices: [0]`.

**Start the call UI:**

```bash
python run.py --ui
```

A dark-themed window should open with your webcam in the main view. Use **End call** to close.

If you get **“PyQt5 is required”**: activate the venv and run `pip install PyQt5` (or re-run `pip install -r requirements.txt`).

---

## 6. (Optional) DeepFaceLive – face swap in the UI

To use **Source: DeepFaceLive** in the call UI you need:

1. DeepFaceLive installed and runnable
2. A virtual camera (e.g. OBS Virtual Camera) so the UI can read DeepFaceLive’s output
3. At least one `.dfm` model in `workspace/dfm_models/` (from training or a pre-made model)

**6a. DeepFaceLive on Mac**

- Follow **DeepFaceLive_macOS/README_MAC.md** (get repo, Python 3.9 venv, install deps, apply patches).
- Run DeepFaceLive with the shared workspace:
  ```bash
  python main.py run DeepFaceLive --no-cuda --userdata-dir /Applications/face-live/workspace
  ```
  Or use `DeepFaceLive_macOS/run_deepfacelive_mac.sh` if you use that script.

**6b. Virtual camera**

- Install OBS, add **Virtual Camera**, start it. Or use another virtual camera that appears as a system device.
- Run `python list_cameras.py` again; note the new index (e.g. 1 or 2).
- Set that index in `config.json` as `deepfacelive_camera_index`, then in the UI use **Source: DeepFaceLive**.

**6b2. Participant 1 = DeepFaceLive output**

To show the DeepFaceLive feed in the **Participant 1** panel (in addition to or instead of the main view):

1. In `config.json`, set:
   - `deepfacelive_camera_index`: the index of your virtual camera (from `python list_cameras.py`).
   - `participant_sources`: `["deepfacelive", "mirror"]` so Participant 1 uses DeepFaceLive and Participant 2 mirrors the main feed.

2. Start the UI (`python run.py --ui` or `python run.py --ui --with-deepfacelive`). Participant 1 will show the DeepFaceLive camera; if that camera isn’t available, the tile will show an error.

**6c. DFM models**

- Put `.dfm` files in `workspace/dfm_models/`. DeepFaceLive loads them when started with `--userdata-dir /Applications/face-live/workspace`.
- To train your own: see **TRAINING.md** and **DeepFaceLab/TRAIN_MAC.md**.

---

## 7. (Optional) Training your own face model

Training uses **DeepFaceLab** and is CPU-only on Mac (slow but works).

**7a. DeepFaceLab environment**

Use a separate venv (e.g. Python 3.9) and DeepFaceLab’s Mac requirements:

```bash
# If you have Python 3.9 via Homebrew:
/usr/local/opt/python@3.9/bin/python3.9 -m venv /Applications/face-live/DeepFaceLab_venv
# Apple Silicon:
# $(brew --prefix python@3.9)/bin/python3.9 -m venv /Applications/face-live/DeepFaceLab_venv

source /Applications/face-live/DeepFaceLab_venv/bin/activate
cd /Applications/face-live/DeepFaceLab
pip install --upgrade pip
pip install -r requirements-mac.txt
```

Or run the existing helper (if present):

```bash
/Applications/face-live/DeepFaceLab/setup_mac_venv.sh
```

**7b. Prepare data and train**

- Put SRC and DST images in folders, then extract/sort into `workspace/src_faces` and `workspace/dst_faces`. See **DeepFaceLab/TRAIN_MAC.md**.
- From project root, with the **DeepFaceLab** venv activated:
  ```bash
  cd /Applications/face-live
  source /Applications/face-live/DeepFaceLab_venv/bin/activate
  python run.py --train
  ```
- When training is done, export for DeepFaceLive:
  ```bash
  python run.py --train --export-only
  ```
  This puts a `.dfm` in `workspace/dfm_models/` for DeepFaceLive.

Full steps: **TRAINING.md** and **DeepFaceLab/TRAIN_MAC.md**.

---

## 8. Quick reference

| Goal | Command |
|------|--------|
| Activate main venv | `source .venv/bin/activate` |
| Start call UI | `python run.py --ui` |
| UI + start DeepFaceLive in background | `python run.py --ui --with-deepfacelive` |
| List cameras | `python list_cameras.py` |
| Train model (needs workspace/src_faces, dst_faces) | `python run.py --train` (use DeepFaceLab venv) |
| Export model for DeepFaceLive | `python run.py --train --export-only` |

**Paths (customize if different):**

- Project root: `/Applications/face-live`
- Main venv: `/Applications/face-live/.venv`
- Config: `/Applications/face-live/config.json`
- Workspace: `/Applications/face-live/workspace`
- DFM models for DeepFaceLive: `workspace/dfm_models/`

---

## 9. Troubleshooting

- **“PyQt5 is required”**  
  Activate `.venv` and run: `pip install PyQt5` or `pip install -r requirements.txt`.

- **“Camera not found” / “Could not open camera index 1”**  
  Run `python list_cameras.py` and set `webcam_index` or `deepfacelive_camera_index` in `config.json` to an index that appears in the list. Index 0 is usually the built-in webcam.

- **“No cameras found”**  
  Grant camera access: **System Settings → Privacy & Security → Camera** and allow Terminal (or your IDE).

- **DeepFaceLive won’t start**  
  See **DeepFaceLive_macOS/README_MAC.md** (Python 3.9, deps, patches). Ensure you run it with `--userdata-dir /Applications/face-live/workspace` so it sees `workspace/dfm_models/`.

- **Training fails (DeepFaceLab)**  
  Use the DeepFaceLab venv and install `DeepFaceLab/requirements-mac.txt`. Ensure `workspace/src_faces` and `workspace/dst_faces` exist and contain extracted faces (see **DeepFaceLab/TRAIN_MAC.md**).
