#
#   submit_theta_no_gamma.py
#
#   Submit job(s) to the cluster/workstation: no gamma oscillations (i.e. no
#   uniform inhibitory feedback
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

from default_params import defaultParameters
from submitting.submitters         import *

import logging as lg


lg.basicConfig(level=lg.DEBUG)


CLUSTER = False  # if True, submit on a cluster using qsub


parameters = defaultParameters

parameters['time']              = 5e3       # ms
parameters['ndumps']            = 1

parameters['placeT']            = 10e3      # ms

#parameters['tau_AMPA']          = 2         # ms
#parameters['g_AMPA_total']      = 700       # nS
#parameters['tau_GABA_A_fall']   = 20        # ms
#parameters['g_GABA_total']      = 540       # nS
#parameters['noise_sigma']       = 2          # mV

parameters['bumpCurrentSlope']  = 0.759     # pA/(cm/s), !! this will depend on prefDirC !!
parameters['gridSep']           = 70        # cm, grid field inter-peak distance
startJobNum = 0
numRepeat = 1

# Workstation parameters
programName         = 'nice python2.6 simulation_theta_no_gamma.py'
blocking            = False

# Cluster parameters
cluster_scriptName  = 'eddie_submit.sh simulation_theta_no_gamma.py'
qsub_params         = "-P inf_ndtc -cwd -j y -l h_rt=13:00:00 -pe memory-2G 2"
qsub_output_dir     = parameters['output_dir']

ac = ArgumentCreator(parameters)

iterparams = {
#        'bumpCurrentSlope'  : [0.75, 0.759, 0.77]
#        'noise_sigma' : [2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5]
        'Iext_e_theta' : [200, 225, 250, 275, 300, 325, 350, 375]
}
        
ac.insertDict(iterparams, mult=False)

if CLUSTER:
    submitter = QsubSubmitter(ac, cluster_scriptName, qsub_params, qsub_output_dir)
else:
    submitter = GenericSubmitter(ac, programName, blocking=blocking)
submitter.submitAll(startJobNum, numRepeat, dry_run=False)