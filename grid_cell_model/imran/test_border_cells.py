import nest
nest.Install("gridcellsmodule")

# Create border cells
border_cells = nest.Create("border_cell_generator",4)

# Set borders of arena
nest.SetStatus([border_cells[0]], {"border_start_x": -50.0, "border_start_y": -50.0, "border_end_x": 50.0, "border_end_y": 50.0})
nest.SetStatus([border_cells[1]], {"border_start_x": 50.0, "border_start_y": 50.0, "border_end_x": 50.0, "border_end_y": -50.0})
nest.SetStatus([border_cells[2]], {"border_start_x": 50.0, "border_start_y": -50.0, "border_end_x": -50.0, "border_end_y": -50.0})
nest.SetStatus([border_cells[3]], {"border_start_x": -50.0, "border_start_y": -50.0, "border_end_x": -50.0, "border_end_y": 50.0})

# Create spike detectors
spike_detectors = nest.Create("spike_detector",4)#, params={"withgid": True, "withtime": True})

# Connect spike detectors to border cells (one-to-one mapping)
nest.Connect(border_cells, spike_detectors)

# Create simple rat trajectory (tracking along borders)
x_positions = [-50.0, -25.0,  0.0, 25.0, 50.0, 50.0, 50.0,  50.0,  50.0,  25.0,   0.0, -25.0, -50.0, -50.0, -50.0, -50.0, -50.0]
y_positions = [ 50.0,  50.0, 50.0, 50.0, 50.0, 25.0,  0.0, -25.0, -50.0, -50.0, -50.0, -50.0, -50.0, -25.0,   0.0,  25.0,  50.0]
nest.SetStatus(border_cells, {"rat_pos_x": x_positions})
nest.SetStatus(border_cells, {"rat_pos_y": y_positions})

# set time step for rat position changes
rat_dt = 20.0
nest.SetStatus(border_cells, {"rat_pos_dt": rat_dt})

#set simulation time
sim_time = len(x_positions)*rat_dt + 10.0

# run simulation
nest.Simulate(sim_time)
