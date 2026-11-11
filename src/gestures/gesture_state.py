class GestureState:
    def __init__(self, on=.045, off=.065, debounce=.12):
        self.on=on; self.off=off; self.debounce=debounce; self.pinched=False
        self.since=None; self.candidate_since=None
    def update_pinch(self, d, now):
        wanted=d < (self.off if self.pinched else self.on)
        if wanted == self.pinched:
            self.candidate_since=None
            return None
        if self.candidate_since is None:
            self.candidate_since=now
            return None
        if now-self.candidate_since < self.debounce:
            return None
        self.pinched=wanted; self.since=now; self.candidate_since=None
        return "down" if wanted else "up"
    def reset(self):
        self.pinched=False; self.candidate_since=None
