#
#   submit_basic_grids_full_record.py
#
#   Submit job(s) to the cluster/workstation: full state monitor recordings
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


CLUSTER = True  # if True, submit on a cluster using qsub


parameters = defaultParameters

parameters['time']              = 1199.9e3  # ms
parameters['ndumps']            = 10

parameters['prefDirC_e']        = 4
parameters['prefDirC_i']        = 0

parameters['placeT']            = 10e3      # ms
parameters['placeDur']          = 100       # ms

parameters['bumpCurrentSlope']  = 1.05      # pA/(cm/s), !! this will depend on prefDirC !!
parameters['gridSep']           = 70        # cm, grid field inter-peak distance
parameters['theta_noise_sigma'] = 0         # pA

parameters['uni_GABA_density']   = 0.4

parameters['output_dir']        = 'output_local'
parameters['stateRec_dt']       = 0.25      # ms

startJobNum = 3100
numRepeat = 10

# Workstation parameters
programName         = 'nice python2.6 simulation_basic_grids_full_record.py'
blocking            = False

# Cluster parameters
cluster_scriptName  = 'eddie_submit.sh simulation_basic_grids_full_record.py'
qsub_params         = "-P inf_ndtc -cwd -j y -l h_rt=14:00:00 -pe memory-2G 2"
qsub_output_dir     = parameters['output_dir']

ac = ArgumentCreator(parameters)

#iterparams = {
#        'bumpCurrentSlope'  : [0.95, 1.05, 1.15]
#}
#ac.insertDict(iterparams, mult=False)

if CLUSTER:
    submitter = QsubSubmitter(ac, cluster_scriptName, qsub_params, qsub_output_dir)
else:
    submitter = GenericSubmitter(ac, programName, blocking=blocking)
submitter.submitAll(startJobNum, numRepeat, dry_run=False)
