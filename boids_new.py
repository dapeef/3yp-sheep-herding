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
        self.vel = pg.Vector2(0,0)# pg.Vector2(randint(-100, 100), randint(-100, 100))
        self.pos = pg.Vector2(self.rect.center)

    def update_old(self, dt, tuning):
        max_speed = tuning["max_speed"]
        max_force = tuning["max_force"]


        def sep_function(distance):
            y_int = 1 # y intercept
            x_int = tuning["target_dist"] # x intercept

            return - y_int / x_int * distance + y_int 

        def get_force(steer):
            if steer.magnitude() != 0:
                steer = steer.normalize()
                steer *= max_speed
                steer -= self.vel
                steer = clamp_magnitude(steer, max_force)

            return steer

        target_dist = tuning["target_dist"] # Ideal separation from other boids
        influence_dist = tuning["influence_dist"]

        # Make list of nearby boids, sorted by distance
        otherBoids = np.delete(self.data.boids, self.bnum, 0)
        array_dists = (self.pos.x - otherBoids[:,0])**2 + (self.pos.y - otherBoids[:,1])**2 # distance^2 to save computation time
        closeBoidIs = np.argsort(array_dists)[:7] # Look at 7 closest boids only
        neiboids = otherBoids[closeBoidIs]
        neiboids[:,4] = np.sqrt(array_dists[closeBoidIs])
        neiboids = neiboids[neiboids[:,4] < influence_dist["boid"]]

        # Initialise steering vectors
        sep_steer = pg.Vector2(0,0)
        ali_steer = pg.Vector2(0,0)
        coh_steer = pg.Vector2(0,0)
        fear_steer = pg.Vector2(0,0)

        if neiboids.size > 1:  # if has neighbours, do math and sim rules
            # Apply the 3 criteria - separation, cohesion, alignment

            # Separation
            sep_count = 0
            for boid in neiboids:
                if (boid[4] < target_dist):
                    # Get normalised direction of force
                    direction = (self.pos - pg.Vector2(boid[0:2].tolist())).normalize()
                    # Weight by distance and add to sum
                    sep_steer += direction * sep_function(boid[4])
                    sep_count += 1
            # Normalise by number of boids influencing
            if sep_count > 0: sep_steer /= sep_count

            # Alignment
            ali_steer = pg.Vector2(np.mean(neiboids[:,2] / neiboids[:,4]), np.mean(neiboids[:,3] / neiboids[:,4]))


            # Cohesion
            # Weighted averages
            # denom = np.sum(1 / neiboids[:,4])
            # avg_pos_x = np.mean(neiboids[:,0] / neiboids[:,4]) / denom
            # avg_pos_y = np.mean(neiboids[:,1] / neiboids[:,4]) / denom
            # avg_pos = pg.Vector2(avg_pos_x, avg_pos_y)
            # coh_steer = avg_pos - self.pos

            avg_pos = (np.mean(neiboids[:,0]), np.mean(neiboids[:,1]))
            coh_steer = pg.Vector2(avg_pos) - self.pos
        
        # Fear
        self.data.fears[:,2] = np.sqrt((self.pos.x - self.data.fears[:,0])**2 + (self.pos.y - self.data.fears[:,1])**2)
        for fear in self.data.fears:
            if (fear[2] < influence_dist["fear"]):
                # Get normalised direction of force
                direction = (self.pos - pg.Vector2(fear[0:2].tolist())).normalize()
                # Weight by distance and add to sum
                fear_steer += direction / (fear[2] / tuning["fear_const"])**tuning["fear_decay"]

        # Get forces from steer vectors, including weightings
        weightings = tuning["weightings"]
        sep_force = get_force(sep_steer) * weightings["sep"]
        ali_force = get_force(ali_steer) * weightings["ali"]
        coh_force = get_force(coh_steer) * weightings["coh"]
        fear_force = get_force(fear_steer) * weightings["fear"]

        # Sum forces
        force = sep_force + ali_force + coh_force + fear_force

        # Adjust velocity to reflect force
        self.vel += force

        # Get angle of velocity for rendering
        self.ang = self.vel.as_polar()[1]

        # Adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()
        
        # Ensure max_speed is not exceeded
        self.vel = clamp_magnitude(self.vel, max_speed)

        # Add speed decay
        self.vel /= tuning["speed_decay"] ** dt

        if self.bnum == 0:
            print(sep_force, ali_force, coh_force, fear_force)
            #print(self.vel, self.vel.magnitude())

        # Change position based on velocity
        self.pos += self.vel * dt

        # Update position of rendered boid
        self.rect.center = self.pos

        # Finally, output pos and vel to array
        self.data.boids[self.bnum,:4] = [self.pos[0], self.pos[1], self.vel[0], self.vel[1]]

    def update(self, dt, tuning):
        self.accel = pg.Vector2(100, 0)



class Data():
    def __init__(self, n_boids, n_fears=1):
        self.boids = np.zeros((n_boids, 5), dtype=float)
        self.fears = np.zeros((n_fears, 3), dtype=float)


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
            
            data.fears[0][0] = mouse_pos[0]
            data.fears[0][1] = mouse_pos[1]

        for e in pg.event.get():
            # Handle quitting
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            
            if e.type == pg.MOUSEBUTTONDOWN and MOUSEFEAR:
                data.fears = np.append(data.fears, [[mouse_pos[0], mouse_pos[1], 0]], axis=0)

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        for fear in data.fears:
            pg.draw.circle(screen, (255, 0, 0), (fear[0], fear[1]), 5) # Draw red circle on mouse position
        nBoids.update(dt, TUNING)
        nBoids.draw(screen)

        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
