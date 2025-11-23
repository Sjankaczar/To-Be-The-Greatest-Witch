import pygame
from src.config import *

class Lantern:
    def __init__(self):
        self.level = 1
        self.base_radius = 100
        self.radius = self.base_radius
    
    def upgrade(self):
        self.level += 1
        self.radius = self.base_radius + (self.level - 1) * 50
        print(f"Lantern upgraded to level {self.level}, radius: {self.radius}")

    def get_radius(self):
        return self.radius
