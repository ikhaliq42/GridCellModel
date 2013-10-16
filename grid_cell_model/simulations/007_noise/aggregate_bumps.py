#!/usr/bin/env python
#
#   aggregate_bumps.py
#
#   Aggregate bump data into the reductions file.
#
#       Copyright (C) 2012  Lukas Solanka <l.solanka@sms.ed.ac.uk>
#       
#       This program is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import numpy as np
from parameters  import JobTrialSpace2D
import logging as lg
#lg.basicConfig(level=lg.WARN)
lg.basicConfig(level=lg.INFO)


ns_all  = [0, 150, 300]
ns_none = [-100]
dirs = \
    ("output/detailed_noise/gamma_bump/non_monotonic",  (31, 9),  ns_none)
    #("output/even_spacing/gamma_bump/{0}pA",            (31, 31), ns_all)

NTrials = 5
trialNumList = xrange(NTrials)
varListBase = ['analysis']
loadData = False

################################################################################
shape        = dirs[1]
noise_sigmas = dirs[2]
for noise_sigma in noise_sigmas:
    rootDir = dirs[0].format(int(noise_sigma))

    sp = JobTrialSpace2D(shape, rootDir)
    sp.aggregateData(varListBase + ['bump_e', 'sigma'], trialNumList,
            funReduce=None, loadData=loadData,saveData=True,
            output_dtype='array')
    sp.aggregateData(varListBase + ['bump_e', 'err2'], trialNumList,
            funReduce=None, loadData=loadData, saveData=True,
            output_dtype='array')
    sp.aggregateData(varListBase + ['bump_e', 'bump_e_rateMap'], trialNumList,
            funReduce=None, loadData=loadData, saveData=True,
            output_dtype='list')

    sp.aggregateData(varListBase + ['acVal'], trialNumList, funReduce=np.mean,
            loadData=loadData, saveData=True, output_dtype='array')
    sp.aggregateData(varListBase + ['acVec'], trialNumList, funReduce=None,
            loadData=loadData, saveData=True, output_dtype='list')
