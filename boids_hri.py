import boids
import pygame as pg

sim = boids.Simulation(
    num_fears=1,
    num_boids=30,
    mouse_fear=True,
    image_save_type="hri",
    save_rate=1000,
    spawn_zone=pg.Rect([2397.05, -6989.29], [100,100]),
    camera_tracking=True
)

sim.addWallsFromHRI()
# sim.addTestWalls()

sim.mainloop()