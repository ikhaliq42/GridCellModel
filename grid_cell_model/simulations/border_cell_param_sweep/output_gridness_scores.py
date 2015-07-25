# same as analysis but for rectangular arenas

import h5py
import numpy as np
import math
import sys
import argparse
import os.path

from gridcells.analysis import information_specificity
from grid_cell_model.analysis.grid_cells import SNSpatialRate2DRect, cellGridnessScoreRect

parser = argparse.ArgumentParser()
parser.add_argument("sim_name", type=str, help="directory path of simulation data")
parser.add_argument("--spike_mon_type", type=str, default='spikeMon_e')
parser.add_argument("--neuron_idx", type=int, help="Index of neuron to analyse, default = 0", default=0)
parser.add_argument("--trial_no", type=int, help="Trial number, default = 0", default=0)
args = parser.parse_args()

bcConnStds          = [1.0, 2.0, 3.0, 4.0, 5.0]
bc_field_stds       = [1.0, 5.0, 10.0, 15.0, 20.0]
results_G_i         = np.zeros((len(bcConnStds),len(bc_field_stds)))
#results_crossCorr_i = np.zeros((len(bcConnStds),len(bc_field_stds)))
#results_angles_i    = np.zeros((len(bcConnStds),len(bc_field_stds)))

for i in range(len(bcConnStds)):

    for j in range(len(bc_field_stds)):
    
        trial_no = args.trial_no
        spike_mon_type = args.spike_mon_type
        neuron_idx = args.neuron_idx
        sim_name = args.sim_name
        assert not (args.sim_name == "") 
        label = 'bcConnStd_{0}_bc_field_std_{1}'.format(int(bcConnStds[i]),int(bc_field_stds[j]))
        data = h5py.File(args.sim_name + '/' + label + '/job00000_output.h5', 'r+')
        
        # read data
        results_G_i[i,j] = float(np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['analysis']['neuron_'+str(neuron_idx)]['Gridness_Score']))
        
        # close data file
        data.close()

#output results
print("Gridness Scores:")
print(results_G_i)
