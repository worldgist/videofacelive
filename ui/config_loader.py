"""
Load and save UI/video configuration (config.json in project root).
Keeps video source and camera indices separate from UI layout.
"""
import json
import os

CONFIG_FILENAME = "config.json"

# Source type constants
SOURCE_WEBCAM = "webcam"
SOURCE_DEEPFACELIVE = "deepfacelive"
SOURCE_AVATARIFY = "avatarify"

# Participant panel source: mirror, camera, deepfacelive, avatarify (virtual cameras), remote = placeholder
PARTICIPANT_SOURCE_MIRROR = "mirror"
PARTICIPANT_SOURCE_CAMERA = "camera"
PARTICIPANT_SOURCE_DEEPFACELIVE = "deepfacelive"
PARTICIPANT_SOURCE_AVATARIFY = "avatarify"
PARTICIPANT_SOURCE_REMOTE = "remote"
VALID_PARTICIPANT_SOURCES = (PARTICIPANT_SOURCE_MIRROR, PARTICIPANT_SOURCE_CAMERA, PARTICIPANT_SOURCE_DEEPFACELIVE, PARTICIPANT_SOURCE_AVATARIFY, PARTICIPANT_SOURCE_REMOTE)

DEFAULT_CONFIG = {
    "video_source": SOURCE_WEBCAM,
    "camera_index": 0,
    "webcam_index": 0,
    "deepfacelive_camera_index": 1,
    "avatarify_camera_index": 1,
    "custom_avatar_path": "",
    "participant_sources": [PARTICIPANT_SOURCE_MIRROR, PARTICIPANT_SOURCE_MIRROR],
    "participant_camera_index": 1,
}


def get_config_path(project_root: str) -> str:
    """Return path to config.json inside project root."""
    return os.path.join(project_root, CONFIG_FILENAME)


def load_config(project_root: str) -> dict:
    """
    Load config from project root config.json.
    Returns dict with video_source, camera_index, webcam_index, deepfacelive_camera_index.
    Missing keys are filled from DEFAULT_CONFIG.
    """
    path = get_config_path(project_root)
    out = dict(DEFAULT_CONFIG)
    if not os.path.isfile(path):
        return out
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in DEFAULT_CONFIG:
            if key in data:
                out[key] = data[key]
    except (json.JSONDecodeError, OSError):
        pass
    return out


def save_config(project_root: str, config: dict) -> None:
    """Write config to project root config.json. Only known keys are written."""
    path = get_config_path(project_root)
    to_write = {k: config.get(k, v) for k, v in DEFAULT_CONFIG.items()}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(to_write, f, indent=2)
    except OSError:
        pass


def get_participant_sources(config: dict) -> list:
    """Return list of participant source types (mirror, camera, deepfacelive, remote). Length 2 for Participant 1 and 2."""
    raw = config.get("participant_sources")
    if isinstance(raw, list) and len(raw) >= 2:
        return [
            str(raw[0]) if raw[0] in VALID_PARTICIPANT_SOURCES else PARTICIPANT_SOURCE_MIRROR,
            str(raw[1]) if raw[1] in VALID_PARTICIPANT_SOURCES else PARTICIPANT_SOURCE_MIRROR,
        ]
    return [PARTICIPANT_SOURCE_MIRROR, PARTICIPANT_SOURCE_MIRROR]


def get_current_camera_index(config: dict) -> int:
    """Return the camera index that should be used for the current video_source."""
    if config.get("video_source") == SOURCE_DEEPFACELIVE:
        return config.get("deepfacelive_camera_index", DEFAULT_CONFIG["deepfacelive_camera_index"])
    if config.get("video_source") == SOURCE_AVATARIFY:
        return config.get("avatarify_camera_index", DEFAULT_CONFIG["avatarify_camera_index"])
    return config.get("webcam_index", DEFAULT_CONFIG["webcam_index"])
