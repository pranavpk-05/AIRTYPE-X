# AIRTYPE X

Windows webcam controller using one OpenCV/MediaPipe Tasks worker, a PySide6 dashboard, a temporal gesture interpreter, and a shared simulation/real input gateway. Source is independent; see docs/ATTRIBUTION.md.

## Run

From the project root, install `python -m pip install -r requirements.txt`, then run `python -m src.main`. Python 3.13.14 and the pinned Qt Essentials stack have been used here. The model must exist at `assets/hand_landmarker.task`.

Start Tracking opens the camera. Start also resumes after Pause. Simulation is the default on every launch. Turn off simulation and explicitly enable real control, then resume, only after checking the simulation. F10 is registered globally on Windows using RegisterHotKey; it pauses even while another application has focus. Real activation is blocked if registration fails. PyAutoGUI's corner fail-safe remains enabled.

## Controls

Select Air Mouse for absolute movement or Air Touchpad for relative movement. Index-only moves; a short thumb/index pinch queues a click, two taps within the configured window become a double click, and holding beyond Drag time starts a drag. Release drops. Open hand clutches/repositions. Two fingers scroll along the dominant motion axis. Fist click is disabled until the user enables it after physical calibration; it triggers once per activation after 250 ms.

The interaction edge margin narrows the camera region used for absolute full-screen mapping. At margin .1, camera coordinates .1 through .9 cover the display. Smoothing is EMA alpha: higher values respond faster. The normal hand score display is MediaPipe handedness confidence, not a gesture certainty score. Finger-state rules assume upright hands; rotated/occluded poses need calibration.

Show the floating keyboard to give it interaction priority. Camera coordinates map across its entire local area; hover highlights a key and a debounced pinch selects it. Shift, Caps Lock, digits, symbols, Space, Enter and Backspace are supported. Keep Notepad focused for real typing; click-driven keyboard focus behavior needs manual checking.

## Verify manually

Start in simulation. Move to four corners and center; verify cursor coordinates and intent text. Test one tap, two taps, long pinch and release, both scroll directions, neutral and tracking loss. Switch to Touchpad, move, open palm to clutch, reposition and return to index pose without a jump. Verify Emergency Pause freezes execution; resume with Start. Show keyboard and test every special key in simulation, then explicitly enable real input and repeat in an empty Notepad document. No automated test injects real desktop input.

Previous physical checks confirmed camera capture and 21-landmark observations. The integrated interaction modes have not been physically calibrated. Inspect hand poses individually; no false-positive rate is claimed.

## Tests and build

`python -m pytest -q`

`python -m PyInstaller --clean pyinstaller.spec`

The one-directory executable is `dist/AIRTYPE-X/AIRTYPE-X.exe`. The spec includes the model and Qt's built-in PyInstaller hooks collect required plugins. Packaged launch and webcam operation require separate verification. Volume control is deferred.
