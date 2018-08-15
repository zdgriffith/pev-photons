#!/usr/bin/env python

########################################################################
# Plot systematic comparison of fitted spectral index, nsources, etc.
########################################################################

import numpy as np

import matplotlib.pyplot as plt
from pev-photons.utils.support import prefix
from pev-photons.utils.support import fig_dir, plot_setter, plot_style

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

def plot_bias(kind='ns'):
    energy_bias = 100*np.arange(0.1, 2.00, 0.1)
    ns_fits = np.load(prefix+'all_sky/{}_fit_test_bias.npy'.format(kind))
    low = np.percentile(ns_fits, 16, axis=1)
    high = np.percentile(ns_fits, 84, axis=1)
    plt.plot(energy_bias, np.median(ns_fits, axis=1),
             color=colors[0], label = 'n$_{inj}$=20')
    plt.fill_between(energy_bias, low, high,
                     color=colors[0], edgecolor='none',
                     rasterized=True, alpha=0.5)
    plt.tight_layout()
    plt.xlabel('Added bias to E$_{reco}$ [\%]')
    if kind=='ns':
        plt.axhline(y=20, color=colors[0], ls='--')
        plt.ylim([0,40])
        plt.ylabel('Fitted n$_s$')
    else:
        plt.ylabel('Fitted Flux')
    plt.legend()
    plt.savefig(fig_dir+'systematics/{}_bias.png'.format(kind))
    plt.close()

if __name__ == "__main__":
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']
    #index_x_events()
    #events_x_events()
    plot_bias()
    plot_bias(kind='flux')
