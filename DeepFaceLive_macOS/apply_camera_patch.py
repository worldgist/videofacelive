#!/usr/bin/env python3
"""Apply macOS camera patch to DeepFaceLive CameraSource.py. Usage: python apply_camera_patch.py <path_to_CameraSource.py>"""
import sys

path = sys.argv[1] if len(sys.argv) > 1 else None
if not path:
    sys.exit(1)

with open(path) as f:
    content = f.read()

old = """            cv_api = {_DriverType.COMPATIBLE: cv2.CAP_ANY,
                      _DriverType.DSHOW: cv2.CAP_DSHOW,
                      _DriverType.MSMF: cv2.CAP_MSMF,
                      _DriverType.GSTREAMER: cv2.CAP_GSTREAMER,
                      }[state.driver]"""

new = """            if platform.system() == 'Darwin':
                cv_api = cv2.CAP_ANY
            else:
                cv_api = {_DriverType.COMPATIBLE: cv2.CAP_ANY,
                          _DriverType.DSHOW: cv2.CAP_DSHOW,
                          _DriverType.MSMF: cv2.CAP_MSMF,
                          _DriverType.GSTREAMER: cv2.CAP_GSTREAMER,
                          }[state.driver]"""

if "platform.system() == 'Darwin'" in content and "cv_api = cv2.CAP_ANY" in content:
    print("  CameraSource.py already patched.")
    sys.exit(0)
if old in content:
    content = content.replace(old, new, 1)
    with open(path, "w") as f:
        f.write(content)
    print("  Patched CameraSource.py for macOS.")
    sys.exit(0)
print("  CameraSource.py: block not found (different version?).")
sys.exit(0)
