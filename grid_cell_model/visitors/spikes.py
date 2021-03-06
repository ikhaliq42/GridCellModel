'''
Visitors that perform (raw) spikes analysis.
'''
from __future__ import absolute_import, print_function

import logging

import numpy as np

from ..analysis import spikes as aspikes
from ..data_storage.sim_models import ei as simei
from ..otherpkg.log import getClassLogger
from .interface import DictDSVisitor

FRLogger = getClassLogger("FiringRateVisitor", __name__)
statsLogger = getClassLogger("SpikeStatsVisitor", __name__)

__all__ = ['FiringRateVisitor', 'SpikeStatsVisitor']



##############################################################################
#                           Firing rates

class FiringRateVisitor(DictDSVisitor):
    '''
    Determine various firing rate statistics of a population of neurons on the
    spiking data dataset:
        * Average firing rate of all the neurons.

    '''

    def __init__(self, winLen, winDt, tStart=None, tEnd=None, forceUpdate=False,
                 sliding_analysis=True):
        '''
        Initialize the visitor.

        Parameters
        ----------
        winLen : float (ms)
            Length of the firing rate window as a fraction of the theta cycle
            time (0, 1>.
        winDt : float (ms)
            ``dt`` of the firing rate window.
        tStart : float (ms)
            Start time of the analysis.
        tEnd : float (ms)
            Analysis end time. If None, extract from the data
        forceUpdate : boolean, optional
            Whether to do the data analysis even if the data already exists.
        sliding_analysis : boolean, optional
            Whether to perform sliding window analysis. Might consume lots of
            RAM on long simulation times.
        '''
        self.tStart      = tStart
        self.tEnd        = tEnd
        self.winLen      = winLen
        self.winDt       = winDt
        self.forceUpdate = forceUpdate
        self.sliding     = sliding_analysis


    def _getSpikeTrain(self, data, monName, dimList):
        senders, times, N = DictDSVisitor._getSpikeTrain(self, data, monName,
                dimList)
        return aspikes.PopulationSpikes(N, senders, times)

    def visitDictDataSet(self, ds, **kw):
        data = ds.data
        if (not self.folderExists(data, ['analysis'])):
            data['analysis'] = {}
        a = data['analysis']

        tStart = self._checkAttrIsNone(self.tStart, 'theta_start_t', data)
        tEnd = self._checkAttrIsNone(self.tEnd, 'time', data)

        eSp = self._getSpikeTrain(data, 'spikeMon_e', ['Ne_x', 'Ne_y'])
        iSp = self._getSpikeTrain(data, 'spikeMon_i', ['Ni_x', 'Ni_y'])

        if (not self.folderExists(a, ['FR_e']) or self.forceUpdate):
            FRLogger.info("Analysing (FR_e)")
            eFR = eSp.avgFiringRate(tStart, tEnd)
            a['FR_e'] = {
                    'all'             : eFR,
                    'avg'             : np.mean(eFR),
            }
        else:
            FRLogger.info("Data present (FR_e), skipping.")


        if self.sliding:
            frE = a['FR_e']
            if not ('popSliding' in frE.keys() and 'popSlidingTimes' in
                    frE.keys()):
                FRLogger.info("Analysing (sliding FR_e)")
                eSlidingFR, eSlidingFRt = eSp.slidingFiringRate(
                                            tStart, tEnd, self.winDt,
                                            self.winLen)
                frE.update({
                        'popSliding'      : np.mean(eSlidingFR, axis=0),
                        'popSlidingTimes' : eSlidingFRt
                })
            else:
                FRLogger.info("Data present (sliding FR_e), skipping.")


        if (not self.folderExists(a, ['FR_i']) or self.forceUpdate):
            FRLogger.info("Analysing (FR_i)")
            iFR = iSp.avgFiringRate(tStart, tEnd)
            a['FR_i'] = {
                    'all'             : iFR,
                    'avg'             : np.mean(iFR)
            }
        else:
            FRLogger.info("Data present (FR_i), skipping.")


        if self.sliding:
            frI = a['FR_i']
            if not ('popSliding' in frI.keys() and 'popSlidingTimes' in
                    frI.keys()):
                FRLogger.info("Analysing (sliding FR_i)")
                iSlidingFR, iSlidingFRt = iSp.slidingFiringRate(
                                            tStart, tEnd, self.winDt,
                                            self.winLen)
                frI.update({
                        'popSliding'      : np.mean(iSlidingFR, axis=0),
                        'popSlidingTimes' : iSlidingFRt
                })
            else:
                FRLogger.info("Data present (sliding FR_i), skipping.")



##############################################################################

class SpikeStatsVisitor(DictDSVisitor):
    def __init__(self, monitorName, forceUpdate=False):
        '''
        Parameters:

        monitorName : string
            Name of the monitor in the data hierarchy.
        '''
        self.allowedMonitors = ['spikeMon_e', 'spikeMon_i']
        if (not monitorName in self.allowedMonitors):
            msg = "monitorName must be one of {0}".format(allowedMonitors)
            raise ValueError(msg)

        self.monitorName = monitorName
        self.forceUpdate = forceUpdate

        if (self.monitorName == "spikeMon_e"):
            self.NName = "net_Ne"
            self.outputName = "CV_e"
        elif (self.monitorName == "spikeMon_i"):
            self.NName = "net_Ni"
            self.outputName = "CV_i"


    def visitDictDataSet(self, ds, **kw):
        data = ds.data

        if (not self.folderExists(data, ['analysis'])):
            data['analysis'] = {}
        a = data['analysis']

        if (self.outputName in a.keys() and not self.forceUpdate):
            statsLogger.info("Data present. Skipping analysis.")
            return

        spikes = simei.MonitoredSpikes(data, self.monitorName, self.NName)
        a[self.outputName] = np.array(spikes.ISICV())
