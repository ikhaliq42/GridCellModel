import h5py; import numpy as np
import grid_cell_model.plotting.connections
import matplotlib.pyplot as plt
import scipy.io

plotter = grid_cell_model.plotting.connections.plot2DWeightMatrix

# get connections
d = h5py.File("output_dir/demo_output_data/job00000_output.h5")
conns = np.array(d['trials']['0']['connections']['B->E'])
conns = conns.transpose()

# arrange data in to a dictionary
connections = {}
for i in range(len(conns)):
    connections['border'+str(i)] = conns[i].reshape(34,30)

#save to matlab file
scipy.io.savemat('ConnMatrix.mat', mdict=connections)
#plot data for first and second border cell
ax = plotter(connections['border0'])
plt.show()
