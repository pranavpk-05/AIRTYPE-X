from dataclasses import dataclass

@dataclass(frozen=True)
class HandObservation:
    landmarks: tuple[tuple[float, float, float], ...]
    confidence: float
    handedness: str = "Unknown"

    def point(self, index: int) -> tuple[float, float, float]:
        return self.landmarks[index]
