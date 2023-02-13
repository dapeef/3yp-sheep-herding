import boids
import pygame as pg
import push
import math
import numpy as np

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50, render=True)
fear = boids.TUNING["influence_dist"]["fear"]

# Add some predefined walls
sim.addTestWalls()

# sheeps = sim.data.boids
# new_arr = []
# for i in range(len(sheeps)):
#     coords = sheeps[i][0]
#     x = float(coords.x)
#     y = float(coords.y)
#     new_arr.append([x,y])
# sheep = np.asarray(new_arr)
# print(sheep[0,0] + sheep[0,1])
# exit()

while True:
    #Write your shit here
    #fear target index indicates the drone which is being controlled
    # Gate centre = (600, 450)
    # sim.data.boids          #sheep positions

    # sim.data.fear_targets[0] = pg.Vector2(x, y)
    # sim.data.fear_targets[0].update(x, y)
    sheeps = sim.data.boids
    new_arr = []
    for i in range(len(sheeps)):
        coords = sheeps[i][0]
        x = float(coords.x)
        y = float(coords.y)
        new_arr.append([x,y])
    sheep = np.asarray(new_arr)
    # print(sheep)
    targets = push.Bucket.get_targets(sheep,fear/2,[600,450],math.pi/6)
    for i in range(len(targets)):
        sim.data.fear_targets[i] = pg.Vector2(targets[i][0], targets[i][1])
        # sim.data.fear_targets[i].update(x, y)
    # print(targets)
    # break


    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break