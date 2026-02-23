# Train DeepFaceLive (face model)

Face models used by **DeepFaceLive** are trained with **DeepFaceLab**. Training produces a `.dfm` model that you load in DeepFaceLive for real-time face swap.

## Quick start (from project root)

1. **Prepare data** (one-time)
   - **SRC**: Many images of the face to put on camera (e.g. a celebrity or yourself). Different angles, lighting, expressions. 500+ recommended.
   - **DST**: Many images of the face to replace (e.g. yourself for live streaming). Same variety.

   Put raw images in folders, then extract and sort faces with DeepFaceLab (see [DeepFaceLab/TRAIN_MAC.md](DeepFaceLab/TRAIN_MAC.md)).

2. **Extract and sort faces** (from project root). `run.py` uses **DeepFaceLab_venv** for extract/train/export when present; create it and install deps once.

   DeepFaceLab needs **Python 3.8 or 3.9**. If you don’t have `python3.9`:

   - **Option A** — Use your current Python if it’s 3.8 or 3.9: `python3 --version`, then:
     ```bash
     cd /Applications/face-live
     python3 -m venv DeepFaceLab_venv
     source DeepFaceLab_venv/bin/activate
     pip install -r DeepFaceLab/requirements-mac.txt
     ```
   - **Option B** — Install Python 3.9 (e.g. Homebrew), then create the venv:
     ```bash
     brew install python@3.9
     cd /Applications/face-live
     $(brew --prefix python@3.9)/bin/python3.9 -m venv DeepFaceLab_venv
     source DeepFaceLab_venv/bin/activate
     pip install -r DeepFaceLab/requirements-mac.txt
     ```
   - If **h5py** fails to build (e.g. `ModuleNotFoundError: No module named 'Cython'`), pip’s isolated build env doesn’t see Cython. Install h5py without build isolation, then re-run the requirements:
     ```bash
     pip install --no-build-isolation h5py>=2.10,<3
     pip install -r DeepFaceLab/requirements-mac.txt
     ```

   Then from project root (any venv is fine; run.py will use DeepFaceLab_venv for DeepFaceLab):

   ```bash
   cd /Applications/face-live
   source DeepFaceLab_venv/bin/activate   # or: source .venv/bin/activate

   # Extract SRC (face to put on camera) -> workspace/src_faces
   python run.py --extract-src --input-dir /path/to/src_images

   # Extract DST (face to replace) -> workspace/dst_faces
   python run.py --extract-dst --input-dir /path/to/dst_images

   # Sort both facesets (by hist)
   python run.py --sort-faces
   ```

   Remove bad faces from `workspace/src_faces` and `workspace/dst_faces` if needed.

3. **Train** (from project root; use the venv that has DeepFaceLab deps, e.g. `DeepFaceLab_venv` or project `.venv` if you installed DFL there):

   ```bash
   python run.py --train
   ```

   Use `--quick` for a faster, lower-quality run:

   ```bash
   python run.py --train --quick
   ```

   Training is CPU-only on Mac and can take hours or days. You can stop with Ctrl+C and resume later (same `workspace/model`).

4. **Export for DeepFaceLive**

   After training, export the model to `.dfm` and copy it where DeepFaceLive expects it:

   ```bash
   python run.py --train --export-only
   ```

   This runs `exportdfm` and copies `.dfm` into `workspace/dfm_models/`. DeepFaceLive (when started with `--userdata-dir workspace`) loads models from there.

5. **Use in the call UI**

   Start DeepFaceLive, set it to output to a virtual camera, then run the call UI and switch source to DeepFaceLive:

   ```bash
   python run.py --ui --with-deepfacelive
   ```

## Train in Google Colab, then use in DeepFaceLive

Yes. You can **train the model in Google Colab** (GPU) and **export a `.dfm`** to use in DeepFaceLive on your Mac. Colab is much faster than CPU training locally.

1. **Use a DeepFaceLab Colab notebook**  
   For example: [DFL-Colab](https://github.com/chervonij/DFL-Colab) or similar. The official [iperov/DeepFaceLab](https://github.com/iperov/DeepFaceLab) repo also documents `requirements-colab.txt` for Colab. Follow the notebook’s steps to upload data (or use Drive), extract faces, and train (e.g. **Model_SAEHD** or **Model_Quick96**).

2. **Export to `.dfm` in Colab**  
   After training, in the Colab notebook run the same export command (paths will match the notebook’s layout, e.g. a `workspace` or `model` folder):
   ```text
   python main.py exportdfm --model-dir /path/to/your/model_dir --model Model_SAEHD
   ```
   (Use the same `--model` name you trained with, e.g. `Model_Quick96`.) This creates a `.dfm` file in that model directory.

3. **Download the `.dfm`**  
   Download the generated `.dfm` from Colab (e.g. from the Files panel or from Google Drive if the notebook saves it there).

4. **Use it in face-live**  
   Copy the `.dfm` into your local face-live workspace so DeepFaceLive can load it:
   ```bash
   cp /path/to/downloaded/model.dfm /Applications/face-live/workspace/dfm_models/
   ```
   Then start DeepFaceLive with that workspace (e.g. `python run.py --ui --with-deepfacelive`); it loads models from `workspace/dfm_models/`.

**Tip:** If you extract faces locally first (e.g. `run.py --extract-src`, `--extract-dst`, `--sort-faces`), you can zip `workspace/src_faces` and `workspace/dst_faces`, upload to Colab, train there, export `.dfm`, then download and drop it into `workspace/dfm_models/` for DeepFaceLive.

## Workspace layout

| Path | Purpose |
|------|--------|
| `workspace/src_faces/` | Extracted SRC faces (input for training) |
| `workspace/dst_faces/` | Extracted DST faces (input for training) |
| `workspace/model/` | Trained model and exported `.dfm` |
| `workspace/dfm_models/` | DFM files loaded by DeepFaceLive |

## Commands summary

| Command | Description |
|---------|-------------|
| `./run_pipeline.sh` | Extract (workspace/src_images, workspace/dst_images) + sort |
| `./run_pipeline.sh train` | Pipeline + train |
| `./run_pipeline.sh train export` | Pipeline + train + export to dfm_models |
| `python run.py --pipeline` | Same as run_pipeline.sh (extract + sort, default dirs) |
| `python run.py --pipeline --train` | Extract + sort + train |
| `python run.py --extract-src --input-dir <path>` | Extract SRC faces → workspace/src_faces |
| `python run.py --extract-dst --input-dir <path>` | Extract DST faces → workspace/dst_faces |
| `python run.py --sort-faces` | Sort src_faces and dst_faces (by hist) |
| `python run.py --train` | Train model (SRC + DST from workspace) |
| `python run.py --train --quick` | Train with Model_Quick96 (faster) |
| `python run.py --train --export-only` | Export model to .dfm and copy to dfm_models |
| `./workspace/copy_dfm_to_deepfacelive.sh` | Manual copy of .dfm to dfm_models |

## Full pipeline (DeepFaceLab)

For extract/sort/merge and detailed options (pretrained models, SAEHD settings, etc.), see **[DeepFaceLab/TRAIN_MAC.md](DeepFaceLab/TRAIN_MAC.md)**.

For training a **celebrity-style** model so your face drives theirs (talk, smile, laugh) in DeepFaceLive, see **[TRAIN_CELEBRITY.md](TRAIN_CELEBRITY.md)**. More quality tips: **DeepFaceLive/doc/user_faq/user_faq.md** (e.g. “I want to swap my face to a particular celebrity”).
