"""Python twin of play/engine.js mulberry32, bit for bit (32-bit unsigned arithmetic)."""
M = 0xFFFFFFFF
def _imul(a, b):
    return (a * b) & M
class Mulberry32:
    def __init__(self, seed): self.a = seed & M
    def random(self):
        self.a = (self.a + 0x6D2B79F5) & M
        t = self.a
        t = _imul(t ^ (t >> 15), t | 1)
        t ^= (t + _imul(t ^ (t >> 7), t | 61)) & M
        return ((t ^ (t >> 14)) & M) / 4294967296
