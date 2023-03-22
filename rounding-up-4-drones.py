import boids
import pygame as pg
import numpy as np
import roundup4drones as roundup

# Initiate simulation
sim = boids.Simulation(num_fears=4, num_boids=50, spawn_zone=pg.Rect(50, 50, 1100, 700), window_size=pg.Vector2(1200, 800))
fear = boids.TUNING["influence_dist"]["fear"]

sim.data.fears[1] = pg.Vector2(50, 800)
sim.data.fears[2] = pg.Vector2(1000,50)
sim.data.fears[3] = pg.Vector2(1000,800)

# Add some predefined walls
sim.addTestWalls(add_gate=False)

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
    drone3 = [sim.data.fears[2].x,sim.data.fears[2].y]
    drone4 = [sim.data.fears[3].x,sim.data.fears[3].y]

    fear = boids.TUNING["influence_dist"]["fear"]
    # fears = [roundup.scale_parameter(drone1, [x_cg,y_cg], fear, 300, 1000,1.3,1.5),roundup.scale_parameter(drone2, [x_cg,y_cg], fear, 300, 1000,1.3,1.5)]
    # fear = max(fears)

    hull = roundup.GiftWrap.gift_wrapping(sheep)
    hull.append(hull[0])
    path = roundup.offset_curve(hull,80)
    targets = roundup.get_targets(path)

    next_pos1,next_pos2,next_pos3,next_pos4 = roundup.navigate_loop(targets,drone1,drone2,drone3,drone4)
    sim.data.fear_targets[0] = pg.Vector2(next_pos1[0],next_pos1[1])
    sim.data.fear_targets[1] = pg.Vector2(next_pos2[0],next_pos2[1])
    sim.data.fear_targets[2] = pg.Vector2(next_pos3[0],next_pos3[1])
    sim.data.fear_targets[3] = pg.Vector2(next_pos4[0],next_pos4[1])
        
    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break