'''Main simulation run: Run a simulation with velocity inputs decoupled, and 
test bump movement close to an activated border.

This simulation will overwrite any old files that are present in the output
directory.
'''
from __future__ import absolute_import, print_function, division

from nest.hl_api import NESTError

from parameters import getOptParser
from grid_cell_model.models.gc_net_nest import BasicGridCellNetwork, ConstPosInputs, PosInputs
from grid_cell_model.models.seeds import TrialSeedGenerator
from grid_cell_model.data_storage import DataStorage
import numpy as np

parser = getOptParser()
parser.add_argument("--velON", type=int, choices=[0, 1], default=0, help="Velocity inputs ON?")
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--spcON", type=int, choices=[0, 1], default=1, help="Start cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=1, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--bcConnMethod", type=str, default="place", help="Border cell connect method; default = line")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=0, help="Get connection matrices?")
parser.add_argument("--inputStartTime", type=float, required=True, help="Determines when the place or border cells become active.")
(o, args) = parser.parse_args()

output_fname = "{0}/{1}job{2:05}_output.h5".format(o.output_dir,
                                                   o.fileNamePrefix, o.job_num)
d = DataStorage.open(output_fname, 'w')
d['trials'] = []

#create borders
startPos_x = [-90.0, 90.0, 90.0,-90.0]
startPos_y = [ 90.0, 90.0,-90.0,-90.0]
endPos_x   = [ 90.0, 90.0,-90.0,-90.0]
endPos_y   = [ 90.0,-90.0,-90.0, 90.0]
arena_borders = zip(zip(startPos_x,startPos_y),zip(endPos_x,endPos_y))

# create bump start positions for each iteration
bump_pos_x = [ 0.0,  0.0,  0.0,  0.0, 85.0, 80.0, 75.0, 70.0]
bump_pos_y = [85.0, 80.0, 75.0, 70.0,  0.0,  0.0,  0.0,  0.0]
#bump_pos_x = [ 0.0,  0.0,  0.0,  0.0,  5.0, 10.0, 15.0, 20.0]
#bump_pos_y = [ 5.0, 10.0, 15.0, 20.0,  0.0,  0.0,  0.0,  0.0]

# create constant rat positions for each iteration
rat_pos_x = [  0.0,  0.0,  0.0,  0.0, 90.0, 90.0, 90.0, 90.0]
rat_pos_y = [ 90.0, 90.0, 90.0, 90.0,  0.0,  0.0,  0.0,  0.0]
#rat_pos_x = [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
#rat_pos_y = [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]
rat_dt=20.0

overalT = 0.
stop = False
###############################################################################
seed_gen = TrialSeedGenerator(int(o.master_seed))
for trial_idx in range(o.ntrials):
    seed_gen.set_generators(trial_idx)  # Each trial is reproducible
    d['master_seed'] = int(o.master_seed)
    d['invalidated'] = 1

    ei_net = BasicGridCellNetwork(o, simulationOpts=None)
    d['net_params'] = ei_net.getNetParams()  # Common settings will stay

    # turn velocity inputs on
    if o.velON:
        ei_net.setVelocityCurrentInput_e()
    
    # position inputs (constant)
    bump_pos = ConstPosInputs(bump_pos_x[trial_idx], bump_pos_y[trial_idx])
    posIn_x = [rat_pos_x[trial_idx]] * int(o.time / rat_dt)
    posIn_y = [rat_pos_y[trial_idx]] * int(o.time / rat_dt)
    rat_pos = PosInputs(posIn_x, posIn_y, rat_dt)
    # place cells
    if o.pcON:
        # activate place cells (including start place cells))
        ei_net.setPlaceCells(posIn=rat_pos,start=o.inputStartTime)
        
    # start place cells
    if o.spcON:
        # activate start place cells only
        ei_net.setStartPlaceCells(bump_pos) 

    # border cells
    if o.bcON:
        borders= arena_borders[0] if trial_idx < 4 else arena_borders[1]
        ei_net.create_border_cells(borders=[borders], N_per_border=o.bcNum, posIn=rat_pos, start=o.inputStartTime)
        # connect border cells according to chosen method
        if o.bcConnMethod == "line":
            ei_net.connect_border_cells_line_method(o.bc_conn_weight)
        elif o.bcConnMethod == "place":
            ei_net.connect_border_cells_modified_place_cell_method(o.bc_conn_weight)
        elif o.bcConnMethod == "none":
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
