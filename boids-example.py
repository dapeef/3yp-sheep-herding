import boids
import pygame as pg

# Initiate simulation
sim = boids.Simulation(num_fears=2, num_boids=50)

# Add some predefined walls
sim.addTestWalls()

# Probs not used - add walls from HRI
# sim.addWallsFromHRI()

# Change one of the fear position's target position
sim.data.fear_targets[1] = pg.Vector2(500, 500)
# Equivalent to: sim.data.fear_targets[1].update(500, 500)

# Set the simulation running
# sim.mainloop()

while True:
    # sim.data.fear_targets[2] = 

    info = sim.stepTime()

    if info == "quit":
        pg.quit()

        break