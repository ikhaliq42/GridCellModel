import h5py
import matplotlib.pyplot as mpl
import numpy as np
import scipy.io
import scipy.stats
import argparse
from grid_cell_model.analysis.spikes import slidingFiringRateTuple

#*********************************************************************************************

def spike_trains(senders, times, nSenders, end, dt):
    print("Generating spike train...")
    nBins = int(end/dt)
    #import pdb; pdb.set_trace()
    spike_trains = np.zeros((nSenders,nBins))
    spike_times  = np.zeros((nSenders,nBins))
    for i in range(nSenders):
        i_times = np.extract(senders==i,times)
        for t in (i_times): 
            spike_trains[i,t] += 1
            spike_times[i,t]  = t
    return spike_trains, spike_times     

def sliding_window(a, window):
    print("Calculating rates (sliding window)...")
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

#********************************************************************************************

parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="Path to simulation data")
parser.add_argument("--noise", type=int, default=150, help="Noise sigma")
parser.add_argument("--ntrials", type=int, default=1, help="number of trials") 
parser.add_argument("--recalc", type=bool, help="Force recals, default = 0", default=0)
o = parser.parse_args()

ntrials = o.ntrials
path = o.path
noise = str(o.noise) + 'pA'
recalc = o.recalc

# open data file
data = h5py.File(path +'/' + noise + '/job00000_output.h5')

for trial_no in range(ntrials):
    print("Trial {0}...".format(trial_no))

    # ****************** load simulation data *************************************************
    print("Loading simulation data...")
    # grid cell spikes
    e_senders = np.array(data['trials'][str(trial_no)]['spikeMon_e']['events']['senders'], dtype=np.int32)
    e_times = np.array(data['trials'][str(trial_no)]['spikeMon_e']['events']['times'], dtype=np.float32)
    # border cell spikes
    b_senders = np.array(data['trials'][str(trial_no)]['spikeMon_b']['events']['senders'], dtype=np.int32)
    b_times = np.array(data['trials'][str(trial_no)]['spikeMon_b']['events']['times'], dtype=np.float32)
    # grid cell population size
    N_e = len(data['trials'][str(trial_no)]['net_attr']['E_pop'])
    # border cell population size
    N_b = len(data['trials'][str(trial_no)]['net_attr']['border_cells'])
    # time step
    dt = float(np.array(data['trials'][str(trial_no)]['options']['sim_dt']))
    #simulation time
    tstart = 0  #float(np.array(data['trials'][str(trial_no)]['options']['theta_start_t']))
    tend = float(np.array(data['trials'][str(trial_no)]['options']['time']))
    # *****************************************************************************************

    # other parameters
    winLen = 1.0
    data_path_e = '/trials/'+str(trial_no)+'/spikeMon_e/events/'
    data_path_b = '/trials/'+str(trial_no)+'/spikeMon_b/events/'

    # estimate firing rates for both populations
    e_spike_trains, e_firing_rate_times = spike_trains(e_senders, e_times, N_e, tend, dt)
    e_firing_rates = np.mean(sliding_window(e_spike_trains, winLen), -1)
    b_spike_trains, b_firing_rate_times = spike_trains(b_senders, b_times, N_b, tend, dt)
    b_firing_rates = np.mean(sliding_window(b_spike_trains, winLen), -1)

    # ********************* save results to hdf5 file ***********************************************

    # e cells
    if ('firing_rates') in data['trials'][str(trial_no)]['spikeMon_e']['events']: 
        if recalc: 
            del data[data_path_e + 'firing_rates']
            data.create_dataset(data_path_e + 'firing_rates', data=e_firing_rates)
    else:
        data.create_dataset(data_path_e + 'firing_rates', data=e_firing_rates)
    if ('firing_rate_times') in data['trials'][str(trial_no)]['spikeMon_e']['events']:
        if recalc:
            del data[data_path_e + 'firing_rate_times']
            data.create_dataset(data_path_e + 'firing_rate_times', data=e_firing_rate_times)
    else:
        data.create_dataset(data_path_e + 'firing_rate_times', data=e_firing_rate_times)

    # border cells	
    if ('firing_rates') in data['trials'][str(trial_no)]['spikeMon_b']['events']:
        if recalc: 
            del data[data_path_b + 'firing_rates']
            data.create_dataset(data_path_b + 'firing_rates', data=b_firing_rates)
    else:
        data.create_dataset(data_path_b + 'firing_rates', data=b_firing_rates)
    # border cells
    if ('firing_rate_times') in data['trials'][str(trial_no)]['spikeMon_b']['events']:
        if recalc:
            del data[data_path_b + 'firing_rate_times']
            data.create_dataset(data_path_b + 'firing_rate_times', data=b_firing_rate_times)
    else:
        data.create_dataset(data_path_b + 'firing_rate_times', data=b_firing_rate_times)

    # ************************************************************************************************
        
#scipy.io.savemat(path +'/' + noise + '/firing_rates' + str(trial_no)  + '.mat', 
#                        mdict={'e_firing_rates': e_firing_rates, 'b_firing_rates': b_firing_rates,
#                        'spike_counts_e':spike_counts_e, 'spike_counts_b':spike_counts_b})

# close data file
data.close()
