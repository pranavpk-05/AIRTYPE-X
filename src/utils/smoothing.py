class CursorSmoother:
    def __init__(self, alpha=.35): self.alpha=alpha; self.value=None
    def update(self, point):
        self.value = point if self.value is None else tuple(self.alpha*n+(1-self.alpha)*o for n,o in zip(point,self.value))
        return self.value
    def reset(self): self.value=None
