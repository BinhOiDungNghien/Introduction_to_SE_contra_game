import os
import pygame
from pygame.math import Vector2 as vector
import json
from entity import Entity
import sys

class Player(Entity):
    def __init__(self,position,group,path,collision_sprites,shoot):
        super().__init__(position, group, path, shoot)
        self.shoot=shoot

        # movement
        self.gravity=40
        self.jump_speed=1100
        self.on_floor=False
        self.moving_floor=None
        
        self.collision_sprites=collision_sprites

    def get_status(self):
        # idle
        if self.direction.x==0 and self.on_floor:
            self.status=self.status.split('_')[0]+'_idle'
        # jump
        if self.direction.y!=0 and not self.on_floor:
            self.status=self.status.split('_')[0]+'_jump'
        # duck
        if self.on_floor and self.duck:
            self.status=self.status.split('_')[0]+'_duck'

    def check_contact(self):
        bottom_rect=pygame.Rect(0,0,self.rect.width,5)
        bottom_rect.midtop=self.rect.midbottom
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(bottom_rect):
                if self.direction.y>0:
                    self.on_floor=True
                if hasattr(sprite,'direction'):
                    self.moving_floor=sprite

    def collision(self,direction):
        for sprite in self.collision_sprites.sprites():
            if sprite.rect.colliderect(self.rect):
                if direction=='horizontal':
                    # left collision
                    if self.rect.left<=sprite.rect.right and self.old_rect.left>=sprite.old_rect.right:
                        self.rect.left=sprite.rect.right
                    # right collision
                    if self.rect.right>=sprite.rect.left and self.old_rect.right<=sprite.old_rect.left:
                        self.rect.right=sprite.rect.left
                    self.position.x=self.rect.x
                else:
                    # down collision
                    if self.rect.bottom>=sprite.rect.top and self.old_rect.bottom<=sprite.old_rect.top:
                        self.rect.bottom=sprite.rect.top
                        self.on_floor=True
                    # up collision
                    if self.rect.top<=sprite.rect.bottom and self.old_rect.top>=sprite.rect.bottom:
                        self.rect.top=sprite.rect.bottom
                    self.position.y=self.rect.y
                    self.direction.y=0
        if self.on_floor and self.direction.y!=0:
            self.on_floor=False

    def check_death(self):
        if self.health<=0:
            pygame.quit()
            sys.exit()

    def input(self):
        keys=pygame.key.get_pressed()
        # horizontal movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x=-1
            self.status='left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x=1
            self.status='right'
        else:
            self.direction.x=0
        
        # vertical movement
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_floor:
            self.direction.y=-self.jump_speed
        elif keys[pygame.K_DOWN] or keys[pygame.K_s] or keys[pygame.K_LCTRL]:
            self.duck=True
        else:
            self.duck=False
        if self.duck and self.on_floor:
            self.direction.x=0
        
        # shoot
        if keys[pygame.K_SPACE] and self.can_shoot:
            direction=vector(1,0) if self.status.split('_')[0]=='right' else vector(-1,0)
            position=self.rect.center+direction*80
            y_offset=vector(0,-16) if not self.duck else vector(0,10)
            self.shoot(position+y_offset,direction,self)
            self.bullet_sound.play()
            self.can_shoot=False
            self.shoot_time=pygame.time.get_ticks()
    
    def move(self,dt):
        # horizontal movement
        self.position.x+=self.direction.x*self.speed*dt
        self.rect.x=round(self.position.x)
        self.collision('horizontal')
    
        # vertical movement
        self.direction.y+=self.gravity
        self.position.y+=self.direction.y*dt

        # glue the player to the platform
        if self.moving_floor and self.moving_floor.direction.y>0 and self.direction.y>0:
            self.direction.y=0
            self.rect.bottom=self.moving_floor.rect.top
            self.position.y=self.rect.y
            self.on_floor=True

        self.rect.y=round(self.position.y)
        self.collision('vertical')
        self.moving_floor=None
    
    def update(self,dt):
        self.old_rect=self.rect.copy()
        self.input()
        self.get_status()
        self.move(dt)
        self.check_contact()
        self.animate(dt)
        self.blink()

        # timers
        self.shoot_timer()
        self.invul_timer()

        # death check
        self.check_death()