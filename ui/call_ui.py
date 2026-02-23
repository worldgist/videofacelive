#!/usr/bin/env python3
"""
Simulated video call UI for FACE-LIVE.

Architecture:
- One real camera feed (the user's webcam) is the primary video source.
- That feed can be shown raw (Webcam) or after face processing (DeepFaceLive):
  DeepFaceLive transforms the user's face and movements into another appearance in
  real time (expressions, speech, head movements drive the replacement face).
- The same stream is sent to all participant panels: main view + Participant 1 + 2.
- Use cases: single-user call testing, avatar/face-swap streaming, UI development.
- Later, mirrored participant panels can be replaced with real remote users' streams.

Run: python ui/call_ui.py (from project root) or python run.py --ui [--with-deepfacelive]
"""
import os
import sys

# Ensure project root is on path when run as script (e.g. python ui/call_ui.py)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QFrame,
        QPushButton,
        QMessageBox,
        QButtonGroup,
        QGroupBox,
        QSizePolicy,
        QFileDialog,
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QImage, QPixmap
except ImportError:
    print("PyQt5 is required for the UI. Install with: pip install PyQt5 PyYAML", file=sys.stderr)
    sys.exit(1)

import cv2

from ui.config_loader import (
    load_config,
    save_config,
    SOURCE_WEBCAM,
    SOURCE_DEEPFACELIVE,
    SOURCE_AVATARIFY,
    get_participant_sources,
    PARTICIPANT_SOURCE_MIRROR,
    PARTICIPANT_SOURCE_CAMERA,
    PARTICIPANT_SOURCE_DEEPFACELIVE,
    PARTICIPANT_SOURCE_AVATARIFY,
    PARTICIPANT_SOURCE_REMOTE,
)
from ui.video_capture import VideoCaptureManager, OptionalCameraCapture


def _project_root():
    """Project root (parent of ui/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --- Dark theme styles ---
DARK_STYLESHEET = """
    QMainWindow, QWidget {
        background-color: #1a1a2e;
    }
    QLabel {
        color: #eaeaea;
        font-size: 14px;
    }
    QLabel#participantLabel {
        font-size: 12px;
        color: #a0a0a0;
    }
    QFrame#videoFrame {
        background-color: #16213e;
        border: 1px solid #0f3460;
        border-radius: 8px;
    }
    QFrame#controlFrame {
        background-color: #0f3460;
        border-radius: 12px;
        padding: 8px;
    }
    QPushButton {
        background-color: #1a1a2e;
        color: #eaeaea;
        border: 1px solid #0f3460;
        border-radius: 24px;
        min-width: 48px;
        min-height: 48px;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #16213e;
        border-color: #e94560;
    }
    QPushButton:pressed {
        background-color: #0f3460;
    }
    QPushButton#endCallButton {
        background-color: #c1121f;
        color: white;
        border-color: #9d0208;
    }
    QPushButton#endCallButton:hover {
        background-color: #9d0208;
    }
    QPushButton:disabled {
        background-color: #2a2a4a;
        color: #666;
    }
    QFrame#cameraPanel {
        background-color: #16213e;
        border: 1px solid #0f3460;
        border-radius: 8px;
        padding: 10px;
    }
    QGroupBox {
        font-size: 13px;
        font-weight: bold;
        color: #eaeaea;
        border: 1px solid #0f3460;
        border-radius: 6px;
        margin-top: 8px;
        padding-top: 8px;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
        color: #e94560;
    }
    QPushButton#sourceBtn {
        min-height: 36px;
        font-size: 12px;
        border-radius: 6px;
    }
    QPushButton#sourceBtn:checked {
        background-color: #0f3460;
        border-color: #e94560;
        color: #fff;
    }
    QLabel#cameraStatus {
        font-size: 11px;
        color: #a0a0a0;
        padding: 4px 0;
    }
"""


class CameraControlPanel(QFrame):
    """
    Panel to control camera access: primary source (Webcam / DeepFaceLive / Avatarify),
    status, and camera on/off for the main feed.
    """

    def __init__(self, capture_manager, config, project_root, parent=None):
        super().__init__(parent)
        self.setObjectName("cameraPanel")
        self._capture_manager = capture_manager
        self._config = dict(config)
        self._project_root = project_root
        self._custom_avatar_path = self._config.get("custom_avatar_path", "") or ""
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # --- Avatarify: upload custom photo (first so it's easy to find) ---
        avatarify_group = QGroupBox("Upload photo for Avatarify")
        ag_layout = QVBoxLayout(avatarify_group)
        ag_layout.setSpacing(6)
        hint = QLabel("Your photo becomes the avatar. The main camera drives it in real time when you choose Source: Avatarify.")
        hint.setObjectName("cameraStatus")
        hint.setWordWrap(True)
        ag_layout.addWidget(hint)
        self._upload_avatar_btn = QPushButton("📤 Upload custom photo")
        self._upload_avatar_btn.setObjectName("sourceBtn")
        self._upload_avatar_btn.setMinimumHeight(40)
        self._upload_avatar_btn.setToolTip("Choose a face photo (jpg/png); it will be animated by your webcam")
        self._upload_avatar_btn.clicked.connect(self._on_upload_custom_photo)
        ag_layout.addWidget(self._upload_avatar_btn)
        self._custom_avatar_label = QLabel("No custom photo")
        self._custom_avatar_label.setObjectName("cameraStatus")
        ag_layout.addWidget(self._custom_avatar_label)
        # Thumbnail preview so the uploaded photo is visible
        self._avatar_preview = QLabel()
        self._avatar_preview.setAlignment(Qt.AlignCenter)
        self._avatar_preview.setMinimumSize(120, 120)
        self._avatar_preview.setMaximumHeight(140)
        self._avatar_preview.setStyleSheet("background-color: #0f3460; border-radius: 6px; padding: 4px;")
        self._avatar_preview.setText("No photo")
        ag_layout.addWidget(self._avatar_preview)
        self._clear_avatar_btn = QPushButton("Clear custom photo")
        self._clear_avatar_btn.setObjectName("sourceBtn")
        self._clear_avatar_btn.setToolTip("Remove the custom avatar photo")
        self._clear_avatar_btn.clicked.connect(self._on_clear_custom_photo)
        ag_layout.addWidget(self._clear_avatar_btn)
        layout.addWidget(avatarify_group)

        # --- Camera: source and on/off ---
        group = QGroupBox("Camera")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(6)

        # Source selection: Webcam | DeepFaceLive | Avatarify
        source_row = QHBoxLayout()
        source_row.setSpacing(6)
        self._source_buttons = {}
        self._button_group = QButtonGroup(self)
        for key, label in [
            (SOURCE_WEBCAM, "Webcam"),
            (SOURCE_DEEPFACELIVE, "DeepFaceLive"),
            (SOURCE_AVATARIFY, "Avatarify"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("sourceBtn")
            btn.setCheckable(True)
            btn.setToolTip(f"Use {label} as main video source")
            self._button_group.addButton(btn)
            self._source_buttons[key] = btn
            source_row.addWidget(btn)
        self._button_group.buttonClicked.connect(self._on_source_button_clicked)
        group_layout.addLayout(source_row)

        # Status: active source and index or fallback
        self._status_label = QLabel()
        self._status_label.setObjectName("cameraStatus")
        self._status_label.setWordWrap(True)
        group_layout.addWidget(self._status_label)

        # Camera on/off (main feed)
        self._camera_off_btn = QPushButton("📷 Camera on")
        self._camera_off_btn.setObjectName("sourceBtn")
        self._camera_off_btn.setCheckable(True)
        self._camera_off_btn.setChecked(False)
        self._camera_off_btn.setToolTip("Turn main camera feed on or off")
        group_layout.addWidget(self._camera_off_btn)

        layout.addWidget(group)

        # --- DeepFaceLive: same custom photo (display when uploaded for Avatarify) ---
        dfl_group = QGroupBox("DeepFaceLive — custom photo")
        dfl_layout = QVBoxLayout(dfl_group)
        dfl_layout.setSpacing(6)
        dfl_hint = QLabel("Same photo as Avatarify. Use Source: DeepFaceLive to see face-swap output (needs virtual camera).")
        dfl_hint.setObjectName("cameraStatus")
        dfl_hint.setWordWrap(True)
        dfl_layout.addWidget(dfl_hint)
        self._dfl_photo_preview = QLabel()
        self._dfl_photo_preview.setAlignment(Qt.AlignCenter)
        self._dfl_photo_preview.setMinimumSize(120, 120)
        self._dfl_photo_preview.setMaximumHeight(140)
        self._dfl_photo_preview.setStyleSheet("background-color: #0f3460; border-radius: 6px; padding: 4px;")
        self._dfl_photo_preview.setText("No photo — upload above")
        dfl_layout.addWidget(self._dfl_photo_preview)
        layout.addWidget(dfl_group)

        layout.addStretch()
        self._update_ui_from_source()
        self._load_custom_avatar_from_folder()
        self._update_custom_avatar_ui()

    def _load_custom_avatar_from_folder(self):
        """If no custom avatar in config or file missing, load from workspace/avatarify_custom/ so preview shows on startup."""
        if self._custom_avatar_path and os.path.isfile(self._custom_avatar_path):
            return
        custom_dir = self._custom_avatar_dir()
        if not os.path.isdir(custom_dir):
            return
        for name in sorted(os.listdir(custom_dir)):
            lower = name.lower()
            if lower.endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(custom_dir, name)
                if os.path.isfile(path):
                    self._custom_avatar_path = path
                    if getattr(self, "_custom_avatar_changed", None):
                        self._custom_avatar_changed(path)
                    return

    def persist_custom_avatar_to_config(self):
        """Call after callbacks are set: if we have a custom avatar path (e.g. loaded from folder), save it to config."""
        if self._custom_avatar_path and getattr(self, "_custom_avatar_changed", None):
            self._custom_avatar_changed(self._custom_avatar_path)

    def set_camera_off_callback(self, callback):
        """Set callback(camera_off: bool) when user toggles camera on/off."""
        self._camera_off_btn.toggled.connect(callback)

    def set_save_config_callback(self, callback):
        """Called after source change so parent can save config."""
        self._save_config = callback

    def set_custom_avatar_changed_callback(self, callback):
        """Called with (path: str) when custom avatar is uploaded or cleared. Parent should save config."""
        self._custom_avatar_changed = callback

    def _custom_avatar_dir(self):
        return os.path.join(self._project_root, "workspace", "avatarify_custom")

    def _on_upload_custom_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose a face photo for Avatarify",
            "",
            "Images (*.jpg *.jpeg *.png);;All files (*)",
        )
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            QMessageBox.warning(self, "Invalid file", "Please choose a .jpg, .jpeg, or .png image.")
            return
        dest_dir = self._custom_avatar_dir()
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, "avatar" + ext)
        try:
            import shutil
            shutil.copy2(path, dest_path)
        except OSError as e:
            QMessageBox.warning(self, "Upload failed", f"Could not copy file: {e}")
            return
        self._custom_avatar_path = dest_path
        if getattr(self, "_custom_avatar_changed", None):
            self._custom_avatar_changed(dest_path)
        self._update_custom_avatar_ui()

    def _on_clear_custom_photo(self):
        if self._custom_avatar_path and os.path.isfile(self._custom_avatar_path):
            try:
                os.remove(self._custom_avatar_path)
            except OSError:
                pass
        self._custom_avatar_path = ""
        if getattr(self, "_custom_avatar_changed", None):
            self._custom_avatar_changed("")
        self._update_custom_avatar_ui()

    def _update_custom_avatar_ui(self):
        path = self._custom_avatar_path
        if path and os.path.isfile(path):
            self._custom_avatar_label.setText("Custom: " + os.path.basename(path))
            self._clear_avatar_btn.setEnabled(True)
            # Show thumbnail in Avatarify section and in DeepFaceLive section
            try:
                img = cv2.imread(path)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = img.copy()  # ensure data lives for QImage
                    h, w = img.shape[:2]
                    bytes_per_line = 3 * w
                    qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
                    pixmap = QPixmap.fromImage(qimg)
                    thumb = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self._avatar_preview.setPixmap(thumb)
                    self._avatar_preview.setText("")
                    self._dfl_photo_preview.setPixmap(thumb)
                    self._dfl_photo_preview.setText("")
                else:
                    self._avatar_preview.setPixmap(QPixmap())
                    self._avatar_preview.setText("(preview unavailable)")
                    self._dfl_photo_preview.setPixmap(QPixmap())
                    self._dfl_photo_preview.setText("(preview unavailable)")
            except Exception:
                self._avatar_preview.setPixmap(QPixmap())
                self._avatar_preview.setText("(preview unavailable)")
                self._dfl_photo_preview.setPixmap(QPixmap())
                self._dfl_photo_preview.setText("(preview unavailable)")
        else:
            self._custom_avatar_label.setText("No custom photo")
            self._clear_avatar_btn.setEnabled(False)
            self._avatar_preview.setPixmap(QPixmap())
            self._avatar_preview.setText("No photo")
            self._dfl_photo_preview.setPixmap(QPixmap())
            self._dfl_photo_preview.setText("No photo — upload above")

    def _on_source_button_clicked(self, btn):
        for source, b in self._source_buttons.items():
            if b is btn:
                ok, err = self._capture_manager.switch_source(source, self._config)
                if ok:
                    self._config = self._capture_manager.get_config()
                    if getattr(self, "_save_config", None):
                        self._save_config()
                    self._update_ui_from_source()
                else:
                    QMessageBox.warning(
                        self,
                        "Camera error",
                        f"Could not switch to {source}.\n{err}\n\n"
                        "Run: python list_cameras.py to see available indices, then set config.json.",
                    )
                return

    def _update_ui_from_source(self):
        src = self._capture_manager.get_current_source()
        cfg = self._capture_manager.get_config()
        for source, btn in self._source_buttons.items():
            btn.setChecked(src == source)
        # Status text (use manager config so panel stays in sync when source changes from bar)
        if src == SOURCE_WEBCAM:
            idx = cfg.get("webcam_index", 0)
            self._status_label.setText(f"Active: Webcam (index {idx})")
        elif src == SOURCE_DEEPFACELIVE:
            idx = cfg.get("deepfacelive_camera_index", 1)
            if self._capture_manager.is_deepfacelive_fallback():
                self._status_label.setText(f"DeepFaceLive → webcam fallback (index {idx} not available)")
            else:
                self._status_label.setText(f"Active: DeepFaceLive (index {idx})")
        elif src == SOURCE_AVATARIFY:
            idx = cfg.get("avatarify_camera_index", 1)
            if self._capture_manager.is_avatarify_fallback():
                self._status_label.setText(f"Avatarify → webcam fallback (index {idx} not available)")
            else:
                self._status_label.setText(f"Active: Avatarify (index {idx})")
        else:
            self._status_label.setText("Active: —")

    def update_status(self):
        """Refresh source buttons and status (e.g. after config load)."""
        self._update_ui_from_source()

    def set_camera_off_checked(self, checked):
        """Set the camera on/off button state without emitting signal."""
        self._camera_off_btn.blockSignals(True)
        self._camera_off_btn.setChecked(checked)
        self._camera_off_btn.blockSignals(False)
        self._camera_off_btn.setText("📷 Camera off" if checked else "📷 Camera on")


class VideoWidget(QFrame):
    """
    Displays a single video stream. Supports:
    - Display-only mode (camera_id=None): frames set via set_frame from external capture.
    - Optional internal capture (camera_id set): for backward compat / participant tiles.
    """

    def __init__(self, parent=None, camera_id=None, title="Video", show_placeholder=False):
        super().__init__(parent)
        self.setObjectName("videoFrame")
        self.setFrameStyle(QFrame.StyledPanel)
        self._camera_id = camera_id
        self._base_title = title  # full display title without (muted), e.g. "You — Webcam"
        self._title = title
        self._show_placeholder = show_placeholder or camera_id is None
        self._capture = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("participantLabel")
        self._title_label.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(self._title_label)

        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignCenter)
        self._image_label.setMinimumSize(160, 120)
        self._image_label.setStyleSheet("background-color: #0f3460; border-radius: 4px;")
        self._layout.addWidget(self._image_label, 1)

        if self._camera_id is not None:
            self._capture = cv2.VideoCapture(self._camera_id)
            if not self._capture.isOpened():
                self._capture = None
                self._show_placeholder = True
                self._title_label.setText(f"{title} (no camera)")

        if self._show_placeholder:
            self._image_label.setText("No video")
            self._image_label.setStyleSheet(
                "background-color: #0f3460; color: #666; border-radius: 4px; font-size: 12px;"
            )

        self._camera_paused = False

    def set_camera_paused(self, paused: bool):
        """When True, stop showing camera and display 'Camera off'."""
        self._camera_paused = paused
        if paused:
            self._image_label.setText("Camera off")
            self._image_label.setStyleSheet(
                "background-color: #0f3460; color: #666; border-radius: 4px; font-size: 12px;"
            )
        else:
            self._image_label.setText("")
            self._image_label.setStyleSheet(
                "background-color: #0f3460; border-radius: 4px;"
            )

    def set_source_label(self, source_name: str):
        """Set the subtitle to show current source (e.g. 'Webcam' or 'DeepFaceLive')."""
        base = self._base_title.split(" — ")[0].strip() or self._title
        self._base_title = f"{base} — {source_name}"
        self._title_label.setText(self._base_title)

    def set_muted(self, muted: bool):
        """Update title to show mute state."""
        self._title_label.setText(f"{self._base_title} (muted)" if muted else self._base_title)

    def set_error_message(self, message: str):
        """Show an error state (e.g. camera not found)."""
        self._image_label.setText(message)
        self._image_label.setPixmap(QPixmap())
        self._image_label.setStyleSheet(
                "background-color: #0f3460; color: #e94560; border-radius: 4px; font-size: 12px;"
        )

    def clear_error(self):
        """Clear error/placeholder text so frame can be shown."""
        self._image_label.setText("")
        self._image_label.setStyleSheet(
                "background-color: #0f3460; border-radius: 4px;"
        )

    def read_frame(self):
        """Read one frame from internal camera if any. Returns BGR array or None."""
        if self._camera_paused or self._capture is None or not self._capture.isOpened():
            return None
        ret, frame = self._capture.read()
        return frame if ret else None

    def set_frame(self, frame):
        """Display an OpenCV BGR frame in the widget."""
        if frame is None:
            return
        self.clear_error()
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_format = QImage.Format_RGB888
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qimg = QImage(rgb.data, w, h, bytes_per_line, qt_format)
        pixmap = QPixmap.fromImage(qimg)
        self._image_label.setPixmap(
            pixmap.scaled(
                self._image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

    def release(self):
        """Release internal camera if any."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def closeEvent(self, event):
        self.release()
        super().closeEvent(event)


class CallWindow(QMainWindow):
    """
    Simulated video call window: one primary source drives all panels.

    - Primary source: webcam (index from config) or DeepFaceLive virtual camera.
    - Main panel + Participant 1 + Participant 2 all receive the same frames (mirrored).
    - Source button toggles Webcam vs DeepFaceLive for avatar/face-swap testing.
    - Participant slots are ready to be wired to real remote streams later.
    """

    def __init__(self, project_root=None):
        super().__init__()
        self._project_root = project_root or _project_root()
        self._config = load_config(self._project_root)
        self._capture_manager = VideoCaptureManager(self._config)

        self.setWindowTitle("FACE-LIVE — Video Call")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        content = QHBoxLayout()
        content.setSpacing(12)

        # Right column: Camera control panel + participant panels
        side_column = QVBoxLayout()
        side_column.setSpacing(12)

        # Camera control panel (source selection, status, camera on/off)
        self._camera_panel = CameraControlPanel(
            self._capture_manager,
            self._config,
            self._project_root,
            parent=central,
        )
        self._camera_panel.set_save_config_callback(self._on_camera_panel_source_changed)
        self._camera_panel.set_camera_off_callback(self._on_camera_toggled_from_panel)
        self._camera_panel.set_custom_avatar_changed_callback(self._on_custom_avatar_changed)
        self._camera_panel.persist_custom_avatar_to_config()
        side_column.addWidget(self._camera_panel)

        # Main video: display-only, fed by VideoCaptureManager
        self._main_video = VideoWidget(
            parent=central,
            camera_id=None,
            title="You",
            show_placeholder=False,
        )
        self._main_video.setMinimumSize(640, 480)
        self._update_main_video_source_label()
        if not self._capture_manager.is_opened():
            self._main_video.set_error_message("Camera not found. Check config or switch source.")
        content.addWidget(self._main_video, 3)

        # Participant panels: source per config (mirror, camera, deepfacelive, avatarify, remote)
        side_layout = QVBoxLayout()
        side_layout.setSpacing(12)
        self._participant_sources = get_participant_sources(self._config)
        participant_camera_index = self._config.get("participant_camera_index", 1)
        deepfacelive_camera_index = self._config.get("deepfacelive_camera_index", 1)
        avatarify_camera_index = self._config.get("avatarify_camera_index", 1)
        webcam_index = self._config.get("webcam_index", 0)
        self._participant_widgets = []
        self._participant_captures = []  # OptionalCameraCapture or None per slot
        for i, src in enumerate(self._participant_sources):
            title = f"Participant {i + 1}"
            if src == PARTICIPANT_SOURCE_DEEPFACELIVE:
                title = f"Participant {i + 1} — DeepFaceLive"
            elif src == PARTICIPANT_SOURCE_AVATARIFY:
                title = f"Participant {i + 1} — Avatarify"
            w = VideoWidget(
                parent=central,
                camera_id=None,
                title=title,
                show_placeholder=(src == PARTICIPANT_SOURCE_REMOTE),
            )
            if src == PARTICIPANT_SOURCE_CAMERA:
                cap = OptionalCameraCapture(participant_camera_index, fallback_index=webcam_index)
                if not cap.is_opened():
                    w.set_error_message(f"Camera {participant_camera_index} not found")
                self._participant_captures.append(cap)
            elif src == PARTICIPANT_SOURCE_DEEPFACELIVE:
                cap = OptionalCameraCapture(deepfacelive_camera_index, fallback_index=webcam_index)
                if not cap.is_opened():
                    w.set_error_message(f"DeepFaceLive camera {deepfacelive_camera_index} not found")
                self._participant_captures.append(cap)
            elif src == PARTICIPANT_SOURCE_AVATARIFY:
                cap = OptionalCameraCapture(avatarify_camera_index, fallback_index=webcam_index)
                if not cap.is_opened():
                    w.set_error_message(f"Avatarify camera {avatarify_camera_index} not found")
                self._participant_captures.append(cap)
            else:
                self._participant_captures.append(None)
            if src == PARTICIPANT_SOURCE_REMOTE:
                w.set_error_message("Waiting for remote…")
            self._participant_widgets.append(w)
            side_layout.addWidget(w, 1)
        side_column.addLayout(side_layout, 1)
        content.addLayout(side_column, 1)
        main_layout.addLayout(content, 1)

        # Bottom control bar: Source, Mic, Camera, End
        control_frame = QFrame()
        control_frame.setObjectName("controlFrame")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(16, 12, 16, 12)
        control_layout.setSpacing(24)
        control_layout.addStretch()

        self._source_btn = QPushButton(self._source_button_label())
        self._source_btn.setToolTip("Cycle: Webcam → DeepFaceLive → Avatarify (virtual cameras)")
        self._source_btn.clicked.connect(self._on_source_clicked)
        control_layout.addWidget(self._source_btn)

        self._mic_btn = QPushButton("🎤 Mic")
        self._mic_btn.setCheckable(True)
        self._mic_btn.setChecked(False)
        self._mic_btn.toggled.connect(self._on_mic_toggled)
        control_layout.addWidget(self._mic_btn)

        self._camera_btn = QPushButton("📷 Camera")
        self._camera_btn.setCheckable(True)
        self._camera_btn.setChecked(False)
        self._camera_btn.toggled.connect(self._on_camera_toggled)
        control_layout.addWidget(self._camera_btn)

        self._end_btn = QPushButton("End call")
        self._end_btn.setObjectName("endCallButton")
        self._end_btn.clicked.connect(self._on_end_call)
        control_layout.addWidget(self._end_btn)
        control_layout.addStretch()

        main_layout.addWidget(control_frame)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frames)
        self._timer.start(1000 // 30)

        self._camera_muted = False
        self._mic_muted = False

        # Sync panel with initial camera mute state
        self._camera_panel.set_camera_off_checked(self._camera_muted)

    def _on_camera_panel_source_changed(self):
        """Called when the camera panel changes source; save config and refresh main UI."""
        self._config = self._capture_manager.get_config()
        save_config(self._project_root, self._config)
        self._source_btn.setText(self._source_button_label())
        self._update_main_video_source_label()
        self._main_video.clear_error()

    def _on_camera_toggled_from_panel(self, checked):
        """When camera on/off is toggled from the camera panel, sync bottom bar and main video."""
        self._camera_muted = checked
        self._camera_btn.setChecked(checked)
        self._camera_btn.setText("📷 Camera (off)" if checked else "📷 Camera")
        self._main_video.set_camera_paused(checked)

    def _on_custom_avatar_changed(self, path):
        """When user uploads or clears custom avatar photo; save to config."""
        self._config["custom_avatar_path"] = path
        save_config(self._project_root, self._config)

    def _source_button_label(self):
        src = self._capture_manager.get_current_source()
        if src == SOURCE_DEEPFACELIVE:
            return "📹 Source: DeepFaceLive"
        if src == SOURCE_AVATARIFY:
            return "📹 Source: Avatarify"
        return "📹 Source: Webcam"

    def _update_main_video_source_label(self):
        src = self._capture_manager.get_current_source()
        if src == SOURCE_DEEPFACELIVE:
            name = "DeepFaceLive (webcam)" if self._capture_manager.is_deepfacelive_fallback() else "DeepFaceLive"
        elif src == SOURCE_AVATARIFY:
            name = "Avatarify (webcam)" if self._capture_manager.is_avatarify_fallback() else "Avatarify"
        else:
            name = "Webcam"
        self._main_video.set_source_label(name)

    def _on_source_clicked(self):
        current = self._capture_manager.get_current_source()
        cycle = [SOURCE_WEBCAM, SOURCE_DEEPFACELIVE, SOURCE_AVATARIFY]
        idx = cycle.index(current) if current in cycle else 0
        new_source = cycle[(idx + 1) % len(cycle)]
        ok, err = self._capture_manager.switch_source(new_source, self._config)
        if ok:
            self._config = self._capture_manager.get_config()
            save_config(self._project_root, self._config)
            self._source_btn.setText(self._source_button_label())
            self._update_main_video_source_label()
            self._main_video.clear_error()
            self._camera_panel.update_status()
        else:
            QMessageBox.warning(
                self,
                "Camera error",
                f"Could not switch to {new_source}.\n{err}\n\n"
                "Run from project root: python list_cameras.py\n"
                "to see available camera indices, then set the corresponding camera index in config.json.",
            )
            self._main_video.set_error_message(err)

    def _on_mic_toggled(self, checked):
        self._mic_muted = checked
        self._mic_btn.setText("🎤 Mic (off)" if checked else "🎤 Mic")
        self._main_video.set_muted(self._mic_muted)

    def _on_camera_toggled(self, checked):
        self._camera_muted = checked
        self._camera_btn.setText("📷 Camera (off)" if checked else "📷 Camera")
        self._main_video.set_camera_paused(checked)
        self._camera_panel.set_camera_off_checked(checked)
        self._camera_panel.set_camera_off_checked(checked)

    def _on_end_call(self):
        self._timer.stop()
        self._capture_manager.release()
        self._main_video.release()
        for w in self._participant_widgets:
            w.release()
        for cap in self._participant_captures:
            if cap is not None:
                cap.release()
        QApplication.quit()

    def _update_frames(self):
        if self._camera_muted:
            return
        primary_frame, err = self._capture_manager.read_frame()
        if err:
            self._main_video.set_error_message(err)
            return
        if primary_frame is not None:
            self._main_video.set_frame(primary_frame)
        for i, (widget, src) in enumerate(zip(self._participant_widgets, self._participant_sources)):
            if src == PARTICIPANT_SOURCE_MIRROR and primary_frame is not None:
                widget.set_frame(primary_frame)
            elif src in (PARTICIPANT_SOURCE_CAMERA, PARTICIPANT_SOURCE_DEEPFACELIVE, PARTICIPANT_SOURCE_AVATARIFY):
                cap = self._participant_captures[i]
                if cap is not None:
                    frame, cap_err = cap.read_frame()
                    if frame is not None:
                        widget.set_frame(frame)
                    elif cap_err:
                        widget.set_error_message(cap_err)
            # PARTICIPANT_SOURCE_REMOTE: keep "Waiting for remote…" (no frame)

    def closeEvent(self, event):
        self._timer.stop()
        self._capture_manager.release()
        self._main_video.release()
        for w in self._participant_widgets:
            w.release()
        for cap in self._participant_captures:
            if cap is not None:
                cap.release()
        event.accept()


def main(project_root=None):
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = CallWindow(project_root=project_root)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
