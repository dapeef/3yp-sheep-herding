import boids
import pygame as pg

# Initialise simulation
sim = boids.Simulation(
    num_fears=1,
    num_boids=50,
    mouse_fear=True,
    window_size=pg.Vector2(1500, 900),
    spawn_zone=pg.Rect(250,250,100,100)
)

sim.addTestWalls(add_gate=False)

# sim.data.fear_targets[1] = pg.Vector2(200,200)

sim.mainloop()
