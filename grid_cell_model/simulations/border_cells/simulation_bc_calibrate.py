'''Run a test simulation to calibrate the border cell connections to e cells
This simulation will overwrite any old files that are present in the output
directory.
'''
from __future__ import absolute_import, print_function, division

from nest.hl_api import NESTError

from parameters import getOptParser
from grid_cell_model.models.gc_net_nest import BasicGridCellNetwork, ConstPosInputs
from grid_cell_model.models.seeds import TrialSeedGenerator
from grid_cell_model.data_storage import DataStorage
from grid_cell_model.models.gc_net_nest import PosInputs

def create_square_arena(arena_dim):
    x_starts = [-arena_dim/2, arena_dim/2, arena_dim/2,-arena_dim/2]
    y_starts = [ arena_dim/2, arena_dim/2,-arena_dim/2,-arena_dim/2]
    x_ends   = [ arena_dim/2, arena_dim/2,-arena_dim/2,-arena_dim/2]
    y_ends   = [ arena_dim/2,-arena_dim/2,-arena_dim/2, arena_dim/2]
    return zip(zip(x_starts,y_starts), zip(x_ends, y_ends))

def create_square_trajectory(sim_time, arena_borders, rat_dt, scale=1.0):
    # Create simple rat trajectory (scaled rectangle in same proportions as arena)
    steps_per_border = int(sim_time / 4.0 / rat_dt)
    rat_x = []
    rat_y = []        
    for i in range(4):
        # start and end points of rat trajectory
        x_start = arena_borders[i][0][0] * scale
        y_start = arena_borders[i][0][1] * scale
        x_end  = arena_borders[i][1][0] * scale
        y_end  = arena_borders[i][1][1] * scale
        # x and y distances
        x_dist = x_end - x_start
        y_dist = y_end - y_start
        step_x = x_dist / steps_per_border
        step_y = y_dist / steps_per_border    
        for n in range(0, steps_per_border): rat_x.append(x_start + n*step_x)
        for m in range(0, steps_per_border): rat_y.append(y_start + m*step_y)
    return PosInputs(rat_x, rat_y, rat_dt)

###############################################################################

parser = getOptParser()
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=0, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--bcConnMethod", type=str, default="line", help="Border cell connect method; default = line")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=0, help="Get connection matrices?")
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
        ei_net.setStartPlaceCells(ConstPosInputs(0, 0)) 

    # border cells
    if o.bcON:
        # create the border cells
        arena_borders = create_square_arena(o.arenaSize)
        rat_trajectory = create_square_trajectory(o.time, arena_borders, rat_dt=20.0, scale=1.0)
        ei_net.create_border_cells(arena_borders, o.bcNum, rat_trajectory)
        # connect border cells according to chosen method
        if o.border_cell_connect_method == "line":
            ei_net.connect_border_cells_line_method(o.bc_conn_weight)
        elif o.border_cell_connect_method == "none":
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
