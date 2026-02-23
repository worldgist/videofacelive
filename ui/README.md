# FACE-LIVE Call UI

Zoom-style simulated video call interface where **one real camera feed** controls **multiple participant panels**.

## How it works

1. **Primary video source**  
   The user’s webcam (or the same feed after face processing) is the single input. It is chosen in the UI:
   - **Webcam** – raw camera (index from `config.json`).
   - **DeepFaceLive** – virtual camera fed by DeepFaceLive (face swap/avatar).

2. **Main view and participant panels**  
   - **Main** (center): uses the primary source (Webcam or DeepFaceLive) chosen with the **Source** button.
   - **Participant 1 / 2**: each has its own source from `config.json` → `participant_sources`:
     - **`mirror`** – same as the main feed.
     - **`deepfacelive`** – feed from the DeepFaceLive virtual camera (index `deepfacelive_camera_index`). Use this to show the face-swap output in one panel while the main view stays on webcam.
     - **`camera`** – separate camera (index `participant_camera_index`).
     - **`remote`** – placeholder (“Waiting for remote…”).

   Example: **Participant 1 = DeepFaceLive output, main = webcam**  
   Set `participant_sources` to `["deepfacelive", "mirror"]`. Run DeepFaceLive and a virtual camera; set `deepfacelive_camera_index` in config to that camera’s index. The main view shows your webcam; Participant 1 shows the face-swapped feed.

3. **Face processing (DeepFaceLive)**  
   With DeepFaceLive running and outputting to a virtual camera:
   - The user’s expressions, speech, and head movements drive the replacement face.
   - The UI reads from the virtual camera and shows that “avatar” feed in all panels.
   - Use this for avatar video communication and face-swap streaming.

4. **Later: real remote users**  
   The same layout can later use real remote streams: keep the main panel as “you” (webcam or DeepFaceLive), and feed **Participant 1** / **Participant 2** from your call backend instead of mirroring the main feed.

## Running

- From project root:
  - `python run.py --ui` – UI only (webcam or existing virtual camera).
  - `python run.py --ui --with-deepfacelive` – start DeepFaceLive in the background, then open the UI.
- Standalone: `python ui/call_ui.py` (must be run from project root so `ui` is importable).

**Config** (`config.json` in project root):

- `webcam_index`, `deepfacelive_camera_index` – camera indices (use `python list_cameras.py` to list).
- `participant_sources` – `["mirror", "mirror"]` (default). Use `["deepfacelive", "mirror"]` to show **DeepFaceLive output in Participant 1** and mirror in Participant 2. Also: `"camera"` (second device), `"remote"` (placeholder).
- `participant_camera_index` – device index used when a participant source is `"camera"`.
