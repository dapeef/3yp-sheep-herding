import time
import boids
import pygame as pg
import push
import math
import numpy as np


times = []

successes = 0

start_start = time.time()

for i in range(100):

    start_time = time.time()

    # Initiate simulation
    sim = boids.Simulation(num_fears=2, num_boids=200, window_size=pg.Vector2(1200, 800))
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

        targets = push.Bucket.get_targets(sheep, 100, [600, 450], 6*0.174533)

        if targets == False:
            pg.quit()
            successes += 1
            break

        for i in range(len(targets)):
            sim.data.fear_targets[i] = pg.Vector2(targets[i][0], targets[i][1])
            
        info = sim.stepTime()

        if info == "quit":
            pg.quit()

            break 

        # exit criteria:
        # center = np.mean(sheep, axis=0)
        # distances = np.linalg.norm(sheep - center, axis=1)
        # max_distance= max(distances)   
        # if max_distance <= 60:
        #     pg.quit()
        #     successes += 1
        #     break

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