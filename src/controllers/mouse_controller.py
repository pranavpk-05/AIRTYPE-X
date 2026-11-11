try:
    import pyautogui
except ImportError:
    pyautogui = None
from src.utils.smoothing import CursorSmoother
from .input_gateway import InputGateway

class MouseController:
    """Absolute air mouse and relative air touchpad; emits intents in simulation."""
    def __init__(self, settings, emit):
        self.settings=settings; self.emit=emit; self.smoother=CursorSmoother(settings.smoothing)
        self.held=False; self.paused=True; self.mode="Air Mouse"; self.position=None; self.previous=None
        self.gateway=InputGateway(settings,emit,pyautogui)
    def _size(self): return pyautogui.size() if pyautogui else (1920,1080)
    def _allowed(self): return not self.paused and not self.settings.simulation and self.settings.real_control
    def _move_to(self, target):
        w,h=self._size(); target=(min(max(target[0],0),w-1),min(max(target[1],0),h-1))
        self.position=self.smoother.update(target); x,y=(int(v) for v in self.position)
        self.emit(f"Move {x}, {y}")
        self.send("move",x=x,y=y)
        return x,y
    def move(self, x, y):
        w,h=self._size()
        if self.mode=="Air Touchpad":
            point=(x*w,y*h)
            if self.previous is None:
                self.previous=point
                if self.position is None: self.position=(w/2,h/2)
                return self.position
            dx=(point[0]-self.previous[0])*self.settings.sensitivity
            dy=(point[1]-self.previous[1])*self.settings.sensitivity
            self.previous=point
            return self._move_to(((self.position or (w/2,h/2))[0]+dx,(self.position or (w/2,h/2))[1]+dy))
        margin=getattr(self.settings,"region_margin",0.0)
        x=(x-margin)/(1-2*margin); y=(y-margin)/(1-2*margin)
        self.previous=(x*w,y*h)
        center=(w/2,h/2); target=(center[0]+(min(max(x,0),1)*(w-1)-center[0])*self.settings.sensitivity,center[1]+(min(max(y,0),1)*(h-1)-center[1])*self.settings.sensitivity)
        return self._move_to(target)
    def clutch(self): self.previous=None; self.emit("Touchpad reposition")
    def scroll(self, dx=0, dy=0):
        self.emit(f"Scroll x={int(dx)} y={int(dy)}")
        self.send("scroll",dx=int(dx),dy=int(dy))
    def click(self, button="left", clicks=1):
        self.emit(f"{button.title()} click" if clicks==1 else f"{button.title()} double-click")
        self.send("click",button=button,clicks=clicks)
    def hold(self):
        if self.held: return
        self.held=True; self.emit("Drag start")
        self.send("down")
    def release(self):
        if self.held:
            self.held=False; self.emit("Drag release")
            self.send("up")
    def pause(self):
        self.paused=True; self.gateway.suspend(); self.held=False; self.previous=None
    def send(self, kind, **data):
        self.gateway.paused=self.paused
        self.gateway.action(kind,**data)
