#!/bin/sh
for n in 0 50 100 150 200 250 300 350 400 450 500 550 600 650 700 750 800 850 900 950 1000
do
    python analysis_rect_no_plot.py sim_place_only --neuron_idx=$n
done
