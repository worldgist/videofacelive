# SRC images (source face)

Put **raw images** of the face that will **appear** in the stream (e.g. celebrity – Elon Musk).

- **elonmusk.png** is the SRC face image (celebrity) used for this project. Keep it; add more SRC images (different angles, expressions) for better training—500+ recommended.
- **placeholder.png** is a 1×1 pixel placeholder; you can delete it.
- Use 500+ images: different angles, expressions (talk, smile, laugh), lighting.
- Supported: `.jpg`, `.jpeg`, `.png` (and frames if you extracted from video).

Then from project root:

```bash
python run.py --extract-src --input-dir workspace/src_images
```

This fills `workspace/src_faces/`. See **TRAIN_CELEBRITY.md**.
