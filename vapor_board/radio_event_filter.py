"""Ignore worker events from a superseded connection generation."""

class EventGenerationFilter:
    def __init__(self):
        self.generation = 0

    def begin(self):
        self.generation += 1
        return self.generation

    def invalidate(self):
        self.generation += 1

    def accept(self, generation, event):
        if type(generation) is not int:
            return None
        return event if generation == self.generation else None
