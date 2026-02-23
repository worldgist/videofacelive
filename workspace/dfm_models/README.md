# DFM models (DeepFaceLive)

Put `.dfm` model files here. DeepFaceLive loads them when started with:

```bash
--userdata-dir /Applications/face-live/workspace
```

After training, export with:

```bash
python run.py --train --export-only
```

That copies the exported `.dfm` into this folder automatically.
