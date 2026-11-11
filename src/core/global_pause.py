"""Windows global F10 registration on Qt's GUI message thread."""
import ctypes
import sys
from PySide6.QtCore import QAbstractNativeEventFilter

class GlobalPause(QAbstractNativeEventFilter):
    HOTKEY_ID=0x4158
    def __init__(self, app, pause, user32=None):
        super().__init__()
        self.app=app; self.pause=pause; self.registered=False; self.error=None
        self.user32=user32
        if self.user32 is None and sys.platform=='win32':
            self.user32=ctypes.WinDLL('user32',use_last_error=True)
        if self.user32 is not None:
            self.registered=bool(self.user32.RegisterHotKey(None,self.HOTKEY_ID,0x4000,0x79))
            if self.registered: app.installNativeEventFilter(self)
            else: self.error='Global F10 registration failed; another application may own it.'
        else: self.error='Global F10 is available on Windows only.'
    def handle_message(self, message, identifier):
        if self.registered and message==0x0312 and identifier==self.HOTKEY_ID:
            self.pause(); return True
        return False
    def nativeEventFilter(self,event_type,message):
        from ctypes.wintypes import MSG
        if bytes(event_type) in (b'windows_generic_MSG',b'windows_dispatcher_MSG'):
            msg=MSG.from_address(int(message))
            if self.handle_message(msg.message,msg.wParam): return True,0
        return False,0
    def close(self):
        if self.registered:
            self.app.removeNativeEventFilter(self)
            self.user32.UnregisterHotKey(None,self.HOTKEY_ID)
            self.registered=False
