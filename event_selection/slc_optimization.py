#!/usr/bin/env python

########################################################################
# Plot optimized slc selection region.
########################################################################

import simFunctions
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from support_functions import get_fig_dir, plot_setter
fig_dir = get_fig_dir()
import dashi
dashi.visual()
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
import colormaps as cmaps
import tables as t
import pandas as pd

def rhombus(width, depth, cos_zen, color):
    start = 4.8/(cos_zen+0.05)
    end = start + 260/((cos_zen+0.05)*300) 
    plt.plot([start, end], [1, depth+1],
             color=color, label='Selection Region')
    plt.plot([start+width, end+width], [1,depth+1],
             color=color)
    plt.plot([end, end+width], [depth+1, depth+1],
             color=color)

#Plot distribution of slcs
def slc_plot(f, cos_zen, fname='slc_dist.png'):
    time_bins = np.arange(4.5,10.1,0.1)
    dom_bins = np.arange(1,61,1)
    times = f['time'] 
    doms = f['dom'] 
    charge = np.array(f['charge'])
    hist2d = dashi.histfactory.hist2d((times/1000., doms),
                                      (time_bins, dom_bins))
    hist2d.imshow(cmap=cmaps.plasma)
    plt.colorbar(label='Hits')
    plt.xlabel('t$_{pulse}$ - t$_{trigger}$ ($\mu s$)')
    plt.ylabel('Vertical DOM Number')
    currentAxis = plt.gca()
    currentAxis.invert_yaxis()
    slope = .06
    rhombus(1.8, 16, cos_zen, colors[2])
    plt.xlim([4.5, 10])
    plt.ylim([60, 1])
    l = plt.legend(loc='lower left', frameon=True)
    plot_setter(plt.gca(),l)
    plt.tight_layout()
    plt.savefig(fig_dir+fname)
    if zen_min == 0.95:
        plt.savefig('/home/zgriffith/public_html/paper/slc_optimization.pdf')
    plt.close()


if __name__ == "__main__":
    pf = '/data/user/zgriffith/ShowerLLH/'
    f = t.openFile(pf+'/IT81-II_data/files/burn_sample/slcs/burn_sample.hdf5')
    cosZen = np.cos(f.root.Laputop.cols.zenith[:])

    for i, zen_min in enumerate([0.80,0.85,0.90,0.95]):
        slcs = f.root.slcs.read()
        slcs = pd.DataFrame(slcs)
        slcs = pd.DataFrame(slcs).drop(['SubEvent', 'SubEventStream',
                                        'vector_index', 'exists'], 1)
        slcs['run_event'] = (slcs["Run"].map(int).map(str) + '_'
                             + slcs["Event"].map(int).map(str))
        run_event = np.core.defchararray.add(
                        np.core.defchararray.add(
                            f.root.I3EventHeader.cols.Run[:].astype(str),'_'),
                        f.root.I3EventHeader.cols.Event[:].astype(str))
        mask = np.greater_equal(cosZen,zen_min)&np.less(cosZen,zen_min+0.05)
        runs = run_event[mask]
        slcs = slcs[np.in1d(slcs.run_event,runs)&(slcs.dist<130)]
        slc_plot(slcs, zen_min, fname='slcs_cosZen_gt_%.2f.png' % zen_min)

