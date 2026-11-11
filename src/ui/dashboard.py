import time
import cv2
from PySide6.QtCore import Qt, QThread, Signal, Slot, QPoint, QTimer
from PySide6.QtGui import QImage, QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QCheckBox,QSlider,QFrame,QComboBox,QApplication)
from src.core.config import Settings, MODEL_PATH
from src.core.global_pause import GlobalPause
from src.vision.hand_tracker import HandTracker
from src.vision.camera import CameraPipeline
from src.gestures.classifier import classify, distance
from src.gestures.gesture_state import GestureState
from src.controllers.mouse_controller import MouseController
from src.controllers.keyboard_controller import KeyboardController
from src.keyboard.virtual_keyboard import VirtualKeyboard
from src.ui.styles import STYLE
from src.gestures.interaction import Interaction
from PySide6.QtCore import QSettings

class Worker(QThread):
    frame=Signal(object,object,float,str); error=Signal(str)
    def __init__(self,settings): super().__init__(); self.settings=settings; self.running=True
    def run(self):
        pipeline=None
        try:
            tracker=HandTracker(MODEL_PATH,self.settings.confidence); pipeline=CameraPipeline(self.settings.camera_index,tracker); pipeline.open(); last=time.perf_counter()
            while self.running:
                frame,hands=pipeline.read();
                if frame is None: raise RuntimeError("Camera stopped returning frames")
                now=time.perf_counter(); fps=1/max(now-last,1e-5); last=now
                self.frame.emit(frame,hands,fps,classify(hands[0],self.settings.pinch_on,self.settings.confidence) if hands else "No hand")
        except Exception as e: self.error.emit(str(e))
        finally:
            if pipeline: pipeline.close()
    def stop(self): self.running=False; return self.wait(2500)

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("AIRTYPE X | Touchless Control System"); self.resize(1120,760); self.setStyleSheet(STYLE)
        self.settings=Settings(); self.store=QSettings("AIRTYPE", "AIRTYPE X"); self.settings.sensitivity=float(self.store.value("sensitivity",1.0)); self.settings.camera_index=int(self.store.value("camera_index",0)); self.worker=None; self.state=GestureState(self.settings.pinch_on,self.settings.pinch_off); self.paused=True; self.last_action=0; self.last_y=None
        root=QWidget(); self.setCentralWidget(root); layout=QVBoxLayout(root)
        top=QHBoxLayout(); title=QLabel("AIRTYPE X"); title.setObjectName("title"); top.addWidget(title); top.addWidget(QLabel("TOUCHLESS DESKTOP CONTROL")); top.addStretch(); self.status=QLabel("? STANDBY"); top.addWidget(self.status); layout.addLayout(top)
        body=QHBoxLayout(); layout.addLayout(body,1); panel=QFrame(); panel.setObjectName("panel"); pv=QVBoxLayout(panel); self.preview=QLabel("CAMERA OFFLINE\nStart tracking to connect"); self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter); self.preview.setMinimumSize(640,480); self.preview.setStyleSheet("background:#05090d;border-radius:10px"); pv.addWidget(self.preview); body.addWidget(panel,3)
        side=QFrame(); side.setObjectName("panel"); sv=QVBoxLayout(side); body.addWidget(side,2)
        self.gesture=QLabel("Gesture: ?"); self.fps=QLabel("FPS: ?"); self.hands=QLabel("Hand: not tracked"); [sv.addWidget(x) for x in (self.gesture,self.fps,self.hands)]
        self.camera=QComboBox(); self.camera.addItems(["Camera 0","Camera 1","Camera 2","Camera 3"]); sv.addWidget(QLabel("Camera")); sv.addWidget(self.camera)
        self.sens=QSlider(Qt.Orientation.Horizontal); self.sens.setRange(30,200); self.sens.setValue(int(self.settings.sensitivity*100)); sv.addWidget(QLabel("Cursor sensitivity")); sv.addWidget(self.sens)
        self.sim=QCheckBox("Simulation mode (safe)"); self.sim.setChecked(True); sv.addWidget(self.sim); self.real=QCheckBox("Enable real desktop control"); sv.addWidget(self.real)
        self.btn_start=QPushButton("START TRACKING"); self.btn_stop=QPushButton("STOP TRACKING"); self.pause_btn=QPushButton("EMERGENCY PAUSE"); self.keyboard_btn=QPushButton("TOGGLE FLOATING KEYBOARD"); [sv.addWidget(x) for x in (self.btn_start,self.btn_stop,self.pause_btn,self.keyboard_btn)]
        sv.addStretch(); sv.addWidget(QLabel("Safety: real control is OFF by default. F10 pauses immediately."))
        self.log=QLabel("Intent: waiting"); layout.addWidget(self.log)
        for attr in ('smoothing','pinch_on','confidence','scroll_sensitivity','drag_time','double_click_time','region_margin'):
            setattr(self.settings,attr,float(self.store.value(attr,getattr(self.settings,attr))))
        self.settings.pinch_off=self.settings.pinch_on*1.45
        self.mouse=MouseController(self.settings, self.set_intent); self.engine=Interaction(self.mouse,self.settings); self.keyboard=KeyboardController(self.set_intent,lambda:self._allowed(),self.mouse.gateway); self.virtual=VirtualKeyboard(self.keyboard.press); self.key_buttons=self.virtual.findChildren(QPushButton)
        self.camera.setCurrentIndex(self.settings.camera_index)
        self.btn_start.clicked.connect(self.start); self.btn_stop.clicked.connect(self.stop); self.pause_btn.clicked.connect(self.pause); self.keyboard_btn.clicked.connect(self.toggle_keyboard); self.sim.toggled.connect(self.set_mode); self.real.toggled.connect(self.set_real); self.camera.currentIndexChanged.connect(self.set_camera); self.sens.valueChanged.connect(self.set_sensitivity)
        self.modes=QComboBox(); self.modes.addItems(['Air Mouse','Air Touchpad']); sv.insertWidget(0,self.modes)
        self.modes.setCurrentText(str(self.store.value('mode','Air Mouse'))); self.mouse.mode=self.modes.currentText()
        self.modes.currentTextChanged.connect(self.change_controller_mode)
        for title, attr, low, high, scale in [('Smoothing','smoothing',5,100,100),('Pinch','pinch_on',10,100,1000),('Confidence','confidence',20,99,100),('Scroll','scroll_sensitivity',10,300,100),('Drag time','drag_time',25,150,100),('Double click time','double_click_time',15,70,100),('Interaction edge margin','region_margin',0,35,100)]:
            slider=QSlider(Qt.Orientation.Horizontal); slider.setRange(low,high); slider.setValue(int(getattr(self.settings,attr)*scale)); sv.addWidget(QLabel(title)); sv.addWidget(slider)
            slider.valueChanged.connect(lambda v,a=attr,k=scale:self.setting(a,v/k))
        self.right=QCheckBox('Enable fist click after calibration'); sv.addWidget(self.right); self.right.toggled.connect(lambda v:setattr(self.settings,'right_click_enabled',v))
        self.global_pause=GlobalPause(QApplication.instance(),self.pause)
        self.hotkey_status=QLabel('Global emergency pause: F10' if self.global_pause.registered else self.global_pause.error)
        sv.addWidget(self.hotkey_status)
        self.shortcut=QShortcut(QKeySequence("F10"),self); self.shortcut.activated.connect(self.pause)
    def _allowed(self): return not self.paused and self.settings.real_control and not self.settings.simulation
    def set_intent(self,text): self.log.setText("Intent: "+text)
    def change_controller_mode(self,mode):
        self.mouse.release(); self.engine.reset(); self.mouse.clutch(); self.mouse.smoother.reset(); self.mouse.mode=mode; self.store.setValue('mode',mode)
    def setting(self,attr,value):
        setattr(self.settings,attr,value); self.store.setValue(attr,value)
        self.mouse.smoother.alpha=self.settings.smoothing
        self.settings.pinch_off=self.settings.pinch_on*1.45
    def set_mode(self,v):
        self.pause(); self.settings.simulation=v
        if v: self.real.setChecked(False)
    def set_real(self,v):
        if v and not self.global_pause.registered:
            self.real.setChecked(False); self.pause(); self.set_intent(self.global_pause.error); return
        self.pause(); self.settings.real_control=v
        if v: self.sim.setChecked(False)
    def set_camera(self,i): self.settings.camera_index=i; self.store.setValue("camera_index",i)
    def set_sensitivity(self,v): self.settings.sensitivity=v/100; self.store.setValue("sensitivity",v/100)
    def start(self):
        if self.worker and self.worker.isRunning():
            self.paused=False; self.mouse.paused=False; self.status.setText("ACTIVE"); return
        self.settings.camera_index=self.camera.currentIndex(); self.paused=False; self.mouse.paused=False; self.status.setText("? ACTIVE ? SIMULATION" if self.settings.simulation else "? ACTIVE ? REAL INPUT"); self.worker=Worker(self.settings); self.worker.frame.connect(self.on_frame); self.worker.error.connect(self.on_error); self.worker.start()
    def stop(self):
        if self.worker:
            try: self.worker.frame.disconnect(self.on_frame)
            except (RuntimeError,TypeError): pass
            self.worker.stop()
            if not self.worker.isRunning(): self.worker=None
        self.pause(); self.status.setText("? STANDBY"); self.preview.setText("CAMERA OFFLINE")
    def pause(self): self.paused=True; self.mouse.pause(); self.state.reset(); self.engine.reset(); self.status.setText("? PAUSED"); self.set_intent("Emergency pause ? inputs released")
    def toggle_keyboard(self): self.virtual.setVisible(not self.virtual.isVisible())
    @Slot(object,object,float,str)
    def on_frame(self,frame,hands,fps,gesture):
        h,w,c=frame.shape; q=QImage(frame.data,w,h,c*w,QImage.Format.Format_BGR888); self.preview.setPixmap(QPixmap.fromImage(q).scaled(self.preview.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)); self.gesture.setText("Gesture: "+gesture); self.fps.setText(f"FPS: {fps:.1f}"); self.hands.setText("Hand: tracked" if hands else "Hand: lost")
        hand=hands[0] if hands else None
        key=None
        if hand and self.virtual.isVisible():
            point=QPoint(int(hand.landmarks[8][0]*self.virtual.width()),int(hand.landmarks[8][1]*self.virtual.height()))
            target=next((b for b in self.key_buttons if b.geometry().contains(point)),None)
            for button in self.key_buttons: button.setStyleSheet('background:#07516a' if button is target else '')
            key=target.text() if target else None
        self.engine.update(hand,gesture,time.monotonic(),self.virtual.isVisible(),key,self.keyboard.press)
        self.hands.setText(f'Hands: {len(hands)} | Landmarks: {len(hand.landmarks) if hand else 0} | Handedness score: {hand.confidence:.2f}' if hand else 'Tracking lost')
        self.gesture.setText(f'{gesture} | previous: {self.engine.previous} | {self.engine.state}')
        self.fps.setText(f'FPS: {fps:.1f} | {self.mouse.mode} | Cursor: {self.mouse.position}')
    def on_error(self,msg): self.pause(); self.status.setText("? CAMERA ERROR"); self.preview.setText("CAMERA / TRACKER ERROR\n"+msg)
    def closeEvent(self,event):
        self.stop()
        if self.worker and self.worker.isRunning():
            event.ignore(); QTimer.singleShot(500,self.close); return
        self.global_pause.close(); self.virtual.close(); event.accept()
