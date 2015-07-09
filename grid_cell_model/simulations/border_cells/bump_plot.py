import h5py
import matplotlib.pyplot as mpl
import numpy as np
import scipy.io
from grid_cell_model.analysis.bumps import SingleBumpPopulation
from grid_cell_model.plotting.bumps import bumpPosition

trial_no = str(0)
spike_mon_type = 'spikeMon_e'

# open data file
data = h5py.File('output_dir/output_data/job00000_output.h5')

# loadsimulation data
print("Loading simulation data...")
senders = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['senders'])
times = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['times'])
Ne_x = float(d['trials'][str(trial_no)]['net_attr']['Ne_x'])
Ne_y = float(d['trials'][str(trial_no)]['net_attr']['Ne_y'])
sheetSize = (Ne_x, Ne_y)
dt = float(np.array(data['trials'][str(trial_no)]['options']['sim_dt']))

# plotting parameters
tstart = 0; tend = 1000; winLen = 1.0

# single bump population
singleBump = SingleBumpPopulation(senders, times, sheetSize)

# get gaussian fit
gauss_params = singleBump.bump_position(tstart, tend, dt, winLen)

# save params to matlab file
scipy.io.savemat('BumpParams.mat', mdict={'params':gauss_params})

#spikes = (senders,times)
#bumpPosition(spikes, sheetSize, tstart, tend, dt, winLen, units="s")

# close data file
data.close()
