from multiprocessing import Process, Pipe, set_start_method
import hri
import boids

set_start_method('spawn')

# Initialise pipe
parent_pipe, child_pipe = Pipe(duplex=True)

# Create HRI and pass pipe end
HRI = hri.Hri(parent_pipe)
p_hri = Process(target=HRI.mainloop)
p_hri.daemon = True
p_hri.start()

# Create boids and pass pipe end
sim = boids.Simulation(num_fears=2, num_boids=50, mouse_fear=True, image_save_type="hri", data_pipe=child_pipe)
sim.addWallsFromHRI()
p_sim = Process(target=sim.mainloop)
p_sim.start()