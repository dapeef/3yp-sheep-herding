import boids
import pygame as pg
import numpy as np
import roundup3drones as roundup
import time

times = []

successes = 0

start_start = time.time()

for i in range(50):

    start_time = time.time()

    # Initiate simulation
    sim = boids.Simulation(num_fears=3, num_boids=50, spawn_zone=pg.Rect(50, 50, 1100, 700), window_size=pg.Vector2(1200, 800))
    fear = boids.TUNING["influence_dist"]["fear"]

    sim.data.fears[1] = pg.Vector2(50, 800)
    sim.data.fears[2] = pg.Vector2(1000,50)

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

        fear = boids.TUNING["influence_dist"]["fear"]
        # fears = [roundup.scale_parameter(drone1, [x_cg,y_cg], fear, 300, 1000,1.3,1.5),roundup.scale_parameter(drone2, [x_cg,y_cg], fear, 300, 1000,1.3,1.5)]
        # fear = max(fears)

        hull = roundup.GiftWrap.gift_wrapping(sheep)
        hull.append(hull[0])
        path = roundup.offset_curve(hull,50)
        targets = roundup.get_targets(path)

        next_pos1,next_pos2,next_pos3 = roundup.navigate_loop(targets,drone1,drone2,drone3)
        sim.data.fear_targets[0] = pg.Vector2(next_pos1[0],next_pos1[1])
        sim.data.fear_targets[1] = pg.Vector2(next_pos2[0],next_pos2[1])
        sim.data.fear_targets[2] = pg.Vector2(next_pos3[0],next_pos3[1])
            
        info = sim.stepTime()

        if info == "quit":
            pg.quit()

            break   

        # exit criteria:
        center = np.mean(sheep, axis=0)
        distances = np.linalg.norm(sheep - center, axis=1)
        max_distance= max(distances)   
        if max_distance <= 60:
            pg.quit()
            successes += 1
            break

        elif time.time() - start_time >= 120:
            pg.quit()
            
            break
            

    end_time = time.time()
    if end_time - start_time < 120:
        times.append(end_time - start_time)

end_end = time.time()
overall = end_end - start_start

# calculate mean and standard deviation
mean_time = np.mean(times)
std_dev = np.std(times)

# remove outliers
outliers = np.abs(times - mean_time) > 2 * std_dev
no = len(outliers)
# good_times = times[~outliers]

# recalculate mean and standard deviation without outliers
# mean_time = np.mean(good_times)
# std_dev = np.std(good_times)

print("mean time = ",mean_time,", std_dev = ", std_dev ,", n successes = ",successes)