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
MAX_SPEED = 150         # Max movement speed
MAX_FORCE = 1.5         # Max acceleration force
WIDTH = 1200            # Window Width (1200)
HEIGHT = 800            # Window Height (800)
BGCOLOR = (0, 0, 0)     # Background color in RGB
FPS = 90                # 30-90
SHOWFPS = True          # Show frame rate
WEIGHTINGS = {          # Force weightings
    'sep': 2,
    'ali': 1,
    'coh': 1
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

        self.data = data # Stores positions & rotations of all boids
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

    def _update_old(self, dt, speed, ejWrap=False):
        maxW, maxH = self.drawSurf.get_size()
        turnDir = yat = xat = 0
        turnRate = 120 * dt  # about 120 degrees/sec seems ok
        margin = 42 # Padding distance around the edge, in which boids will turn around

        # Make list of nearby boids, sorted by distance
        otherBoids = np.delete(self.data, self.bnum, 0)
        array_dists = (self.pos.x - otherBoids[:,0])**2 + (self.pos.y - otherBoids[:,1])**2 # distance^2 to save computation time
        closeBoidIs = np.argsort(array_dists)[:7] # Look at 7 closest boids only
        neiboids = otherBoids[closeBoidIs]
        neiboids[:,3] = np.sqrt(array_dists[closeBoidIs])
        neiboids = neiboids[neiboids[:,3] < self.bSize*12]

        if neiboids.size > 1:  # if has neighbors, do math and sim rules
            # averages the positions and angles of neighbors
            yat = np.sum(np.sin(np.deg2rad(neiboids[:,2])))
            xat = np.sum(np.cos(np.deg2rad(neiboids[:,2])))
            tAvejAng = np.rad2deg(np.arctan2(yat, xat)) # arctan etc is necessary because of 360 degree wrapping

            targetV = (np.mean(neiboids[:,0]), np.mean(neiboids[:,1]))

            # if too close, move away from closest neighbor
            if neiboids[0,3] < self.bSize : targetV = (neiboids[0,0], neiboids[0,1])

            # get angle differences for steering
            tDiff = pg.Vector2(targetV) - self.pos
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)

            # if boid is close enough to neighbors, match their average angle
            if tDistance < self.bSize*6 : tAngle = tAvejAng

            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.ang) + 180
            if abs(tAngle - self.ang) > 1.2: turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180

            # if boid gets too close to target, steer away
            if tDistance < self.bSize and targetV == (neiboids[0,0], neiboids[0,1]) : turnDir = -turnDir

        # Avoid edges of screen by turning toward the edge normal-angle
        if not ejWrap and min(self.pos.x, self.pos.y, maxW - self.pos.x, maxH - self.pos.y) < margin:
            # If in the zone near edge
            if self.pos.x < margin : tAngle = 0
            elif self.pos.x > maxW - margin : tAngle = 180
            if self.pos.y < margin : tAngle = 90
            elif self.pos.y > maxH - margin : tAngle = 270

            angleDiff = (tAngle - self.ang) + 180  # if in margin, increase turnRate to ensure stays on screen
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            edgeDist = min(self.pos.x, self.pos.y, maxW - self.pos.x, maxH - self.pos.y)
            turnRate = turnRate + (1 - edgeDist / margin) * (20 - turnRate) #minRate+(1-dist/margin)*(maxRate-minRate)

        if turnDir != 0:  # steers based on turnDir, handles left or right
            self.ang += turnRate * abs(turnDir) / turnDir
            self.ang %= 360  # ensures that the angle stays within 0-360

        # Adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()

        # Change position based on velocity
        self.pos += self.dir * dt * (speed + (7 - neiboids.size) * 2)  # movement speed

        # Optional screen wrap
        if ejWrap and not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = maxH
            elif self.rect.top > maxH : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = maxW
            elif self.rect.left > maxW : self.pos.x = 0

        # Actually update position of boid
        self.rect.center = self.pos

        # Finally, output pos/ang to array
        self.data[self.bnum,:3] = [self.pos[0], self.pos[1], self.ang]

    def update(self, dt, max_speed, max_force, weightings):
        def get_force(steer):
            if steer.magnitude() != 0:
                steer = steer.normalize()
                steer *= max_speed
                steer -= self.vel
                steer = clamp_magnitude(steer, max_force)

            return steer

        target_dist = 40 # Ideal separation from other boids
        influence_dist = target_dist * 4

        # Make list of nearby boids, sorted by distance
        otherBoids = np.delete(self.data, self.bnum, 0)
        array_dists = (self.pos.x - otherBoids[:,0])**2 + (self.pos.y - otherBoids[:,1])**2 # distance^2 to save computation time
        closeBoidIs = np.argsort(array_dists)[:7] # Look at 7 closest boids only
        neiboids = otherBoids[closeBoidIs]
        neiboids[:,4] = np.sqrt(array_dists[closeBoidIs])
        neiboids = neiboids[neiboids[:,4] < influence_dist]

        # Initialise steering vectors
        sep_steer = pg.Vector2(0,0)
        ali_steer = pg.Vector2(0,0)
        coh_steer = pg.Vector2(0,0)

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

            # Get forces from steer vectors, including weightings
            sep_force = get_force(sep_steer) * weightings["sep"]
            ali_force = get_force(ali_steer) * weightings["ali"]
            coh_force = get_force(coh_steer) * weightings["coh"]

            # Sum forces
            force = sep_force + ali_force + coh_force

            # Adjust velocity to reflect force
            self.vel += force


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

        # Finally, output pos/ang to array
        self.data[self.bnum,:4] = [self.pos[0], self.pos[1], self.vel[0], self.vel[1]]


def main():
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try: pg.display.set_icon(pg.image.load("nboids.png"))
    except: print("FYI: nboids.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED)
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

    nBoids = pg.sprite.Group()
    dataArray = np.zeros((BOIDZ, 5), dtype=float)
    for n in range(BOIDZ):
        nBoids.add(Boid(n, dataArray, screen))  # spawns desired # of boidz

    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)

    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        nBoids.update(dt, MAX_SPEED, MAX_FORCE, WEIGHTINGS)
        nBoids.draw(screen)

        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
