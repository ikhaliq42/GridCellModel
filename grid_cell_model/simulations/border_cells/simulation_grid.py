'''Main simulation run: Run a test simulation using rat trajectory data

This simulation will overwrite any old files that are present in the output
directory.
'''
from __future__ import absolute_import, print_function, division

from nest.hl_api import NESTError

from parameters import getOptParser
from grid_cell_model.models.gc_net_nest import BasicGridCellNetwork, ConstPosInputs
from grid_cell_model.models.seeds import TrialSeedGenerator
from grid_cell_model.data_storage import DataStorage

parser = getOptParser()
parser.add_argument("--velON", type=int, choices=[0, 1], default=1, help="Velocity inputs ON?")
parser.add_argument("--spcON", type=int, choices=[0, 1], default=1, help="Start place cell input ON?")
parser.add_argument("--pcON", type=int, choices=[0, 1], default=1, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=1, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--bcConnMethod", type=str, default="place", help="Border cell connect method; default = predef")
parser.add_argument("--bcConnStd", type=float, required=False, help="Divergence of Border cell connection to E cells (does not apply to predef weights)")
parser.add_argument("--bcMargin", type=float, required=False, help="Arena margin where border cells have maximum activtiy, default is zero")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=0, help="Get connection matrices?")
(o, args) = parser.parse_args()

output_fname = "{0}/{1}job{2:05}_output.h5".format(o.output_dir,
                                                   o.fileNamePrefix, o.job_num)
d = DataStorage.open(output_fname, 'w')
d['trials'] = []

#create borders
mrg = o.bcMargin
startPos_x = [-90.0+mrg, 90.0-mrg, 90.0-mrg,-90.0+mrg]
startPos_y = [ 90.0-mrg, 90.0-mrg,-90.0+mrg,-90.0+mrg]
endPos_x   = [ 90.0-mrg, 90.0-mrg,-90.0+mrg,-90.0+mrg]
endPos_y   = [ 90.0-mrg,-90.0+mrg,-90.0+mrg, 90.0-mrg]
directions = ['N','E','S','W']
arena_borders = zip(zip(startPos_x,startPos_y),zip(endPos_x,endPos_y))

overalT = 0.
stop = False
###############################################################################
seed_gen = TrialSeedGenerator(int(o.master_seed))
for trial_idx in range(o.ntrials):
    seed_gen.set_generators(trial_idx)  # Each trial is reproducible
    d['master_seed'] = int(o.master_seed)
    d['invalidated'] = 1

    #const_v = [0.0, -o.Ivel]
    ei_net = BasicGridCellNetwork(o, simulationOpts=None)
    d['net_params'] = ei_net.getNetParams()  # Common settings will stay

    # turn velocity inputs on
    if o.velON:
        ei_net.setVelocityCurrentInput_e()
    
    # place cells
    if o.pcON:
        # activate place cells (including start place cells))
        ei_net.setPlaceCells()
    elif o.spcON:
        # activate start place cells only
        ei_net.setStartPlaceCells(ConstPosInputs(0, 0))
    else:
        pass

    # border cells
    if o.bcON:
        # create the border cells
        ei_net.create_border_cells(borders=arena_borders, N_per_border=o.bcNum)
        # connect border cells according to chosen method
        if o.bcConnMethod == "place":
            ei_net.connect_border_cells_modified_place_cell_method(directions, o.bc_conn_weight, o.bcConnStd)
        elif o.bcConnMethod == "predef":
            ei_net.connect_border_cells_predefined_weights(o.bc_conn_weight)
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
