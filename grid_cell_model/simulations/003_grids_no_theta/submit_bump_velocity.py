#
#   submit_bump_velocity.py
#
#   Submit job(s) to the cluster/workstation: bump velocity estimation
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

parameters['time']              = 10.0e3      # ms
parameters['ngenerations']      = 10
parameters['velModulationType'] = 'excitatory'
parameters['prefDirC_e']        = 7
parameters['prefDirC_i']        = 0

#parameters['Ivel']              = 40        # pA

startJobNum = 240
numRepeat = 1

# Workstation parameters
programName         = 'python2.6 simulation_bump_velocity.py'
blocking            = False

# Cluster parameters
cluster_scriptName  = 'eddie_submit.sh simulation_bump_velocity.py'
qsub_params         = "-P inf_ndtc -cwd -j y -l h_rt=01:30:00 -pe memory-2G 2"
qsub_output_dir     = parameters['output_dir']

ac = ArgumentCreator(parameters)

iterparams = {
        'Ivel'       : [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]}
ac.insertDict(iterparams, mult=True)

if CLUSTER:
    submitter = QsubSubmitter(ac, cluster_scriptName, qsub_params, qsub_output_dir)
else:
    submitter = GenericSubmitter(ac, programName, blocking=blocking)
submitter.submitAll(startJobNum, numRepeat, dry_run=False)
