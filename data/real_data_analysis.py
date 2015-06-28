import numpy as np
import scipy.io
import math
import sys

from matplotlib.pyplot import (figure, plot, pcolormesh, subplot2grid, savefig,
        colorbar, axis, xlabel, ylabel)

#from gridcells.analysis import information_specificity
from grid_cell_model.analysis.grid_cells import (SNSpatialRate2DRect, cellGridnessScoreRect)


smoothingSigma=3.0
source_data = 'Sargolini_2006_t2c1.mat'
minGridnessT = 0.0

# open data file 
data = scipy.io.loadmat(source_data)

# load simulation data
print("Loading simulation data...")
spikes = data['ts'].flatten()
rat_pos_x = data['pos_x'].flatten()
rat_pos_y = data['pos_y'].flatten()
arena_dim_x = 100 # max(rat_pos_x) - min(rat_pos_x); 
arena_dim_y = 100 # max(rat_pos_y) - min(rat_pos_y);
rat_dt = float(data['dt'].flatten())

# create a spatial rate map
print("\nGenerating spatial map...")    
rateMap, xedges, yedges = SNSpatialRate2DRect(spikes, rat_pos_x, rat_pos_y, rat_dt, 
                                    arena_dim_x, arena_dim_y, smoothingSigma)
rateMap *= 1e3 # should be Hz
X, Y = np.meshgrid(xedges, yedges)

'''
# Calculate gridness score
G_i, crossCorr_i, angles_i = cellGridnessScoreRect(rateMap, arena_dim_x, arena_dim_y, 
                                                   smoothingSigma, gridSep/2)
# Gridness score valid only when T >= minGridnessT
lastSpikeT = times[-1] if len(times) != 0 else np.nan
if lastSpikeT >= minGridnessT:
    print "\ngridness score = " , G_i
    print "gridness correlation = " , crossCorr_i
    print "gridness angles = " , angles_i
else:
    print "Simulation too short, Gridness score NaN"
'''
# Draw ratemap plots
print("\nCreating plot...") 
figure()
pcolormesh(X, Y, rateMap)
colorbar()
axis('equal')
axis('off')
print("Saving plot")
savefig('{0}.png'.format(source_data + '_rateMap'))
