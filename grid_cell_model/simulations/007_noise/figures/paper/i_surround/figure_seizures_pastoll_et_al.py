#!/usr/bin/env python
'''Seizure figures for the I-surround with the original E-surround
configuration.'''
from __future__ import absolute_import, print_function, division

from grid_cell_model.submitting import flagparse
import noisefigs
from noisefigs.env import NoiseEnvironment

import config_pastoll as config

parser = flagparse.FlagParser()
parser.add_flag('--theta_signal')
parser.add_flag('--rastersFlag')
parser.add_flag('--rates')
parser.add_flag('--maxFRSweeps')
parser.add_flag('--seizureProportion')
args = parser.parse_args()

env = NoiseEnvironment(user_config=config.get_config())

if args.theta_signal or args.all:
    env.register_plotter(noisefigs.plotters.ThetaSignalPlotter)

if args.rastersFlag or args.all:
    env.register_plotter(noisefigs.plotters.EIRasterPlotter)

if args.rates or args.all:
    env.register_plotter(noisefigs.plotters.EIRatePlotter)

if args.maxFRSweeps or args.all:
    env.register_plotter(noisefigs.plotters.MaxPopulationFRSweepsPlotter)

if args.seizureProportion or args.all:
    env.register_plotter(noisefigs.plotters.PSeizureSweepPlotter)

env.plot()

