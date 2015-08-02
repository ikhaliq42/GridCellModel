# same as analysis but for rectangular arenas

import h5py
import numpy as np
import math
import sys
import argparse
import os.path

from matplotlib.pyplot import (figure, plot, pcolormesh, subplot2grid, savefig,
        colorbar, axis, xlabel, ylabel)

from gridcells.analysis import information_specificity
from grid_cell_model.analysis.grid_cells import SNSpatialRate2DRect, cellGridnessScoreRect

parser = argparse.ArgumentParser()
parser.add_argument("sim_name", type=str, help="directory path of simulation data")
parser.add_argument("--spike_mon_type", type=str, default='spikeMon_e')
parser.add_argument("--neuron_idx", type=int, help="Index of neuron to analyse, default = 0", default=0)
parser.add_argument("--trial_no", type=int, help="Trial number, default = 0", default=0)
parser.add_argument("--recalc", type=bool, help="Force recals, default = 0", default=0)
parser.add_argument("--replot", type=bool, help="Force re-plot, default = 0", default=0)
parser.add_argument("--sub_sim", type=str, help="sub simulation name", default='150pA')
args = parser.parse_args()

sub_sim = args.sub_sim
trial_no = args.trial_no
spike_mon_type = args.spike_mon_type
neuron_idx = args.neuron_idx
arenaDim_x = 180.0; arenaDim_y = 180.0
smoothingSigma=3.0
sim_name = args.sim_name
minGridnessT = 0.0
args = parser.parse_args()
recalc = args.recalc
replot = args.replot
# open data file
assert not (args.sim_name == "") 
data = h5py.File(args.sim_name + '/' + sub_sim + '/job00000_output.h5', 'r+')

# load simulation data
print("Loading simulation data...")
senders = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['senders'])
times = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['times'])
rat_pos_x = np.array(data['trials'][str(trial_no)]['net_attr']['rat_pos_x'])
rat_pos_y = np.array(data['trials'][str(trial_no)]['net_attr']['rat_pos_y'])
rat_dt = float(np.array(data['trials'][str(trial_no)]['net_attr']['rat_dt']))
sim_time = float(np.array(data['trials'][str(trial_no)]['options']['time']))
sim_dt = float(np.array(data['trials'][str(trial_no)]['options']['sim_dt']))
theta_start_t = float(np.array(data['trials'][str(trial_no)]['options']['theta_start_t']))
gridSep = float(np.array(data['trials'][str(trial_no)]['options']['gridSep']))
# data path
data_path = '/trials/'+str(trial_no)+'/'+spike_mon_type+'/events/'

# calculate rate map if not already present in data, otherwise load from data
import pdb; pdb.set_trace()
if ('analysis/neuron_' + str(neuron_idx) + '/rateMap') not in \
              data['trials'][str(trial_no)][spike_mon_type]['events'] or recalc: 
    # extract single neuron spike times
    spikes = np.extract(senders == neuron_idx, times)
     
    # create a spatial rate map if one does not already exist
    print("\nGenerating spatial map...")   
    
    rateMap, xedges, yedges = SNSpatialRate2DRect(spikes, rat_pos_x, rat_pos_y, rat_dt, 
                                               arenaDim_x, arenaDim_y, smoothingSigma)
    X, Y = np.meshgrid(xedges, yedges)
    rateMap *= 1e3 # should be Hz
    if recalc: 
        del data[data_path + 'analysis/neuron_' +str(neuron_idx) + '/rateMap']
        del data[data_path + 'analysis/neuron_' +str(neuron_idx) + '/X']
        del data[data_path + 'analysis/neuron_' +str(neuron_idx) + '/Y']
    data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/rateMap', data=rateMap)
    data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/X', data=X)
    data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Y', data=Y)
else:
    print("\nRate map already exists - loading. (Use--recalc=1 to overwrite.)")
    rateMap = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/rateMap'))
    X = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/X'))
    Y = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Y'))

# close data file
data.close()

# Calculate gridness score
G_i, crossCorr_i, angles_i = cellGridnessScoreRect(rateMap, arenaDim_x, arenaDim_y,
                                                   smoothingSigma, gridSep/2)
# Gridness score valid only when T >= minGridnessT
lastSpikeT = times[-1] if len(times) != 0 else np.nan
if lastSpikeT >= minGridnessT:
    print "\ngridness score = " , G_i
    #print "gridness correlation = " , crossCorr_i
    #print "gridness angles = " , angles_i
else:
    print "Simulation too short, Gridness score NaN"

# Draw ratemap plots
path = '{0}trial_{1}_rateMap_{2}_{3}.png'.format(sim_name+'/'+sub_sim+'/',str(trial_no) ,spike_mon_type, neuron_idx)
if not os.path.exists(path) or replot==1:
    print("\nCreating plot...") 
    figure()
    pcolormesh(X, Y, rateMap)
    colorbar()
    axis('equal')
    axis('off')
    print("Saving plot")
    savefig(path)
else:
	print("\nFigure already exists; use --replot=1 to overwrite.")




