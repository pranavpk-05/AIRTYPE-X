from math import hypot

def distance(a,b): return hypot(a[0]-b[0], a[1]-b[1])
def finger_extended(hand,tip,pip): return hand.landmarks[tip][1] < hand.landmarks[pip][1]
def classify(hand,pinch_on=.045,confidence=.55):
    if not hand or hand.confidence < confidence: return "No hand"
    lm=hand.landmarks
    if distance(lm[4],lm[8]) < pinch_on: return "Pinch"
    i=finger_extended(hand,8,6); m=finger_extended(hand,12,10); r=finger_extended(hand,16,14); p=finger_extended(hand,20,18)
    if i and m and not r and not p: return "Scroll"
    if i and not m and not r and not p: return "Move"
    if not i and not m and not r and not p: return "Right click"
    return "Open hand"
