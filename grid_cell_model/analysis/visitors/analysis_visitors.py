#
#   analysis_visitors.py
#
#   Visitors that perform data analysis on data.
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
from scipy.optimize import leastsq
from os.path        import splitext

from interface        import DictDSVisitor, extractStateVariable, \
        extractSpikes, sumAllVariables
from otherpkg.log     import log_info
from analysis.signal  import localExtrema, butterBandPass, autoCorrelation
from analysis.image   import Position2D, fitGaussianBumpTT
from analysis.spikes  import slidingFiringRateTuple, ThetaSpikeAnalysis, \
        TorusPopulationSpikes


__all__ = ['AutoCorrelationVisitor', 'BumpFittingVisitor', 'FiringRateVisitor',
        'BumpVelocityVisitor']


def findFreq(ac, dt, ext_idx, ext_t):
    '''
    Find the first local maximum in an autocorrelation function and extract the
    frequency and the value of the autocorrelation at the detected frequency.

    Parameter, 'BumpVelocityVisitor']
    ----------
    ac : numpy vector
        A vector containing the autocorrelation function
    dt : float
        Sampling rate
    ext_idx : numpy array
        An array containig the indexes of local extrema (both maxima and
        minima) in 'ac'
    ext_t : numpy array
        The array of the same size as 'ext_idx', which contains the types of
        the local extrema ( >0 ... max, <0 ... min)
    output
        A tuple containig ('freq', 'corr'), where 'freq' is the frequency at
        the first local maximum and 'corr' is the value of the autocorrelation
        function at the same point.
    '''
    max_idx = np.nonzero(ext_t > 0)[0]
    if (len(max_idx) == 0):
        return (np.nan, np.nan)
    
    # First local maximum ac[0] excluded
    max1_idx = ext_idx[max_idx[0]]
    max1_t   = max1_idx * dt
    max1     = ac[max1_idx]

    return (1./max1_t, max1)




class AutoCorrelationVisitor(DictDSVisitor):
    '''
    A visitor to compute autocorrelations of state monitor data and extract
    information from them.

    The autocorrelation visitor takes as an input a state monitor, computes
    autocorrelations (with specified lag) of the specified synaptic currents
    and detects the major frequency, and power at that frequency, for all the
    monitored neurons. The results will be stored to the dictionary where the
    data came from.
    '''
    def __init__(self, monName, stateList, dtMult=1e-3, tStart=None, tEnd=None,
            norm=True, bandStart=20, bandEnd=200, forceUpdate=False):
        '''
        Initialise the visitor.

        Parameters
        ----------
        monName : string
            Name of the monitor; key in the data set dictionary
        stateList : list of strings
            A list of strings naming the state variables to extract (and sum)
        dtMult : float, optional
            dt Multiplier to transform dt into seconds
        tStart : float, optional
            Start time of the analysis. If None, the signal will not be
            cropped. The first value of the signal array is treated as time
            zero.
        tEnd : float, optional
            End time of the analysis. If None, the signal will not be cropped.
        norm : bool, optional
            Whether the autocorrelation function should be normalized
        bandStart : float, optional
            Bandpass start frequency
        bandEnd   : float, optional
            Bandpass end frequency
        forceUpdate : bool
            Whether to compute and store all the data even if they already
            exist in the data set.
        '''
        self.monName     = monName
        self.stateList   = stateList
        self.maxLag      = None
        self.dtMult      = dtMult
        self.tStart      = tStart
        self.tEnd        = tEnd
        self.norm        = norm
        self.bandStart   = bandStart
        self.bandEnd     = bandEnd
        self.forceUpdate = forceUpdate



    def extractACStat(self, mon):
        '''
        Extract autocorrelation statistics from a monitor.

        For each monitored neuron, extract the (highest) frequency, value of
        the autocorrelation at the frequency and the autocorrelation function
        itself.
    
        Parameters
        ----------
        mon : list of dicts
            A list of (NEST) state monitors' status dictionaries
        output : tuple
            A tuple (freq, acval, acVec), containing the arrays of frequencies
            for the monitored neurons, autocorrelation values at the
            corresponding frequencies, and autocorrelation functions of all the
            neurons.
        '''
        freq   = [] # Frequency of input signal
        acval  = [] # Auto-correlation at the corresponding frequency
        acVec  = []
        for n_id in range(len(mon)):
        #for n_id in range(5):
            #print "n_id: ", n_id
            sig, dt = sumAllVariables(mon, n_id, self.stateList)
            startIdx = 0
            endIdx   = len(sig)
            print(len(sig))
            if (self.tStart is not None):
                startIdx = int(self.tStart / dt)
            if (self.tEnd is not None):
                endIdx = int(self.tEnd / dt)
            sig = sig[startIdx:endIdx]
            print(len(sig))
            sig = butterBandPass(sig, dt*self.dtMult, self.bandStart,
                    self.bandEnd)
            ac = autoCorrelation(sig - np.mean(sig), max_lag=self.maxLag/dt,
                    norm=self.norm)
            ext_idx, ext_t = localExtrema(ac)
            acVec.append(ac)
    
            f, a = findFreq(ac, dt*self.dtMult, ext_idx, ext_t)
            freq.append(f)
            acval.append(a)
    
        return freq, acval, acVec, dt


    def visitDictDataSet(self, ds, **kw):
        '''
        Visit the dictionary data set and extract frequency, autocorrelation
        for the detected frequency, and autocorrelation functions, for all the
        monitored neurons.  The parameters are defined by the constructor of
        the object.

        If the analysed data is already present, the analysis and storage of
        the data will be skipped.

        Parameters
        ----------
        ds : a dict-like object
            A data set to perform analysis on.
        '''
        data = ds.data
        if (not self.folderExists(data, ['analysis'])):
            data['analysis'] = {}
        a = data['analysis']

        if (('freq' not in a.keys()) or self.forceUpdate):
            log_info("AutoCorrelationVisitor", "Analysing a dataset")
            o = data['options']
            self.maxLag = 1. / (o['theta_freq'] * 1e-3)
            freq, acVal, acVec, dt = self.extractACStat(data[self.monName])
            print freq
            a['freq']  = np.array(freq)
            a['acVal'] = np.array(acVal)
            a['acVec'] = np.array(acVec)
            a['ac_dt'] = dt
        else:
            log_info("AutoCorrelationVisitor", "Data present. Skipping analysis.")



class BumpFittingVisitor(DictDSVisitor):
    '''
    The bump fitting visitor takes spikes of the neural population (in the
    dictionary data set provided) and tries to
    fit a Gaussian shaped function to the population firing rate map (which is
    assumed to be a twisted torus). It saves the data under the 'analysis' key
    into the dataset.

    If the corresponding data is already present the visitor skips the data
    analysis and saving.
    '''
    
    def __init__(self, forceUpdate=False):
        self.forceUpdate = forceUpdate

        # Population FR parameters
        # All time units in msec
        self.dt     = 20.0
        self.winLen = 250.0

    def fitGaussianToMon(self, mon, Nx, Ny, tstart, tend):
        '''
        Fit a Gaussian function to the monitor mon, and return the results.
        '''
        N = Nx * Ny

        senders, times = extractSpikes(mon)
        F, Ft = slidingFiringRateTuple((senders, times), N, tstart, tend,
                self.dt, self.winLen)
            
        bumpT = tend - 2*self.winLen
        bumpI = bumpT / self.dt
        bump = np.reshape(F[:, bumpI], (Ny, Nx))
        dim = Position2D()
        dim.x = Nx
        dim.y = Ny
        return fitGaussianBumpTT(bump, dim)

    def visitDictDataSet(self, ds, **kw):
        '''
        Apply the bump fitting procedure onto the dataset 'ds' if necessary,
        and save the data into the dataset.
        '''
        data = ds.data
        if (('analysis' not in data.keys())):
            data['analysis'] = {}

        a = data['analysis']
        tstart = 0.0
        tend   = self.getOption(data, 'time')
        if (('bump_e' not in a.keys()) or self.forceUpdate):
            log_info("BumpFittingVisitor", "Analysing a dataset")
            # Fit the Gaussian onto E neurons
            Nx  = self.getNetParam(data, 'Ne_x')
            Ny  = self.getNetParam(data, 'Ne_y')
            mon = data['spikeMon_e']
            (A, mu_x, mu_y, sigma), err2 = self.fitGaussianToMon(mon, Nx, Ny,
                    tstart, tend)
            a['bump_e'] = {
                    'A' : A,
                    'mu_x' : mu_x,
                    'mu_y' : mu_y,
                    'sigma' : np.abs(sigma),
                    'err2'  : np.sum(err2)
            }

            # Fit the Gaussian onto I neurons
            # TODO
        else:
            log_info("BumpFittingVisitor", "Data present. Skipping analysis.")


class FiringRateVisitor(DictDSVisitor):
    '''
    Determine various firing rate statistics of a population of neurons on the
    spiking data dataset:
        * Average firing rate in the middle of the theta cycle

    Save the data to the original data set.
    '''

    def __init__(self, winLen=0.5, thetaStartT=None, thetaFreq=None, tEnd=None, 
            forceUpdate=False):
        '''
        Initialize the visitor.

        Parameters
        ----------
        winLen : float (ms)
            Length of the firing rate window as a fraction of the theta cycle
            time (0, 1>.
        thetaStartT : float (ms)
            Start time of the theta signal. The center of the firing rate
            window will be in the middle of the theta signal. Therefore it is
            up to the user to ensure that the peak of the theta signal is in
            the middle. If None, extract from the data when performing analysis
        thetaFreq : float (Hz)
            Theta signal frequency. If None, extract from the data
        tEnd : float (ms)
            Analysis end time. If None, extract from the data
        forceUpdate : boolean, optional
            Whether to do the data analysis even if the data already exists.
        '''
        self.thetaStartT = thetaStartT
        self.thetaFreq   = thetaFreq
        self.tEnd        = tEnd
        self.winLen      = winLen
        self.forceUpdate = forceUpdate


    def _getSpikeTrain(self, data, monName, dimList):
        senders, times, N = DictDSVisitor._getSpikeTrain(self, data, monName,
                dimList)
        return ThetaSpikeAnalysis(N, senders, times)

    def visitDictDataSet(self, ds, **kw):
        data = ds.data
        if (not self.folderExists(data, ['analysis'])):
            data['analysis'] = {}
        a = data['analysis']

        thetaStartT = self._checkAttrIsNone(self.thetaStartT,
                'theta_start_t', data)
        thetaFreq = self._checkAttrIsNone(self.thetaFreq, 'theta_freq',
                data)
        tEnd = self._checkAttrIsNone(self.tEnd, 'time', data)
        if (not self.folderExists(a, ['FR_e']) or self.forceUpdate):
            log_info('FiringRateVisitor', "Analysing...")
            eSp = self._getSpikeTrain(data, 'spikeMon_e', ['Ne_x', 'Ne_y'])
            eFR = eSp.avgFiringRate(thetaStartT, tEnd)
            a['FR_e'] = {
                    'all' : eFR,
                    'avg' : np.mean(eFR)
            }

            iSp = self._getSpikeTrain(data, 'spikeMon_i', ['Ni_x', 'Ni_y'])
            iFR = iSp.avgFiringRate(thetaStartT, tEnd)
            a['FR_i'] = {
                    'all' : iFR,
                    'avg' : np.mean(iFR)
            }
        else:
            log_info("FiringRateVisitor", "Data present. Skipping analysis.")


###############################################################################


def fitCircularSlope(bumpPos, times, normFac):
    '''
    Fit a (circular) slope line onto velocity response of the bump and extract
    the slope (velocity), in neurons/s

    Parameters
    ----------
    bumpPos : numpy array
        An array of bump positions
    times : numpy array
        A corresponding vector of times, of the same size as bumpPos
    normFac : float
        Normalizing factor for the positional vector. In fact this is the size
        of the toroidal sheet (X direction).
    output : float
        Estimated bump speed (neurons/time unit).
    '''
    t = np.array(times) - times[0]
    bumpPos_norm = np.unwrap(1.0 * bumpPos / normFac * 2 * np.pi) # normalise to 2*Pi
    func = lambda X: X[0]*t - bumpPos_norm
    x0 = np.array([0.0])  # slope
    x = leastsq(func, x0)
    return x[0][0] / 2. / np.pi * normFac
    

def getLineFit(Y):
    '''
    Fit a line to data
    '''
    X = np.arange(len(Y))
    
    func = lambda P: P[0]*X  - Y
    P0 = np.array([0.0]) # slope
    P = leastsq(func, P0)
    return P[0][0]*X, P[0][0]


class BumpVelocityVisitor(DictDSVisitor):
    '''
    A visitor that estimates the relationship between injected velocity current
    and bump speed.
    '''

    def __init__(self, win_dt=20.0, winLen=250.0, forceUpdate=False,
            printSlope=False, lineFitMaxIdx=None):
        self.win_dt = win_dt
        self.winLen = winLen
        self.forceUpdate = forceUpdate
        self.printSlope = printSlope
        self.lineFitMaxIdx = lineFitMaxIdx


    def _getSpikeTrain(self, data, monName, dimList):
        N_x = self.getNetParam(data, dimList[0])
        N_y = self.getNetParam(data, dimList[1])
        senders, times = extractSpikes(data[monName])
        return senders, times, (N_x, N_y)


    def visitDictDataSet(self, ds, **kw):
        '''
        Visit a data set that contains all the trials and Ivel simulations.
        '''
        data = ds.data
        trials = data['trials']

        slopes = []
        for trialNum in xrange(len(trials)):
            log_info('BumpVelocityVisitor', "Trial no. {0}.".format(trialNum))
            slopes.append([])
            IvelVec = trials[trialNum]['IvelVec']
            for IvelIdx in xrange(len(IvelVec)):
                iData = trials[trialNum]['IvelData'][IvelIdx]
                #if 'analysis' in iData.keys() and not self.forceUpdate:
                #    log_info('BumpVelocityVisitor', "Data present. Skipping analysis.")
                #    continue

                senders, times, sheetSize =  self._getSpikeTrain(iData,
                        'spikeMon_e', ['Ne_x', 'Ne_y'])
                pop = TorusPopulationSpikes(senders, times, sheetSize)
                tStart = self.getOption(iData, 'theta_start_t')
                tEnd   = self.getOption(iData, 'time')
                bumpPos, bumpPos_t = pop.populationVector(tStart, tEnd,
                        self.win_dt, self.winLen)
                slope = fitCircularSlope(bumpPos[:, 0], bumpPos_t,
                        sheetSize[0]/2.0)*1e3
                slopes[trialNum].append(slope)
                iData['analysis'] = {
                        'bumpPos'   : bumpPos,
                        'bumpPos_t' : bumpPos_t,
                        'slope'     : slope
                }
        slopes = np.array(slopes)

        analysisTop = {'bumpVelAll' : slopes}


        if (self.printSlope and 'fileName' not in kw.keys()):
            msg = 'printSlope requested, but did not receive the fileName ' + \
                    'as a keyword argument.'
            log_warn('BumpVelocityVisitor', msg)
            return
        elif (self.printSlope):
            if (len(trials) == 0):
                msg = 'Something wrong: len(trials) == 0'
                log_warn('BumpVelocityVisitor', msg)
                return


            # Plot the estimated bump velocities (nrns/s)
            from matplotlib.pyplot import figure, errorbar, xlabel, ylabel, \
                    plot, title, savefig, legend
            figure()
            IvelVec = trials[0]['IvelVec'] # All the same
            avgSlope = np.mean(slopes, axis=0)
            stdErrSlope = np.std(slopes, axis=0) / np.sqrt(len(trials))
            errorbar(IvelVec, avgSlope, stdErrSlope, fmt='o-')
            xlabel('Velocity current (pA)')
            ylabel('Bump velocity (neurons/s)')

            # Fit a line (nrns/s/pA)
            if (self.lineFitMaxIdx is None):
                fitRange = len(IvelVec)
            else:
                fitRange = min(self.lineFitMaxIdx+1, len(IvelVec))
            log_info('BumpVelocityVisitor', 'fitRange == {0}'.format(fitRange))
            fitAvgSlope = avgSlope[0:fitRange]
            fitIvelVec  = IvelVec[0:fitRange]
            line, slope = getLineFit(fitAvgSlope)
            lineFitErr = np.abs(line - fitAvgSlope)
            slope = slope/(fitIvelVec[1] - fitIvelVec[0])
            plot(fitIvelVec, line, 'o-')
            title("Line fit slope: {0:.3f} nrns/s/pA".format(slope))
            legend(['Estimated bump speed', 'Line fit'], loc='best')
            
            fileName = splitext(kw['fileName'])[0] + '.pdf'
            savefig(fileName)

            analysisTop.update({
                'lineFitLine'  : line,
                'lineFitSlope' : slope,
                'lineFitErr'   : lineFitErr,
                'fitRange'     : fitRange
            })

        data['analysis'] = analysisTop