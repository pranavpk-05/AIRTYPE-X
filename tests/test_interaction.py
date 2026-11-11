from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from src.controllers.mouse_controller import MouseController
from src.controllers.keyboard_controller import KeyboardController
from src.core.config import Settings
from src.gestures.interaction import Interaction
from src.vision.landmarks import HandObservation

def hand(pinched=False,x=.5,y=.5):
    pts=[(.8,.8,0)]*21; pts[8]=(x,y,0); pts[4]=(x+(.01 if pinched else .2),y,0)
    return HandObservation(tuple(pts),.99)

@pytest.fixture
def setup(monkeypatch):
    import src.controllers.mouse_controller as mod
    adapter=Mock(); adapter.size.return_value=(1000,800)
    monkeypatch.setattr(mod,'pyautogui',adapter)
    events=[]; m=MouseController(Settings(smoothing=1),events.append); m.paused=False
    return m,Interaction(m,m.settings),events,adapter

def tap(e,t):
    e.update(hand(True),'Pinch',t); e.update(hand(True),'Pinch',t+.13)
    e.update(hand(),'Move',t+.16); e.update(hand(),'Move',t+.29)

def test_absolute_bounds(setup):
    m,e,events,a=setup
    assert m.move(-1,2)==(0,799)
    assert m.move(1,0)==(999,0)

def test_relative_clutch(setup):
    m,e,events,a=setup; m.mode='Air Touchpad'
    m.move(.5,.5); assert m.move(.6,.5)==(600,400)
    m.clutch(); m.move(.1,.1); assert m.position==(600,400)

def test_single_and_double_tap(setup):
    m,e,events,a=setup
    tap(e,1); e.update(hand(),'Move',1.7)
    assert events.count('Left click')==1
    tap(e,2); tap(e,2.3)
    assert events.count('Left double-click')==1
    a.click.assert_not_called()

def test_drag_release_and_loss(setup):
    m,e,events,a=setup
    e.update(hand(True),'Pinch',1); e.update(hand(True),'Pinch',1.13); e.update(hand(True),'Pinch',1.7)
    assert m.held
    e.update(None,'No hand',1.8); assert not m.held and e.state=='Tracking lost'
    a.mouseDown.assert_not_called(); a.mouseUp.assert_not_called()

def test_scroll_and_fist_once(setup):
    m,e,events,a=setup
    e.update(hand(),'Scroll',1); e.update(hand(y=.3),'Scroll',1.1)
    e.update(hand(x=.7,y=.3),'Scroll',1.2)
    assert any('Scroll x=0 y=24' in x for x in events)
    assert any('Scroll x=23 y=0' in x or 'Scroll x=24 y=0' in x for x in events)
    m.settings.right_click_enabled=True
    for t in (2,2.3,2.6,3): e.update(hand(),'Right click',t)
    assert events.count('Right click')==1
    a.scroll.assert_not_called(); a.hscroll.assert_not_called()

def test_pause_and_keyboard(setup):
    m,e,events,a=setup; m.pause(); e.update(hand(),'Move',1)
    assert e.state=='Paused'; a.moveTo.assert_not_called()
    m.paused=False; m.gateway.tracked=True
    k=KeyboardController(events.append,lambda:False,m.gateway)
    for key in ('Shift','a','Space','Enter','Backspace','Caps Lock','b','1','!'): k.press(key)
    assert 'Type: A' in events and 'Type: B' in events
    a.write.assert_not_called(); a.press.assert_not_called()


def test_keyboard_pinch_latch(setup):
    m,e,events,a=setup; typed=[]
    for t in (1,1.13,1.3,1.6): e.update(hand(True),'Pinch',t,True,'a',typed.append)
    assert typed==['a']
    e.update(hand(),'Move',1.7,True,'a',typed.append)
    e.update(hand(),'Move',1.84,True,'a',typed.append)
    e.update(hand(True),'Pinch',2,True,'b',typed.append)
    e.update(hand(True),'Pinch',2.13,True,'b',typed.append)
    assert typed==['a','b']

def test_real_gateway_requires_all_gates(setup):
    m,e,events,a=setup
    m.gateway.action('click'); a.click.assert_not_called()
    m.settings.simulation=False; m.settings.real_control=True
    m.gateway.paused=False; m.gateway.tracked=False
    m.gateway.action('click'); a.click.assert_not_called()
    m.gateway.tracked=True; m.gateway.action('click'); a.click.assert_called_once()
    m.gateway.action('down'); m.gateway.suspend()
    a.mouseUp.assert_called_once(); assert not m.gateway.buttons

def test_calibrated_region(setup):
    m,e,events,a=setup; m.settings.region_margin=.1
    assert m.move(.1,.1)==(0,0)
    assert m.move(.9,.9)==(999,799)
