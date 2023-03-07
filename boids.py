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


BGCOLOR = (0, 0, 0)     # Background color in RGB
FPS = 60                # 30-90
TUNING = {
    "max_speed": 150,       # Max movement speed=
    "weightings": {         # Force weightings
        'sep': 2,
        'ali': 1,
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
    "target_vel": pg.Vector2(0, 0),  # Speed which the boids tend towards under no other forces
    "wall_thickness": 5       # Amount of padding given to the wall (x on either side of the wall)
}
PIX_PER_METER = 15      # Number of pixels per meter in the real world
FEAR_SPEED = 300        # Speed of drones
BOID_SIZE = pg.Vector2(9, 15)/3 * 2


def clamp_magnitude(vector, magnitude):
    # Clamps the magnitude of a vector

    if vector.magnitude() > magnitude:
        return vector.normalize() * magnitude
    
    else:
        return vector

def translate_for_camera(vector, camera_pos, window_size):
    return vector - camera_pos + window_size/2


class Boid(pg.sprite.Sprite):
    def __init__(self, boid_num, data, spawn_zone, draw_surf=None):
        super().__init__()

        self.data = data # Stores positions & rotations of all boids and fears
        self.bnum = boid_num # This boid's number (ID)

        self.ang = pg.Vector2(0,0)
        self.accel = pg.Vector2(0,0)
        self.vel = pg.Vector2(randint(-100, 100), randint(-100, 100))
        self.pos = pg.Vector2(
            randint(spawn_zone.left, spawn_zone.right),
            randint(spawn_zone.top, spawn_zone.bottom)
        )
        self.data.boids[self.bnum, :2] = [self.pos, self.vel] # Save initial pos and vel to data object

        self.draw_surf = draw_surf # Main screen surface

        self.image = pg.Surface((15, 15)).convert() # Area to render boid onto
        self.image.set_colorkey(0)
        self.color = pg.Color(0)  # preps color so we can use hsva
        # if self.bnum == 0:
        # self.color.hsva = (randint(0,360), 90, 90)
        # else:
        self.color.hsva = (0, 0, 100)
        # pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0))) # Arrow shape
        pg.draw.ellipse(self.image, self.color, pg.Rect((15-BOID_SIZE.x)/2, (15-BOID_SIZE.y)/2, BOID_SIZE.x, BOID_SIZE.y)) # Blob shape
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)

        # maxW, maxH = self.draw_surf.get_size()
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def update(self, dt, tuning, camera_pos, window_size):
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

        # Sum weighted components to get acceleration
        self.accel = sep + ali + decel + fear + wall

        # Change velocity and position based on acceleration
        self.vel += self.accel * dt
        self.vel = clamp_magnitude(self.vel, tuning["max_speed"])
        self.pos += self.vel * dt

        # Update data array
        self.data.boids[self.bnum, :2] = [self.pos, self.vel]
        
        # Update position of rendered boid
        self.rect.center = translate_for_camera(self.pos, camera_pos, window_size)

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

    def getMeanBoidPos(self):
        sum = pg.Vector2(0, 0)

        for boid_pos in self.boids[:, 0]:
            sum += boid_pos
        
        try:
            return sum / len(self.boids)
        
        except ZeroDivisionError:
            return sum

    def drawWalls(self, surface, camera_pos):
        window_size = pg.Vector2(surface.get_size())
        for wall in self.walls:
            trans_wall_0 = translate_for_camera(wall[0], camera_pos, window_size)
            trans_wall_1 = translate_for_camera(wall[1], camera_pos, window_size)

            pg.draw.line(surface, (255, 0, 0), trans_wall_0, trans_wall_1, 5) # Draw line between points
            pg.draw.circle(surface, (255, 0, 0), trans_wall_0, 2.5) # Draw red circle on each end
            pg.draw.circle(surface, (255, 0, 0), trans_wall_1, 2.5) # Draw red circle on other end

    def drawFears(self, surface, camera_pos):
        window_size = pg.Vector2(surface.get_size())
        alpha_surface = pg.Surface((window_size.x, window_size.y))
        alpha_surface.set_colorkey((0,0,0))
        alpha_surface.set_alpha(128)

        for fear in self.fears:
            pg.draw.circle(alpha_surface, (100, 0, 0), translate_for_camera(fear, camera_pos, window_size), TUNING["influence_dist"]["fear"]) # Draw big circle at every fear

        surface.blit(alpha_surface, (0, 0))

        for fear in self.fears:
            pg.draw.circle(surface, (255, 0, 0), translate_for_camera(fear, camera_pos, window_size), 5) # Draw dot at avery fear


class Simulation():
    def __init__(self,
                 num_fears=2,
                 num_boids=50,
                 mouse_fear=False,
                 spawn_zone=pg.Rect(300, 300, 100, 100),
                 image_save_type=None,
                 save_rate=500,
                 camera_tracking=False,
                 window_size=pg.Vector2(500, 1000)):
        pg.init()  # prepare window
        pg.display.set_caption("Sheeeeeeep") # Window title

        self.window_size = window_size

        if image_save_type == None or \
            image_save_type == "hri" or \
            image_save_type == "dataset":
            self.image_save_type = image_save_type
        
        else:
            raise Exception("\"" + image_save_type + "\" is not a valid input for image_save_type. Options are None, \"hri\" or \"dataset\".")
        
        self.mouse_fear = mouse_fear

        # setup window
        self.screen = pg.display.set_mode((self.window_size.x, self.window_size.y))

        # If mouse controls fear
        if self.mouse_fear:
            pg.mouse.set_visible(False)

        self.font = pg.font.Font(None, 30)

        if self.image_save_type != None:
            self.last_image_save = 0
            self.image_save_rate = save_rate # Time between image saves, ms
            self.save_count = 0
    
        # Set up camera tracking
        self.camera_tracking = camera_tracking
        if self.camera_tracking:
            self.camera_pos = pg.Vector2(spawn_zone.center)
        
        else:
            self.camera_pos = self.window_size/2
        

        # Clock
        self.clock = pg.time.Clock()

        # Set up boids and their data
        self.data = Data(num_boids, num_fears)

        self.nBoids = pg.sprite.Group()
        for n in range(num_boids):
            self.nBoids.add(Boid(n, self.data, spawn_zone, self.screen))  # spawns desired number of boidz
        
        # Create Transform object
        with open("infrastructure-data.json") as f:
            bounds = tf.GetWallBounds(json.load(f)["walls"])
    
    def addWallsFromHRI(self):
        num_segments = 0

        with open("infrastructure-data.json") as f:
            JSON = json.load(f)["walls"]#[:5]

        for wall in JSON:
            num_segments += len(wall["points"]) - 1

        self.data.initWalls(num_segments)

        for wall in JSON:
            points = wall["points"]

            for i in range(len(points) - 1):
                self.data.makeWall(
                    start_point=tf.TransformLP(pg.Vector2(points[i][0], points[i][1])),
                    end_point=tf.TransformLP(pg.Vector2(points[i+1][0], points[i+1][1]))
                )

    def addTestWalls(self, add_gate=True):
        pad = 40

        self.data.initWalls(6)

        self.data.makeWall(pg.Vector2(pad, pad), pg.Vector2(self.window_size.x-pad, pad))
        self.data.makeWall(pg.Vector2(self.window_size.x-pad, pad), pg.Vector2(self.window_size.x-pad, self.window_size.y-pad))
        self.data.makeWall(pg.Vector2(self.window_size.x-pad, self.window_size.y-pad), pg.Vector2(pad, self.window_size.y-pad))
        self.data.makeWall(pg.Vector2(pad, self.window_size.y-pad), pg.Vector2(pad, pad))
        if add_gate:
            self.data.makeWall(pg.Vector2(600, pad), pg.Vector2(600, 400))
            self.data.makeWall(pg.Vector2(600, 500), pg.Vector2(600, self.window_size.y-pad))

    def mainloop(self):
        # main loop
        while True:
            info = self.stepTime()

            if info == "quit":
                pg.quit()

                return

    def stepTime(self):
        # Get mouse position if self.mouse_fear
        if self.mouse_fear:
            mouse_pos = pg.mouse.get_pos()

            # Translate for camera position
            mouse_pos += self.camera_pos - self.window_size/2
            
            self.data.fears[0] = pg.Vector2(mouse_pos)
            self.data.fear_targets[0] = pg.Vector2(mouse_pos)

        for e in pg.event.get():
                # Handle quitting
                if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    return "quit"

        dt = self.clock.tick(FPS) / 1000

        self.nBoids.update(dt, TUNING, self.camera_pos, self.window_size)

        for i in range(len(self.data.fears)):
            diff = self.data.fear_targets[i] - self.data.fears[i]

            if diff.length() < dt * FEAR_SPEED:
                self.data.fears[i] = self.data.fear_targets[i]
            
            else:
                self.data.fears[i] = self.data.fears[i] +  diff.normalize() * dt * FEAR_SPEED

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

                print("Images saved:", self.save_count)

            elif self.image_save_type == "hri":
                if not '.\\temp' in [ f.path for f in os.scandir(".") if f.is_dir() ]:
                    os.mkdir(".\\temp")

                pg.image.save(self.screen, "temp\\boids.png") # Image in bytes

                # Format position data
                boids_dump = []
                for pos in self.data.boids[:, 0]:
                    trans_pos = tf.TransformPL(pos)
                    boids_dump.append([trans_pos.x, trans_pos.y])

                # Format fears data
                fear_dump = []
                for pos in self.data.fears:
                    trans_pos = tf.TransformPL(pos)
                    fear_dump.append([trans_pos.x, trans_pos.y])

                # Set monitor drone position to centre of screen
                monitor_pos = tf.TransformPL(self.camera_pos)
                monitor_dump = [[monitor_pos.x, monitor_pos.y]]

                # # Get image in string
                # image_bytes = pg.image.tostring(self.screen, "RGB") # Image in bytes
                # img = Image.frombytes("RGB", (self.window_size.x, self.window_size.y), image_bytes)
                # image = np.array(img).tolist()

                all_dump = {
                    "sheep": boids_dump,
                    "drones": fear_dump,
                    "monitoring": monitor_dump,
                    # "image": image
                    "window_size": {
                        "width": self.window_size.x,
                        "height": self.window_size.y
                    }
                }

                sys.stdout.write(json.dumps(all_dump))
                sys.stdout.flush()

            # Iterate and update timers
            self.last_image_save = pg.time.get_ticks()
            self.save_count += 1

        self.data.drawFears(self.screen, self.camera_pos)
        self.data.drawWalls(self.screen, self.camera_pos)

        self.screen.blit(self.font.render(str(int(self.clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

        if self.camera_tracking:
            self.camera_pos = self.data.getMeanBoidPos()


if __name__ == '__main__':
    sim = Simulation(
        num_fears=2,
        num_boids=30,
        mouse_fear=True,
        image_save_type="hri",
        save_rate=1000,
        spawn_zone=pg.Rect([2397.05, -6989.29], [100,100]),
        camera_tracking=True
    )
    
    sim.addWallsFromHRI()
    # sim.addTestWalls()

    sim.mainloop()
