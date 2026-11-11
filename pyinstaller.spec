# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

mediapipe_data = collect_data_files('mediapipe', includes=['modules/**'])
hidden = collect_submodules('mediapipe.tasks.python.vision') + ['cv2']
a = Analysis(['src/main.py'], pathex=['.'], binaries=collect_dynamic_libs("mediapipe"), datas=mediapipe_data + [('assets/hand_landmarker.task', 'assets')], hiddenimports=hidden, hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=['tkinter','torch','jax','tensorflow','mediapipe.tasks.python.genai.converter','PyQt5','PyQt6'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='AIRTYPE-X', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, name='AIRTYPE-X')
