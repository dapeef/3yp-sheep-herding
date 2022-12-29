#!/usr/bin/env python3
from random import randint
import pygame as pg
import numpy as np

'''
PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
Uses numpy array math instead of math lib, more efficient.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''

FLLSCRN = False         # True for Fullscreen, or False for Window
BOIDZ = 50              # How many boids to spawn, too many may slow fps
WIDTH = 1200            # Window Width (1200)
HEIGHT = 800            # Window Height (800)
BGCOLOR = (0, 0, 0)     # Background color in RGB
FPS = 60                # 30-90
SHOWFPS = True          # Show frame rate
MOUSEFEAR = True        # Is there a fear node on the cursor
TUNING = {
    # "max_speed": 150,       # Max movement speed
    # "max_force": 5,         # Max acceleration force
    "weightings": {         # Force weightings
        'sep': 1,
        'ali': 1,
        # 'coh': 1,
        'fear': 1,
        'decel': 1
    },
    "target_dist": 40,      # Target separation
    "influence_dist": {
        "boid": 200,        # "visibility" distance for the boids
        "fear": 200
    },
    # "fear_decay": 1,        # see below
    # "fear_const": .05,      # 1/(r/k)^a -> k is const, a is decay
    # "speed_decay": 2        # Decay rate of speed -> v /= speed_decay * dt
    "target_speed": pg.Vector2(0, 0)
}


def clamp_magnitude(vector, magnitude):
    # Clamps the magnitude of a vector

    if vector.magnitude() > magnitude:
        return vector.normalize() * magnitude
    
    else:
        return vector


class Boid(pg.sprite.Sprite):
    def __init__(self, boidNum, data, drawSurf, cHSV=None):
        super().__init__()

        self.data = data # Stores positions & rotations of all boids and fears
        self.bnum = boidNum # This boid's number (ID)
        self.drawSurf = drawSurf # Main screen surface

        self.image = pg.Surface((15, 15)).convert() # Area to render boid onto
        self.image.set_colorkey(0)
        self.color = pg.Color(0)  # preps color so we can use hsva
        if boidNum == 0:
            self.color.hsva = (randint(0,360), 90, 90) if cHSV is None else cHSV # randint(5,55) #4goldfish
        else:
            self.color.hsva = (0, 0, 20)
        pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0))) # Arrow shape
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)

        self.bSize = 17 # "personal space" size
        self.dir = pg.Vector2(1, 0)  # sets up forward direction
        maxW, maxH = self.drawSurf.get_size()
        self.rect = self.image.get_rect(center=(randint(50, maxW - 50), randint(50, maxH - 50)))
        self.ang = randint(0, 360)  # random start angle, & position ^
        self.accel = pg.Vector2(0,0)
        self.vel = pg.Vector2(0,0)# pg.Vector2(randint(-100, 100), randint(-100, 100))
        self.pos = pg.Vector2(self.rect.center)
        # Finally, output pos and vel to array
        self.data.boids[self.bnum, :2] = [self.pos, self.vel]

    
    def update(self, dt, tuning):

        # Test acceleration
        self.accel = pg.Vector2(100, 0)

        # Change velocity and position based on acceleration
        self.vel += self.accel * dt
        self.pos += self.vel * dt
        
        # Update position of rendered boid
        self.rect.center = self.pos

        # Get angle of velocity for rendering
        self.ang = self.vel.as_polar()[1]

        # Adjusts angle of rendered boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()

        # Finally, output pos and vel to array
        self.data.boids[self.bnum, :2] = [self.pos, self.vel]



class Data():
    def __init__(self, n_boids, n_fears=1):
        boid_item = np.array([[pg.Vector2(0, 0), pg.Vector2(0, 0), 0]], dtype=object)
        self.boids = np.repeat(boid_item, n_boids, 0)
        fear_item = np.array([[pg.Vector2(0, 0), 0]], dtype=object)
        self.fears = np.repeat(fear_item, n_fears, 0)


def main():
    pg.init()  # prepare window
    pg.display.set_caption("Sheeeeeeep") # Window title

    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED)
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

    # If mouse controls fear
    if MOUSEFEAR:
        pg.mouse.set_visible(False)
    

    # Set up boids and their data
    nBoids = pg.sprite.Group()
    data = Data(BOIDZ)
    for n in range(BOIDZ):
        nBoids.add(Boid(n, data, screen))  # spawns desired # of boidz

    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)

    # main loop
    while True:
        # Get mouse position if MOUSEFEAR
        if MOUSEFEAR:
            mouse_pos = pg.mouse.get_pos()
            
            data.fears[0][0] = pg.Vector2(mouse_pos)

        for e in pg.event.get():
            # Handle quitting
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            
            if e.type == pg.MOUSEBUTTONDOWN and MOUSEFEAR:
                data.fears = np.append(data.fears, [[pg.Vector2(mouse_pos), 0]], axis=0)

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        for fear in data.fears:
            pg.draw.circle(screen, (255, 0, 0), fear[0], 5) # Draw red circle on mouse position
        nBoids.update(dt, TUNING)
        nBoids.draw(screen)

        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
