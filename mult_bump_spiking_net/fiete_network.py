from brian import *
from brian.library.IF import *
from brian.library.synapses import *
from brian.membrane_equations import *

from scipy import linspace
from scipy.io import loadmat
from optparse import OptionParser
from datetime import datetime

import time
import math
import random

# define provisional model parameters - these might be changed in the future

refractory = 20*ms;

# Synapse parameters
Ee=0*mvolt
Ei=-80*mvolt



def get_exp_IF(C, gL, EL, VT, DeltaT, Ei, taui, noise_sigma):
    #eqs=exp_IF(C,gL,EL,VT,DeltaT)
    taum = C/gL
    eqs = '''
        dvm/dt = 1/C*Im + (noise_sigma*xi/taum**.5): volt
        Im = gL*(EL-vm)+gL*DeltaT*exp((vm-VT)/DeltaT) + gi*(Ei - vm) + B  : amp
        dgi/dt = -gi/taui : siemens
        B : amp
        '''
    #eqs = MembraneEquation(C)+\
    #       Current('Im=gL*(EL-vm)+gL*DeltaT*exp((vm-VT)/DeltaT):amp',\
    #               gL=gL,EL=EL,DeltaT=DeltaT,exp=exp,VT=VT)

    #eqs=leaky_IF(taum, EL)
    # Use only inhibitory connections from Burak&Fiete, 2009. Should work if the
    # velocity input is non-zero even when speed is zero.
    #eqs+=exp_conductance('gi',Ei,taui) # from library.synapses
    #eqs+=Current('''B : amp''')

    # Noise current
    #eqs+=Current('xi/taum**.5 : amp',taum=taum)
    return eqs


# Get a preferred direction for a neuron
def getPreferredDirection(pos_x, pos_y):
# pos_x/y - position of neuron in 2d sheet
    pos4_x = pos_x % 2
    pos2_y = pos_y % 2
    if pos4_x == 0:
        if pos2_y == 0:
            return [-1, 0] # Left
        else:
            return [0, -1] # Down
    else:
        if pos2_y == 0:
            return [0, 1] # up
        else:
            return [1, 0] # Right

def getPreferredDirectionRandom(pos_x, pos_y):
    # return random preferred direction on the sheet
    return random.choice([[0, 1], [0, -1], [-1, 0], [1, 0]]);


def createNetwork(sheet_size, lambda_net, l, a, connMult, clock, taum_ms,
        taui_ms, threshold_mV, noise_sigma_mV, W = None):
    C=200*pF
    taum=taum_ms*msecond
    taui=taui_ms*msecond
    threshold=threshold_mV*mvolt
    noise_sigma = noise_sigma_mV*mvolt
    gL=C/taum
    EL=-70*mV
    VT=-55*mV
    DeltaT=3*mV

    beta = 3.0 / lambda_net**2
    gamma = 1.05 * beta

    sheetGroup=NeuronGroup(sheet_size**2,model=get_exp_IF(C, gL, EL, VT, DeltaT, Ei, taui, noise_sigma),threshold=threshold,reset=EL,refractory=refractory, clock=clock)

    if (W == None):
        inhibConn = Connection(sheetGroup, sheetGroup, 'gi', structure='dense');
        inh_matrix = asarray(inhibConn.W)
    
        # Create toroidal connections matrix on the 2d sheet
        for j in xrange(len(sheetGroup)):
            j_x = j % sheet_size
            j_y = j // sheet_size
            prefDir = getPreferredDirection(j_x, j_y)
            #prefDir = getPreferredDirectionRandom(j_x, j_y)
            for i in xrange(len(sheetGroup)):
                i_x = i % sheet_size
                i_y = i // sheet_size
                
                if abs(j_x - i_x) > sheet_size/2:
                    if i_x > sheet_size/2:
                        i_x = i_x - sheet_size
                    else:
                        i_x = i_x + sheet_size
                if abs(j_y - i_y) > sheet_size/2:
                    if i_y > sheet_size/2:
                        i_y = i_y - sheet_size
                    else:
                        i_y = i_y + sheet_size
        
                abs_x_sq = (i_x - j_x -l*prefDir[0])**2 + (i_y - j_y - l*prefDir[1])**2
                w = a*math.e**(-gamma*(abs_x_sq)) - math.e**(-beta*(abs_x_sq));
                inh_matrix[j, i] = connMult*abs(w)*nS
    else:
        inhibConn = Connection(sheetGroup, sheetGroup, 'gi', structure='dense')
        print 'Initializing connections from file...'
        inhibConn.connect(sheetGroup, sheetGroup, W)


    # Initialize membrane potential randomly
    if (noise_sigma == 0):
        sheetGroup.vm = EL + (VT-EL) * rand(len(sheetGroup))
    else:
        sheetGroup.vm = EL + zeros(len(sheetGroup))

    return [sheetGroup, inhibConn]


def printConn(sheet_size, conn, write_data, print_only_conn):
    # Plot connection matrix for neuron at position defined by row_i
    rows_i = [0.25*sheet_size**2 + 0.25*sheet_size, 0.25*sheet_size**2 +
            0.75*sheet_size, 0.75*sheet_size**2 + 0.25*sheet_size,
            0.75*sheet_size**2 + 0.75*sheet_size]
    plot_i = 1
    for row_i in rows_i:
        #col_i = row_i
        connRow = conn[row_i, :]
        #connCol = conn[:, col_i]
        
        x = arange(0, sheet_size)
        y = arange(0, sheet_size)
        X, Y = meshgrid(x, y)
        subplot(2,2, plot_i)
        contour(X, Y, reshape(connRow, (sheet_size, sheet_size)))
        #figure()
        #contour(X, Y, reshape(connCol, (sheet_size, sheet_size)))
        plot_i += 1
    xlabel("Neuron number")
    ylabel("Neuron number")
    if write_data:
        savefig(conn_fname, format="eps")
    elif print_only_conn == True:
        show()
        exit()
