#
#   submit_theta_no_gamma_velocity.py
#
#   Submit job(s) to the cluster/workstation: velocity estimation for the non-gamma variant
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

parameters['time']              = 10e3      # ms
parameters['ngenerations']      = 10
parameters['velModulationType'] = 'excitatory'
parameters['prefDirC_e']        = 3
parameters['prefDirC_i']        = 0


parameters['Iext_e_theta']      = 275    # pA
parameters['g_AMPA_total']      = 2000   # nS
parameters['g_GABA_total']      = 800   # nS

#parameters['Iext_e_const']      = 500       # pA
#parameters['Iext_i_const']      = 200       # pA

#parameters['EL_e_spread']       = 1     # mV
parameters['taum_i_spread']     = 1     # mV
parameters['EL_i_spread']       = 5     # mV
parameters['theta_noise_sigma'] = 0     # pA

#parameters['Ivel']              = 40        # pA

startJobNum = 1120
numRepeat = 1

# Workstation parameters
programName         = 'nice python2.6 simulation_theta_no_gamma_velocity.py'
blocking            = False

# Cluster parameters
cluster_scriptName  = 'eddie_submit.sh simulation_theta_no_gamma_velocity.py'
qsub_params         = "-P inf_ndtc -cwd -j y -l h_rt=01:30:00 -pe memory-2G 2"
qsub_output_dir     = parameters['output_dir']

ac = ArgumentCreator(parameters)

iterparams = {
        'Ivel'       : [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
}
ac.insertDict(iterparams, mult=True)

if CLUSTER:
    submitter = QsubSubmitter(ac, cluster_scriptName, qsub_params, qsub_output_dir)
else:
    submitter = GenericSubmitter(ac, programName, blocking=blocking)
submitter.submitAll(startJobNum, numRepeat, dry_run=False)