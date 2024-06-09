import pygame
import os
from pygame.math import Vector2 as vector
import json
from math import sin

class Entity(pygame.sprite.Sprite):
    def __init__(self,position,group,path,shoot):
        super().__init__(group)
        self.import_assets(path)
        self.frameidx=0
        self.status='right'
        f=open('settings.json')
        self.settings=json.load(f)
        del f
        self.image=self.animations[self.status][self.frameidx]
        self.rect=self.image.get_rect(topleft=position)
        self.z=self.settings['layers']['Level']
        self.mask=pygame.mask.from_surface(self.image)

        # movement
        self.position=vector(self.rect.center)
        self.direction=vector()
        self.speed=500

        # collisions
        self.old_rect=self.rect.copy()

        # bullet timer
        self.can_shoot=True
        self.shoot_time=None
        self.duck=False
        self.cooldown=200
        self.is_vulnerable=True
        self.hit_time=None
        self.invul_duration=200

        # health
        self.health=20

        # sounds
        self.bullet_sound=pygame.mixer.Sound(os.path.join('audio','bullet.wav'))
        self.bullet_sound.set_volume(.5)
        self.hit_sound=pygame.mixer.Sound(os.path.join('audio','hit.wav'))
        self.hit_sound.set_volume(.5)
    
    def import_assets(self,path):
        self.animations={}
        for root in os.walk(path):
            for folder in root[1]:
                self.animations[folder]=[]
                folder_path=os.path.join(path,folder)
                for file in os.listdir(folder_path):
                    file_path=os.path.join(folder_path,file)
                    surface=pygame.image.load(file_path).convert_alpha()
                    self.animations[folder].append(surface)
    
    def blink(self):
        if not self.is_vulnerable:
            if self.wave_value():
                mask=pygame.mask.from_surface(self.image)
                white_surface=mask.to_surface()
                white_surface.set_colorkey((0,0,0))
                self.image=white_surface

    def wave_value(self):
        value=sin(pygame.time.get_ticks())
        return value>0

    def shoot_timer(self):
        if not self.can_shoot:
            current_time=pygame.time.get_ticks()
            if current_time-self.shoot_time>self.cooldown:
                self.can_shoot=True
    
    def invul_timer(self):
        if not self.is_vulnerable:
            if pygame.time.get_ticks()-self.hit_time>self.invul_duration:
                self.is_vulnerable=True

    def damage(self):
        if self.is_vulnerable:
            self.health-=1
            self.hit_sound.play()
            self.is_vulnerable=False
            self.hit_time=pygame.time.get_ticks()

    def check_death(self):
        if self.health<=0:
            self.kill()

    def animate(self,dt):
        self.frameidx+=(7*dt)
        if self.frameidx>=len(self.animations[self.status]):
            self.frameidx=0
        self.image=self.animations[self.status][int(self.frameidx)]
        self.mask=pygame.mask.from_surface(self.image)