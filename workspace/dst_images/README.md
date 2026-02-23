# DST images (destination / driver face)

Put **raw images** of **your** face (the person in front of the camera who will “drive” the SRC face).

- **placeholder.png** is a minimal 1×1 pixel image so the folder is not empty. **Replace it** with your real DST face images (500+ recommended).
- Use 500+ images: same variety (angles, talk, smile, laugh).
- Supported: `.jpg`, `.jpeg`, `.png` (and frames from video).

Then from project root:

```bash
python run.py --extract-dst --input-dir workspace/dst_images
```

This fills `workspace/dst_faces/`. See **TRAIN_CELEBRITY.md**.
