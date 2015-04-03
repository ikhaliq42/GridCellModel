#!/usr/bin/env python
from __future__ import absolute_import, print_function

from grid_cell_model.submitting import flagparse
import noisefigs
from noisefigs.env import NoiseEnvironment

import config

parser = flagparse.FlagParser()
parser.add_flag('--pbumps_sweep')
parser.add_flag('--pbumps_threshold_sweep')
parser.add_flag('--bump_examples')
parser.add_flag('--bump_examples_isbump')
args = parser.parse_args()


env = NoiseEnvironment(user_config=config.get_config())

if args.pbumps_sweep or args.all:
    env.register_plotter(noisefigs.plotters.MainBumpFormationPlotter)

if args.pbumps_threshold_sweep or args.all:
    env.register_plotter(noisefigs.plotters.MainIsBumpPlotter)

if args.bump_examples or args.all:
    env.register_plotter(noisefigs.plotters.BumpExamplePlotter)

if args.bump_examples_isbump or args.all:
    env.register_plotter(noisefigs.plotters.IsBumpExamplePlotter)

env.plot()

