# Train a celebrity face (e.g. Elon Musk) for DeepFaceLive

This guide trains a model so **your face drives the celebrity’s face** in real time: when you talk, smile, laugh, or move, the stream shows the celebrity (e.g. Elon Musk) doing the same. Training is done in **DeepFaceLab**; the exported model is used in **DeepFaceLive**.

---

## Roles

| Role | Who | Purpose |
|------|-----|--------|
| **SRC** | Celebrity (e.g. Elon Musk) | The face that will **appear** in the stream (talk, smile, laugh, expressions). |
| **DST** | You | The face that will be **replaced**. Your movements and expressions drive the SRC face. |

You need many images of **both** faces, with a variety of angles, expressions (talk, smile, laugh, neutral), and lighting.

---

## 1. Gather images

### SRC (celebrity – e.g. Elon Musk)

- **Goal:** 500+ aligned face images: talking, smiling, laughing, different angles.
- **Options:**
  - **Photos:** High‑resolution front-facing photos (press, interviews, social). Mix expressions and angles.
  - **Video:** Extract frames from interviews or public videos to get natural talking/smiling/laughing. Use DeepFaceLab to extract frames first (see below).
- **Where to put them:** e.g. `workspace/src_images/` (any folder you like).

**Extract frames from a video (optional, for more expressions):**

```bash
cd /Applications/face-live/DeepFaceLab
source /Applications/face-live/DeepFaceLab_venv/bin/activate
python main.py videoed extract-video --input-file /path/to/celebrity_video.mp4 --output-dir /path/to/workspace/src_frames --fps 1
```

Then use the frames folder as `--input-dir` for `--extract-src` below.

### DST (you – the driver)

- **Goal:** 500+ images of **your** face: same variety (talk, smile, laugh, angles).
- **Options:** Selfies, webcam recordings, or extract frames from a short video of yourself talking/smiling.
- **Where to put them:** e.g. `workspace/dst_images/`.

You are responsible for obtaining all images and videos in a way that respects copyright and privacy.

---

## 2. Extract faces (DeepFaceLab)

From **project root**, with the DeepFaceLab venv activated:

```bash
cd /Applications/face-live
source DeepFaceLab_venv/bin/activate

# SRC = celebrity face (e.g. Elon Musk) -> will APPEAR in stream
python run.py --extract-src --input-dir workspace/src_images

# DST = your face -> will be REPLACED (you drive the celebrity)
python run.py --extract-dst --input-dir workspace/dst_images
```

If you used video frames, use that folder instead of `workspace/src_images` or `workspace/dst_images`.

---

## 3. Sort and clean

```bash
python run.py --sort-faces
```

Then open `workspace/src_faces` and `workspace/dst_faces` and **delete** bad crops (wrong face, blur, duplicates). More good faces = better model.

---

## 4. Train

```bash
python run.py --train
```

- **Model_SAEHD** (default): better quality, slower. Good for a final “Elon Musk” style model.
- **Quick test:** `python run.py --train --quick` (Model_Quick96) to check the pipeline faster.

Training on Mac is CPU-only and can take a long time. You can stop with **Ctrl+C** and resume later with the same command (same `workspace/model`).

---

## 5. Export to DeepFaceLive

When training looks good (preview in the training window):

```bash
python run.py --train --export-only
```

This creates a `.dfm` and copies it to `workspace/dfm_models/`. DeepFaceLive loads models from there.

---

## 6. Use in DeepFaceLive (talk, smile, laugh, etc.)

1. **Start DeepFaceLive** with the shared workspace (so it sees your `.dfm`):
   ```bash
   /Applications/face-live/DeepFaceLive_macOS/run_deepfacelive_mac.sh
   ```
   Or: `python main.py run DeepFaceLive --no-cuda --userdata-dir /Applications/face-live/workspace` from the `DeepFaceLive` directory.

2. In **DeepFaceLive**: select your **camera** (webcam) and the **model** you exported (e.g. the one trained on Elon Musk).

3. Your face now **drives** the celebrity face: when you talk, smile, laugh, or move, the stream shows the SRC face (e.g. Elon Musk) doing the same.

4. **Virtual camera:** Use OBS (or similar) to capture the DeepFaceLive window and start a virtual camera. Then in the call UI choose **Source: DeepFaceLive** to use it in calls/streaming.

---

## Commands summary (copy-paste)

Replace `workspace/src_images` and `workspace/dst_images` with your actual folders (or use full paths).

```bash
cd /Applications/face-live
source DeepFaceLab_venv/bin/activate

# 1. Extract SRC (celebrity) and DST (you)
python run.py --extract-src --input-dir workspace/src_images
python run.py --extract-dst --input-dir workspace/dst_images

# 2. Sort and then remove bad faces in workspace/src_faces and workspace/dst_faces
python run.py --sort-faces

# 3. Train (Ctrl+C to stop; run again to resume)
python run.py --train

# 4. Export for DeepFaceLive
python run.py --train --export-only
```

After step 4, open DeepFaceLive, load the model from `workspace/dfm_models/`, and your webcam will drive the celebrity face so it can talk, smile, laugh, and mirror your expressions.
