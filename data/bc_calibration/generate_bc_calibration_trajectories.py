'''Generate straight line trajectories for help with calibrating
   border cell connection weights
'''

import argparse
from grid_cell_model.models.gc_net_nest import ConstPosInputs, PosInputs
import scipy.io
import numpy as np

################################################################################################

def create_square_arena(arena_dim):
    x_starts = [-arena_dim/2, arena_dim/2, arena_dim/2,-arena_dim/2]
    y_starts = [ arena_dim/2, arena_dim/2,-arena_dim/2,-arena_dim/2]
    x_ends   = [ arena_dim/2, arena_dim/2,-arena_dim/2,-arena_dim/2]
    y_ends   = [ arena_dim/2,-arena_dim/2,-arena_dim/2, arena_dim/2]
    return zip(zip(x_starts,y_starts), zip(x_ends, y_ends))

def create_trajectory(sim_time, borders, rat_dt, scale=1.0):
    # Create simple rat trajectory (scaled rectangle in same proportions as arena)
    steps_per_border = int(sim_time / len(borders) / rat_dt)
    rat_x = []
    rat_y = []        
    for i in range(len(borders)):
        # start and end points of rat trajectory
        x_start = borders[i][0][0] * scale
        y_start = borders[i][0][1] * scale
        x_end  = borders[i][1][0] * scale
        y_end  = borders[i][1][1] * scale
        # x and y distances
        x_dist = x_end - x_start
        y_dist = y_end - y_start
        step_x = x_dist / steps_per_border
        step_y = y_dist / steps_per_border    
        for n in range(0, steps_per_border): rat_x.append(x_start + n*step_x)
        for m in range(0, steps_per_border): rat_y.append(y_start + m*step_y)
    return PosInputs(rat_x, rat_y, rat_dt)

################################################################################################

parser = argparse.ArgumentParser()
parser.add_argument("--arenaSize", type=float, default=180.0, help="Size of square anena (square cm)")
parser.add_argument("--time", type=float, default=800.0, help="Duration of animal movement")
parser.add_argument("--rat_dt", type=float, default=20.0, help="Time step of animal movement")

o = parser.parse_args()

# create borders
arena_borders = create_square_arena(o.arenaSize)

# create trajectory
directions = ['N','E','S','W']
for i in range(len(arena_borders)):
    rat_traj = create_trajectory(o.time, [arena_borders[i]], o.rat_dt, scale=1.0)
    output_fname = "bc_calibration_traj_{0}.mat".format(directions[i])
    data = {'pos_x' : rat_traj.pos_x, 'pos_y' : rat_traj.pos_y, 'dt' : rat_traj.pos_dt}
    scipy.io.savemat(output_fname,mdict=data)
