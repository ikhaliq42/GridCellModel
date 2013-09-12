#!/usr/bin/env python
#
#   submit_param_sweep_velocity.py
#
#   Submit job(s) to the cluster/workstation: velocity estimation parameter
#   sweeps (noise)
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
from default_params import defaultParameters as p
from param_sweep    import submitParamSweep
import logging as lg
#lg.basicConfig(level=lg.DEBUG)
lg.basicConfig(level=lg.INFO)


p['noise_sigma']       = 300.0     # pA

# Submitting
ENV         = 'cluster'
simRootDir  = 'output/velocity'
simLabel    = 'EI_param_sweep_{0}pA'.format(int(p['noise_sigma']))
appName     = 'simulation_velocity.py'
rtLimit     = '02:00:00'
numCPU      = 4
blocking    = True
timePrefix  = False
numRepeat   = 1
dry_run     = False


p['time']     = 10e3  # ms
p['nthreads'] = 4
p['ntrials']  = 10

p['IvelMax']  = 100
p['dIvel']    = 10


# Range of parameters around default values
Nvals        = 30    # Number of values for each dimension
startFrac    = 0.
endFrac      = 2.8572

###############################################################################

submitParamSweep(p, startFrac, endFrac, Nvals, ENV, simRootDir, simLabel,
        appName, rtLimit, numCPU, blocking, timePrefix, numRepeat, dry_run)