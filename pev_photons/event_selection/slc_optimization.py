#!/usr/bin/env python

########################################################################
# Plot optimized slc selection region.
########################################################################

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import dashi
from pev_photons.utils.support import fig_dir, resource_dir
from pev_photons.utils.support import plot_setter, plot_style, plasma_map

def rhombus(width, depth, cos_zen, color):
    """plot a rhombus"""

    start = 4.8/(cos_zen+0.05)
    end = start + 260/((cos_zen+0.05)*300) 
    plt.plot([start, end], [1, depth+1],
             color=color, label='Selection Region')
    plt.plot([start+width, end+width], [1,depth+1],
             color=color)
    plt.plot([end, end+width], [depth+1, depth+1],
             color=color)

def slc_plot(f, cos_zen):
    """plot the distribution of slc hits for given events"""

    time_bins = np.arange(4.5,10.1,0.1)
    dom_bins = np.arange(1,61,1)
    hist2d = dashi.histfactory.hist2d((f['time'].values/1000., f['dom'].values),
                                      (time_bins, dom_bins))
    hist2d.imshow(cmap=plasma_map)

    colors = plt.rcParams['axes.color_cycle']
    rhombus(1.8, 16, cos_zen, colors[2])

    plt.gca().invert_yaxis()
    plt.xlim([4.5, 10])
    plt.ylim([60, 1])
    l = plt.legend(loc='lower left', frameon=True)
    plot_setter(plt.gca(),l)

    plt.xlabel('t$_{pulse}$ - t$_{trigger}$ ($\mu s$)')
    plt.ylabel('Vertical DOM Number')
    plt.colorbar(label='Number of Hit DOMs')
    plt.tight_layout()

    plt.savefig(fig_dir+'event_selection/slcs_cosZen_%.2f.png' % zen_min)
    if zen_min == 0.95:
        plt.savefig(fig_dir+'paper/slc_optimization.pdf')
    plt.close()


if __name__ == "__main__":
    dashi.visual()
    plt.style.use(plot_style)

    # Has 1 row for each event
    events = pd.read_hdf(resource_dir+'no_hlcs.hdf5', key='Laputop')

    # Has 1 row for each pulse
    pulses = pd.read_hdf(resource_dir+'no_hlcs.hdf5', key='slcs')

    zenith_bins = [0.80,0.85,0.90,0.95]
    cos_zen = np.cos(events['zenith'].values)
    for i, zen_min in enumerate(zenith_bins):
        # Get events in the zenith bin
        mask = np.greater_equal(cos_zen, zen_min) & np.less(cos_zen, zen_min+0.05)

        # Get all pulses that are in the events selected
        slc_mask = (np.all(pulses[['Run','Event']].isin(events[mask][['Run', 'Event']].to_dict('list')), axis=1)
                    & np.less(pulses['dist'], 130))
        slc_plot(pulses[slc_mask], zen_min)
