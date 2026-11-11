from types import SimpleNamespace
from src.controllers.mouse_controller import MouseController
from src.core.config import Settings
import src.controllers.mouse_controller as module

def test_simulation_never_calls_device(monkeypatch):
    called=[]
    fake=SimpleNamespace(size=lambda:(100,100),moveTo=lambda *a,**k:called.append(a),click=lambda **k:called.append(k),mouseDown=lambda:called.append("down"),mouseUp=lambda:called.append("up"))
    monkeypatch.setattr(module,"pyautogui",fake)
    events=[]; ctl=MouseController(Settings(simulation=True),events.append); ctl.paused=False
    ctl.move(.5,.5); ctl.click()
    assert not called and events

def test_pause_releases_held(monkeypatch):
    released=[]; fake=SimpleNamespace(mouseUp=lambda:released.append(True))
    monkeypatch.setattr(module,"pyautogui",fake)
    ctl=MouseController(Settings(),lambda _:None); ctl.held=True; ctl.gateway.buttons.add("left"); ctl.gateway.adapter=SimpleNamespace(mouseUp=lambda **kw:released.append(True)); ctl.pause()
    assert released and not ctl.held and ctl.paused
