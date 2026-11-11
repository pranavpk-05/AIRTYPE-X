from unittest.mock import Mock
import numpy as np
import pytest
from src.gestures.classifier import classify
from src.vision.landmarks import HandObservation
from src.vision.camera import CameraPipeline

@pytest.mark.parametrize('extended,label',[((), 'Right click'),((8,), 'Move'),((8,12),'Scroll'),((8,12,16,20),'Open hand')])
def test_synthetic_upright_geometry(extended,label):
    points=[(.5,.7,0)]*21; points[4]=(0,0,0)
    for tip,pip in ((8,6),(12,10),(16,14),(20,18)):
        points[pip]=(.5,.5,0); points[tip]=(.5,.3 if tip in extended else .7,0)
    assert classify(HandObservation(tuple(points),.99))==label

def test_confidence_gate():
    assert classify(HandObservation(tuple([(.5,.5,0)]*21),.2))=='No hand'

def test_invalid_camera_frame_never_reaches_tracker():
    tracker=Mock(); camera=CameraPipeline(0,tracker); camera.capture=Mock()
    camera.capture.read.return_value=(True,np.array([]))
    assert camera.read()==(None,[]); tracker.process.assert_not_called()
    device=camera.capture; camera.close(); device.release.assert_called_once(); tracker.close.assert_called_once()

def test_camera_model_processing_and_timestamp():
    tracker=Mock(); tracker.process.return_value=[]
    camera=CameraPipeline(0,tracker); camera.capture=Mock()
    camera.capture.read.return_value=(True,np.zeros((480,640,3),dtype=np.uint8))
    frame,hands=camera.read(); t=camera.timestamp_ms
    camera.read(); assert camera.timestamp_ms>t
    assert frame.shape==(480,640,3) and hands==[]
    assert tracker.process.call_count==2; camera.close()
