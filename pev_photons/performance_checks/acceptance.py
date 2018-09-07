#!/usr/bin/env python

########################################################################
# Plot acceptance comparison of IC86 and IC-40.
########################################################################

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from pev_photons.utils.support import resource_dir, prefix, fig_dir, plot_style

def n_thrown(E, theta_min):
    df = pd.read_hdf(prefix+'datasets/corsika/10042.hdf5')
    vals, E_edges, zen_edges = np.histogram2d(np.log10(df['energy'].values), np.degrees(df['zenith'].values),
                                              bins=(np.arange(5,8.1,0.1), np.arange(0,46,1)))
    E_indices = np.floor(10 * np.log10(E)) - 50
    n_bin = []
    for i, E_i in enumerate(E_indices):
        n_bin.append(vals[int(E_i)][int(theta_min[i])]*100)
    return np.array(n_bin)

def int_area(E, theta):

    #Integrated Area times Solid Angle
    radius = (800 * np.greater_equal(E, 1e5)
              + 300 * np.greater_equal(E, 1e6)
              + 300 * np.greater_equal(E, 1e7))
    theta_min = np.floor(theta)
    theta_max = theta_min + 1
    solid_angle = 2*np.pi*(np.cos(np.radians(theta_min))**2 - np.cos(np.radians(theta_max))**2)
    return (np.pi*radius**2)*solid_angle/n_thrown(E, theta_min)

if __name__ == "__main__":
    plt.style.use(plot_style)
    fig, ax = plt.subplots()

    gammas = pd.read_hdf(prefix+'/datasets/training/dataframes/2012/gamma_mc.hdf5')

    labels = ['IC86', 'IC86 (in-ice contained)']
    for i, label in enumerate(labels):
        if i:
            mask = gammas['Laputop_inice_FractionContainment'] <= 1
            gammas = gammas[mask]
        hist, x_e, y_e = np.histogram2d(np.degrees(gammas['true_zenith'].values),
                                        np.log10(gammas['true_energy'].values),
                                        bins=[np.arange(0, 46, 1), np.arange(5, 8.1, 0.1)],
                                        weights=int_area(gammas['true_energy'].values, np.degrees(gammas['true_zenith'].values)))
        E_centers = (y_e[:-1]+y_e[1:])/2.
        bins = np.average(hist, axis=1, weights=np.sum(hist, axis=0)*(10**E_centers)**-2.7/np.sum((10**E_centers)**-2.7))
        left,right = x_e[:-1], x_e[1:]
        X = np.array([left,right]).T.flatten()
        Y = np.array([bins,bins]).T.flatten()
        ax.plot(X, Y, label=label)

    ic40 = np.loadtxt(resource_dir+'ic40.txt')
    x_e = x_e[0:41]
    left,right = x_e[:-1], x_e[1:]
    X = np.array([left,right]).T.flatten()
    Y = np.array([ic40, ic40]).T.flatten()
    ax.plot(X, Y, label='IC40')

    ax.set_xlabel('Zenith (degrees)')
    ax.set_ylabel('Acceptance (m$^2$sr)')
    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(fig_dir+'performance_checks/acceptance.png')
    plt.close()
