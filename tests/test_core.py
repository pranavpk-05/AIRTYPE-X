from src.gestures.gesture_state import GestureState
from src.utils.smoothing import CursorSmoother
from src.vision.landmarks import HandObservation
from src.gestures.classifier import classify

def hand(pinch=.2):
    pts=[(.5,.5,0)]*21; pts[4]=(.5,.5,0); pts[8]=(.5+pinch,.5,0)
    # all fingers curled by default
    return HandObservation(tuple(pts),.9)

def test_classifier_pinched_and_tracking_loss():
    assert classify(hand(.01)) == "Pinch"
    assert classify(None) == "No hand"

def test_pinch_hysteresis_and_debounce():
    state=GestureState(.04,.07,.1)
    assert state.update_pinch(.02,1.0) is None
    assert state.update_pinch(.02,1.11)=="down"
    assert state.update_pinch(.05,1.2) is None
    assert state.update_pinch(.08,1.23) is None
    assert state.update_pinch(.08,1.34)=="up"

def test_smoother():
    smooth=CursorSmoother(.5); assert smooth.update((0,0))==(0,0); assert smooth.update((1,1))==(.5,.5)
