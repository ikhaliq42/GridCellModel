#!/usr/bin/env python
'''Run a network for a short time; save data and plot activity.'''
from __future__ import absolute_import, print_function, division

from grid_cell_model.submitting.factory import SubmitterFactory
from grid_cell_model.submitting.arguments import ArgumentCreator

from param_sweep import SubmissionParserBase
from default_params import defaultParameters as dp

parser = SubmissionParserBase()
parser.add_argument('--nthreads', type=int, default=1,
                    help='Number of simulation threads.')
parser.add_argument('--Ivel', type=float,
                    help='Velocity input (pA). Default is 50 pA.')
o = parser.parse_args()

for noise_sigma in parser.noise_sigmas:
    p = dp.copy()
    p['noise_sigma'] = noise_sigma  # pA

    # Submitting
    ENV         = o.env
    simRootDir  = o.where
    simLabel    = '{0}pA'.format(int(p['noise_sigma']))
    appName     = '../common/simulation_test_network.py'
    rtLimit     = o.rtLimit
    numCPU      = 1
    blocking    = True
    timePrefix  = False
    numRepeat   = 1
    dry_run     = o.dry_run

    p['master_seed'] = 123456
    p['time']        = 10e3 if o.time is None else o.time  # ms
    p['nthreads']    = o.nthreads
    p['ntrials']     = o.ntrials
    p['verbosity']   = o.verbosity
    p['Ivel']        = 50. if o.Ivel is None else o.Ivel  # mA

    ###########################################################################
    ac = ArgumentCreator(p, printout=True)
    submitter = SubmitterFactory.getSubmitter(
        ac, appName, envType=ENV, rtLimit=rtLimit, output_dir=simRootDir,
        label=simLabel, blocking=blocking, timePrefix=timePrefix,
        numCPU=numCPU)
    ac.setOption('output_dir', submitter.outputDir())
    startJobNum = 0
    submitter.submitAll(startJobNum, numRepeat, dry_run=dry_run)
