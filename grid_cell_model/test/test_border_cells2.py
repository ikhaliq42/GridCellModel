import pylab
import nest
import scipy.io
import numpy as np
import sys
from grid_cell_model.analysis.grid_cells import SNSpatialRate2DRect
from matplotlib.pyplot import (figure, plot, pcolormesh, subplot2grid, savefig,
                                                colorbar, axis, xlabel, ylabel)

# Install nest
nest.Install("gridcellsmodule")

# Create border cells
border_cells = nest.Create("border_cell_generator",4)

# Set intrinsic firing rates
nest.SetStatus(border_cells, {"rate": 10.0})

# Set field size
nest.SetStatus(border_cells, {"field_size": 10.0})

# Create spike detectors
spike_detectors = nest.Create("spike_detector",4 , params={"withgid": True, "withtime": True})

# Connect spike detectors to border cells (one-to-one mapping)
nest.Connect(border_cells, spike_detectors)

# Load rat trajectory (scaled rectangle in same proportions as arena)
data = scipy.io.loadmat("../../data/Sargolini_2006")

# set time step for rat position changes
rat_dt = float(data['dt'].flatten()) * 1000
nest.SetStatus(border_cells, {"rat_pos_dt": rat_dt})

# set rat trajectory in simulation
rat_pos_x = data['pos_x'].flatten()
rat_pos_y = data['pos_y'].flatten()
nest.SetStatus(border_cells, {"rat_pos_x": rat_pos_x})
nest.SetStatus(border_cells, {"rat_pos_y": rat_pos_y})

#set simulation time (ms)
sim_time = len(rat_pos_x) * rat_dt

# Set borders of arena
x_starts = [min(rat_pos_x), max(rat_pos_x), max(rat_pos_x), min(rat_pos_x)]
y_starts = [max(rat_pos_y), max(rat_pos_y), min(rat_pos_y), min(rat_pos_y)]
x_ends   = [max(rat_pos_x), max(rat_pos_x), min(rat_pos_x), min(rat_pos_x)]
y_ends   = [max(rat_pos_y), min(rat_pos_y), min(rat_pos_y), max(rat_pos_y)]
arena_dim_x = max(x_starts)-min(x_starts)
arena_dim_y = max(y_starts)-min(y_starts)
for i in range(len(x_starts)):
    nest.SetStatus([border_cells[i]], {"border_start_x": x_starts[i], "border_start_y": y_starts[i]})
    nest.SetStatus([border_cells[i]], {  "border_end_x":   x_ends[i],   "border_end_y":   y_ends[i]})

# run simulation
nest.Simulate(sim_time)

# get results
dSD = nest.GetStatus(spike_detectors,keys='events')
evs = []
ts = []
for d in dSD: 
    evs.append(d["senders"])
    ts.append(d["times"])

# set smoothing sigma
smoothingSigma = 3.0

# create a spatial rate map
rateMaps = []
for i in range(len(ts)):
    print "\nGenerating spatial maps...", i+1, " of ", len(ts)
    rateMap, xedges, yedges = SNSpatialRate2DRect(ts[i], rat_pos_x, rat_pos_y, rat_dt, 
                                        arena_dim_x, arena_dim_y, smoothingSigma)
    rateMap *= 1e3 # should be Hz
    rateMaps.append(rateMap)

# Draw plot    
X, Y = np.meshgrid(xedges, yedges)
for i in range(len(rateMaps)):
    print "\nCreating plots...", i+1, " of ", len(rateMaps) 
    figure(i)
    pcolormesh(X, Y, rateMaps[i])
    colorbar()
    axis('equal')
    axis('off')
    print("Saving plot")
    savefig('{0}{1}_rateMap.png'.format("border_cell", i))


