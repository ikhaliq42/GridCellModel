import h5py
import matplotlib.pyplot as mpl
import numpy as np
import scipy.io
import argparse
from grid_cell_model.analysis.bumps import SingleBumpPopulation
from grid_cell_model.plotting.bumps import bumpPosition

parser = argparse.ArgumentParser()
parser.add_argument("sim_name", type=str, help="directory path of simulation data")
parser.add_argument("--spike_mon_type", type=str, default='spikeMon_e')
parser.add_argument("--trial_no", type=int, help="Trial number, default = 0", default=0)
parser.add_argument("--noise", type=str, help="Noise sigma of simulation", default='150pA')
args = parser.parse_args()

trial_no = args.trial_no
spike_mon_type = args.spike_mon_type
sim_name = args.sim_name
noise = args.noise

# open data file
data = h5py.File(sim_name + '/' + noise + '/' + 'job00000_output.h5')

# loadsimulation data
print("Loading simulation data...")
senders = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['senders'])
times = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['times'])
Ne_x = int(np.array(data['trials'][str(trial_no)]['net_attr']['Ne_x']))
Ne_y = int(np.array(data['trials'][str(trial_no)]['net_attr']['Ne_y']))
sheetSize = (Ne_x, Ne_y)
dt = float(np.array(data['trials'][str(trial_no)]['options']['sim_dt']))
tstart = float(np.array(data['trials'][str(trial_no)]['options']['theta_start_t']))
tend = float(np.array(data['trials'][str(trial_no)]['options']['time']))
# plotting parameters
winLen = 1.0

# single bump population
singleBump = SingleBumpPopulation(senders, times, sheetSize)

# get gaussian fit
gauss_params = singleBump.bump_position(tstart, tend, dt, winLen)

# save params to matlab file
scipy.io.savemat(sim_name + '/' + noise + '/' + 'BumpParams_trial' + str(trial_no) + '.mat', mdict={'params' :gauss_params})

# close data file
data.close()
