'''Run a test simulation to calibrate the border cell connections to e cells
Runs a separate trial for each border of a square arena
This simulation will overwrite any old files that are present in the output
directory.
'''
from __future__ import absolute_import, print_function, division

from nest.hl_api import NESTError

from parameters import getOptParser
from grid_cell_model.models.gc_net_nest import BasicGridCellNetwork, ConstPosInputs, PosInputs
from grid_cell_model.models.seeds import TrialSeedGenerator
from grid_cell_model.data_storage import DataStorage
from grid_cell_model.models.gc_net_nest import PosInputs
import numpy as np

parser = getOptParser()
parser.add_argument("--pcON", type=int, choices=[0, 1], default=1, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=1, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=1, help="Get connection matrices?")
parser.add_argument("--bcConnMethod", type=str, default="none", help="Border cell connect method; default = none")
(o, args) = parser.parse_args()

output_fname = "{0}/{1}job{2:05}_output.h5".format(o.output_dir,
                                                   o.fileNamePrefix, o.job_num)
d = DataStorage.open(output_fname, 'w')
d['trials'] = []

overalT = 0.
stop = False


###############################################################################
seed_gen = TrialSeedGenerator(int(o.master_seed))
for trial_idx in range(o.ntrials):
    seed_gen.set_generators(trial_idx)  # Each trial is reproducible
    d['master_seed'] = int(o.master_seed)
    d['invalidated'] = 1

    # override default trajectory
    directions = ['N','E','S','W']
    o.ratVelFName = '../../../data/bc_calibration/bc_calibration_traj_{0}.mat'.format(directions[trial_idx])

    #const_v = [0.0, -o.Ivel]
    ei_net = BasicGridCellNetwork(o, simulationOpts=None)
    d['net_params'] = ei_net.getNetParams()  # Common settings will stay

    # turn velocity inputs on
    ei_net.setVelocityCurrentInput_e()
    
    # place cells
    if o.pcON:
        # activate place cells (including start place cells))
        ei_net.setPlaceCells()
    else:
        # activate start place cells only
	start_x = arena_borders[trial_idx][0].pos_x
	start_y = arena_borders[trial_idx][0].pos_y
        ei_net.setStartPlaceCells(ConstPosInputs(0.0,0.0)) 

    # border cells
    if o.bcON:
        # create the border cells
        borders=[((-90.0,90.0),(90.0,90.0)),((90.0,90.0),(90.0,-90.0)),((90.0,-90.0),(-90.0,-90.0)),((-90.0,-90.0),(-90.0,90.0))]
        ei_net.create_border_cells(borders, N_per_border=o.bcNum)
        # connect border cells according to chosen method
        if o.bcConnMethod == "line":
            ei_net.connect_border_cells_line_method(o.bc_conn_weight)
        elif o.bcConnMethod == "place":
            ei_net.connect_border_cells_modified_place_cell_method(o.bc_conn_weight)
        else:
            pass

    try:
        ei_net.simulate(o.time, printTime=o.printTime)
    except NESTError as e:
        print("Simulation interrupted. Message: {0}".format(str(e)))
        print("Not saving the data. Trying to clean up if possible...")
        stop = True
    ei_net.endSimulation()
    # get simulation data
    sim_data = ei_net.getAllData()
    # add connection matrices if selected
    if o.getConnMatrices:
        print("Getting connection matrices...")
        sim_data['connections'] = ei_net.getConnections()
    # save simulation data
    d['trials'].append(sim_data)
    d.flush()
    constrT, simT, totalT = ei_net.printTimes()
    overalT += totalT
    if stop:
        break

 

d.close()
print("Script total run time: {0} s".format(overalT))
###############################################################################
