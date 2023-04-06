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
from matplotlib import pyplot as plt

# Add some predefined walls

# Run the simulation 10 times

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

sheep_x = []
sheep_y = []
for i in range(len(sheep_positions)):
    curr_x = sheep_positions[i][:,0]
    curr_y = sheep_positions[i][:,1]
    sheep_x.append(curr_x)
    sheep_y.append(curr_y)

sheep_x = np.asarray(sheep_x)
sheep_y = np.asarray(sheep_y)

sheep_y = 800-sheep_y

outer = np.array([[0,0],[1200,0],[1200,800],[0,800],[0,0]])
wall1 = np.array([[600,400],[600,800]])
wall2 = np.array([[600,0],[600,300]])

plt.plot(outer[:,0],outer[:,1],'r-',label = 'Field walls')
plt.plot(wall1[:,0],wall1[:,1],'r-')
plt.plot(wall2[:,0],wall2[:,1],'r-')

for i in range(50):
    plt.plot(sheep_x[:,i],sheep_y[:,i])

# for i in range(len(sheep_positions)):
#     curr_sheep = sheep_positions[i]
#     plt.plot(curr_sheep[:,0],curr_sheep[:,1])

plt.show()