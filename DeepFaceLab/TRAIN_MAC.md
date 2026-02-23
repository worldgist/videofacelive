# Train a face model on macOS (DeepFaceLab)

Training is **CPU-only** on Mac and will be slow. For faster training use **Google Colab** or a Windows machine with GPU.

## 1. Environment

Use a Python env that has DeepFaceLab dependencies (TensorFlow, etc.). Either the project’s `.venv` (if you installed `DeepFaceLab/requirements-mac.txt` there) or a dedicated `DeepFaceLab_venv`:

```bash
# Option A: project venv (from project root)
source /Applications/face-live/.venv/bin/activate
# Option B: dedicated DeepFaceLab venv (if you created it)
# source /Applications/face-live/DeepFaceLab_venv/bin/activate
cd /Applications/face-live/DeepFaceLab
```

From project root you can also run training without changing directory: `python run.py --train` (see [TRAINING.md](../TRAINING.md)).

## 2. Prepare data

- **SRC** = face you want to put on the video (e.g. your face or a celebrity).
- **DST** = face in the target video (the person to replace).

You need:
- **SRC**: Many images (or a video) of the source face (different angles, lighting). ~500+ images recommended.
- **DST**: Frames (or video) of the destination video.

### Extract frames from a video (optional)

```bash
python main.py videoed extract-video \
  --input-file /path/to/video.mp4 \
  --output-dir /path/to/dst_frames \
  --fps 1
```

### Extract faces from images/frames

**Source faces (SRC):**
```bash
python main.py extract \
  --input-dir /path/to/src_images \
  --output-dir /path/to/workspace/src_faces \
  --detector s3fd \
  --cpu-only
```

**Destination faces (DST):**
```bash
python main.py extract \
  --input-dir /path/to/dst_frames \
  --output-dir /path/to/workspace/dst_faces \
  --detector s3fd \
  --cpu-only
```

### Sort faces (recommended)

```bash
python main.py sort --input-dir /path/to/workspace/src_faces --by hist
python main.py sort --input-dir /path/to/workspace/dst_faces --by hist
```

Remove bad/aligned images from the `*_faces` folders if needed.

## 3. Train

**Available models:** `Model_Quick96`, `Model_SAEHD`, `Model_AMP`, `Model_XSeg` (XSeg is for masks, not full face swap).

- **Model_Quick96** – faster, lower resolution, good for testing.
- **Model_SAEHD** – higher quality, slower.

```bash
python main.py train \
  --training-data-src-dir /path/to/workspace/src_faces \
  --training-data-dst-dir /path/to/workspace/dst_faces \
  --model-dir /path/to/workspace/model \
  --model Model_SAEHD \
  --cpu-only
```

Use `Model_Quick96` instead of `Model_SAEHD` for quicker runs. Training can take hours/days on CPU; you can stop with Ctrl+C and resume later (same `--model-dir` and `--model`).

## 4. Merge (apply the model to video)

After training, extract faces from your **destination video** (if not done already), then merge:

```bash
python main.py merge \
  --input-dir /path/to/dst_frames \
  --output-dir /path/to/workspace/merged \
  --model-dir /path/to/workspace/model \
  --model Model_SAEHD \
  --cpu-only
```

Then combine merged frames into a video with ffmpeg or the DeepFaceLab videoed tools.

## 5. Export for DeepFaceLive (optional)

Export the trained model to a `.dfm` file for real-time use in DeepFaceLive:

```bash
python main.py exportdfm \
  --model-dir /Applications/face-live/workspace/model \
  --model Model_SAEHD
```

This writes a `.dfm` file into `workspace/model/`. DeepFaceLive expects DFM models in **`workspace/dfm_models/`**. Copy the exported file(s) there:

```bash
cp /Applications/face-live/workspace/model/*.dfm /Applications/face-live/workspace/dfm_models/
```

Or run the helper script (from project root): `./workspace/copy_dfm_to_deepfacelive.sh`

Then run DeepFaceLive (it uses `workspace` as userdata and loads `workspace/dfm_models/*.dfm`):

```bash
/Applications/face-live/DeepFaceLive_macOS/run_deepfacelive_mac.sh
```

---

**Quick test (minimal data):** Create small folders with a few dozen face images each for SRC and DST, run extract → sort → train with `Model_Quick96` and `--model-dir ./test_model` to verify the pipeline.
