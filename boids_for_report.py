import boids
import pygame as pg

# Initialise simulation
sim = boids.Simulation(
    num_fears=0,
    num_boids=0,
    mouse_fear=False,
    window_size=pg.Vector2(800, 400),
    spawn_zone=pg.Rect(250,250,100,100)
)

# sim.addTestWalls(add_gate=False)
sim.addWallsFromHRI()

sim.mainloop()
