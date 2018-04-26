#!/usr/bin/env python

########################################################################
# Plot systematic comparison of fitted spectral index, nsources, etc.
########################################################################

import numpy as np

import matplotlib.pyplot as plt
from pev_photons.utils.support import prefix
from pev_photons.utils.support import fig_dir, plot_setter, plot_style

def index_x_events():
    alpha_fits = np.load(prefix+'all_sky/alpha_fit_test_-60.npy')
    
    n_list = np.arange(0, 21, 1)
    alpha_list = [2.0, 2.7]
    for i, alpha in enumerate(alpha_list):
        low = np.percentile(alpha_fits[i], 16, axis=1)
        high = np.percentile(alpha_fits[i], 84, axis=1)
        plt.plot(n_list, np.median(alpha_fits[i], axis=1),
                 color=colors[i])
        plt.fill_between(n_list, low, high,
                         color=colors[i], edgecolor='none',
                         rasterized = True, alpha=0.5)
        plt.axhline(y=alpha, label = 'injected E$^{-%s}$'%alpha,
                    linestyle= '--', color = colors[i])
    plt.xlabel('Injected Signal Events')
    plt.ylabel('Fitted Index (1$\sigma$ contour)')
    l = plt.legend(loc=0, fontsize = 18, prop={'weight':'bold'})
    plot_setter(plt.gca(), l)
    plt.xlim([0, 20])
    plt.ylim([1.0, 4.0])
    plt.tight_layout()
    plt.savefig(fig_dir+'systematics/spectral_index_test.png')
    plt.close()

def events_x_events():
    ns_fits = np.load(prefix+'all_sky/ns_fit_test_-60.npy')
    
    n_list = np.arange(0, 21, 1)
    alpha_list = [2.0, 2.7]
    for i, alpha in enumerate(alpha_list):
        low = np.percentile(ns_fits[i], 16, axis=1)
        high = np.percentile(ns_fits[i], 84, axis=1)
        plt.plot(n_list, np.median(ns_fits[i], axis=1),
                 color=colors[i], label = 'injected E$^{-%s}$'%alpha)
        plt.fill_between(n_list, low, high,
                         color=colors[i], edgecolor='none',
                         rasterized = True, alpha=0.5)
    plt.plot(n_list, n_list, linestyle= '--', color = 'k')
    plt.xlabel('Injected Signal Events')
    plt.ylabel('Fitted Signal Events')
    l = plt.legend(loc=0, fontsize = 18, prop={'weight':'bold'})
    plot_setter(plt.gca(), l)
    plt.xlim([0, 20])
    plt.ylim([0, 40])
    plt.tight_layout()
    plt.savefig(fig_dir+'systematics/ns_index_test.png')
    plt.close()

if __name__ == "__main__":
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    index_x_events()
    events_x_events()
