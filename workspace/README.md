# Workspace layout

| Folder | Purpose |
|--------|---------|
| `src_images/` | **Input:** Put raw SRC images here (e.g. celebrity photos). Then run: `python run.py --extract-src --input-dir workspace/src_images` |
| `dst_images/` | **Input:** Put raw DST images here (e.g. your photos). Then run: `python run.py --extract-dst --input-dir workspace/dst_images` |
| `src_faces/` | **Output of extract:** Extracted SRC faces. Do not edit by hand except to delete bad crops. |
| `dst_faces/` | **Output of extract:** Extracted DST faces. Do not edit by hand except to delete bad crops. |
| `model/` | **Output of train:** Trained model and, after export, `.dfm` files. |
| `dfm_models/` | **For DeepFaceLive:** Copy or export `.dfm` here. DeepFaceLive loads models from this folder. |
| `avatarify_custom/` | **For Avatarify:** Custom photo upload from the call UI is saved here. |

**Run the pipeline (from project root):**

```bash
# 1. Extract + sort (after putting images in src_images/ and dst_images/)
./run_pipeline.sh

# 2. Train (then optionally remove bad faces in src_faces/ and dst_faces/)
./run_pipeline.sh train

# 3. Export to DeepFaceLive
python run.py --train --export-only
```

Or in one go (extract + sort + train + export): `./run_pipeline.sh train export`

See **TRAINING.md** and **TRAIN_CELEBRITY.md** for details.
