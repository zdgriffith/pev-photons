#!/usr/bin/env python

########################################################################
# Functions to plot the behavior of the fitted spectral index.
########################################################################

import numpy as np
import matplotlib.pyplot as plt

from pev_photons.support import prefix, plot_style, fig_dir, plot_setter

def index_vs_events():
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fit = np.load(prefix+'all_sky/systematics/index_vs_events.npy').item()
    
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
    plt.savefig(fig_dir+'all_sky/index_vs_events.png')
    plt.close()

if __name__ == "__main__":
    index_vs_events()
