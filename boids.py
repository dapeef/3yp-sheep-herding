#!/usr/bin/env python3
from random import randint, choice
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame as pg
import numpy as np
import json
import transform as tf
import sys
from PIL import Image


FLLSCRN = False         # True for Fullscreen, or False for Window
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
    "target_dist": 20,      # Target separation
    "influence_dist": {
        "boid": 200,        # "visibility" distance for the boids
        "fear": 200,
        "wall": 25
    },
    # "fear_decay": 1,        # see below
    # "fear_const": .05,      # 1/(r/k)^a -> k is const, a is decay
    # "speed_decay": 2        # Decay rate of speed -> v /= speed_decay * dt
    "target_vel": pg.Vector2(0, 0),  # Speed which the boids tend towards under no other forces
    "wall_thickness": 5       # Amount of padding given to the wall (x on either side of the wall)
}
PIX_PER_METER = 15      # Number of pixels per meter in the real world
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
            # if self.bnum == 0:
            # self.color.hsva = (randint(0,360), 90, 90)
            # else:
            self.color.hsva = (0, 0, 100)
            # pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0))) # Arrow shape
            pg.draw.ellipse(self.image, self.color, pg.Rect(3, 0, 9, 15)) # Blob shape
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

            if rel_pos.length() == 0: # Handle boid being exactly on the line
                    rel_pos = pg.Vector2(choice([-2, -1, 1, 2]), choice([-2, -1, 1, 2]))

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
                dist = max(rel_pos.length() - tuning["wall_thickness"], 1)
                fear += (1 / dist**8) * rel_pos

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
        alpha_surface = pg.Surface((WIDTH, HEIGHT))
        alpha_surface.set_colorkey((0,0,0))
        alpha_surface.set_alpha(128)

        for fear in self.fears:
            pg.draw.circle(alpha_surface, (100, 0, 0), fear, TUNING["influence_dist"]["fear"]) # Draw big circle at every fear

        surface.blit(alpha_surface, (0, 0))

        for fear in self.fears:
            pg.draw.circle(surface, (255, 0, 0), fear, 5) # Draw dot at avery fear


class Simulation():
    def __init__(self,
                 num_fears = 2,
                 num_boids=50,
                 render=True,
                 mouse_fear=False,
                 spawn_zone=pg.Rect(300, 300, 100, 100),
                 image_save_type=None,
                 save_rate=500,
                 data_pipe=None):
        self.render = render # Whether to render the pygame screen or not

        if self.render:
            pg.init()  # prepare window
            pg.display.set_caption("Sheeeeeeep") # Window title

            if image_save_type == None or \
               image_save_type == "hri" or \
               image_save_type == "dataset":
                self.image_save_type = image_save_type
            
            else:
                raise Exception("\"" + image_save_type + "\" is not a valid input for image_save_type. Options are None, \"hri\" or \"dataset\".")
            
            # if self.image_save_type == "hri":
            #     if data_pipe == None:
            #         raise Exception("If using image_save_type=\"hri\", you must also pass a data_pipe")
            
            self.mouse_fear = mouse_fear

            # setup fullscreen or window mode
            if FLLSCRN:
                currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
                self.screen = pg.display.set_mode(currentRez, pg.SCALED)
                pg.mouse.set_visible(False)
            else: self.screen = pg.display.set_mode((WIDTH, HEIGHT))

            # If mouse controls fear
            if self.mouse_fear:
                pg.mouse.set_visible(False)

            if SHOWFPS : self.font = pg.font.Font(None, 30)

            if self.image_save_type != None:
                self.last_image_save = 0
                self.image_save_rate = save_rate # Time between image saves, ms
                self.save_count = 0
        
        else:
            self.screen = None
        
        # Clock
        self.clock = pg.time.Clock()

        # Set up boids and their data
        self.data = Data(num_boids, num_fears)

        self.nBoids = pg.sprite.Group()
        for n in range(num_boids):
            self.nBoids.add(Boid(n, self.data, self.render, spawn_zone, self.screen))  # spawns desired number of boidz
        
        # Create Transform object
        with open("infrastructure-data.json") as f:
            bounds = tf.GetWallBounds(json.load(f)["walls"])

        self.transform = tf.Transform(bounds, PIX_PER_METER, HEIGHT)
    
    def addWallsFromHRI(self):
        num_segments = 0

        with open("infrastructure-data.json") as f:
            JSON = json.load(f)["walls"][:5]

        for wall in JSON:
            num_segments += len(wall["points"]) - 1

        self.data.initWalls(num_segments)

        for wall in JSON:
            points = wall["points"]

            for i in range(len(points) - 1):
                self.data.makeWall(
                    start_point=self.transform.TransformLP(pg.Vector2(points[i][0], points[i][1])),
                    end_point=self.transform.TransformLP(pg.Vector2(points[i+1][0], points[i+1][1]))
                )
        
        # print(self.transform.TransformLP(pg.Vector2(51.625341, -2.512354)))

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

            self.nBoids.draw(self.screen)

            if self.image_save_type != None and pg.time.get_ticks() > self.last_image_save + self.image_save_rate:
                if self.image_save_type == "dataset":
                    if not '.\\dataset' in [ f.path for f in os.scandir(".") if f.is_dir() ]:
                        os.mkdir(".\\dataset")

                    file_name = "dataset\\" + str(self.save_count)
                    
                    # Format position data
                    boids_dump = []
                    for pos in self.data.boids[:, 0]:
                        boids_dump.append([pos.x, pos.y])
                
                    # Save position data
                    with open(file_name + ".json", 'w') as f:
                        json.dump(boids_dump, f, indent=4)

                    pg.image.save(self.screen, file_name + ".png") # Save image

                elif self.image_save_type == "hri":
                    if not '.\\temp' in [ f.path for f in os.scandir(".") if f.is_dir() ]:
                        os.mkdir(".\\temp")

                    pg.image.save(self.screen, "temp\\boids.png") # Image in bytes

                    # Format position data
                    boids_dump = []
                    for pos in self.data.boids[:, 0]:
                        trans_pos = self.transform.TransformPL(pos)
                        boids_dump.append([trans_pos.x, trans_pos.y])

                    # Format fears data
                    fear_dump = []
                    for pos in self.data.fears:
                        trans_pos = self.transform.TransformPL(pos)
                        fear_dump.append([trans_pos.x, trans_pos.y])

                    # Set monitor drone position to centre of screen
                    monitor_pos = self.transform.TransformPL(pg.Vector2(WIDTH/2, HEIGHT/2))
                    monitor_dump = [[monitor_pos.x, monitor_pos.y]]

                    # # Get image in string
                    # image_bytes = pg.image.tostring(self.screen, "RGB") # Image in bytes
                    # img = Image.frombytes("RGB", (WIDTH, HEIGHT), image_bytes)
                    # image = np.array(img).tolist()

                    all_dump = {
                        "sheep": boids_dump,
                        "drones": fear_dump,
                        "monitoring": monitor_dump,
                        # "image": image
                    }

                    sys.stdout.write(json.dumps(all_dump))
                    sys.stdout.flush()

                # Iterate and update timers
                self.last_image_save = pg.time.get_ticks()
                self.save_count += 1

            self.data.drawFears(self.screen)
            self.data.drawWalls(self.screen)

            if SHOWFPS : self.screen.blit(self.font.render(str(int(self.clock.get_fps())), True, [0,200,0]), (8, 8))

            pg.display.update()

        
        else:
            print("FPS:", self.clock.get_fps())


if __name__ == '__main__':
    sim = Simulation(
        num_fears=2,
        num_boids=50,
        mouse_fear=True,
        image_save_type="hri",
        save_rate=500,
        spawn_zone=pg.Rect([2397.05, -6989.29], [100,100])
    )
    
    sim.addWallsFromHRI()
    # sim.addTestWalls()

    sim.mainloop()
