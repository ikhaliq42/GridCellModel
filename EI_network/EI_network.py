from brian import *
from brian.library.IF import *
from brian.library.synapses import *
from brian.membrane_equations import *

from scipy import linspace
from scipy.io import loadmat
from optparse import OptionParser
from datetime import datetime

import numpy as np

import time
import math
import random



class EI_Network:
    def __init__(self, o, clk):
        if o.ndim == 1:
            self.net_Ne = o.Ne
            self.net_Ni = o.Ni
        elif o.ndim == 2:
            self.net_Ne = o.Ne**2
            self.net_Ni = o.Ni**2
        else:
            raise Exception("Number of Mexican hat dimensions must be 0 or 1" +
                ", not" + str(ndim) + ".")

        self._createBasicNet(o, clk)


    def _createBasicNet(self, o, clk):

        noise_sigma=o.noise_sigma*volt

        # Setup neuron equations
        # Using exponential integrate and fire model
        # Excitatory population
        Rm_e = o.Rm_e*ohm
        taum_e = o.taum_e*second
        Ce = taum_e/Rm_e
        EL_e = o.EL_e*volt
        deltaT_e = o.deltaT_e*volt
        Vt_e = o.Vt_e*volt
        Vr_e = o.Vr_e*volt
        tau_GABA_rise = o.tau_GABA_rise*second
        tau_GABA_fall = o.tau_GABA_fall*second
        tau1_GABA = tau_GABA_fall
        tau2_GABA = tau_GABA_rise*tau_GABA_fall / (tau_GABA_rise + tau_GABA_fall);
        self.B_GABA = 1/((tau2_GABA/tau1_GABA)**(tau_GABA_rise/tau1_GABA) - 
                (tau2_GABA/tau1_GABA)**(tau_GABA_rise/tau2_GABA))
        tau_ad_e = o.ad_tau_e_mean*second
        
        Vrev_GABA = o.Vrev_GABA*volt


        self.eqs_e = Equations('''
            dvm/dt = 1/C*Im + (noise_sigma*xi/taum**.5): volt
            Im = gL*(EL-vm)*(1+g_ad/gL)+gL*deltaT*exp((vm-Vt)/deltaT) + Isyn + Iext  : amp
            Isyn = (gi1 - gi2)*(Esyn - vm) : amp
            dgi1/dt = -gi1/syn_tau1 : siemens
            dgi2/dt = -gi2/syn_tau2 : siemens
            dg_ad/dt = -g_ad/tau_ad : siemens
            Iext : amp
            ''',
            C=Ce,
            gL=1/Rm_e,
            noise_sigma=noise_sigma,
            taum=taum_e,
            EL=EL_e,
            deltaT=deltaT_e,
            Vt=Vt_e,
            Esyn=Vrev_GABA,
            syn_tau1=tau1_GABA,
            syn_tau2=tau2_GABA,
            tau_ad=tau_ad_e)


        # Inhibitory population
        Rm_i = o.Rm_i*ohm
        taum_i = o.taum_i*second
        Ci = taum_i/Rm_i
        EL_i = o.EL_i*volt
        deltaT_i = o.deltaT_i*volt
        Vt_i = o.Vt_i*volt
        Vr_i = o.Vr_i*volt
        Vrev_AMPA = o.Vrev_AMPA*volt
        tau_AMPA = o.tau_AMPA*second
        tau_ad_i = o.ad_tau_i_mean*second
        
        self.eqs_i = Equations('''
            dvm/dt = 1/C*Im + (noise_sigma*xi/taum**.5): volt
            Im = gL*(EL-vm)*(1+g_ad/gL) + gL*deltaT*exp((vm-Vt)/deltaT) + Isyn + Iext  : amp
            Isyn = ge*(Esyn - vm) : amp
            dge/dt = -ge/syn_tau : siemens
            dg_ad/dt = -g_ad/tau_ad : siemens
            Iext : amp
            ''',
            C=Ci,
            gL=1/Rm_i,
            noise_sigma=noise_sigma,
            taum=taum_i,
            EL=EL_i,
            deltaT=deltaT_i,
            Vt=Vt_i,
            Esyn=Vrev_AMPA,
            syn_tau=tau_AMPA,
            tau_ad=tau_ad_i)


        # Other constants
        refrac_abs = o.refrac_abs*second
        spike_detect_th = o.spike_detect_th*volt



        # Setup neuron groups and connections
        self.E_pop = NeuronGroup(
                N = self.net_Ne,
                model=self.eqs_e,
                threshold=spike_detect_th,
                reset=Vr_e,
                refractory=refrac_abs,
                clock=clk)

        self.I_pop = NeuronGroup(
                N = self.net_Ni,
                model=self.eqs_i,
                threshold=spike_detect_th,
                reset=Vr_i,
                refractory=refrac_abs,
                clock=clk)



        ## Setup adaptation connections: neuron on itself
        #self.adaptConn_e = IdentityConnection(self.E_pop, self.E_pop,  'g_ad',
        #        weight=o.ad_e_g_inc*siemens)
        #self.adaptConn_i = IdentityConnection(self.I_pop, self.I_pop, 'g_ad',
        #        weight=o.ad_i_g_inc*siemens)


        # Initialize membrane potential randomly
        self.E_pop.vm = EL_e + (Vt_e-EL_e) * rand(len(self.E_pop))
        self.I_pop.vm = EL_i + (Vt_i-EL_i) * rand(len(self.I_pop))


        # Create network (withough any monitors
        self.net = Network(
                self.E_pop,
                self.I_pop)
                #self.adaptConn_e,
                #self.adaptConn_i)

        self.setBackgroundInput(o.Iext_e*amp, o.Iext_i*amp)

        self.o = o


    def setBackgroundInput(self, Iext_e, Iext_i):
        self.E_pop.Iext = linspace(Iext_e, Iext_e, len(self.E_pop))
        self.I_pop.Iext = linspace(Iext_i, Iext_i, len(self.I_pop))

    def _generate_pAMPA_template1D(self, N, mu, sigma):
        '''Generate AMPA probability profile function on an interval [0, N-1]. For
        now it will be a Gaussian profile, with mean mu and std. dev. sigma. The
        boundaries are wrapped-around (N==0). This is distance-dependent
        profile, which take wrap around boundaries into account.'''
        self.pAMPA_templ = np.exp(-(np.arange(N/2+1) - mu)**2/2.0/sigma**2)
        self.pAMPA_templ = np.concatenate((self.pAMPA_templ,
            self.pAMPA_templ[1:N-len(self.pAMPA_templ)+1][::-1]))

    def _generate_pAMPA_template2D(self, N, mu, sigma):
        mg = np.mgrid[0:N/2+1, 0:N/2+1]
        self.pAMPA_templ = np.exp(-(np.sqrt(mg[0]**2 + mg[1]**2) - mu)**2/2.0/sigma**2)

        # Stack horizontally and vertically
        ncols = len(self.pAMPA_templ[0])
        self.pAMPA_templ = np.hstack((self.pAMPA_templ, self.pAMPA_templ[:,
            1:N-ncols+1][:, ::-1]))
        nrows = len(self.pAMPA_templ)
        self.pAMPA_templ = np.vstack((self.pAMPA_templ,
            self.pAMPA_templ[1:N-nrows+1, :][::-1, :]))

    def _generate_pGABA_template1D(self, N, sigma):
        '''Generate GABA probability profile function on an interval [0, N-1].
        It is similar to generate_pAMPA_template but the mean is 0'''
        self.pGABA_templ = np.exp(-(np.arange(N/2+1))**2/2.0/sigma**2)
        self.pGABA_templ = np.concatenate((self.pGABA_templ,
            self.pGABA_templ[1:N-len(self.pGABA_templ)+1][::-1]))


    def _generate_pGABA_template2D(self, N, sigma):
        mg = np.mgrid[0:N/2+1, 0:N/2+1]
        self.pGABA_templ = np.exp(-(mg[0]**2 + mg[1]**2)/2.0/sigma**2)

        # Stack horizontally and vertically
        ncols = len(self.pGABA_templ[0])
        self.pGABA_templ = np.hstack((self.pGABA_templ, self.pGABA_templ[:,
            1:N-ncols+1][:, ::-1]))
        nrows = len(self.pGABA_templ)
        self.pGABA_templ = np.vstack((self.pGABA_templ,
            self.pGABA_templ[1:N-nrows+1, :][::-1, :]))

        
    def connMexicanHat(self, pAMPA_mu, pAMPA_sigma, pGABA_sigma):
        '''Create excitatory and inhibitory connections, Mexican hat ring model.
            pAMPA_mu    Mean of the AMPA Gaussian profile of connection
                        probability
            pAMPA_sigma Std. dev. of the AMPA Gaussian profile of connection
                        probability
            pGABA_sigma Std. dev. of the GABA Gaussian profile of connection
                        probability (Mean of GABA connections is local)
            ndim        Number of dimensions (1 or 2)
        '''

        g_AMPA_mean = self.o.g_AMPA_total/self.net_Ne
        g_AMPA_sigma = np.sqrt(np.log(1 + self.o.g_AMPA_std**2/g_AMPA_mean**2))
        g_AMPA_mu = np.log(g_AMPA_mean) - 1/2*g_AMPA_sigma**2
        g_GABA_mean = self.o.g_GABA_total / self.net_Ni * siemens

        # Generate connection-probability profile functions for GABA and AMPA connections
        self.pAMPA_mu = pAMPA_mu * self.o.Ni
        self.pAMPA_sigma = pAMPA_sigma * self.o.Ni
        self.pGABA_sigma = pGABA_sigma * self.o.Ne

        self.AMPA_conn = Connection(self.E_pop, self.I_pop, 'ge')
        self.GABA_conn1 = Connection(self.I_pop, self.E_pop, 'gi1')
        self.GABA_conn2 = Connection(self.I_pop, self.E_pop, 'gi2')

        if (self.o.ndim ==1):
            self._generate_pAMPA_template1D(self.o.Ni, self.pAMPA_mu, self.pAMPA_sigma)
            self._generate_pGABA_template1D(self.o.Ne, self.pGABA_sigma)
            for i in xrange(self.o.Ne):
                e_norm = int(round(np.double(i)/self.o.Ne*self.o.Ni))

                tmp_templ = np.roll(self.pAMPA_templ, e_norm)
                self.AMPA_conn.W.rows[i] = list((rand(self.o.Ni) <
                    self.o.AMPA_density*tmp_templ).nonzero()[0])
                self.AMPA_conn.W.data[i] = np.random.lognormal(g_AMPA_mu,
                        g_AMPA_sigma, len(self.AMPA_conn.W.rows[i]))*siemens

            for i in xrange(self.o.Ni):
                i_norm = int(round(np.double(i)/self.o.Ni*self.o.Ne))
                

                tmp_templ = np.roll(self.pGABA_templ, i_norm)
                self.GABA_conn1.W.rows[i] = list((rand(self.o.Ne) <
                    self.o.GABA_density*tmp_templ).nonzero()[0])
                self.GABA_conn1.W.data[i] = [self.B_GABA*g_GABA_mean] * len(self.GABA_conn1.W.rows[i])

        elif (self.o.ndim == 2):
            self._generate_pAMPA_template2D(self.o.Ni, self.pAMPA_mu, self.pAMPA_sigma)
            self._generate_pGABA_template2D(self.o.Ne, self.pGABA_sigma)

            # Do the same rolling as in the case of ndim==1, but in two
            # dimensions
            for r in xrange(self.o.Ne):
                r_e_norm = int(round(np.double(r)/self.o.Ne*self.o.Ni))
                tmp_r_templ = np.roll(self.pAMPA_templ, r_e_norm, 0)
                for c in xrange(self.o.Ne):
                    c_e_norm = int(round(np.double(c)/self.o.Ne*self.o.Ni))

                    tmp_templ = np.roll(tmp_r_templ, c_e_norm, 1).ravel('C')
                    it = r*self.o.Ne + c
                    self.AMPA_conn.W.rows[it] = list((rand(self.o.Ni**2) <
                        self.o.AMPA_density*tmp_templ).nonzero()[0])
                    self.AMPA_conn.W.data[it] = np.random.lognormal(g_AMPA_mu,
                            g_AMPA_sigma, len(self.AMPA_conn.W.rows[it]))*siemens

            for r in xrange(self.o.Ni):
                r_i_norm = int(round(np.double(r)/self.o.Ni*self.o.Ne))
                tmp_r_templ = np.roll(self.pGABA_templ, r_i_norm, axis=0)
                for c in xrange(self.o.Ni):
                    c_e_norm = int(round(np.double(c)/self.o.Ni*self.o.Ne))

                    tmp_templ = np.roll(tmp_r_templ, c_e_norm,
                            axis=1).ravel('C')
                    it = r*self.o.Ni + c
                    self.GABA_conn1.W.rows[it] = list((rand(self.o.Ne**2) <
                        self.o.GABA_density*tmp_templ).nonzero()[0])
                    self.GABA_conn1.W.data[it] = [self.B_GABA*g_GABA_mean] * len(self.GABA_conn1.W.rows[it])

        else:
            raise Exception("Number of Mexican hat dimensions must be 0 or 1" +
                ", not" + str(ndim) + ".")


        self.GABA_conn2.connect(self.I_pop, self.E_pop, self.GABA_conn1.W)

        self.net.add(self.AMPA_conn, self.GABA_conn1, self.GABA_conn2)
        self.ndim = ndim
