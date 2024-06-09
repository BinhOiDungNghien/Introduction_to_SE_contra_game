import os
import json
from pygame.math import Vector2 as vector
import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self,position,surface,group,z):
        super().__init__(group)
        self.image=surface
        self.rect=self.image.get_rect(topleft=position)
        self.z=z
        
        # collisions
        self.hitbox=self.rect.inflate(0,-self.rect.width/2)

class CollisionTile(Tile):
    def __init__(self, position, surface, group):
        f=open('settings.json')
        self.settings=json.load(f)
        del f
        super().__init__(position, surface, group,self.settings['layers']['Level'])
        self.old_rect=self.rect.copy()
        
class MovingPlatform(CollisionTile):
    def __init__(self, position, surface, group):
        super().__init__(position, surface, group)
        self.direction=vector(0,-1)
        self.speed=200
        self.position=vector(self.rect.center)
    
    def move(self,dt):
        self.position.y+=self.direction.y*self.speed*dt
        self.rect.centery=round(self.position.y)
    
    def update(self,dt):
        self.old_rect=self.rect.copy()
        self.move(dt)