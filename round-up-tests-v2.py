import boids
import pygame as pg
# import push
import math
import numpy as np
import roundup

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50, spawn_zone=pg.Rect(50, 50, 1100, 700), window_size=pg.Vector2(1200, 800))
fear = boids.TUNING["influence_dist"]["fear"]
error = 10       # radius of targets required to reach. Just arbitrary for the moment

sim.data.fears[1] = pg.Vector2(50, 800)

# Add some predefined walls
sim.addTestWalls(add_gate=False)

i = 0
j = -20

while True:


    sheeps = sim.data.boids
    new_arr = []
    for n in range(len(sheeps)):
        coords = sheeps[n][0]
        x = float(coords.x)
        y = float(coords.y)
        new_arr.append([x, y])
    sheep = np.asarray(new_arr)
    x_cg,y_cg = roundup.centroid(sheep)

    drone1 = [sim.data.fears[0].x,sim.data.fears[0].y]
    drone2 = [sim.data.fears[1].x,sim.data.fears[1].y]

    fear = boids.TUNING["influence_dist"]["fear"]
    fears = [roundup.scale_parameter(drone1, [x_cg,y_cg], fear, 300, 1000),roundup.scale_parameter(drone2, [x_cg,y_cg], fear, 300, 1000)]
    fear = max(fears)

    points = roundup.get_points(sheep,fear)
    points.append(points[0])
    new_points = roundup.interpolate_points(points,10)
    points = new_points

    next_pos1,next_pos2 = roundup.navigate_loop(points,drone1,drone2)
    sim.data.fear_targets[0] = pg.Vector2(next_pos1[0],next_pos1[1])
    sim.data.fear_targets[1] = pg.Vector2(next_pos2[0],next_pos2[1])
        
    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break