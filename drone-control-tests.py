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
    
    sheeps = sim.data.boids
    new_arr = []
    for i in range(len(sheeps)):
        coords = sheeps[i][0]
        x = float(coords.x)
        y = float(coords.y)
        new_arr.append([x, y])
    sheep = np.asarray(new_arr)
    targets = push.Bucket.get_targets(sheep, fear/3, [600, 450], math.pi/6)
    for i in range(len(targets)):
        sim.data.fear_targets[i] = pg.Vector2(targets[i][0], targets[i][1])
        
    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break