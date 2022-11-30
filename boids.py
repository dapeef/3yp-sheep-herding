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
FPS = 60               # 30-90
SHOWFPS = True          # Show frame rate
TUNING = {
    "max_speed": 150,       # Max movement speed
    "max_force": 5,         # Max acceleration force
    "weightings": {         # Force weightings
        'sep': 2,
        'ali': 1,
        'coh': 1,
        'fear': 2
    },
    "target_dist": 40,      # Target separation
    "influence_dist": 200,  # "visibility" distance for the boids
    "fear_decay": 2         # 1/r^k relationship (where k is decay)
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
        self.color.hsva = (randint(0,360), 90, 90) if cHSV is None else cHSV # randint(5,55) #4goldfish
        pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0))) # Arrow shape
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)

        self.bSize = 17 # "personal space" size
        self.dir = pg.Vector2(1, 0)  # sets up forward direction
        maxW, maxH = self.drawSurf.get_size()
        self.rect = self.image.get_rect(center=(randint(50, maxW - 50), randint(50, maxH - 50)))
        self.ang = randint(0, 360)  # random start angle, & position ^
        self.vel = pg.Vector2(0,0)# pg.Vector2(randint(-100, 100), randint(-100, 100))
        self.pos = pg.Vector2(self.rect.center)

    def update(self, dt, tuning):
        max_speed = tuning["max_speed"]
        max_force = tuning["max_force"]

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
        neiboids = neiboids[neiboids[:,4] < influence_dist]

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
                    sep_steer += direction / boid[4]
                    sep_count += 1
            # Normalise by number of boids influencing
            if sep_count > 0: sep_steer /= sep_count

            # Alignment
            ali_steer = pg.Vector2(np.mean(neiboids[:,2]), np.mean(neiboids[:,3]))

            # Cohesion
            avg_pos = (np.mean(neiboids[:,0]), np.mean(neiboids[:,1]))
            coh_steer = pg.Vector2(avg_pos) - self.pos
        
        # Fear
        self.data.fears[:,2] = np.sqrt((self.pos.x - self.data.fears[:,0])**2 + (self.pos.y - self.data.fears[:,1])**2)
        for fear in self.data.fears:
            if (fear[2] < influence_dist):
                # Get normalised direction of force
                direction = (self.pos - pg.Vector2(fear[0:2].tolist())).normalize()
                # Weight by distance and add to sum
                fear_steer += direction / fear[2]**tuning["fear_decay"]

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

        # Change position based on velocity
        self.pos += self.vel * dt

        # Update position of rendered boid
        self.rect.center = self.pos

        # Finally, output pos and vel to array
        self.data.boids[self.bnum,:4] = [self.pos[0], self.pos[1], self.vel[0], self.vel[1]]


class Data():
    def __init__(self, n_boids, n_fears=1000):
        self.boids = np.zeros((n_boids, 5), dtype=float)
        self.fears = np.zeros((1, 3), dtype=float)


def main():
    pg.init()  # prepare window
    pg.display.set_caption("Sheeeeeeep") # Window title

    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
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
        # Get mouse position
        mouse_pos = pg.mouse.get_pos()

        for e in pg.event.get():
            # Handle quitting
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            
            if e.type == pg.MOUSEBUTTONDOWN:
                print("click!")

                data.fears = np.append(data.fears, [[mouse_pos[0], mouse_pos[1], 0]], axis=0)

                print(data.fears)
        
        data.fears[0][0] = mouse_pos[0]
        data.fears[0][1] = mouse_pos[1]

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        nBoids.update(dt, TUNING)
        for fear in data.fears:
            pg.draw.circle(screen, (255, 0, 0), (fear[0], fear[1]), 5) # Draw red circle on mouse position
        nBoids.draw(screen)

        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
