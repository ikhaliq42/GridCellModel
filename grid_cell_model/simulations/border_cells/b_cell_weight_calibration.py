import h5py
import matplotlib.pyplot as mpl
import numpy as np
import scipy.io
import scipy.stats
import argparse
from grid_cell_model.analysis.spikes import slidingFiringRateTuple

parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="Path to simulation data")
parser.add_argument("--noise", type=int, default=150, help="Noise sigma")
parser.add_argument("--trial_no", type=int, default=0, help="index number of trial") 
o = parser.parse_args()

trial_no = o.trial_no
path = o.path
noise = str(o.noise) + 'pA'

# open data file
data = h5py.File(path +'/' + noise + '/job00000_output.h5','r')

# ****************** load simulation data *************************************************
print("Loading simulation data...")
# grid cell spikes
e_senders = np.array(data['trials'][str(trial_no)]['spikeMon_e']['events']['senders'], dtype=np.int32)
e_times = np.array(data['trials'][str(trial_no)]['spikeMon_e']['events']['times'], dtype=np.float32)
# border cell spikes
#b_senders = np.array(data['trials'][str(trial_no)]['spikeMon_b']['events']['senders'], dtype=np.int32)
#b_times = np.array(data['trials'][str(trial_no)]['spikeMon_b']['events']['times'], dtype=np.float32)
# grid cell population size
N_e = len(data['trials'][str(trial_no)]['net_attr']['E_pop'])
# border cell population size
#N_b = len(data['trials'][str(trial_no)]['net_attr']['border_cells'])
#N_b = max(b_senders)+1
# time step
dt = float(np.array(data['trials'][str(trial_no)]['options']['sim_dt']))
#simulation time
tstart = float(np.array(data['trials'][str(trial_no)]['options']['theta_start_t']))
tend = float(np.array(data['trials'][str(trial_no)]['options']['time']))
# *****************************************************************************************

# other parameters
winLen = 1.0

# estimate firing rates for both populations
print("Estimating firing rate (sliding window method)...")
e_spikes = e_senders, e_times
#b_spikes = b_senders, b_times
e_firing_rates, _ = slidingFiringRateTuple(e_spikes, N_e, tstart, tend, dt, winLen, True)
#b_firing_rates, _ = slidingFiringRateTuple(b_spikes, N_b, tstart, tend, dt, winLen, True)

# calculate weight matrix (row are b cells, columns are e cells)
print("Calculating weight matix...")
#W = b_firing_rates.dot(e_firing_rates.transpose())
W = e_firing_rates.sum(1)
# also get spike counts for each grid cell for information purposes
spike_counts_e = scipy.stats.itemfreq(e_senders)

# normalise weightings
print("Normalising...")
w_max = W.max()
for i in range(W.shape[0]):    
    if w_max != 0.0: W[i] = W[i] / w_max

# save params to matlab file
scipy.io.savemat(path +'/' + noise + '/bc_Weights_trial' + str(trial_no)  + '.mat', 
                             mdict={'WeightMatrix': W, 
                                  'spike_counts_e':spike_counts_e})

# close data file
data.close()
