#
#   grid_cell_network.py
#
#     Copyright (C) 2012  Lukas Solanka <l.solanka@sms.ed.ac.uk>
#     
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


################################################################################
#  Grid cell network set up
#
#  This file is a module for the grid cell network. It allows you to create a
#  network of Exponential integrate and fire neurons. There are two populations:
#    Stellate cells -- excitatory neurons (E)
#    Interneurons   -- inhibitory (I)
#
#  In the current model, the connections are only E --> I and I --> E. That is
#  the main idea behind the model, which is supported by experimental evidence.
#
#  Both neuron types can receive AMPA, NMDA and GABA_A events. NMDA is only in
#  E --> I direction.
#
#  The topology of connections has several characteristics:
#
#   - Both neuron models are uniformly placed on a surface of a twisted torus,
#     the sides of which are scaled as X:Y = 1:sqrt(3)/2, to accomodate the
#     hexagonal nature of grid-cell receptive fields.
#
#   - The user can set the number of neurons in the larger side of the toroidal
#     sheet (always X dimension)
#
#   - The connections follow a center-surround profile, i.e. either E-->I
#     connections have a surround profile and I-->E connections have a center
#     profile, or vice-versa. This can be used to test the effect of the type of
#     excitatory or inhibitory profile on the stability of the attractor
#
#   - GABA_A connections (I-->E) can also contain extra, randomly generated
#     inhibitory synapses onto stellate cells in order to allow generation of
#     gamma oscillations.
#
#   - Technically, the basic functionality of the model (attractor emergence,
#     oscillations), shouldn't be very dependent on the spiking neuron type.
#     After some parameter setups/changes, one should be able to set the
#     simulation with any kind of spiking model (leaky IaF, Hodgkin-Huxley,
#     etc.)
#

from common import *

import numpy as np
import logging as lg
from scipy import linspace
from np.random import rand


class GridCellNetwork(object):
    '''
    This is an interface to the grid cell network. One should be able to set
    it up, simulate and record from neurons, quite independently of a specific
    simulator. We don't use PyNN here because its generic interface is not
    suitable for this purpose

    The GridCellNetwork creates two separate populations and connects them
    according to the specified connectivity rules.
    '''

    def __init__(self, neuronOpts, simulationOpts):
        self.no = neuronOpts
        self.so = simulationOpts

        # Setup neuron numbers for each dimension (X, Y)
        # We have a single bump and to get hexagonal receptive fields the X:Y
        # size ratio must be 1:sqrt(3)/2
        self.y_dim = np.sqrt(3)/2.0
        self.Ne_x = o.Ne
        self.Ne_y = int(np.ceil(o.Ne * self.y_dim)) // 2 * 2

        self.Ni_x = o.Ni
        self.Ni_y = int(np.ceil(o.Ni * self.y_dim)) // 2 * 2

        self.net_Ne = self.Ne_x * self.Ne_y
        self.net_Ni = self.Ni_x * self.Ni_y

    def simulate(self, time):
        raise NotImplementedException("GridCellNetwork.simulate")


    def _divergentConnectEI(self, pre, post, weights):
        '''
        Simply connect a 'pre' neuron in the E population to all neurons in
        the I population from post, with given weights
        '''
        raise NotImplementedException("GridCellNetwork.divergentConnectEI")

    def _divergentConnectIE(self, pre, post, weights):
        '''
        Simply connect a 'pre' neuron in the I population to all neurons in
        the E population from post, with given weights
        '''
        raise NotImplementedException("GridCellNetwork.divergentConnectIE")

    def getOutgoingConnections(self, prePop, postPop, nid):
        '''
        Return an array of target neuron ids (local within postPop) and their
        weights, of a neuron with nid, within prePop
        '''
        raise NotImplementedException("GridCellNetwork.getOutgoingConnections")



    def _remap_twisted_torus(self, a, others, prefDir):
        a_x = a[0, 0]
        a_y = a[0, 1]
        prefDir_x = prefDir[0, 0]
        prefDir_y = prefDir[0, 1]

        others_x = others[:, 0] + prefDir_x
        others_y = others[:, 1] + prefDir_y

        d1 = sqrt((a_x - others_x)**2 + (a_y - others_y)**2)
        d2 = sqrt((a_x - others_x - 1.)**2 + (a_y - others_y)**2)
        d3 = sqrt((a_x - others_x + 1.)**2 + (a_y - others_y)**2)
        d4 = sqrt((a_x - others_x + 0.5)**2 + (a_y - others_y - self.y_dim)**2)
        d5 = sqrt((a_x - others_x - 0.5)**2 + (a_y - others_y - self.y_dim)**2)
        d6 = sqrt((a_x - others_x + 0.5)**2 + (a_y - others_y + self.y_dim)**2)
        d7 = sqrt((a_x - others_x - 0.5)**2 + (a_y - others_y + self.y_dim)**2)
        
        return np.min((d1, d2, d3, d4, d5, d6, d7), 0)
            

    def _generate_pAMPA_twisted_torus(self, a, others, pAMPA_mu, pAMPA_sigma,
            prefDir, prefDirC):
        '''
        Here we assume that X coordinates are normalised to <0, 1), and Y
        coordinates are normalised to <0, sqrt(3)/2)
        Y coordinates are twisted, i.e. X will have additional position shifts
        when determining minimum
        '''
        prefDir = np.array(prefDir, dtype=float)
        prefDir[0, 0] = 1. * prefDir[0, 0] * prefDirC / self.Ni_x
        prefDir[0, 1] = 1. * prefDir[0, 1] * prefDirC / self.Ni_y * self.y_dim
        d = self._remap_twisted_torus(a, others, prefDir)
        return np.exp(-(d - pAMPA_mu)**2/2/pAMPA_sigma**2)


    def _generate_pGABA_twisted_torus(self, a, others, sigma, prefDir,
        prefDirC):

        #import pdb; pdb.set_trace()
        prefDir = np.array(prefDir, dtype=float)
        prefDir[0, 0] = 1. * prefDir[0, 0] * prefDirC / self.Ne_x
        prefDir[0, 1] = 1. * prefDir[0, 1] * prefDirC / self.Ne_y * self.y_dim
        d = self._remap_twisted_torus(a, others, prefDir)
        return np.exp(-d**2/2./sigma**2)


    def _centerSurroundConnection(self, pAMPA_mu, pAMPA_sigma, pGABA_sigma):
        '''
        Create a center-surround excitatory and inhibitory connections between
        both populations.

        The connections are remapped to [1.0, sqrt(3)/2], whether the topology
        is a twisted torus or just a regular torus.
        '''

        g_AMPA_mean = self.o.g_AMPA_total / self.net_Ne
        g_GABA_mean = self.o.g_GABA_total / self.net_Ni

        # E --> I connections
        X, Y = np.meshgrid(np.arange(self.Ni_x), np.arange(self.Ni_y))
        X = 1. * X / self.Ni_x
        Y = 1. * Y / self.Ni_y * self.y_dim
        others_e = np.vstack((X.ravel(), Y.ravel())).T

        self.prefDirs_e = np.ndarray((self.net_Ne, 2))
        E_W = np.asarray(self.AMPA_conn.W)
        for y in xrange(self.Ne_y):
            y_e_norm = float(y) / self.Ne_y * self.y_dim

            for x in xrange(self.Ne_x):
                it = y*self.Ne_x + x

                x_e_norm = float(x) / self.Ne_x

                a = np.array([[x_e_norm, y_e_norm]])
                pd = getPreferredDirection(x, y)
                self.prefDirs_e[it, :] = pd
                tmp_templ = self._generate_pAMPA_twisted_torus(a, others_e,
                        pAMPA_mu, pAMPA_sigma, np.array([[pd[0], pd[1]]]),
                        self.o.prefDirC)

                self._divergentConnectEI(it, range(self.net_Ni),
                        tmp_templ*g_AMPA_mean)

        # I --> E connections
        conn_th = 1e-5
        self.prefDirs_i = np.ndarray((self.net_Ni, 2))
        X, Y = np.meshgrid(np.arange(self.Ne_x), np.arange(self.Ne_y))
        X = 1. * X / self.Ne_x
        Y = 1. * Y / self.Ne_y * self.y_dim
        others_i = np.vstack((X.ravel(), Y.ravel())).T
        for y in xrange(self.Ni_y):
            y_i_norm = float(y) / self.Ni_y * self.y_dim
            for x in xrange(self.Ni_x):
                x_i_norm = float(x) / self.Ni_x
                it = y*self.Ni_x + x

                a = np.array([[x_i_norm, y_i_norm]])
                pd = np.array([0, 0])
                self.prefDirs_i[it, :] = pd
                tmp_templ = self._generate_pGABA_twisted_torus(a, others_i,
                        pGABA_sigma, [[pd[0], pd[1]]], self.o.prefDirC)

                E_nid = (tmp_templ > conn_th).nonzero()[0]
                self._divergentConnectIE(it, E_nid, self.B_GABA*g_GABA_mean*tmp_templ[E_nid])


    #def randomInhibition(self, total_strength, density):
    #    '''Random inhibitory connections from I to E only'''

    #    g_GABA_mean = total_strength / self.net_Ni / density * siemens

    #    self.extraGABA_conn1 = Connection(self.I_pop, self.E_pop, 'gi1')
    #    self.extraGABA_conn2 = Connection(self.I_pop, self.E_pop, 'gi2')

    #    self.extraGABA_conn1.connect_random(self.I_pop, self.E_pop, density,
    #            weight=self.B_GABA*g_GABA_mean)
    #    self.extraGABA_conn2.connect(self.I_pop, self.E_pop, self.extraGABA_conn1.W) 

    #    self.net.add(self.extraGABA_conn1, self.extraGABA_conn2)

