#!/bin/bash
#
#   copy_to_dropbox.sh
#
#   Copy figures to the shared folder in dropbox
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

dst_dir=~/Dropbox/shared_data/noise/figures/

files="
    figure1.pdf
    figure2.pdf
    figure3.pdf
    figure4.png
    suppFigure_grid_sweeps.png
    suppFigure_model.pdf
    suppFigure_velocity.pdf
    suppFigure_no_theta.png
    suppFigure_bumps
    suppFigure_grids
    slices
    "

ls $dst_dir
for f in $files
do
    cp -r $f $dst_dir
done