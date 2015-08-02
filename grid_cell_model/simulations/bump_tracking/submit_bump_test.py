#!/usr/bin/env python
'''Run a network for a short time; save data and plot activity.'''
from __future__ import absolute_import, print_function, division

from grid_cell_model.submitting.base.templates import DemoSimulation
from default_params import defaultParameters as dp

sim_label = str(int(dp['noise_sigma'])) + "pA"
sim = DemoSimulation('../border_cells/simulation_bump_test.py', sim_label, dp)

parser = sim.parser
parser.add_argument('--nthreads', type=int, default=1,
                    help='Number of simulation threads.')
parser.add_argument("--velON", type=int, choices=[0, 1], default=0, help="Velocity input ON?")
parser.add_argument("--spcON", type=int, choices=[0, 1], default=1, help="Start place cell input ON?")
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=1, help="Border cell input ON?")
parser.add_argument("--bcNum", type=int, required=False, help="Number of border cells per border")
parser.add_argument("--pcNum", type=int, required=False, help="Number of place cells per arena edge")
parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=1, help="Get connection matrices?")
parser.add_argument("--bcConnMethod", type=str, default="place", help="Border cell connect method; default = place")
parser.add_argument("--bcConnStd", type=float, required=False, help="Divergence of Border cell connection to E cells (does not apply to predef weights)")
parser.add_argument("--strongBorder", type=int, choices=[0, 1], default=0, help="Very Strong border input on?")
parser.add_argument("--strongPlace", type=int, choices=[0, 1], default=0, help="Very Strong place input on?")
parser.add_argument("--inputStartTime", type=float, required=True, help="Determines when the place or border cells become active.")
#parser.add_argument('--Ivel', type=float, help='Velocity input (pA). Default is 50 pA.')
o = parser.parse_args()

p = {}
p['master_seed'] = 123456

p['time']                   = 10e3 if o.time is None else o.time  # ms
p['nthreads']               = o.nthreads
p['verbosity']              = o.verbosity
p['pcON']                   = o.pcON
p['spcON']                  = o.spcON
p['bcON']                   = o.bcON
p['velON']                  = o.velON
p['bcNum']                  = dp['bc_N_per_border'] if o.bcNum is None else o.bcNum
if o.pcNum is not None: p['N_place_cells'] = o.pcNum
p['getConnMatrices']        = o.getConnMatrices
p['bcConnMethod']           = o.bcConnMethod
p['bcConnStd']              = dp['gridSep'] / 2. / 6. if o.bcConnStd is None else o.bcConnStd
p['inputStartTime']         = o.inputStartTime
#p['Ivel']                  = 50. if o.Ivel is None else o.Ivel  # mA
if o.strongBorder==1:
    p['bc_max_rate']            = 100.0
    p['bc_conn_weight']         = 5.0
if o.strongPlace==1:
    p['pc_max_rate']            = 100.0
    p['pc_conn_weight']         = 5.0

# submit simulations
for n in range(8):
    p['experiment_no']          = n
    sim._sim_label = "experiment_" + str(n)
    sim.update_user_parameters(p)
    sim.run()

