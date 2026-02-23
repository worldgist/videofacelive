#!/usr/bin/env python3
"""List available camera indices (OpenCV). Run from project root: python list_cameras.py"""
import os
import sys
import platform

try:
    import cv2
except ImportError:
    print("opencv-python required: pip install opencv-python", file=sys.stderr)
    sys.exit(1)

# On macOS, use AVFoundation so virtual cameras (e.g. OBS) are more likely to be detected
backend = cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY

print("Checking camera indices 0–9 (backend={})...".format("AVFoundation" if backend == cv2.CAP_AVFOUNDATION else "default"))
available = []
# Suppress OpenCV "out device of bound" spam when probing indices
devnull = open(os.devnull, "w")
old_stderr = os.dup(2)
os.dup2(devnull.fileno(), 2)
try:
    for i in range(10):
        cap = cv2.VideoCapture(i, backend)
        if cap.isOpened():
            available.append(i)
            cap.release()
finally:
    os.dup2(old_stderr, 2)
    os.close(old_stderr)
    devnull.close()

if not available:
    print("No cameras found. Check permissions (e.g. System Settings → Privacy → Camera).")
else:
    print("Available camera indices:", available)
    print("Set webcam_index / deepfacelive_camera_index in config.json to one of these.")
    if available == [0]:
        print("\nOnly index 0 is available (built-in webcam). For DeepFaceLive:")
        print("  1. Start OBS and add 'Virtual Camera', or run DeepFaceLive with virtual output.")
        print("  2. Run this script again to see the new camera index.")
        print("  3. Set deepfacelive_camera_index in config.json to that index.")
