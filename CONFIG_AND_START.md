# Config and start – FACE-LIVE call UI

## 1. Config (`config.json`)

Located in the project root. Main keys:

| Key | Meaning | Typical value |
|-----|--------|----------------|
| `webcam_index` | Built-in or main webcam | `0` |
| `deepfacelive_camera_index` | Virtual camera for DeepFaceLive (e.g. OBS) | `1` (or run `python list_cameras.py` to see) |
| `avatarify_camera_index` | Virtual camera for Avatarify (e.g. OBS capturing Avatarify window) | `1` |
| `video_source` | What the main view shows at startup | `"webcam"` (safest), `"deepfacelive"`, or `"avatarify"` |
| `participant_sources` | Source for Participant 1 and 2 | `["mirror","mirror"]` or e.g. `["deepfacelive","mirror"]` |

If you only have one camera (index 0), leave indices at `0`/`1`; the app will use the webcam when a virtual camera isn’t available.

## 2. One-time setup

```bash
cd /Applications/face-live
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Start the call UI

```bash
cd /Applications/face-live
source .venv/bin/activate
python run.py --ui
```

- Main view shows **Webcam** by default. Use the **Source** button to cycle: Webcam → DeepFaceLive → Avatarify.
- If a virtual camera isn’t available, DeepFaceLive/Avatarify will fall back to the webcam (label shows “(webcam)”).

## 4. Optional: list cameras

To see which camera indices you have (e.g. after starting OBS Virtual Camera):

```bash
source .venv/bin/activate
python list_cameras.py
```

Then set `deepfacelive_camera_index` or `avatarify_camera_index` in `config.json` to the index you want.

## 5. Avatarify custom photo (live driven by main camera)

In the **Camera** panel, open **Avatarify — custom photo**:

1. Click **Upload custom photo** and choose a face image (jpg/png). It is saved to `workspace/avatarify_custom/avatar.*`.
2. The text **Custom: avatar.jpg** (or similar) confirms the upload. Use **Clear custom photo** to remove it.
3. When you start Avatarify (e.g. `python run.py --ui --with-avatarify`), that photo is used as the **only** avatar and is **driven by your main camera**: your webcam controls the face in the photo in real time.
4. Capture the Avatarify window with OBS Virtual Camera, then in the UI choose **Source: Avatarify** to see the animated custom photo in the call.

## 6. Optional: start with Avatarify or DeepFaceLive

- **With Avatarify** (Avatarify window + OBS to capture it):
  ```bash
  python run.py --ui --with-avatarify
  ```
- **With DeepFaceLive** (if DeepFaceLive is set up):
  ```bash
  python run.py --ui --with-deepfacelive
  ```

## 7. Quick reference

| Goal | Command |
|------|--------|
| Run call UI (webcam) | `python run.py --ui` |
| Run UI + start Avatarify in background | `python run.py --ui --with-avatarify` |
| Run UI + start DeepFaceLive in background | `python run.py --ui --with-deepfacelive` |
| List camera indices | `python list_cameras.py` |
| Run Avatarify only (no UI) | `python run.py --config avatarify.yaml` |
