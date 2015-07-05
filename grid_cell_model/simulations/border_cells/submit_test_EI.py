#!/usr/bin/env python
'''Run a network for a short time; save data and plot activity.'''
from __future__ import absolute_import, print_function, division

from grid_cell_model.submitting.base.templates import DemoSimulation
from default_params import defaultParameters as dp

sim_label = "output_data"
sim = DemoSimulation('simulation_const_velocity.py', sim_label, dp)

parser = sim.parser
parser.add_argument('--nthreads', type=int, default=1, help='Number of simulation threads.')
parser.add_argument('--Ivel', type=float, help='Velocity input (pA). Default is 50 pA.')
parser.add_argument("--pcON", type=int, choices=[0, 1], default=0, help="Place cell input ON?")
parser.add_argument("--bcON", type=int, choices=[0, 1], default=0, help="Border cell input ON?")
o = parser.parse_args()

p = {}
p['master_seed'] = 123456

p['time']                   = 10e3 if o.time is None else o.time  # ms
p['nthreads']               = o.nthreads
p['verbosity']              = o.verbosity
p['Ivel']                   = 50. if o.Ivel is None else o.Ivel  # mA
p['pcON']                   = o.pcON
p['bcON']                   = o.bcON


sim.update_user_parameters(p)
sim.run()
