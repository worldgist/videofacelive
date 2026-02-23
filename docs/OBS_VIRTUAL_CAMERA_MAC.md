# OBS Virtual Camera on Mac

Use **OBS Studio** to turn Avatarify or DeepFaceLive output into a virtual webcam that Zoom, Meet, Teams, etc. can use.

## 1. Install OBS Studio

- Download: [obsproject.com](https://obsproject.com/) → **macOS**.
- Install and open OBS.

**OBS 28+** includes Virtual Camera on Mac; no extra plugin.

If you have an older OBS and no “Start Virtual Camera” option, install the [OBS Virtual Camera plugin](https://obsproject.com/forum/resources/obs-virtualcam.539/) (choose “Install and register only 1 virtual camera”).

## 2. Capture the avatar window

1. In OBS **Sources**, click **+** (Add).
2. Add **Window Capture** (or **Display Capture** if you prefer).
3. **Window Capture**: choose the **avatarify** or **python** window that shows the avatar (the one that says “avatarify” in the title or shows the animated face).
4. Resize/fit: right‑click the source → **Transform** → **Fit to screen** (or **Stretch to screen**).

## 3. Start Virtual Camera

1. In OBS menu: **Tools** → **Start Virtual Camera** (or **VirtualCam** in older versions).
2. Optional: **Tools** → **Virtual Camera** (if available) → enable **Auto-Start**, set **Buffered Frames** to **0** for lower latency.
3. Leave OBS running. The virtual camera name is usually **“OBS Virtual Camera”** (or **“OBS-Camera”** with the plugin).

## 4. Use in apps

- **Zoom / Meet / Teams / Slack**: open **Settings** → **Video** → **Camera** and select **OBS Virtual Camera** (or **OBS-Camera**).
- The camera feed will be whatever OBS is showing (your avatar window).

## 5. Reduce latency (optional)

- In OBS: right‑click the **Preview** → uncheck **Enable Preview** to lower CPU and latency.
- In Avatarify: use **T** to flip output if needed; keep the avatar window visible and not covered.

## Quick checklist

| Step | Action |
|------|--------|
| 1 | Install OBS Studio (and VirtualCam plugin if &lt; OBS 28). |
| 2 | Run Avatarify: `python run.py --config avatarify.yaml` (press **X** to calibrate). |
| 3 | In OBS: Add **Window Capture** → select the avatarify window. |
| 4 | **Tools** → **Start Virtual Camera**. |
| 5 | In Zoom/Meet: choose **OBS Virtual Camera** as camera. |

## Alternative: CamTwist

The original Avatarify Mac docs suggest [CamTwist](http://camtwiststudio.com): use **Desktop+** and “Confine to Application Window” → select the avatarify window. OBS Virtual Camera is usually simpler and works the same way for videoconferencing.
