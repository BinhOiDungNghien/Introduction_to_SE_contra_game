import pygame
import os
from pygame.math import Vector2 as vector

class Bullet(pygame.sprite.Sprite):
    def __init__(self,position,surface,direction,group,settings):
        super().__init__(group)
        self.image=surface
        if direction.x<0:
            self.image=pygame.transform.flip(surface, True, False)
        self.rect=self.image.get_rect(center=position)
        self.z=settings['layers']['Level']
        self.mask=pygame.mask.from_surface(self.image)
        self.start_time=pygame.time.get_ticks()

        # position
        self.position=vector(self.rect.center)
        self.direction=direction
        self.speed=2000

    def move(self,dt):
        self.position+=self.direction*self.speed*dt
        self.rect.center=(round(self.position.x),round(self.position.y))
        

    def update(self,dt):
        self.move(dt)
        if pygame.time.get_ticks()-self.start_time>1000:
            self.kill()

class FireAnimation(pygame.sprite.Sprite):
    def __init__(self,position,direction,surface_list,group,settings,entity):
        super().__init__(group)
        # offset
        xoffset=60 if direction.x>0 else -60
        yoffset=10 if entity.duck else -16
        self.offset=vector(xoffset,yoffset)

        self.entity=entity
        self.frames=[pygame.transform.flip(surface,True,False) if direction.x<0 else surface for surface in surface_list]
        self.frameidx=0
        self.image=self.frames[self.frameidx]
        self.rect=self.image.get_rect(center=self.entity.rect.center+self.offset)
        self.z=settings['layers']['Level']
    
    def animate(self,dt):
        self.frameidx+=15*dt
        if self.frameidx>=len(self.frames):
            self.kill()
        else:
            self.image=self.frames[int(self.frameidx)]

    def move(self,dt):
        self.rect.center=self.entity.rect.center+self.offset

    def update(self,dt):
        self.animate(dt)
        self.move(dt)