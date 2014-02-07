#!/usr/bin/env python
#
'''
Perform analysis on whole 2D data sets.
'''
import matplotlib
matplotlib.use('agg')

import visitors as vis
from parameters import JobTrialSpace2D
from submitting import flagparse

###############################################################################
parser = flagparse.FlagParser()
parser.add_argument('--row',          type=int, required=True)
parser.add_argument('--col',          type=int, required=True)
parser.add_argument('--shapeRows',    type=int, required=True)
parser.add_argument('--shapeCols',    type=int, required=True)
parser.add_argument('--forceUpdate',  type=int, required=True)
parser.add_argument("--output_dir",   type=str, required=True)
parser.add_argument("--job_num",      type=int) # unused
parser.add_argument("--type",         type=str,
        choices=['gamma-bump', 'velocity', 'grids'], required=True)
parser.add_argument("--bumpSpeedMax", type=float)

o = parser.parse_args()

###############################################################################

shape = (o.shapeRows, o.shapeCols)
dataPoints = [(o.row, o.col)]
trialNums = None

sp = JobTrialSpace2D(shape, o.output_dir, dataPoints=dataPoints)
forceUpdate = bool(o.forceUpdate)

if (o.type == "gamma-bump"):
    monName   = 'stateMonF_e'
    stateList = ['I_clamp_GABA_A']
    iterList  = ['g_AMPA_total', 'g_GABA_total']
    ACVisitor = vis.AutoCorrelationVisitor(monName, stateList,
            forceUpdate=forceUpdate)
    bumpVisitor = vis.BumpFittingVisitor(forceUpdate=forceUpdate,
            tstart='full',
            readme='Bump fitting. Whole simulation, starting at the start of theta stimulation.',
            bumpERoot='bump_e_full',
            bumpIRoot='bump_i_full')
    bumpPosVisitor = vis.bumps.BumpPositionVisitor(
            tstart=0,
            tend=None,
            win_dt=100,
            readme='Bump position estimation. Whole simulation',
            forceUpdate=forceUpdate)
    FRVisitor = vis.FiringRateVisitor(forceUpdate=forceUpdate)
    CCVisitor = vis.CrossCorrelationVisitor(monName, stateList,
            forceUpdate=forceUpdate)
    spikeVisitor_e = vis.SpikeStatsVisitor("spikeMon_e",
            forceUpdate=forceUpdate)

    #sp.visit(ACVisitor)
    #sp.visit(bumpVisitor)
    sp.visit(bumpPosVisitor)
    #sp.visit(FRVisitor)
    #sp.visit(CCVisitor)
    #sp.visit(spikeVisitor_e)
elif (o.type == "velocity"):
    VelVisitor = vis.BumpVelocityVisitor(o.bumpSpeedMax, forceUpdate=forceUpdate, printSlope=True)
    sp.visit(VelVisitor, trialList='all-at-once')
elif (o.type == 'grids'):
    spikeType = 'E'
    po = vis.GridPlotVisitor.PlotOptions()
    gridVisitor = vis.GridPlotVisitor(o.output_dir, spikeType=spikeType,
            plotOptions=po, minGridnessT=300e3)
    ISIVisitor = vis.ISIPlotVisitor(o.output_dir,
            spikeType = spikeType,
            nRows = 5, nCols = 5, range=[0, 1000], bins=40,
            ISINWindows=20)
    FRVisitor = vis.FiringRateVisitor(forceUpdate=forceUpdate)

    sp.visit(gridVisitor)
    sp.visit(ISIVisitor)
    sp.visit(FRVisitor)
else:
    raise ValueError("Unknown analysis type option: {0}".format(o.type))
