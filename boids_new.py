#!/usr/bin/env python3
from random import randint, choice
import pygame as pg
import numpy as np
import math

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
    "max_speed": 150,       # Max movement speed
    # "max_force": 5,         # Max acceleration force
    "weightings": {         # Force weightings
        'sep': 1,
        'ali': 1,
        # 'coh': 1,
        'decel': 1,
        'fear': 2e6,
        'wall': 2e7
    },
    "target_dist": 40,      # Target separation
    "influence_dist": {
        "boid": 200,        # "visibility" distance for the boids
        "fear": 200,
        "wall": 15
    },
    # "fear_decay": 1,        # see below
    # "fear_const": .05,      # 1/(r/k)^a -> k is const, a is decay
    # "speed_decay": 2        # Decay rate of speed -> v /= speed_decay * dt
    "target_vel": pg.Vector2(0, 0)
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
            self.color.hsva = (0, 0, 60)
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
        def getNearest(type, num_select=7):
            # Make list of nearby boids, sorted by distance
            if type == "boid": objects = self.data.boids
            elif type == "fear": objects = self.data.fears
            elif type == "wall": objects = self.data.walls
            otherBoids = np.delete(objects, self.bnum, 0) # delete self
            array_dists = np.zeros(len(otherBoids))
            for i, boid in enumerate(otherBoids):
                if type == "boid": boid_pos = boid[0]
                elif type == "fear" or type == "wall": boid_pos = boid
                array_dists[i] = (self.pos - boid_pos).length() # Get list of distances
            closeBoidIs = np.argsort(array_dists)[:num_select] # Look at $num_select$ closest boids only
            neiboids = otherBoids[closeBoidIs] # pick out chosen boids
            neiboids = neiboids[array_dists[closeBoidIs] < tuning["influence_dist"]["boid"]] # Select only boids within influence radius

            return neiboids

        # Define vectors to hold unweighted acceleration values
        sep = pg.Vector2(0, 0)
        ali = pg.Vector2(0, 0)
        decel = pg.Vector2(0, 0)
        fear = pg.Vector2(0, 0)
        wall = pg.Vector2(0, 0)

        # Loop through near boids and sum sep and ali components
        for boid in getNearest("boid"):
            rel_pos = boid[0] - self.pos # r_{ij} in the paper
            rel_vel = boid[1] - self.vel # v_j - v_i in the paper

            sep += (1 - (tuning["target_dist"] / rel_pos.length())**3) * rel_pos
            ali += rel_vel
        
        # Calculate decel component
        decel = tuning["target_vel"] - self.vel # v_d - v_i in the paper
        
        # Loop through fears and sum fear components
        for fear_obj in self.data.fears:
            rel_pos = self.pos - fear_obj # r_{pi} in the paper

            if rel_pos.length() <= tuning["influence_dist"]["fear"]:
                fear += (1 / rel_pos.length()**3) * rel_pos
        
        # Loop through walls and sum fear components
        for wall_obj in self.data.walls:
            diff = wall_obj[1] - wall_obj[0]
            length2 = diff.length_squared()

            if length2 == 0: # End points of wall are identical
                closest_point = wall_obj[0]
            else:
                # p = self.pos
                # v = wall_obj[0]
                # w = wall_obj[1]
                # Consider the line extending the segment, parameterized as v + t (w - v).
                # We find projection of point p onto the line. 
                # It falls where t = [(p-v) . (w-v)] / |w-v|^2
                # We clamp t from [0,1] to handle points outside the segment vw.
                t = max(0, min(1, (self.pos - wall_obj[0]).dot(diff) / length2))
                closest_point = wall_obj[0] + t * diff

            rel_pos = self.pos - closest_point # r_{pi} in the paper

            if rel_pos.length() <= tuning["influence_dist"]["wall"]:
                if rel_pos.length() == 0: # Handle boid being exactly on the line
                    rel_pos = pg.Vector2(choice([-2, -1, 1, 2]), choice([-2, -1, 1, 2]))
                fear += (1 / rel_pos.length()**8) * rel_pos

        # Apply weights
        sep *= tuning["weightings"]['sep']
        ali *= tuning["weightings"]['ali']
        decel *= tuning["weightings"]['decel']
        fear *= tuning["weightings"]['fear']
        wall *= tuning["weightings"]['wall']

        # Debug print output to help tune
        # if self.bnum == 0:
        #     print(sep, ali, decel, fear, sep="\t")

        # Sum weighted components to get acceleration
        self.accel = sep + ali + decel + fear + wall

        # Change velocity and position based on acceleration
        self.vel += self.accel * dt
        self.vel = clamp_magnitude(self.vel, tuning["max_speed"])
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
    def __init__(self, n_boids, n_fears=100, n_walls=100):
        # Boids array
        self.boids = np.empty((n_boids, 2), dtype=pg.Vector2)
        self.boids.fill(pg.Vector2(0, 0))

        # Fear array
        self.fears = np.empty((n_fears), dtype=pg.Vector2)
        self.fears.fill(pg.Vector2(-10000, -10000)) # Initialise all fears far off screen

        self.num_fears = 1

        # Fear array
        self.walls = np.empty((n_walls, 2), dtype=pg.Vector2)
        self.walls.fill(pg.Vector2(-10000, -10000)) # Initialise all walls far off screen

        self.num_walls = 0
    
    def makeWall(self, start_point, end_point):
        self.walls[self.num_walls] = [start_point, end_point]
        self.num_walls += 1

    def drawWalls(self, surface):
        for wall in self.walls:
            pg.draw.line(surface, (255, 0, 0), wall[0], wall[1], 5) # Draw line between points
            pg.draw.circle(surface, (255, 0, 0), wall[0], 2.5) # Draw red circle on each end
            pg.draw.circle(surface, (255, 0, 0), wall[1], 2.5) # Draw red circle on other end

    def drawFears(self, surface):
        for fear in self.fears:
            pg.draw.circle(surface, (25, 0, 0), fear, TUNING["influence_dist"]["fear"]) # Draw red circle on mouse position
        for fear in self.fears:
            pg.draw.circle(surface, (255, 0, 0), fear, 5) # Draw red circle on mouse position


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

    pad = 50

    data.makeWall(pg.Vector2(pad, pad), pg.Vector2(WIDTH-pad, pad))
    data.makeWall(pg.Vector2(WIDTH-pad, pad), pg.Vector2(WIDTH-pad, HEIGHT-pad))
    data.makeWall(pg.Vector2(WIDTH-pad, HEIGHT-pad), pg.Vector2(pad, HEIGHT-pad))
    data.makeWall(pg.Vector2(pad, HEIGHT-pad), pg.Vector2(pad, pad))
    data.makeWall(pg.Vector2(pad, pad), pg.Vector2(500, 400))
    data.makeWall(pg.Vector2(600, 400), pg.Vector2(WIDTH-pad, HEIGHT-pad))
    data.makeWall(pg.Vector2(500, 150), pg.Vector2(500, 400))

    # main loop
    while True:
        # Get mouse position if MOUSEFEAR
        if MOUSEFEAR:
            mouse_pos = pg.mouse.get_pos()
            
            data.fears[0] = pg.Vector2(mouse_pos)

        for e in pg.event.get():
            # Handle quitting
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            
            if e.type == pg.MOUSEBUTTONDOWN and MOUSEFEAR:
                # data.fears = np.append(data.fears, [pg.Vector2(mouse_pos)], axis=0)
                # data.fears = np.insert(data.fears, pg.Vector2(mouse_pos), len(data.fears))
                data.fears[data.num_fears] = pg.Vector2(mouse_pos)
                data.num_fears += 1

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        data.drawFears(screen)
        data.drawWalls(screen)
        nBoids.update(dt, TUNING)
        nBoids.draw(screen)

        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
