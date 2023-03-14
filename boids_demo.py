import boids
import pygame as pg

# Initialise simulation
sim = boids.Simulation(
    num_fears=2,
    num_boids=50,
    mouse_fear=True,
    window_size=pg.Vector2(1000, 700)
)

# Add some predefined walls
sim.addTestWalls()

# Change one of the fear position's target position
sim.data.fears[1] = pg.Vector2(950, 650)
sim.data.fear_targets[1] = pg.Vector2(50, 50)

# Set the simulation running
sim.mainloop()