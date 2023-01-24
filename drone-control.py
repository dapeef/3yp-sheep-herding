import boids
import pygame as pg

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50, render=True)

# Add some predefined walls
sim.addTestWalls()

while True:
    #Write your shit here
    #fear target index indicates the drone which is being controlled
    # Gate centre = (600, 450)
    # sim.data.boids          #sheep positions

    # sim.data.fear_targets[0] = pg.Vector2(x, y)
    # sim.data.fear_targets[0].update(x, y)



    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break