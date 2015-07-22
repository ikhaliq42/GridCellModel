'''Main simulation run: Run a test simulation run of a bump with constant speed.

This simulation will overwrite any old files that are present in the output
directory.
'''
from __future__ import absolute_import, print_function, division

from nest.hl_api import NESTError

from parameters import getOptParser
from grid_cell_model.models.gc_net_nest import ConstantVelocityNetwork
from grid_cell_model.models.seeds import TrialSeedGenerator
from grid_cell_model.data_storage import DataStorage

parser = getOptParser()
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=0, help="Border cell input ON?")
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
borders = zip(zip(startPos_x,startPos_y),zip(endPos_x,endPos_y))

#velocities
velocities = [[o.Ivel, 0.0],[0.0, -o.Ivel],[-o.Ivel, 0.0],[0.0, o.Ivel]]

overalT = 0.
stop = False
###############################################################################
seed_gen = TrialSeedGenerator(int(o.master_seed))
for trial_idx in range(o.ntrials):
    seed_gen.set_generators(trial_idx)  # Each trial is reproducible
    d['master_seed'] = int(o.master_seed)
    d['invalidated'] = 1
    const_v = velocities[trial_idx]
    startPos = borders[trial_idx][0]
    ei_net = ConstantVelocityNetwork(o, simulationOpts=None, vel=const_v, startPos=startPos)
    d['net_params'] = ei_net.getNetParams()  # Common settings will stay

    # create border cell (unconnected)
    ei_net.create_border_cells(borders, N_per_border=1)
    try:
        ei_net.simulate(o.time, printTime=o.printTime)
    except NESTError as e:
        print("Simulation interrupted. Message: {0}".format(str(e)))
        print("Not saving the data. Trying to clean up if possible...")
        stop = True
    ei_net.endSimulation()
    # get simulation data
    sim_data = ei_net.getAllData()
    # add connection matrices 
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
