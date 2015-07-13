import h5py; import numpy as np
import grid_cell_model.plotting.connections
import matplotlib.pyplot as plt
import scipy.io
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", type=str, help="Path to simulation data")
parser.add_argument("--noise", type=str, help="Noise sigma", default = '150pA')
parser.add_argument("--type", type=str, default='border', help="Neuron type: place or border")
parser.add_argument("--trial_no", type=int, default=0, help="Trial number")
o = parser.parse_args()

trial_no = o.trial_no
path = o.path
noise = o.noise
type = o.type

if type=='place':
    type_key = 'P->E' 
else:
    type_key = 'B->E'

plotter = grid_cell_model.plotting.connections.plot2DWeightMatrix

# get connections
data = h5py.File(path +'/' + noise + '/job00000_output.h5','r')
conns = np.array(data['trials'][str(trial_no)]['connections'][type_key])
conns = conns.transpose()

# arrange data in to a dictionary
connections = {}
for i in range(len(conns)):
    connections[type + str(i)] = conns[i].reshape(30,34)

#save to matlab file
scipy.io.savemat(path +'/' + noise + '/ConnMatrix_trial_' + str(trial_no) + '.mat', mdict=connections)
#plot data for first and second border cell
#ax = plotter(connections[type + str(1)])
#plt.show()
