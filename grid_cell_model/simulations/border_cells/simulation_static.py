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
parser.add_argument("--velON", type=int, choices=[0, 1], default=0, help="Velocity inputs ON?")
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--spcON", type=int, choices=[0, 1], default=0, help="Start cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=0, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--bcConnMethod", type=str, default="line", help="Border cell connect method; default = line")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=0, help="Get connection matrices?")
(o, args) = parser.parse_args()

output_fname = "{0}/{1}job{2:05}_output.h5".format(o.output_dir,
                                                   o.fileNamePrefix, o.job_num)
d = DataStorage.open(output_fname, 'w')
d['trials'] = []

x_off = [0,15,-15, 15]
y_off = [0,15,-15,-15]

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
    
    # animal position inputs (constant)
    pos = ConstPosInputs(0+x_off[trial_idx], 0+y_off[trial_idx])
    
    # place cells
    if o.pcON:
        # activate place cells (including start place cells))
        ei_net.setPlaceCells()
        
    # start place cells
    if o.spcON:
        # activate start place cells only
        ei_net.setStartPlaceCells(pos) 

    # border cells
    if o.bcON:
        # create the border cells - "crosshair"
        arena_borders = [((0.0+x_off[trial_idx], 90.0),(0.0+x_off[trial_idx], -90.0)),  
                                            ((-90.0, 0.0+y_off[trial_idx]),(90.0, 0.0+y_off[trial_idx]))]
        ei_net.create_border_cells(borders=arena_borders, N_per_border=o.bcNum, posIn=pos)
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
