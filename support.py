#!/usr/bin/env python

########################################################################
# Supporting functions and variables
########################################################################

import matplotlib as mpl

prefix = '/data/user/zgriffith/pev_photons/'

# Plotting Style
plot_style = 'gamma_rays_5yr'
colors = mpl.rcParams['axes.color_cycle']

def get_fig_dir():
    """ provide the path for saving figures to public_html """

    import os

    path = os.getcwd() 
    if 'home' in path:
        fig_dir = os.path.expanduser('~') + '/public_html/' + '/'.join(os.getcwd().split('/')[3:]) + '/'
    else:
        fig_dir = os.path.expanduser('~') + '/public_html/' + '/'.join(os.getcwd().split('/')[4:]) + '/'
    return fig_dir

def plot_setter(ax, legend = None, bg_color = 'white', text_color='#262626'):
    """ Make the lines thicker in the legend, standardize text colors """

    ax.set_axis_bgcolor(bg_color)
    for tick in ax.get_xticklines():
        tick.set_color(text_color)
    for tick in ax.get_yticklines():
        tick.set_color(text_color)
    if legend: 
        for text in legend.get_texts():
            text.set_color(text_color)
        for legobj in legend.legendHandles:
            legobj.set_linewidth(3.0)
