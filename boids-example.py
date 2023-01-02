import boids
import pygame as pg

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50, render=True)

# Add some predefined walls
sim.addTestWalls()

# Change one of the fear position's target position
sim.data.fear_targets[1] = pg.Vector2(500, 500)
# Equiv to: sim.data.fear_targets[1].update(500, 500)

# Set the simulation running
sim.mainloop()