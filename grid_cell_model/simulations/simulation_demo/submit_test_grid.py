#!/usr/bin/env python
'''Run a network for a short time; save data and plot activity.'''
from __future__ import absolute_import, print_function, division

from grid_cell_model.submitting.base.templates import DemoSimulation
from default_params import defaultParameters as dp

sim_label = "demo_output_data"
sim = DemoSimulation('../common/simulation_test_grid.py', sim_label, dp)

parser = sim.parser
parser.add_argument('--nthreads', type=int, default=1,
                    help='Number of simulation threads.')
#parser.add_argument('--Ivel', type=float,
#                    help='Velocity input (pA). Default is 50 pA.')
o = parser.parse_args()

p = {}
p['master_seed'] = 123456

p['time']                   = 10e3 if o.time is None else o.time  # ms
p['nthreads']               = o.nthreads
p['verbosity']              = o.verbosity
#p['Ivel']                   = 50. if o.Ivel is None else o.Ivel  # mA

sim.update_user_parameters(p)
sim.run()
