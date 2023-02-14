import boids
import pygame as pg
import push
import math
import numpy as np
import roundup

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50, render=True)
fear = boids.TUNING["influence_dist"]["fear"]
error = 4       # radius of targets required to reach. Just arbitrary for the moment

# Add some predefined walls
sim.addTestWalls()

i = 0
j = -5

while True:

    sheeps = sim.data.boids
    new_arr = []
    for n in range(len(sheeps)):
        coords = sheeps[n][0]
        x = float(coords.x)
        y = float(coords.y)
        new_arr.append([x, y])
    sheep = np.asarray(new_arr)

    points = roundup.get_points(sheep,fear/1.1)
    length = len(points)
    for n in range(2):
        x = sim.data.fears[n][0]            # get fear locations
        y = sim.data.fears[n][1] 
        if n == 0: 
            if i >= length:
                i = 0
            s = math.sqrt((x-points[i][0])**2 + (y-points[i][1])**2)
            if s<=error:
                i += 1
            if i >= length:
                i = 0
            
            sim.data.fear_targets[0] = pg.Vector2(points[i][0], points[i][1])
        else:
            if j >= length:
                j = 0
            s = math.sqrt((x-points[j][0])**2 + (y-points[j][1])**2)
            if s<=error:
                j += 1
            if j >= length:
                j = 0
            
            sim.data.fear_targets[1] = pg.Vector2(points[j][0], points[j][1])
        
    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break