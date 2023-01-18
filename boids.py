#!/usr/bin/env python3
from random import randint, choice
import pygame as pg
import numpy as np
import math
import json

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
        "wall": 25
    },
    # "fear_decay": 1,        # see below
    # "fear_const": .05,      # 1/(r/k)^a -> k is const, a is decay
    # "speed_decay": 2        # Decay rate of speed -> v /= speed_decay * dt
    "target_vel": pg.Vector2(0, 0)
}
PIX_PER_METER = 1.5     # Number of pixels per meter in the real world
FEAR_SPEED = 300        # Speed of drones


def clamp_magnitude(vector, magnitude):
    # Clamps the magnitude of a vector

    if vector.magnitude() > magnitude:
        return vector.normalize() * magnitude
    
    else:
        return vector


class Boid(pg.sprite.Sprite):
    def __init__(self, boid_num, data, render, spawn_zone, draw_surf=None):
        super().__init__()

        self.data = data # Stores positions & rotations of all boids and fears
        self.bnum = boid_num # This boid's number (ID)
        self.render = render # Whether to render the pygame screen or not

        self.ang = pg.Vector2(0,0)
        self.accel = pg.Vector2(0,0)
        self.vel = pg.Vector2(randint(-100, 100), randint(-100, 100))
        self.pos = pg.Vector2(
            randint(spawn_zone.left, spawn_zone.right),
            randint(spawn_zone.top, spawn_zone.bottom)
        )
        # Finally, output pos and vel to array
        self.data.boids[self.bnum, :2] = [self.pos, self.vel]

        if render:
            self.draw_surf = draw_surf # Main screen surface

            self.image = pg.Surface((15, 15)).convert() # Area to render boid onto
            self.image.set_colorkey(0)
            self.color = pg.Color(0)  # preps color so we can use hsva
            if boidNum == 0:
                self.color.hsva = (randint(0,360), 90, 90) if cHSV is None else cHSV # randint(5,55) #4goldfish
            else:
                self.color.hsva = (0, 0, 60)
            pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0))) # Arrow shape
            self.orig_image = pg.transform.rotate(self.image.copy(), -90)

            # maxW, maxH = self.draw_surf.get_size()
            self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))
    
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

        # Update data array
        self.data.boids[self.bnum, :2] = [self.pos, self.vel]
        
        if self.render:
            # Update position of rendered boid
            self.rect.center = self.pos

            # Get angle of velocity for rendering
            self.ang = self.vel.as_polar()[1]

            # Adjusts angle of rendered boid image to match heading
            self.image = pg.transform.rotate(self.orig_image, -self.ang)
            self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix


class Data():
    def __init__(self, n_boids, n_fears=100, n_walls=100):
        self.initBoids(n_boids)
        self.initFears(n_fears, pg.Vector2(100,100))
        self.initWalls(n_walls)

    def initBoids(self, n_boids):
        # Boids array
        self.boids = np.empty((n_boids, 2), dtype=pg.Vector2)
        self.boids.fill(pg.Vector2(0, 0))

    def initFears(self, n_fears, start_pos=pg.Vector2(-10000, -10000)):
        # Fear array
        self.fears = np.empty((n_fears), dtype=pg.Vector2)
        self.fears.fill(start_pos) # Initialise all fears far off screen

        self.num_fears = 0

        # Fear target array
        self.fear_targets = np.empty((n_fears), dtype=pg.Vector2)
        self.fear_targets.fill(start_pos) # Initialise all fears' target position far off screen

    def initWalls(self, n_walls):
        # Walls array
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
            pg.draw.circle(surface, (32, 0, 0), fear, TUNING["influence_dist"]["fear"]) # Draw red circle on mouse position
        for fear in self.fears:
            pg.draw.circle(surface, (255, 0, 0), fear, 5) # Draw red circle on mouse position


class Simulation():
    def __init__(self, num_fears, num_boids=50, render=True, mouse_fear=False, spawn_zone=pg.Rect(300, 300, 100, 100)):
        self.render = render # Whether to render the pygame screen or not

        if self.render:
            pg.init()  # prepare window
            pg.display.set_caption("Sheeeeeeep") # Window title

            self.mouse_fear = mouse_fear

            # setup fullscreen or window mode
            if FLLSCRN:
                currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
                self.screen = pg.display.set_mode(currentRez, pg.SCALED)
                pg.mouse.set_visible(False)
            else: self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

            # If mouse controls fear
            if self.mouse_fear:
                pg.mouse.set_visible(False)

            if SHOWFPS : self.font = pg.font.Font(None, 30)
        
        else:
            self.screen = None
        
        self.clock = pg.time.Clock()

        # Set up boids and their data
        self.data = Data(num_boids, num_fears)

        self.nBoids = pg.sprite.Group()
        for n in range(num_boids):
            self.nBoids.add(Boid(n, self.data, self.render, spawn_zone, self.screen))  # spawns desired # of boidz
    
    def addWallsFromJSON(self, JSON):
        num_segments = 0

        min_point = pg.Vector2(
            JSON[0]["points"][0][0],
            JSON[0]["points"][0][1]
        )
        max_point = pg.Vector2(
            JSON[0]["points"][0][0],
            JSON[0]["points"][0][1]
        )

        for wall in JSON:
            num_segments += len(wall["points"]) - 1

            for point in wall["points"]:
                min_point.x = min(min_point.x, point[0])
                max_point.x = max(max_point.x, point[0])
                min_point.y = min(min_point.y, point[1])
                max_point.y = max(max_point.y, point[1])
        
        center_point = (min_point + max_point)/2

        earth_circ = 40075e3 # km
        m_per_lat = earth_circ / 360 # meters per degree of latitude
        m_per_lng = earth_circ * math.cos(center_point.y / 180 * math.pi) / 360

        def transformCoords(lat_long):
            rel_lat_long = lat_long - min_point

            return pg.Vector2(
                rel_lat_long.y * m_per_lng * PIX_PER_METER,
                HEIGHT - rel_lat_long.x * m_per_lat * PIX_PER_METER # Flipping becaue (0,0) is top left in pg
            ) # switching x and y because lat and long are (y,x)

        self.data.initWalls(num_segments)

        for wall in JSON:
            points = wall["points"]

            for i in range(len(points) - 1):
                self.data.makeWall(
                    start_point=transformCoords(pg.Vector2(points[i][0], points[i][1])),
                    end_point=transformCoords(pg.Vector2(points[i+1][0], points[i+1][1]))
                )

    def addTestWalls(self):
        pad = 40

        self.data.initWalls(6)

        self.data.makeWall(pg.Vector2(pad, pad), pg.Vector2(WIDTH-pad, pad))
        self.data.makeWall(pg.Vector2(WIDTH-pad, pad), pg.Vector2(WIDTH-pad, HEIGHT-pad))
        self.data.makeWall(pg.Vector2(WIDTH-pad, HEIGHT-pad), pg.Vector2(pad, HEIGHT-pad))
        self.data.makeWall(pg.Vector2(pad, HEIGHT-pad), pg.Vector2(pad, pad))
        self.data.makeWall(pg.Vector2(600, pad), pg.Vector2(600, 400))
        self.data.makeWall(pg.Vector2(600, 500), pg.Vector2(600, HEIGHT-pad))

    def mainloop(self):
        # main loop
        while True:
            info = self.stepTime()

            if info == "quit":
                pg.quit()

                return

    def stepTime(self):
        if self.render:
            # Get mouse position if self.mouse_fear
            if self.mouse_fear:
                mouse_pos = pg.mouse.get_pos()
                
                self.data.fears[0] = pg.Vector2(mouse_pos)
                self.data.fear_targets[0] = pg.Vector2(mouse_pos)

            for e in pg.event.get():
                # Handle quitting
                if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    return "quit"
                
                # if e.type == pg.MOUSEBUTTONDOWN and self.mouse_fear:
                #     # data.fears = np.append(data.fears, [pg.Vector2(mouse_pos)], axis=0)
                #     # data.fears = np.insert(data.fears, pg.Vector2(mouse_pos), len(data.fears))
                #     self.data.fears[self.data.num_fears] = pg.Vector2(mouse_pos)
                #     self.data.num_fears += 1

        dt = self.clock.tick(FPS) / 1000

        self.nBoids.update(dt, TUNING)

        for i in range(len(self.data.fears)):
            diff = self.data.fear_targets[i] - self.data.fears[i]

            if diff.length() < dt * FEAR_SPEED:
                self.data.fears[i] = self.data.fear_targets[i]
            
            else:
                self.data.fears[i] = self.data.fears[i] +  diff.normalize() * dt * FEAR_SPEED

        if self.render:
            # Draw
            self.screen.fill(BGCOLOR)
            self.data.drawFears(self.screen)
            self.data.drawWalls(self.screen)
            self.nBoids.draw(self.screen)

            if SHOWFPS : self.screen.blit(self.font.render(str(int(self.clock.get_fps())), True, [0,200,0]), (8, 8))

            pg.display.update()
        
        else:
            print("FPS:", self.clock.get_fps())


if __name__ == '__main__':
    sim = Simulation(num_fears=2, num_boids=BOIDZ, render=True, mouse_fear=True)
    # with open("infrastructure-data.json") as f:
    #     sim.addWallsFromJSON(json.load(f)["walls"][:5])
    sim.addTestWalls()

    sim.mainloop()
