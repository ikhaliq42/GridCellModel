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
#parser.add_argument("--recalc", type=bool, help="Force recals, default = 0", default=0)
args = parser.parse_args()

bcConnStds          = [1.0, 2.0, 3.0, 4.0, 5.0]
bc_field_stds       = [1.0, 5.0, 10.0, 15.0, 20.0]
#results_G_i         = np.zeros((len(bcConnStds),len(bc_field_stds)))
#results_crossCorr_i = np.zeros((len(bcConnStds),len(bc_field_stds)))
#results_angles_i    = np.zeros((len(bcConnStds),len(bc_field_stds)))

for i in range(len(bcConnStds)):

    for j in range(len(bc_field_stds)):
    
        trial_no = args.trial_no
        spike_mon_type = args.spike_mon_type
        neuron_idx = args.neuron_idx
        arenaDim_x = 180.0; arenaDim_y = 180.0
        smoothingSigma=3.0
        sim_name = args.sim_name
        minGridnessT = 0.0
        #args = parser.parse_args()
        #recalc = args.recalc
        # open data file
        assert not (args.sim_name == "") 
        label = 'bcConnStd_{0}_bc_field_std_{1}'.format(int(bcConnStds[i]),int(bc_field_stds[j]))
        data = h5py.File(args.sim_name + '/' + label + '/job00000_output.h5', 'r+')

        # load simulation data
        print('\n'); print(label)
        print("Loading simulation data...")
        #senders = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['senders'])
        times = np.array(data['trials'][str(trial_no)][spike_mon_type]['events']['times'])
        #rat_pos_x = np.array(data['trials'][str(trial_no)]['net_attr']['rat_pos_x'])
        #rat_pos_y = np.array(data['trials'][str(trial_no)]['net_attr']['rat_pos_y'])
        #rat_dt = float(np.array(data['trials'][str(trial_no)]['net_attr']['rat_dt']))
        #sim_time = float(np.array(data['trials'][str(trial_no)]['options']['time']))
        #sim_dt = float(np.array(data['trials'][str(trial_no)]['options']['sim_dt']))
        #theta_start_t = float(np.array(data['trials'][str(trial_no)]['options']['theta_start_t']))
        gridSep = float(np.array(data['trials'][str(trial_no)]['options']['gridSep']))
        
        # data path
        data_path = '/trials/'+str(trial_no)+'/'+spike_mon_type+'/events/'

        print("Loading Rate Map")
        rateMap = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/rateMap'))
        X = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/X'))
        Y = np.array(data.get(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Y'))
            
        # Calculate gridness score
        print("Caclulating gridness scores")
        G_i, crossCorr_i, angles_i = cellGridnessScoreRect(rateMap, arenaDim_x, arenaDim_y,
                                                           smoothingSigma, gridSep/2)
        # Gridness score valid only when T >= minGridnessT
        lastSpikeT = times[-1] if len(times) != 0 else np.nan
        if lastSpikeT >= minGridnessT:
            pass
            #print "\ngridness score = " , G_i
            #print "gridness correlation = " , crossCorr_i
            #print "gridness angles = " , angles_i
        else:
            #print "Simulation too short, Gridness score NaN"
            G_i         = np.nan
            crossCorr_i = np.nan
            angles_i    = np.nan
            
        if ('analysis/neuron_' + str(neuron_idx) + '/Gridness_Score') in \
                      data['trials'][str(trial_no)][spike_mon_type]['events']:
            del data[data_path + 'analysis/neuron_' +str(neuron_idx) + '/Gridness_Score']
            
        if ('analysis/neuron_' + str(neuron_idx) + '/Cross_Correlation') in \
                      data['trials'][str(trial_no)][spike_mon_type]['events']:
            del data[data_path + 'analysis/neuron_' +str(neuron_idx) + '/Cross_Correlation']
            
        if ('analysis/neuron_' + str(neuron_idx) + '/Angles') in \
                      data['trials'][str(trial_no)][spike_mon_type]['events']:
            del data[data_path + 'analysis/neuron_' +str(neuron_idx) + '/Angles']
            
        data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Gridness_Score', data=G_i)
        data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Cross_Correlation', data=crossCorr_i)
        data.create_dataset(data_path + 'analysis/neuron_' +str(neuron_idx) + '/Angles', data=angles_i)

        # close data file
        data.close()