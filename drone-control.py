import boids
import pygame as pg
import push
import math
import numpy as np

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50, window_size=pg.Vector2(1200, 800))
fear = boids.TUNING["influence_dist"]["fear"]

# Add some predefined walls
sim.addTestWalls()

while True:
    #Write your shit here
    #fear target index indicates the drone which is being controlled
    # Gate centre = (600, 450)
    # sim.data.boids          #sheep positions

    # sim.data.fear_targets[0] = pg.Vector2(x, y)
    # sim.data.fear_targets[0].update(x, y)
    sheep = sim.data.boids
    
    targets = push.Bucket.get_targets(sheep,boids.TUNING["influence_dist"]["fear"],[600,450],math.pi/6)



    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break