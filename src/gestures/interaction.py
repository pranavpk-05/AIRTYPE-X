from .gesture_state import GestureState
from .classifier import distance

class Interaction:
    """Temporal arbitration shared by air mouse, touchpad, and keyboard."""
    def __init__(self, mouse, settings):
        self.mouse=mouse; self.settings=settings; self.pinch=GestureState(); self.reset()
    def reset(self):
        self.pinch.reset(); self.started=None; self.pending=None; self.scroll_point=None
        self.label=None; self.since=0; self.fired=False; self.previous='Neutral'; self.state='Neutral'
    def suspend(self):
        self.mouse.release(); self.mouse.gateway.tracked=False; self.mouse.clutch(); self.reset()
    def update(self, hand, gesture, now, keyboard=False, key=None, type_key=None):
        m=self.mouse; s=self.settings
        if m.paused or hand is None or hand.confidence<s.confidence:
            self.suspend(); self.state='Paused' if m.paused else 'Tracking lost'; return
        m.gateway.tracked=True; m.gateway.paused=m.paused
        if gesture!=self.label:
            self.previous=self.label; self.label=gesture; self.since=now; self.fired=False
        self.pinch.on=s.pinch_on; self.pinch.off=s.pinch_off
        edge=self.pinch.update_pinch(distance(hand.landmarks[4],hand.landmarks[8]),now)
        point=hand.landmarks[8][:2]
        if keyboard:
            m.release(); self.pending=None; self.started=None; self.scroll_point=None; m.clutch()
            if edge=='down' and key is not None: type_key(key)
            self.state='Keyboard'; return
        if self.pending is not None and now-self.pending>s.double_click_time:
            m.click(); self.pending=None
        if edge=='down': self.started=now
        if self.started is not None and self.pinch.pinched and now-self.started>=s.drag_time:
            m.hold(); self.pending=None; self.state='Dragging'
        if edge=='up':
            if m.held: m.release()
            elif self.started is not None:
                if self.pending is not None and now-self.pending<=s.double_click_time:
                    m.click(clicks=2); self.pending=None
                else: self.pending=now
            self.started=None
        if self.pinch.pinched or self.started is not None:
            m.move(*point); self.scroll_point=None; self.state='Dragging' if m.held else 'Pinch'; return
        if gesture=='Scroll':
            if self.scroll_point is not None:
                dx=int((point[0]-self.scroll_point[0])*120*s.scroll_sensitivity)
                dy=int((self.scroll_point[1]-point[1])*120*s.scroll_sensitivity)
                if dx or dy:
                    if abs(dx)>abs(dy): m.scroll(dx=dx)
                    else: m.scroll(dy=dy)
                    self.scroll_point=point
            else: self.scroll_point=point
            m.clutch(); self.state='Scrolling'; return
        self.scroll_point=None
        if gesture=='Move': m.move(*point); self.state='Moving'
        else:
            m.clutch(); self.state='Neutral'
            if gesture=='Right click' and s.right_click_enabled and not self.fired and now-self.since>=.25:
                m.click('right'); self.fired=True; self.state='Right click'
