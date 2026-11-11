# AIRTYPE X release candidate checks

Current automated result: 25 passed. All desktop input in tests uses mocks.

The rebuilt EXE is dist/AIRTYPE-X/AIRTYPE-X.exe. Distribute the complete AIRTYPE-X directory. Console diagnostics remain enabled.

Packaged runtime observed: responding dashboard, Start Tracking accessible, live processing at 41.4 and 19.6 FPS, global F10 registration successful, no-hand/tracking-loss states reported. The bundled model hash matches the source model. Live processing implies successful model initialization but does not itself establish visible landmarks or physical gesture accuracy.

Global F10 uses Windows RegisterHotKey with MOD_NOREPEAT. It only pauses. If registration fails, enabling real control is blocked. Cleanup releases tracked keys/buttons and restores PyAutoGUI's fail-safe setting after release attempts. The dashboard pause button remains available.

User-performed checks still require confirmation:

- Simulation: all four corners and center, one click per pinch, two taps, long pinch drag and release, fist calibration, both scroll axes.
- Touchpad: relative motion, sensitivity, open-hand clutch, reposition without jumps, taps and dragging.
- Keyboard in an empty Notepad document: lowercase/uppercase, numbers/symbols, Shift/Caps Lock, Space/Enter/Backspace, no repeated keys.
- While Notepad has focus: press F10 and confirm PAUSED with held inputs released; F10 must never resume. Resume only with Start.
- Remove hand during a drag and confirm input release.
- Stop tracking and confirm preview stops; restart once; close app and confirm process exits and camera becomes available.

Physical pose-to-label calibration, click accuracy, repeat rates, cross-focus F10, real typing, and final camera shutdown are not declared passed without observed results. Keep real control off until simulation is reliable; only the user should activate real control.
