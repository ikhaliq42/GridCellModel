#!/usr/bin/env python
'''Submit job(s) to the cluster/workstation: grid field parameter sweeps.'''

import numpy as np
import pdb

#from grid_cell_model.submitting.noise import SubmissionParser
from grid_cell_model.submitting.base.parsers import GenericSubmissionParser
from grid_cell_model.submitting.factory   import SubmitterFactory
from grid_cell_model.submitting.arguments import ArgumentCreator
from param_sweep import getBumpCurrentSlope
from default_params import defaultParameters as dp

parser = GenericSubmissionParser()
o = parser.parse_args()

#for noise_sigma in parser.noise_sigmas:
p = dp.copy()
#p['noise_sigma'] = noise_sigma # pA
p['noise_sigma'] = 150 # pA

# Submitting
ENV         = o.env
simRootDir  = o.where
simLabel    = '{0}pA'.format(int(p['noise_sigma']))
appName     = 'simulation_grids_with_border.py'
rtLimit     = o.rtLimit
numCPU      = 1
blocking    = True
timePrefix  = False
numRepeat   = 1
dry_run     = o.dry_run

p['master_seed']      = 123456
p['time']             = 600e3 if o.time is None else o.time  # ms
p['nthreads']         = 1
p['ntrials']          = o.ntrials
p['velON']            = 1
p['pcON']             = 1
p['constantPosition'] = 0
p['verbosity']        = o.verbosity


# Range of E/I synaptic conductances
Nvals  = 31      # Number of values for each dimension
startG = 0.0     # nS
endG   = 6120.0  # nS

extraIterparams = {'bumpCurrentSlope' : getBumpCurrentSlope(p['noise_sigma'],
    threshold=-np.infty)}

ac = ArgumentCreator(p, printout=False)

###############################################################################
submitter = SubmitterFactory.getSubmitter(
    ac, appName, envType=ENV, rtLimit=rtLimit, output_dir=simRootDir,
    label=simLabel, blocking=blocking, timePrefix=timePrefix, numCPU=numCPU)
ac.setOption('output_dir', submitter.outputDir())
startJobNum = 0
numRepeat = 1
#pdb.set_trace()
submitter.submitAll(startJobNum, numRepeat, dry_run=dry_run)
#submitter.saveIterParams(iterparams, dimension_labels, dimensions, dry_run=dry_run)


###############################################################################


