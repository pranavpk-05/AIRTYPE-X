from types import SimpleNamespace
from unittest.mock import Mock
from src.core.global_pause import GlobalPause
from src.controllers.input_gateway import InputGateway
from src.core.config import Settings

def test_global_registration_dispatch_and_cleanup():
    app=Mock(); win=Mock(); pause=Mock(); win.RegisterHotKey.return_value=1
    hotkey=GlobalPause(app,pause,win)
    win.RegisterHotKey.assert_called_once_with(None,hotkey.HOTKEY_ID,0x4000,0x79)
    assert not hotkey.handle_message(0x312,123)
    assert hotkey.handle_message(0x312,hotkey.HOTKEY_ID)
    assert hotkey.handle_message(0x312,hotkey.HOTKEY_ID)
    assert pause.call_count==2
    hotkey.close(); hotkey.close(); win.UnregisterHotKey.assert_called_once()
    assert not hotkey.handle_message(0x312,hotkey.HOTKEY_ID)

def test_registration_conflict():
    app=Mock(); win=Mock(); win.RegisterHotKey.return_value=0
    h=GlobalPause(app,Mock(),win)
    assert not h.registered and h.error
    app.installNativeEventFilter.assert_not_called()

def test_cleanup_restores_fail_safe_and_attempts_all_inputs():
    a=Mock(); a.FAILSAFE=True
    a.mouseUp.side_effect=RuntimeError('device failure')
    g=InputGateway(Settings(),Mock(),a); g.buttons={'left'}; g.keys={'shift'}
    g.suspend()
    a.keyUp.assert_called_once_with('shift')
    assert a.FAILSAFE is True and not g.keys and g.release_errors
    assert g.paused and not g.tracked

def test_pause_releases_keys_without_resuming():
    a=Mock(); s=Settings(simulation=False,real_control=True)
    g=InputGateway(s,Mock(),a); g.paused=False; g.tracked=True
    g.action('key_down',key='ctrl'); g.suspend(); g.action('click')
    a.keyUp.assert_called_once_with('ctrl'); a.click.assert_not_called()
    assert g.paused
