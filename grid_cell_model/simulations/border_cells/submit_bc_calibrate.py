#!/usr/bin/env python
'''Run a network for a short time; save data and plot activity.'''
from __future__ import absolute_import, print_function, division

from grid_cell_model.submitting.base.templates import DemoSimulation
from default_params import defaultParameters as dp

sim_label = str(int(dp['noise_sigma'])) + "pA"
sim = DemoSimulation('simulation_bc_calibrate.py', sim_label, dp)

parser = sim.parser
parser.add_argument('--nthreads', type=int, default=1,
                    help='Number of simulation threads.')
parser.add_argument("--pcON", type=int, choices=[0, 1], default=1, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=1, help="Border cell input ON?")
#parser.add_argument("--bcNum", type=int, default=1, help="Number of border cells per border")
#parser.add_argument("--getConnMatrices", type=int, choices=[0, 1], default=1, help="Get connection matrices?")
#parser.add_argument("--bcConnMethod", type=str, default="none", help="Border cell connect method; default = none")
parser.add_argument('--Ivel', type=float, help='Velocity input (pA). Default is 50 pA.')
o = parser.parse_args()

p = {}
p['master_seed'] = 123456

p['time']                   = 10e3 if o.time is None else o.time  # ms
p['nthreads']               = o.nthreads
p['verbosity']              = o.verbosity
p['pcON']                   = o.pcON
p['bcON']                   = o.bcON
#p['bcNum']                  = dp['bc_N_per_border'] if o.bcNum is None else o.bcNum
#p['getConnMatrices']        = o.getConnMatrices
#p['bcConnMethod']           = o.bcConnMethod
p['Ivel']                   = 50. if o.Ivel is None else o.Ivel  # mA

sim.update_user_parameters(p)
sim.run()
