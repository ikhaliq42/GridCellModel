#
#   global.py
#
#   Global plotting definitions
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
import matplotlib.pyplot as plt


def globalAxesSettings(ax):
    ax.tick_params(
            direction='out'
    )

def createColorbar(ax, data=None, label=""):
    if (data is not None):
        mn = np.min(data.flat)
        mx = np.max(data.flat)
        ticks = [mn, mx]
    else:
        ticks = None
    cb = plt.colorbar(ax=ax, ticks=ticks)
    if (label != ""):
        cb.set_label(label)

