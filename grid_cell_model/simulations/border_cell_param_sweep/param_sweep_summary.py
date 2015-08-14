# same as analysis but for rectangular arenas

import h5py
import numpy as np
import math
import sys
import argparse
import os.path
import csv

from gridcells.analysis import information_specificity
from grid_cell_model.analysis.grid_cells import SNSpatialRate2DRect, cellGridnessScoreRect

# ********************************************************************************************************

def get_gridness_scores(bcConnStds, bc_field_stds, trial_no, spike_mon_type, neuron_idx, sim_name):

    results  = np.zeros((len(bcConnStds),len(bc_field_stds)))
    
    for i in range(len(bcConnStds)):

        for j in range(len(bc_field_stds)):    

            label = 'bcConnStd_{0}_bc_field_std_{1}'.format(int(bcConnStds[i]),int(bc_field_stds[j]))
            data = h5py.File(sim_name + '/' + label + '/analysis.h5', 'r')
            
            # read data
            results[i,j] = float(np.array(data['trials'][str(trial_no)][spike_mon_type] \
                                   ['events']['analysis']['neuron_'+str(neuron_idx)]['Gridness_Score']))
        
            # close data file
            data.close()

    # return scores
    return results

# ********************************************************************************************************

parser = argparse.ArgumentParser()
parser.add_argument("--spike_mon_type", type=str, default='spikeMon_e')
parser.add_argument("--neuron_idx", type=int, help="Index of neuron to analyse, default = 0", default=0)
parser.add_argument("--trial_no", type=int, help="Trial number, default = 0", default=0)
args = parser.parse_args()

# command line parameters
trial_no = args.trial_no
spike_mon_type = args.spike_mon_type
neuron_idx = args.neuron_idx

# other parameters
margin              = 0
cell_counts         = [2  , 4  ,  6  ,  8  , 10  ]
bcConnStds          = [1.0, 2.0,  3.0,  4.0,  5.0]
bc_field_stds       = [1.0, 5.0, 10.0, 15.0, 20.0]

# loop through all simulations to get results
results_with_place     = np.zeros((len(cell_counts),len(bcConnStds),len(bc_field_stds)))
results_without_place  = np.zeros((len(cell_counts),len(bcConnStds),len(bc_field_stds)))
for n in range(len(cell_counts)):
    sim_name = 'param_sweep_with_place_margin_{0}_bc_{1}'.format(margin, cell_counts[n]) 
    results_with_place[n] = get_gridness_scores(bcConnStds, bc_field_stds, trial_no, spike_mon_type, neuron_idx, sim_name)
    sim_name = 'param_sweep_without_place_margin_{0}_bc_{1}'.format(margin, cell_counts[n])
    results_without_place[n] = get_gridness_scores(bcConnStds, bc_field_stds, trial_no, spike_mon_type, neuron_idx, sim_name)

#output results to file
file_name = 'param_sweep_summary_margin_{0}_neuron_idx{1}.csv'.format(margin,neuron_idx)
with open(file_name, 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for place_on_off in ["On","Off"]:
        for n in range(len(cell_counts)):
            for i in range(len(bcConnStds)):
                for j in range(len(bc_field_stds)):
                    output =  ["Neuron Index"]
                    output.append(neuron_idx)
                    output.append("Place Cells")
                    output.append(place_on_off)
                    output.append("Border Cells")
                    output.append(cell_counts[n])
                    output.append("bcConnStd")
                    output.append(bcConnStds[i])
                    output.append("bc_field_stds")
                    output.append(bc_field_stds[j])
                    output.append("gridness_score")
                    score = results_with_place[n,i,j] if (place_on_off == "On") \
                                                     else results_without_place[n,i,j]
                    output.append(score) 
                    writer.writerow(output)
                

