#!/usr/bin/env python

########################################################################
# Functions to plot the behavior of the fitted spectral index.
########################################################################

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from support_functions import get_fig_dir, plot_setter

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

def index_vs_events(args):
    fit = np.load(args.prefix+'all_sky/systematics/index_vs_events.npy').item()
    
    for i, index in enumerate(fit['index_list']):
        # Plot the median of the fitted index
        plt.plot(fit['n_list'], np.median(fit['fit_index'][i], axis=1),
                 color=colors[i])

        # Calculate and plot the 1 sigma uncertainty.
        low = np.percentile(fit['fit_index'][i], 16, axis=1)
        high = np.percentile(fit['fit_index'][i], 84, axis=1)
    
        plt.fill_between(fit['n_list'], low, high,
                         color=colors[i], edgecolor='none',
                         rasterized = True, alpha=0.5)

        # Plot the injected index.
        plt.axhline(y=index, label = 'injected E$^{-%s}$' % index,
                    linestyle= '--', color = colors[i])

    plt.xlabel('Injected Signal Events')
    plt.ylabel('Fitted Index (1$\sigma$ contour)')
    l = plt.legend(loc=0)
    plot_setter(plt.gca(), l)
    plt.xlim([fit['n_list'][0],fit['n_list'][-1]])
    plt.ylim([1.0, 4.0])
    plt.tight_layout()
    plt.savefig(fig_dir+'index_vs_events.png')
    plt.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='plot spectral index fitting',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type = str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    args = p.parse_args()

    index_vs_events(args)
