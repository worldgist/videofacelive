#!/usr/bin/env python3
"""Run Avatarify, call UI, or train DeepFaceLive face model (via DeepFaceLab).
Usage:
  python run.py --ui [--with-deepfacelive] [--with-avatarify]   # Video call UI
  python run.py --config avatarify.yaml                          # Run Avatarify only (no UI)
  # DeepFaceLab pipeline: extract -> sort -> train -> export
  python run.py --extract-src --input-dir <path>                 # Extract SRC faces -> workspace/src_faces
  python run.py --extract-dst --input-dir <path>                 # Extract DST faces -> workspace/dst_faces
  python run.py --sort-faces                                     # Sort src_faces and dst_faces (by hist)
  python run.py --train [--model Model_SAEHD] [--quick]          # Train model
  python run.py --train --export-only                            # Export to .dfm -> workspace/dfm_models
See TRAINING.md and DeepFaceLab/TRAIN_MAC.md for full steps.
"""
import argparse
import os
import subprocess
import sys


def get_project_root():
    return os.path.dirname(os.path.abspath(__file__))


def _is_image(name):
    n = name.lower()
    return n.endswith(".jpg") or n.endswith(".jpeg") or n.endswith(".png") or n.endswith(".bmp")


def start_deepfacelive(root: str):
    """Start DeepFaceLive in the background. Returns Popen or None if not started."""
    dfl_dir = os.path.join(root, "DeepFaceLive")
    main_py = os.path.join(dfl_dir, "main.py")
    workspace_dir = os.path.join(root, "workspace")
    if not os.path.isfile(main_py):
        print("DeepFaceLive not found. Run without --with-deepfacelive or set up DeepFaceLive.", file=sys.stderr)
        return None
    try:
        proc = subprocess.Popen(
            [sys.executable, "main.py", "run", "DeepFaceLive", "--userdata-dir", workspace_dir],
            cwd=dfl_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("DeepFaceLive started in background. Configure it to output to a virtual camera, then switch source in the UI.")
        return proc
    except OSError as e:
        print(f"Could not start DeepFaceLive: {e}", file=sys.stderr)
        return None


def start_avatarify(root: str, config_path: str = "avatarify.yaml"):
    """Start Avatarify (cam_fomm) in the background. Returns Popen or None if not started."""
    try:
        import yaml
    except ModuleNotFoundError:
        print("PyYAML is required for --with-avatarify. Install with: pip install PyYAML", file=sys.stderr)
        return None
    avadir = os.path.join(root, "avatarify-python")
    if not os.path.isdir(avadir):
        print("avatarify-python not found. Run without --with-avatarify or set up Avatarify.", file=sys.stderr)
        return None
    cfg_path = os.path.join(root, config_path)
    if not os.path.isfile(cfg_path):
        print(f"Config not found: {cfg_path}", file=sys.stderr)
        return None
    try:
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print(f"Could not load {config_path}: {e}", file=sys.stderr)
        return None
    fomm_config = cfg.get("fomm_config", "fomm/config/vox-adv-256.yaml")
    checkpoint = cfg.get("checkpoint", "vox-adv-cpk.pth.tar")
    config_full = os.path.join(avadir, fomm_config)
    ckpt_full = os.path.join(avadir, checkpoint)
    if not os.path.isfile(config_full):
        print(f"FOMM config not found: {config_full}", file=sys.stderr)
        return None
    cmd = [
        sys.executable,
        os.path.join(avadir, "afy", "cam_fomm.py"),
        "--config", config_full,
        "--checkpoint", ckpt_full,
        "--relative", "--adapt_scale", "--no-pad",
    ]
    # Use custom avatar from UI upload if present (single photo driven by main camera)
    custom_avatars_dir = os.path.join(root, "workspace", "avatarify_custom")
    if os.path.isdir(custom_avatars_dir):
        for f in os.listdir(custom_avatars_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                cmd.extend(["--avatars", os.path.abspath(custom_avatars_dir)])
                break
    if cfg.get("is_client"):
        cmd.append("--is-client")
    if cfg.get("connect"):
        cmd.extend(["--connect", str(cfg["connect"])])
    env = os.environ.copy()
    fomm_path = os.path.join(avadir, "fomm")
    env["PYTHONPATH"] = os.pathsep.join([avadir, fomm_path] if os.path.isdir(fomm_path) else [avadir])
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=avadir,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("Avatarify started in background. Capture its window with OBS Virtual Camera, then set avatarify_camera_index in config.json and use Source: Avatarify in the UI.")
        return proc
    except OSError as e:
        print(f"Could not start Avatarify: {e}", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ui", action="store_true", help="Launch Zoom-style video call UI (webcam / DeepFaceLive / Avatarify)")
    ap.add_argument("--with-deepfacelive", action="store_true", help="Start DeepFaceLive in background before launching UI")
    ap.add_argument("--with-avatarify", action="store_true", help="Start Avatarify in background before launching UI (use OBS to capture its window as virtual camera)")
    ap.add_argument("--config", default="avatarify.yaml", help="Path to config YAML (avatarify)")
    ap.add_argument("--is-client", action="store_true", help="Run in client mode (required on Mac)")
    ap.add_argument("--connect", default="", help="Server host for client mode")
    ap.add_argument("--extract-src", action="store_true", help="Extract SRC faces from images into workspace/src_faces (requires --input-dir)")
    ap.add_argument("--extract-dst", action="store_true", help="Extract DST faces from images into workspace/dst_faces (requires --input-dir)")
    ap.add_argument("--input-dir", default=None, help="Input directory for --extract-src or --extract-dst (images or frames)")
    ap.add_argument("--sort-faces", action="store_true", help="Sort workspace/src_faces and workspace/dst_faces by hist")
    ap.add_argument("--train", action="store_true", help="Train face model (DeepFaceLab). Uses workspace/src_faces, workspace/dst_faces, workspace/model.")
    ap.add_argument("--model", default="Model_SAEHD", help="Model for training (Model_SAEHD or Model_Quick96). Default: Model_SAEHD")
    ap.add_argument("--quick", action="store_true", help="Use Model_Quick96 for faster (lower quality) training.")
    ap.add_argument("--export-only", action="store_true", help="Only export existing model to .dfm and copy to workspace/dfm_models (for DeepFaceLive).")
    ap.add_argument("--pipeline", action="store_true", help="Run full pipeline: extract SRC + DST from workspace/src_images and workspace/dst_images, sort, then optionally --train and export. Use with --train to also train; then run again with --train --export-only to export.")
    ap.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args for cam_fomm.py or train")
    args = ap.parse_args()

    root = get_project_root()
    workspace = os.path.join(root, "workspace")
    dfl_dir = os.path.join(root, "DeepFaceLab")
    main_py = os.path.join(dfl_dir, "main.py")
    # Use DeepFaceLab_venv for extract/train/export so deps (numpy, tensorflow, etc.) are correct.
    # Prefer python3.9 when present (DeepFaceLab deps are for 3.8/3.9).
    dfl_venv = os.path.join(root, "DeepFaceLab_venv", "bin")
    dfl_venv_python39 = os.path.join(dfl_venv, "python3.9")
    dfl_venv_python = os.path.join(dfl_venv, "python")
    if os.path.isfile(dfl_venv_python39):
        dfl_python = dfl_venv_python39
    elif os.path.isfile(dfl_venv_python):
        dfl_python = dfl_venv_python
    else:
        dfl_python = sys.executable
        if args.extract_src or args.extract_dst or args.sort_faces or args.train or args.export_only:
            print("Note: DeepFaceLab_venv not found. Using current Python. If you see ModuleNotFoundError, create it (Python 3.8 or 3.9):", file=sys.stderr)
            print("  python3 -m venv DeepFaceLab_venv  # or: $(brew --prefix python@3.9)/bin/python3.9 -m venv DeepFaceLab_venv", file=sys.stderr)
            print("  source DeepFaceLab_venv/bin/activate && pip install -r DeepFaceLab/requirements-mac.txt", file=sys.stderr)

    # --- Full pipeline: extract (default dirs) + sort, optionally train ---
    if args.pipeline:
        src_images = os.path.join(workspace, "src_images")
        dst_images = os.path.join(workspace, "dst_images")
        if not os.path.isfile(main_py):
            print("DeepFaceLab not found.", file=sys.stderr)
            sys.exit(1)
        steps_done = []
        if os.path.isdir(src_images) and any(_is_image(f) for f in os.listdir(src_images)):
            out = os.path.join(workspace, "src_faces")
            os.makedirs(out, exist_ok=True)
            print("[Pipeline] Extracting SRC:", src_images, "->", out)
            rc = subprocess.call(
                [dfl_python, "main.py", "extract", "--input-dir", src_images, "--output-dir", out, "--detector", "s3fd", "--cpu-only"],
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
            steps_done.append("extract-src")
        else:
            print("[Pipeline] Skip extract-src (no images in workspace/src_images)", file=sys.stderr)
        if os.path.isdir(dst_images) and any(_is_image(f) for f in os.listdir(dst_images)):
            out = os.path.join(workspace, "dst_faces")
            os.makedirs(out, exist_ok=True)
            print("[Pipeline] Extracting DST:", dst_images, "->", out)
            rc = subprocess.call(
                [dfl_python, "main.py", "extract", "--input-dir", dst_images, "--output-dir", out, "--detector", "s3fd", "--cpu-only"],
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
            steps_done.append("extract-dst")
        else:
            print("[Pipeline] Skip extract-dst (no images in workspace/dst_images)", file=sys.stderr)
        src_faces = os.path.join(workspace, "src_faces")
        dst_faces = os.path.join(workspace, "dst_faces")
        if os.path.isdir(src_faces) or os.path.isdir(dst_faces):
            for label, path in [("SRC", src_faces), ("DST", dst_faces)]:
                if os.path.isdir(path):
                    print("[Pipeline] Sorting", label, path)
                    rc = subprocess.call(
                        [dfl_python, "main.py", "sort", "--input-dir", path, "--by", "hist"],
                        cwd=dfl_dir,
                    )
                    if rc != 0:
                        sys.exit(rc)
            steps_done.append("sort")
        if args.train:
            model_dir = os.path.join(workspace, "model")
            model_name = "Model_Quick96" if args.quick else args.model
            if not os.path.isdir(src_faces) or not os.path.isdir(dst_faces):
                print("Pipeline: no src_faces or dst_faces. Put images in workspace/src_images and workspace/dst_images, then run --pipeline again.", file=sys.stderr)
                sys.exit(1)
            print("[Pipeline] Training (model:", model_name, ")")
            rc = subprocess.call(
                [
                    dfl_python, "main.py", "train",
                    "--training-data-src-dir", src_faces,
                    "--training-data-dst-dir", dst_faces,
                    "--model-dir", model_dir,
                    "--model", model_name,
                    "--cpu-only",
                ] + args.extra,
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
            steps_done.append("train")
            if args.export_only:
                print("[Pipeline] Exporting to .dfm")
                rc = subprocess.call(
                    [dfl_python, "main.py", "exportdfm", "--model-dir", model_dir, "--model", model_name],
                    cwd=dfl_dir,
                )
                if rc != 0:
                    sys.exit(rc)
                copy_script = os.path.join(workspace, "copy_dfm_to_deepfacelive.sh")
                if os.path.isfile(copy_script):
                    subprocess.call(["bash", copy_script], cwd=root)
                else:
                    os.makedirs(os.path.join(workspace, "dfm_models"), exist_ok=True)
                    import glob
                    for f in glob.glob(os.path.join(model_dir, "*.dfm")):
                        import shutil
                        shutil.copy2(f, os.path.join(workspace, "dfm_models", os.path.basename(f)))
                steps_done.append("export")
        else:
            if steps_done:
                print("Pipeline done:", ", ".join(steps_done))
                print("Next: remove bad faces from workspace/src_faces and workspace/dst_faces if needed, then run:")
                print("  python run.py --pipeline --train")
                print("When training is done, export: python run.py --train --export-only")
        return

    # --- Extract SRC or DST faces (DeepFaceLab) ---
    if args.extract_src or args.extract_dst:
        if not args.input_dir or not os.path.isdir(args.input_dir):
            print("--input-dir <path> required and must be an existing directory.", file=sys.stderr)
            print("Example: python run.py --extract-src --input-dir ./my_src_images", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(main_py):
            print("DeepFaceLab not found.", file=sys.stderr)
            sys.exit(1)
        if args.extract_src:
            out = os.path.join(workspace, "src_faces")
            os.makedirs(out, exist_ok=True)
            print("Extracting SRC faces:", args.input_dir, "->", out)
            rc = subprocess.call(
                [dfl_python, "main.py", "extract", "--input-dir", args.input_dir, "--output-dir", out, "--detector", "s3fd", "--cpu-only"],
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
        if args.extract_dst:
            out = os.path.join(workspace, "dst_faces")
            os.makedirs(out, exist_ok=True)
            print("Extracting DST faces:", args.input_dir, "->", out)
            rc = subprocess.call(
                [dfl_python, "main.py", "extract", "--input-dir", args.input_dir, "--output-dir", out, "--detector", "s3fd", "--cpu-only"],
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
        print("Done. Next: python run.py --sort-faces then remove bad faces if needed.")
        return

    # --- Sort faces ---
    if args.sort_faces:
        if not os.path.isfile(main_py):
            print("DeepFaceLab not found.", file=sys.stderr)
            sys.exit(1)
        src_faces = os.path.join(workspace, "src_faces")
        dst_faces = os.path.join(workspace, "dst_faces")
        for label, path in [("SRC", src_faces), ("DST", dst_faces)]:
            if not os.path.isdir(path):
                print(f"Skipping {label} (not found): {path}", file=sys.stderr)
                continue
            print("Sorting", label, path, "by hist")
            rc = subprocess.call(
                [dfl_python, "main.py", "sort", "--input-dir", path, "--by", "hist"],
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
        print("Done. Remove bad faces from workspace/src_faces and workspace/dst_faces if needed, then: python run.py --train")
        return

    if args.train or args.export_only:
        model_dir = os.path.join(workspace, "model")
        src_faces = os.path.join(workspace, "src_faces")
        dst_faces = os.path.join(workspace, "dst_faces")
        model_name = "Model_Quick96" if args.quick else args.model

        if args.export_only:
            if not os.path.isdir(model_dir):
                print(f"Model dir not found: {model_dir}", file=sys.stderr)
                print("Train first: python run.py --train", file=sys.stderr)
                sys.exit(1)
            rc = subprocess.call(
                [dfl_python, "main.py", "exportdfm", "--model-dir", model_dir, "--model", model_name],
                cwd=dfl_dir,
            )
            if rc != 0:
                sys.exit(rc)
            copy_script = os.path.join(workspace, "copy_dfm_to_deepfacelive.sh")
            if os.path.isfile(copy_script):
                subprocess.call(["bash", copy_script], cwd=root)
            else:
                os.makedirs(os.path.join(workspace, "dfm_models"), exist_ok=True)
                print(f"Copy .dfm from {model_dir} to workspace/dfm_models/ for DeepFaceLive.")
            return

        if not os.path.isfile(main_py):
            print("DeepFaceLab not found.", file=sys.stderr)
            sys.exit(1)
        if not os.path.isdir(src_faces) or not os.path.isdir(dst_faces):
            print("Prepare SRC and DST faces first. See TRAINING.md and DeepFaceLab/TRAIN_MAC.md", file=sys.stderr)
            print("  workspace/src_faces  = extracted source faces", file=sys.stderr)
            print("  workspace/dst_faces  = extracted destination faces", file=sys.stderr)
            print("Example:", file=sys.stderr)
            print("  cd DeepFaceLab && python main.py extract --input-dir <src_images> --output-dir ../workspace/src_faces --detector s3fd --cpu-only", file=sys.stderr)
            sys.exit(1)
        print("Starting training (DeepFaceLab). Workspace:", workspace)
        print("Model:", model_name, "| SRC:", src_faces, "| DST:", dst_faces)
        rc = subprocess.call(
            [
                dfl_python,
                "main.py",
                "train",
                "--training-data-src-dir", src_faces,
                "--training-data-dst-dir", dst_faces,
                "--model-dir", model_dir,
                "--model", model_name,
                "--cpu-only",
            ] + args.extra,
            cwd=dfl_dir,
        )
        if rc == 0:
            print("Training finished. Export for DeepFaceLive: python run.py --train --export-only")
        sys.exit(rc if rc else 0)

    if args.ui:
        ui_script = os.path.join(root, "ui", "call_ui.py")
        if not os.path.isfile(ui_script):
            print(f"Call UI not found: {ui_script}", file=sys.stderr)
            sys.exit(1)
        if args.with_deepfacelive:
            start_deepfacelive(root)
        if args.with_avatarify:
            start_avatarify(root)
        # Run UI from project root so "ui" package is importable
        subprocess.run([sys.executable, "ui/call_ui.py"], cwd=root)
        return

    import yaml
    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    avadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatarify-python")
    if not os.path.isdir(avadir):
        print("avatarify-python directory not found", file=sys.stderr)
        sys.exit(1)

    fomm_config = cfg.get("fomm_config", "fomm/config/vox-adv-256.yaml")
    checkpoint = cfg.get("checkpoint", "vox-adv-cpk.pth.tar")
    config_path = os.path.join(avadir, fomm_config)
    ckpt_path = os.path.join(avadir, checkpoint)

    if not os.path.isfile(config_path):
        print(f"FOMM config not found: {config_path}", file=sys.stderr)
        print("Ensure the fomm submodule and model config are set up (see avatarify-python README).", file=sys.stderr)
        sys.exit(1)

    cmd = [
        sys.executable,
        os.path.join(avadir, "afy", "cam_fomm.py"),
        "--config", config_path,
        "--checkpoint", ckpt_path,
        "--relative", "--adapt_scale", "--no-pad",
    ]
    if args.is_client or cfg.get("is_client"):
        cmd.append("--is-client")
    if args.connect or cfg.get("connect"):
        cmd.extend(["--connect", args.connect or str(cfg.get("connect", ""))])
    smooth = cfg.get("smooth", 0)
    if smooth:
        cmd.extend(["--smooth", str(smooth)])
    input_smooth = cfg.get("input_smooth", 0)
    if input_smooth:
        cmd.extend(["--input-smooth", str(input_smooth)])
    cmd.extend(args.extra)

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([avadir, os.path.join(avadir, "fomm")] if os.path.isdir(os.path.join(avadir, "fomm")) else [avadir])
    subprocess.run(cmd, cwd=avadir, env=env)

if __name__ == "__main__":
    main()
