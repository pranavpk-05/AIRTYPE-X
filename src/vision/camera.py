import time
import cv2

class CameraPipeline:
    """Single camera owner; read/infer runs in the caller's worker thread."""
    def __init__(self, index, tracker): self.index, self.tracker, self.capture, self.timestamp_ms = index, tracker, None, 0
    def open(self):
        self.capture = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640); self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.capture.isOpened(): self.close(); raise RuntimeError(f"Cannot open camera {self.index}")
    def read(self):
        ok, frame = self.capture.read() if self.capture else (False, None)
        if not ok or frame is None or frame.size == 0: return None, []
        frame = cv2.flip(frame, 1)
        self.timestamp_ms = max(self.timestamp_ms+1, int(time.monotonic()*1000))
        hands = self.tracker.process(frame, self.timestamp_ms)
        for hand in hands:
            pts = [(int(x*frame.shape[1]), int(y*frame.shape[0])) for x,y,_ in hand.landmarks]
            for p in pts: cv2.circle(frame, p, 3, (0,255,220), -1)
            for a,b in ((0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),(13,17),(17,18),(18,19),(19,20),(0,17)):
                cv2.line(frame, pts[a], pts[b], (40,190,255), 2)
        return frame, hands
    def close(self):
        if self.capture is not None: self.capture.release(); self.capture = None
        if self.tracker is not None: self.tracker.close(); self.tracker = None
