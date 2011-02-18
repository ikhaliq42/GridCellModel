#import brian_no_units
from brian import *

from brian import *
from brian.library.IF import *
from brian.library.synapses import *

from scipy import linspace
from scipy.io import loadmat
from scipy.io import savemat
from optparse import OptionParser
from datetime import datetime

import time
import math
import sys
import numpy as np

from fiete_network import *


# Network parameters definition
optParser = OptionParser()
optParser.add_option("--lambda-net", type="float", default=13,
        dest="lambda_net")
optParser.add_option("-s", "--sheet-size", type="int", default=40, dest="sheet_size")
optParser.add_option("-l", type="float", default=2.0, dest="l")
optParser.add_option("-a", type="float", default=1.0, dest="a");
optParser.add_option("-c", "--conn-mult", type="float", default=10.0,
        dest="connMult")
optParser.add_option("-w", "--write-data", action="store_true",
        dest="write_data", default=False)
optParser.add_option("-i", "--input", type="float", default=0.3, dest="input",
        help="Feedforward constant input to all neurons")
optParser.add_option("--noise-sigma", type="float", default=0, dest="noise_sigma", help="Input current Gaussian noise sigma (mV)")
optParser.add_option("-p", "--print-only-conn", action="store_true",
        dest="print_only_conn", default=False)
optParser.add_option("--alpha", type="float", default=0.10315, dest="alpha",
        help="Network alpha parameter (see Burak&Fiete, 2009)")
optParser.add_option("-t", "--time", type="float", default=5.0, dest="time",
        help="Total simulation time [seconds]")
optParser.add_option("-u", '--update-interval', type="float", default=5.0,
        dest="update_interval", help="Duration between simulation status printouts")
optParser.add_option("--sim_dt", type=float, default=0.1, dest="sim_dt",
        help="Simulation time step (ms)")
optParser.add_option("-n", "--job-num", type="int", default=-1, dest="job_num",
        help="Use argument of this option to specify the output file name number, instead of using time")
optParser.add_option("--taum", type="float", default=10, dest="taum",
        help="Neuron membrane time constant (ms)")
optParser.add_option("--taui", type="float", default=10, dest="taui",
        help="Inhibitory synaptic time constant (ms)")
optParser.add_option("--threshold", type="float", default=-20, dest="threshold",
        help="Integrate and fire spiking threshold (mV)")
optParser.add_option("--record-sn", action="store_true", dest="record_sn",
        default=False, help="Record single neuron responses");
optParser.add_option("--record-sn-row", action="store_true",
    dest="record_sn_row", default=False, help="Record membrane potential of row in the middle of the sheet")
optParser.add_option("--save-conn", action="store_true", dest="save_conn",
        default=False, help="Do nothing but save connection matrix to file")
optParser.add_option("--output-dir", type="string", default="results/", dest="output_dir", help="Output directory path.")

(options, args) = optParser.parse_args()
print "Options:"
print options

# Clock definitions
sim_dt = options.sim_dt*ms
vel_dt = 0.02*second
simulationClock = Clock(dt=sim_dt)
SNClock = Clock(dt=10*ms)
velocityClock = Clock(dt=vel_dt)
printStatusClock = Clock(dt=options.update_interval*second)

# Provisional loading of connection weights and initial conditions from a mat file (settings)
connFileName = '../../central_data_store/data/connections_96.mat'
initCondFileName = '../../data/initial_conditions/initial_conditions_96.mat'
vm_init_rand = 10*mV


# Save the results of the simulation in a .mat file
def saveResultsToMat(fileName, options):
    # SNMonitor - monitor of single neurons, defined by list
    # SNList - list of neuron numbers monitored (SN response)
    # spikeMonitor - monitor of spikes of all neurons
    # rateMonitor - rate monitor of several neurons (TODO)
    outData = ratData

    spikeCell = empty((options.sheet_size**2), dtype=object);

    for k,v in spikeMonitor.spiketimes.iteritems():
        spikeCell[k] = v
    outData['spikeCell'] = spikeCell

    if options.record_sn == True:
        outData['SNMonitor_values'] = SNMonitor.values_
        outData['SNMonitor_times'] =  SNMonitor.times_
        outData['SNgMonitor_times'] = SNgMonitor.times_
        outData['SNgMonitor_values'] =SNgMonitor.values_ 
        outData['SNList'] = SNList

    # Merge the rat position and timestamp data into the output so it is self
    # contained
    #for k,v in ratData.iteritems():
    #    outData['ratData_' + k] = v

    # Save options as string - couldn't find any other way how to convert it to
    # variables
    outData['options'] = str(options)
    outData['sheet_size'] = options.sheet_size

    savemat(fileName, outData, do_compression=True)

def saveConnectionsToMat(fileName, conn):
    outData = {};
    outData['connections'] = asarray(conn.W)
    savemat(fileName, outData, do_compression=True)


def loadConnectionsFromMat(fileName):
    return loadmat(fileName)['connections']

def loadInitialConditions(fileName):
    return loadmat(fileName)


# Definition of 2d topography on a sheet and connections
sheet_size = options.sheet_size  # Total no. of neurons will be sheet_size^2

# Definition of connection parameters and setting the connection iteratively:
# Mexican hat connectivity

start_time=time.time()

W = loadConnectionsFromMat(connFileName)
initCond = loadInitialConditions(initCondFileName)

print "Starting network and connections initialization..."
[sheetGroup, inhibConn] = createNetwork(sheet_size, options.lambda_net,
        options.l, options.a, options.connMult, simulationClock, options.taum,
        options.taui, options.threshold, options.noise_sigma, W)
# Provisional - set initial conditions from file
rndNoise = np.random.normal(initCond['membrane_potentials'], vm_init_rand)
sheetGroup.vm = rndNoise


duration=time.time()-start_time
print "Network setup time:",duration,"seconds"

# Print connections if necessary and exit
if (options.save_conn):
    saveConnectionsToMat("results/connection_matrix.mat", inhibConn)
    exit();

ratData = loadmat("../../data/hafting_et_al_2005/Hafting_Fig2c_Trial1_preprocessed.mat")
#print ratData['pos_timeStamps']

# Velocity inputs - for now zero velocity
input = options.input
sheetGroup.B = linspace(input*namp, input*namp, sheet_size**2)
vIndex = 0  # Bad habit, but there are no static variables in python,
rat_pos_x = ratData['pos_x']
rat_pos_y = ratData['pos_y']
@network_operation(velocityClock)
def updateVelocity():
    #updateVelocityLinear()
    #updateVelocityRat()
    #updateVelocityUp()
    updateVelocityZero()



def updateVelocityRat():
    global vIndex
    global input
    # the original data are in cm/s, however, we rather want m/s 
    vel_x = (rat_pos_x[vIndex + 1] - rat_pos_x[vIndex])/vel_dt/100*second
    vel_y = (rat_pos_y[vIndex + 1] - rat_pos_y[vIndex])/vel_dt/100*second
    #vel_x = 0
    #vel_y = 0

    i = 0
    for i_y in xrange(sheet_size):
        for i_x in xrange(sheet_size):
            prefDir = getPreferredDirection(i_x, i_y)
            sheetGroup.B[i] = (input + options.alpha*(prefDir[0]*vel_x +
                prefDir[1]*vel_y))*namp
            i+=1

    vIndex+=1

#linSize = 0.2   # m
ratSpeed = 0.1 # m/s
#dts_side = linSize/ratSpeed/vel_dt # Number of vel_dts to get from one side to
                                   # the other
curr_pos_x = 0                                     


def updateVelocityZero():
    # Velocity is zero, do nothing
    nothing = 5


def updateVelocityUp():
    # Move the rat always to the right
    vel_x = 0
    vel_y = ratSpeed

    i = 0
    for i_y in range(sheet_size):
        for i_x in range(sheet_size):
            prefDir = getPreferredDirection(i_x, i_y)
            sheetGroup.B[i] = (input + options.alpha*(prefDir[0]*vel_x +
                prefDir[1]*vel_y))*namp
            i+=1


def updateVelocityLinear():
    global vIndex
    global input
    global curr_pos_x

    if vIndex == 0:
        vel_x = 0
        vel_y = ratSpeed
    elif vIndex == 1:
        vel_x = 0
        vel_y = 0
    elif vIndex == 2:
        vel_x = ratSpeed/math.sqrt(2)
        vel_y = ratSpeed/math.sqrt(2)
    elif vIndex == 3:
        vel_x = 0
        vel_y = 0
    elif vIndex == 4:
        vel_x = ratSpeed
        vel_y = 0
    elif vIndex == 5:
        vel_x = 0
        vel_y = 0
    elif vIndex == 6:
        vel_x = ratSpeed/math.sqrt(2)
        vel_y = -ratSpeed/math.sqrt(2)
    elif vIndex == 7:
        vel_x = 0
        vel_y = 0
    elif vIndex == 8:
        vel_x = 0
        vel_y = -ratSpeed
    elif vIndex == 9:
        vel_x = 0
        vel_y = 0
    elif vIndex == 10:
        vel_x = -ratSpeed/math.sqrt(2)
        vel_y = -ratSpeed/math.sqrt(2)
    elif vIndex == 11:
        vel_x = 0
        vel_y = 0
    elif vIndex == 12:
        vel_x = -ratSpeed
        vel_y = 0
    elif vIndex == 13:
        vel_x = 0
        vel_y = 0
    elif vIndex == 14:
        vel_x = -ratSpeed/math.sqrt(2)
        vel_y = ratSpeed/math.sqrt(2)
    else: 
        vel_x = 0
        vel_y = 0

    i = 0
    for i_y in range(sheet_size):
        for i_x in range(sheet_size):
            prefDir = getPreferredDirection(i_x, i_y)
            sheetGroup.B[i] = (input + options.alpha*(prefDir[0]*vel_x +
                prefDir[1]*vel_y))*namp
            i+=1

    ratData['pos_x'][0][vIndex] = curr_pos_x*100 # m --> cm
    ratData['pos_y'][0][vIndex] = 0
    curr_pos_x += vel_x*vel_dt
    vIndex+=1
    vIndex = vIndex % 16


@network_operation(printStatusClock)
def printStatus():
    print "Simulated " + str(printStatusClock.t) + " seconds."
    sys.stdout.flush()

# Record the number of spikes
if options.record_sn_row == True:
    #SNList = range(sheet_size**2 / 2, sheet_size**2 / 2 + sheet_size)
    SNList = range(0, sheet_size**2, sheet_size+1)
else:
    #SNList = [sheet_size**2/4, sheet_size**2/2, (sheet_size**2)*3/4]
    SNList = True
SNMonitor = StateMonitor(sheetGroup, 'vm', record = SNList,
        clock=SNClock)
SNgMonitor = StateMonitor(sheetGroup, 'gi', record = SNList,
        clock=SNClock)

spikeGroupStart = int((sheet_size**2)*0.45)
spikeGroupEnd = int(spikeGroupStart + (sheet_size**2)/10)
spikeMonitorG = sheetGroup[spikeGroupStart:spikeGroupEnd]
#spikeMonitor = SpikeMonitor(spikeMonitorG)
spikeMonitor = SpikeMonitor(sheetGroup)

#printConn(sheet_size, inhibConn, options.write_data, options.print_only_conn)

print "Simulation running..."
start_time=time.time()
net = Network(sheetGroup, inhibConn, printStatus, updateVelocity, spikeMonitor)
if options.record_sn == True:
    net.add(SNMonitor)
    net.add(SNgMonitor)

net.run(options.time*second)
duration=time.time()-start_time
print "Simulation time:",duration,"seconds"


# Directory and filenames constants
timeSnapshot = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
dirName = options.output_dir
population_fname = dirName + timeSnapshot + '_spacePlot.eps'
options_fname = dirName + timeSnapshot + '.params'
count_fname = dirName + timeSnapshot + '_linePlot.eps'
conn_fname = dirName + timeSnapshot + "_conn.eps"

output_fname = dirName
if options.job_num != -1:
    output_fname = output_fname + 'job' + str(options.job_num)
output_fname +=  '_' + timeSnapshot + '_output.mat'



# write recorded data into .mat file
if (options.write_data):
    #f = open(options_fname, 'w')
    #f.write(str(options))
    #f.close()
    saveResultsToMat(output_fname, options)
