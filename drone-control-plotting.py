# import boids
# import pygame as pg
# import push
# import math
# import numpy as np

# # Initiate simulation
# sim = boids.Simulation(num_fears=2, num_boids=50, window_size=pg.Vector2(1200, 800))
# fear = boids.TUNING["influence_dist"]["fear"]

# # Add some predefined walls
# sim.addTestWalls()

# # Create lists to store positions of drones and sheep
# drone_positions = []
# sheep_positions = []

# while True:
    
#     sheeps = sim.data.boids
#     new_arr = []
#     for i in range(len(sheeps)):
#         coords = sheeps[i][0]
#         x = float(coords.x)
#         y = float(coords.y)
#         new_arr.append([x, y])
#     sheep = np.asarray(new_arr)

#     # Append current positions of sheep to the list
#     sheep_positions.append(sheep)


#     targets = push.Bucket.get_targets(sheep, 100, [600, 450], 6*0.174533)

#     if targets == False:
#         pg.quit()
#         break

#     for i in range(len(targets)):
#         sim.data.fear_targets[i] = pg.Vector2(targets[i][0], targets[i][1])
        
#     info = sim.stepTime()
#     # Append current positions of drones to the list
#     drone_positions.append([(float(fear.x), float(fear.y)) for fear in sim.data.fears])
    
#     if info == "quit":
#         pg.quit()

#         break


import boids
import pygame as pg
import push
import math
import numpy as np
import csv

# Add some predefined walls

# Run the simulation 10 times
for j in range(10):
    # Create lists to store positions of drones and sheep
    drone_positions = []
    sheep_positions = []

    # Initiate simulation
    sim = boids.Simulation(num_fears=2, num_boids=50, window_size=pg.Vector2(1200, 800))
    fear = boids.TUNING["influence_dist"]["fear"]

    # Add some predefined walls
    sim.addTestWalls()

    # Run the simulation until completion
    while True:
        sheeps = sim.data.boids
        new_arr = []
        for i in range(len(sheeps)):
            coords = sheeps[i][0]
            x = float(coords.x)
            y = float(coords.y)
            new_arr.append([x, y])
        sheep = np.asarray(new_arr)

        # Append current positions of sheep to the list
        sheep_positions.append(sheep)

        targets = push.Bucket.get_targets(sheep, 100, [600, 450], 6*0.174533)

        if targets == False:
            pg.quit()
            break

        for i in range(len(targets)):
            sim.data.fear_targets[i] = pg.Vector2(targets[i][0], targets[i][1])

        info = sim.stepTime()
        # Append current positions of drones to the list
        drone_positions.append([(float(fear.x), float(fear.y)) for fear in sim.data.fears])

        if info == "quit":
            pg.quit()

            break

    # Write the sheep positions to a CSV file
    with open(f'sheep_positions_{j+1}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(sheep_positions)

    # Write the drone positions to a CSV file
    with open(f'drone_positions_{j+1}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(drone_positions)
