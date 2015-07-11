'''Main simulation run: Run a test simulation using rat trajectory data

This simulation will overwrite any old files that are present in the output
directory.
'''
from __future__ import absolute_import, print_function, division

import numpy as np

from nest.hl_api import NESTError

from parameters import getOptParser
from grid_cell_model.models.gc_net_nest import BasicGridCellNetwork, ConstPosInputs
from grid_cell_model.models.seeds import TrialSeedGenerator
from grid_cell_model.data_storage import DataStorage

def create_mesh(top_left_corner, bottom_right_corner, x_spacing, y_spacing):
    '''returns a list of tuples of tuples which define straight line start and
    points. The lines form a mesh covering a rectangle defined by coordinate
    tuples top_left_corner and bottom_right_corner, and the mesh spacing is specified
    by x_spacing and y_spacing
    '''

    x_min = top_left_corner[0]; x_max = bottom_right_corner[0]
    y_min = top_left_corner[1]; y_max = bottom_right_corner[1]

    # vertical lines
    sgn = np.sign(x_max - x_min)
    vert_x_starts = np.arange(x_min,x_max + sgn * x_spacing, sgn * x_spacing)
    vert_x_ends   = vert_x_starts
    vert_y_starts = [y_min] * len(vert_x_starts)
    vert_y_ends   = [y_max] * len(vert_x_starts)
    vert_starts   = zip(vert_x_starts, vert_y_starts)
    vert_ends     = zip(vert_x_ends, vert_y_ends)
    vert_lines    = zip(vert_starts, vert_ends)

    # horizontal lines
    sgn = np.sign(y_max - y_min)
    horiz_y_starts = np.arange(y_min,y_max + sgn * y_spacing, sgn * y_spacing)
    horiz_y_ends   = horiz_y_starts
    horiz_x_starts = [x_min] * len(horiz_y_starts)
    horiz_x_ends   = [x_max] * len(horiz_y_starts)
    horiz_starts   = zip(horiz_x_starts, horiz_y_starts)
    horiz_ends     = zip(horiz_x_ends, horiz_y_ends)
    horiz_lines    = zip(horiz_starts, horiz_ends)

    # return lines
    return horiz_lines + vert_lines


###############################################################################

parser = getOptParser()
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=1, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--bcConnMethod", type=str, default="place", help="Border cell connect method; default = line")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=1, help="Get connection matrices?")
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
        # create a set of border cells defining a mesh over the arena
        lines = create_mesh((-90.0,90.0), (90.0,-90.0), 6.0, 6.0)
        ei_net.create_border_cells(lines, N_per_border=1)
        # connect border cells according to chosen method
        if o.border_cell_connect_method == "line":
            ei_net.connect_border_cells_line_method()
        elif o.border_cell_connect_method == "place":
            ei_net.connect_border_cells_modified_place_cell_method()
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




