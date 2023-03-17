import pygame as pg
import boids

# Initialise simulation
sim = boids.Simulation(
    num_fears=1,
    num_boids=50,
    mouse_fear=True,
    window_size=pg.Vector2(1000, 700),
    image_save_type="dataset"
)

sim.addTestWalls(add_gate=False)

sim.mainloop()
