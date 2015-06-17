import pylab
import nest
nest.Install("gridcellsmodule")

# Create border cells
border_cells = nest.Create("border_cell_generator",4)

# Set intrinsic firing rates
nest.SetStatus(border_cells, {"rate": 10.0})

# Set field size
nest.SetStatus(border_cells, {"field_size": 10.0})

# Set borders of arena
x_starts = [-50.0,  50.0,  50.0, -50.0]
y_starts = [ 50.0,  50.0, -50.0, -50.0]
x_ends   = [ 50.0,  50.0, -50.0, -50.0]
y_ends   = [ 50.0, -50.0, -50.0,  50.0]
for i in range(len(x_starts)):
    nest.SetStatus([border_cells[i]], {"border_start_x": x_starts[i], "border_start_y": y_starts[i]})
    nest.SetStatus([border_cells[i]], {  "border_end_x":   x_ends[i],   "border_end_y":   y_ends[i]})

# Create spike detectors
spike_detectors = nest.Create("spike_detector",4 , params={"withgid": True, "withtime": True})

# Connect spike detectors to border cells (one-to-one mapping)
nest.Connect(border_cells, spike_detectors)

# set time step for rat position changes
rat_dt = 20.0
nest.SetStatus(border_cells, {"rat_pos_dt": rat_dt})

#set simulation time (ms)
sim_time = 8000

# Create simple rat trajectory (scaled rectangle in same proportions as arena)
steps_per_border = int(sim_time / len(x_starts) / rat_dt)
rat_x = []
rat_y = []
scale = 4.0 / 5.0
for i in range(len(x_starts)):
    # start and end points of rat trajectory
    x_start = x_starts[i] * scale
    x_end  = x_ends[i] * scale
    y_start = y_starts[i] * scale
    y_end  = y_ends[i] * scale
    # x and y distances
    x_dist = x_end - x_start
    y_dist = y_end - y_start
    step_x = x_dist / steps_per_border
    step_y = y_dist / steps_per_border    
    for n in range(0, steps_per_border): rat_x.append(x_start + n*step_x)
    for m in range(0, steps_per_border): rat_y.append(y_start + m*step_y)
nest.SetStatus(border_cells, {"rat_pos_x": rat_x})
nest.SetStatus(border_cells, {"rat_pos_y": rat_y})

# run simulation
nest.Simulate(sim_time)

# get results
dSD = nest.GetStatus(spike_detectors,keys='events')
evs = []
ts = []
for d in dSD: 
    evs.append(d["senders"])
    ts.append(d["times"])

# plot results
pylab.figure(1)
for i in range(len(ts)):
    pylab.plot(ts[i], evs[i], ".")
pylab.show()
