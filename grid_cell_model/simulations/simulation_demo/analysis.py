import h5py
import numpy as np
import math
import sys
import argparse

from matplotlib.pyplot import (figure, plot, pcolormesh, subplot2grid, savefig,
        colorbar, axis, xlabel, ylabel)

from gridcells.analysis import information_specificity
from grid_cell_model.analysis.grid_cells import (SNSpatialRate2D, SNAutoCorr,
                                    cellGridnessScore, occupancy_prob_dist,
                                    spatial_sparsity)

parser = argparse.ArgumentParser()
parser.add_argument("sim_name", type=str, help="directory path of simulation data")
parser.add_argument("--neuron_idx", type=int, help="Index of neuron to analyse, default = 0", default=0)
parser.add_argument("--trial_no", type=int, help="Trial number, default = 0", default=0)
args = parser.parse_args()

noise = 'demo_output_data'
trial_no = args.trial_no
neuron_idx = args.neuron_idx
arena_diam = 180.0
smoothingSigma=3.0
sim_name = args.sim_name
args = parser.parse_args()

# open data file
assert not (args.sim_name == "") 
data = h5py.File(args.sim_name + '/' + noise + '/job00000_output.h5', 'r+')

# load simulation data
print("Loading simulation data...")
senders = np.array(data['trials'][str(trial_no)]['spikeMon_e']['events']['senders'])
times = np.array(data['trials'][str(trial_no)]['spikeMon_e']['events']['times'])
rat_pos_x = np.array(data['net_params']['net_attr']['rat_pos_x'])
rat_pos_y = np.array(data['net_params']['net_attr']['rat_pos_y'])
rat_dt = float(np.array(data['net_params']['net_attr']['rat_dt']))
sim_time = float(np.array(data['net_params']['options']['time']))
sim_dt = float(np.array(data['net_params']['options']['sim_dt']))
theta_start_t = float(np.array(data['net_params']['options']['theta_start_t']))

# data path
data_path = '/trials/0/spikeMon_e/events/'

# calculate rate map if not already present in data, otherwise load from data
if ('analysis/neuron_' + str(neuron_idx) + '/rateMap') not in \
                               data['trials'][str(trial_no)]['spikeMon_e']['events']: 
    # extract single neuron spike times
    spikes = np.zeros(sum(senders == neuron_idx))
    j = 0
    print("Extracting single neuron data...")
    length = len(senders)
    for i in range(length):
        progress = round(float(i)/length*100.0,1)
        sys.stdout.write('\rProgress: %g %%' % (progress))
        if (senders[i] == neuron_idx): spikes[j] = times[i]; j += 1
    
    # rat position data needs to be aligned with spike times
    print("\nAligning rat position data to spike times...")
    length = int(sim_time/sim_dt); step = int(rat_dt/sim_dt)
    pos_x = np.zeros(length); pos_y = np.zeros(length)
    for i in range(len(rat_pos_x)-1):
        progress = round(float(i)/len(rat_pos_x)*100.0,1)
        sys.stdout.write('\rProgress: %g %%' % (progress))
        x_mov = rat_pos_x[i+1] - rat_pos_x[i]
        y_mov = rat_pos_y[i+1] - rat_pos_y[i]
        for j in range(step):
            # interpolate positions
            pos_x[i*step + j] = rat_pos_x[i] + x_mov * j / step
            pos_y[i*step + j] = rat_pos_y[i] + y_mov * j / step
    
    # create a spatial rate map if one does not already exist
    print("\nGenerating spatial map...")    
    rateMap, xedges, yedges = SNSpatialRate2D(spikes, pos_x, pos_y, rat_dt, 
                                        arena_diam, smoothingSigma)
    rateMap *= 1e3 # should be Hz
    X, Y = np.meshgrid(xedges, yedges)
    data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/rateMap', data=rateMap)
    data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/X', data=X)
    data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Y', data=Y)
else:
    print("\nRate map already exists - loading.")
    rateMap = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/rateMap'))
    X = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/X'))
    Y = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Y'))

'''
# create an occupancy probablity distribution for animal in arena if not already exists
if ('/analysis/occupancy_prob_' + str(neuron_idx)) not in \
                               data['trials'][str(trial_no)]['spikeMon_e']['events']:
    px = occupancy_prob_dist_rect(spikes, pos_x, pos_y, 
                                             arena_dim_x, arena_dim_y, smoothingSigma)
else:
    print("\Occupancy probability already exists - loading.")
    px = np.array(data.get(data_path + 'occupancy_prob_neuron' + str(neuron_idx)))

# create information specificity if not already exists
if ('occupancy_prob_' + str(neuron_idx)) not in 
                               data['trials'][str(trial_no)]['spikeMon_e']['events']:
    info = information_specificity(rateMap, px)
    sparsity = spatial_sparsity(rateMap, px)
    out['info_specificity'] = info_e
    out['sparsity'] = sparsity_e
'''

# Draw plot
print("\nCreating plot...") 
figure()
pcolormesh(X, Y, rateMap)
colorbar()
axis('equal')
axis('off')
print("Saving plot")
savefig('{0}rateMap_neuron{1}.png'.format(sim_name+'/'+noise+'/', neuron_idx))

print("")
# close data file
data.close()


