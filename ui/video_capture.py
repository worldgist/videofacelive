"""
Video capture layer: OpenCV-based source switching (webcam vs DeepFaceLive virtual camera).
Separate from UI so layout and capture logic stay modular.
"""
from __future__ import annotations

import os
import platform
import cv2

from ui.config_loader import (
    SOURCE_WEBCAM,
    SOURCE_DEEPFACELIVE,
    SOURCE_AVATARIFY,
    get_current_camera_index,
)

# On macOS, use AVFoundation so virtual cameras (e.g. OBS) work reliably
def _capture_backend():
    return cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY


def _open_capture_quiet(index: int):
    """Open VideoCapture(index) while suppressing OpenCV stderr (e.g. 'out device of bound')."""
    backend = _capture_backend()
    devnull = open(os.devnull, "w")
    old_stderr = os.dup(2)
    try:
        os.dup2(devnull.fileno(), 2)
        cap = cv2.VideoCapture(index, backend)
        return cap
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)
        devnull.close()


class VideoCaptureManager:
    """
    Manages a single OpenCV VideoCapture with configurable source.
    Call switch_source() to change between webcam and DeepFaceLive (camera index).
    """

    def __init__(self, config: dict):
        """
        config: dict with video_source, webcam_index, deepfacelive_camera_index.
        """
        self._config = dict(config)
        self._capture = None
        self._deepfacelive_fallback = False
        self._current_index = get_current_camera_index(self._config)
        self._open_capture()

    def _open_capture(self) -> bool:
        """Open or reopen capture at _current_index. Returns True if opened."""
        self.release()
        self._capture = _open_capture_quiet(self._current_index)
        return self._capture is not None and self._capture.isOpened()

    def release(self) -> None:
        """Release the current capture."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def read_frame(self):
        """
        Read one frame. Returns (frame as BGR numpy array or None, error_message or None).
        """
        if self._capture is None or not self._capture.isOpened():
            return None, "Camera not open"
        ret, frame = self._capture.read()
        if not ret:
            return None, "Failed to read frame"
        return frame, None

    def switch_source(self, source: str, config: dict):
        """
        Switch to webcam, deepfacelive, or avatarify. config can be updated (camera indices).
        If DeepFaceLive or Avatarify camera index is not available, falls back to webcam so the UI still works.
        Returns (success: bool, error_message: str).
        """
        self._config.update(config)
        self._config.pop("deepfacelive_fallback", None)
        self._config.pop("avatarify_fallback", None)
        if source == SOURCE_DEEPFACELIVE:
            self._current_index = self._config.get("deepfacelive_camera_index", 1)
            self._config["video_source"] = SOURCE_DEEPFACELIVE
        elif source == SOURCE_AVATARIFY:
            self._current_index = self._config.get("avatarify_camera_index", 1)
            self._config["video_source"] = SOURCE_AVATARIFY
        else:
            self._current_index = self._config.get("webcam_index", 0)
            self._config["video_source"] = SOURCE_WEBCAM

        if self._open_capture():
            return True, ""
        # When only webcam is available, use it for DeepFaceLive/Avatarify so the UI is still usable
        if source in (SOURCE_DEEPFACELIVE, SOURCE_AVATARIFY):
            fallback_index = self._config.get("webcam_index", 0)
            self._current_index = fallback_index
            if self._open_capture():
                self._config[f"{source}_fallback"] = True
                return True, ""
        return False, f"Could not open camera index {self._current_index}"

    def get_current_source(self) -> str:
        return self._config.get("video_source", SOURCE_WEBCAM)

    def is_deepfacelive_fallback(self) -> bool:
        """True when Source is DeepFaceLive but we're using webcam because virtual camera wasn't available."""
        return bool(self._config.get("deepfacelive_fallback"))

    def is_avatarify_fallback(self) -> bool:
        """True when Source is Avatarify but we're using webcam because virtual camera wasn't available."""
        return bool(self._config.get("avatarify_fallback"))

    def get_config(self) -> dict:
        return dict(self._config)

    def is_opened(self) -> bool:
        return self._capture is not None and self._capture.isOpened()


class OptionalCameraCapture:
    """
    Optional OpenCV capture for one participant panel (e.g. second camera or DeepFaceLive).
    Use when participant source is 'camera' or 'deepfacelive'. If requested index fails, falls back to 0.
    """

    def __init__(self, camera_index: int, fallback_index: int = 0):
        self._index = camera_index
        self._fallback_index = fallback_index
        self._capture = None
        self._using_fallback = False
        self._open()

    def _open(self) -> bool:
        self.release()
        self._capture = _open_capture_quiet(self._index)
        if self._capture is not None and self._capture.isOpened():
            return True
        self.release()
        self._capture = _open_capture_quiet(self._fallback_index)
        if self._capture is not None and self._capture.isOpened():
            self._using_fallback = True
            return True
        return False

    def read_frame(self):
        """Returns (frame or None, error_message or None)."""
        if self._capture is None or not self._capture.isOpened():
            return None, "Camera not open"
        ret, frame = self._capture.read()
        if not ret:
            return None, "Failed to read frame"
        return frame, None

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def is_opened(self) -> bool:
        return self._capture is not None and self._capture.isOpened()
