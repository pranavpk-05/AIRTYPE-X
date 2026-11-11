class InputGateway:
    """Single execution boundary. Simulation never calls the desktop adapter."""
    def __init__(self, settings, emit, adapter=None):
        self.settings=settings; self.emit=emit; self.adapter=adapter; self.paused=True
        self.buttons=set(); self.keys=set(); self.tracked=False
    def action(self, kind, **data):
        self.emit(f"{kind}: {data}")
        if self.paused or not self.tracked or self.settings.simulation or not self.settings.real_control or self.adapter is None: return
        a=self.adapter
        try:
            if kind=='move': a.moveTo(data['x'],data['y'],_pause=False)
            elif kind=='click': a.click(button=data.get('button','left'),clicks=data.get('clicks',1),interval=.12)
            elif kind=='down': self.buttons.add('left'); a.mouseDown()
            elif kind=='up': a.mouseUp(); self.buttons.discard('left')
            elif kind=='scroll':
                if data.get('dx'): a.hscroll(data['dx'])
                if data.get('dy'): a.scroll(data['dy'])
            elif kind=='text':
                self.keys.update(data['text']); a.write(data['text'],interval=.01); self.keys.difference_update(data['text'])
            elif kind=='key':
                self.keys.add(data['key']); a.press(data['key']); self.keys.discard(data['key'])
            elif kind=='key_down': self.keys.add(data['key']); a.keyDown(data['key'])
            elif kind=='key_up': a.keyUp(data['key']); self.keys.discard(data['key'])
        except Exception:
            self.paused=True; self.release_all(); raise
    def release_all(self):
        # Fail-safe stays active for normal execution; cleanup only releases inputs.
        a=self.adapter
        self.release_errors=[]
        if a is None: return
        guarded=hasattr(a,'FAILSAFE'); previous=a.FAILSAFE if guarded else None
        try:
            if guarded: a.FAILSAFE=False
            for held,method in ((self.buttons,a.mouseUp if self.buttons else None),(self.keys,a.keyUp if self.keys else None)):
                for value in tuple(held):
                    try:
                        if held is self.buttons: method(button=value)
                        else: method(value)
                    except Exception as exc: self.release_errors.append(str(exc))
                    else: held.discard(value)
        finally:
            if guarded: a.FAILSAFE=previous
    def suspend(self): self.paused=True; self.tracked=False; self.release_all()
