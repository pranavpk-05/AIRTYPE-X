class KeyboardController:
    def __init__(self, emit, allowed, gateway=None):
        self.emit=emit; self.allowed=allowed; self.gateway=gateway; self.shift=False; self.caps=False
    def press(self,key):
        if key=='Shift': self.shift=not self.shift; self.emit(f'Shift: {self.shift}'); return
        if key=='Caps Lock': self.caps=not self.caps; self.emit(f'Caps: {self.caps}'); return
        value=(key.upper() if self.shift != self.caps else key.lower()) if len(key)==1 and key.isalpha() else key
        self.emit('Type: '+value)
        if self.gateway:
            if key in ('Space','Enter','Backspace'): self.gateway.action('key',key={'Space':'space','Enter':'enter','Backspace':'backspace'}[key])
            else: self.gateway.action('text',text=value)
        self.shift=False
