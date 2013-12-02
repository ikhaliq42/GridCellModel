#!/usr/bin/env python
#
#   figure1.py
#
#   Noise publication Figure 1.
#
#       Copyright (C) 2013  Lukas Solanka <l.solanka@sms.ed.ac.uk>
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
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.ticker as ti
from matplotlib.transforms import Bbox

from EI_plotting import sweeps, examples, details
from figures_shared       import NoiseDataSpaces
from parameters           import JobTrialSpace2D

import logging as lg
#lg.basicConfig(level=lg.WARN)
lg.basicConfig(level=lg.INFO)

from matplotlib import rc
rc('pdf', fonttype=42)
rc('mathtext', default='regular')

plt.rcParams['font.size'] = 11

outputDir = "panels/"

NTrials=3
gridTrialNumList = np.arange(NTrials)
iterList  = ['g_AMPA_total', 'g_GABA_total']

noise_sigmas  = [0, 150, 300]
exampleIdx    = [(1, 22), (1, 22), (1, 22)] # (row, col)
bumpDataRoot  = None
velDataRoot   = None
gridsDataRoot = 'output_local/even_spacing/grids'
shape = (31, 31)

grids          = 0
examplesFlag   = 0
detailed_noise = 1

##############################################################################
roots = NoiseDataSpaces.Roots(bumpDataRoot, velDataRoot, gridsDataRoot)
ps    = NoiseDataSpaces(roots, shape, noise_sigmas)


sweepFigSize = (2.8, 3.5)
sweepLeft   = 0.2
sweepBottom = 0.1
sweepRight  = 0.87
sweepTop    = 0.95

cbar_kw= {
    'label'      : 'Gridness score',
    'location'   : 'bottom',
    'shrink'     : 0.8,
    'pad'        : 0.15,
    'ticks'      : ti.MultipleLocator(0.5),
    'rasterized' : True}

vmin = -0.5
vmax = 1.1

##############################################################################
exampleRC = ( (5, 15), (15, 5) )
slice_horizontal = slice(13, 18)
slice_vertical = slice(13, 18)
#sliceAnn = [\
#    dict(
#        sliceSpan=slice_horizontal,
#        type='horizontal',
#        letter=None),
#    dict(
#        sliceSpan=slice_vertical,
#        type='vertical',
#        letter=None)]
sliceAnn = None

ann0 = dict(
        txt='b',
        rc=exampleRC[0],
        xytext_offset=(1.5, 1),
        color='black')
ann1 = dict(
        txt='a',
        rc=exampleRC[1],
        xytext_offset=(0.5, 1.5),
        color='black')
ann = [ann0, ann1]


varList = ['gridnessScore']

if (grids):
    # noise_sigma = 0 pA
    fig = plt.figure("sweeps0", figsize=sweepFigSize)
    exRows = [28, 15]
    exCols = [3, 15]
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    sweeps.plotGridTrial(ps.grids[0], varList, iterList, ps.noise_sigmas[0],
            trialNumList=gridTrialNumList,
            ax=ax,
            r=exampleIdx[0][0], c=exampleIdx[0][1],
            cbar=False, cbar_kw=cbar_kw,
            vmin=vmin, vmax=vmax,
            ignoreNaNs=True,
            annotations=ann,
            sliceAnn=sliceAnn)
    fname = outputDir + "/grids_sweeps0.pdf"
    fig.savefig(fname, dpi=300, transparent=True)
    plt.close()


    # noise_sigma = 150 pA
    #for a in sliceAnn:
    #    a['letterColor'] = 'black'
    fig = plt.figure("sweeps150", figsize=sweepFigSize)
    exRows = [8, 2]
    exCols = [10, 9]
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    sweeps.plotGridTrial(ps.grids[1], varList, iterList, ps.noise_sigmas[1],
            trialNumList=gridTrialNumList,
            ax=ax,
            r=exampleIdx[1][0], c=exampleIdx[1][1],
            cbar=False, cbar_kw=cbar_kw,
            vmin=vmin, vmax=vmax,
            ignoreNaNs=True,
            annotations=ann,
            sliceAnn=sliceAnn)
    fname = outputDir + "/grids_sweeps150.pdf"
    fig.savefig(fname, dpi=300, transparent=True)
    plt.close()


    # noise_sigma = 300 pA
    fig = plt.figure("sweeps300", figsize=sweepFigSize)
    exRows = [16, 15]
    exCols = [6, 23]
    ax = fig.add_axes(Bbox.from_extents(sweepLeft, sweepBottom, sweepRight,
        sweepTop))
    _, _, cax = sweeps.plotGridTrial(ps.grids[2], varList, iterList, ps.noise_sigmas[2],
            trialNumList=gridTrialNumList,
            ax=ax,
            r=exampleIdx[2][0], c=exampleIdx[2][1],
            cbar_kw=cbar_kw,
            vmin=vmin, vmax=vmax,
            ignoreNaNs=True,
            annotations=ann,
            sliceAnn=sliceAnn)
    #for label in cax.yaxis.get_ticklabels():
    #    label.set_ha('right')
    #cax.tick_params(pad=30)
    fname = outputDir + "/grids_sweeps300.pdf"
    fig.savefig(fname, dpi=300, transparent=True)
    plt.close()


##############################################################################
# Grid field examples
exampleGridFName = outputDir + "/grids_examples_{0}pA_{1}.pdf"
exampleACFName = outputDir + "/grids_examples_acorr_{0}pA_{1}.pdf"
exTransparent = True
exampleFigSize = (1, 1.2)
exampleLeft   = 0.01
exampleBottom = 0.01
exampleRight  = 0.99
exampleTop    = 0.85

if (examplesFlag):
    for ns_idx, noise_sigma in enumerate(ps.noise_sigmas):
        for idx, rc in enumerate(exampleRC):
            # Grid field
            fname = exampleGridFName.format(noise_sigma, idx)
            plt.figure(figsize=exampleFigSize)
            gs = examples.plotOneGridExample(ps.grids[ns_idx], rc, iterList,
                    exIdx=exampleIdx[idx],
                    xlabel=False, ylabel=False,
                    xlabel2=False, ylabel2=False, 
                    maxRate=True, plotGScore=False)
            gs.update(left=exampleLeft, bottom=exampleBottom, right=exampleRight,
                    top=exampleTop)
            plt.savefig(fname, dpi=300, transparent=exTransparent)
            plt.close()

            # Autocorrelation
            fname = exampleACFName.format(noise_sigma, idx)
            fig= plt.figure(figsize=exampleFigSize)
            ax = fig.add_axes(Bbox.from_extents(exampleLeft, exampleBottom,
                exampleRight, exampleTop))
            gs = examples.plotOneGridACorrExample(ps.grids[ns_idx], rc, ax=ax)
            plt.savefig(fname, dpi=300, transparent=exTransparent)
            plt.close()
    

##############################################################################
# Detailed noise plots
EI13Root  = 'output_local/detailed_noise/grids/EI-1_3'
EI31Root  = 'output_local/detailed_noise/grids/EI-3_1'
detailedShape = (31, 9)

EI13PS = JobTrialSpace2D(detailedShape, EI13Root)
EI31PS = JobTrialSpace2D(detailedShape, EI31Root)
detailedNTrials = 1


detailFigSize = (4.5, 2.8)
detailLeft   = 0.15
detailBottom = 0.2
detailRight  = 0.95
detailTop    = 0.8
if (detailed_noise):
    ylabelPos = -0.15

    types = ('grids', 'gridnessScore')
    fig = plt.figure(figsize=detailFigSize)
    ax = fig.add_axes(Bbox.from_extents(detailLeft, detailBottom, detailRight,
        detailTop))
    _, p13, l13 = details.plotDetailedNoise(EI13PS, detailedNTrials, types, ax=ax,
            ylabelPos=ylabelPos,
            color='red', markerfacecolor='red', zorder=10)
    _, p31, l31 = details.plotDetailedNoise(EI31PS, detailedNTrials, types, ax=ax,
            ylabel='Gridness score', ylabelPos=ylabelPos,
            color='#505050')
    ax.yaxis.set_major_locator(ti.MultipleLocator(0.4))
    ax.yaxis.set_minor_locator(ti.MultipleLocator(0.2))
    ax.set_ylim([-0.6, 1.2])
    leg = ['a',  'b']
    l = ax.legend([p31, p13], leg, loc=(0.8, 1), fontsize='small', frameon=False,
            numpoints=1, handletextpad=0.05)

    fname = outputDir + "/grids_detailed_noise_gscore.pdf"
    plt.savefig(fname, dpi=300, transparent=True)
    plt.close()


