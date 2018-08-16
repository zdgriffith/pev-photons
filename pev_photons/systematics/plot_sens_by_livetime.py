#!/usr/bin/env python

########################################################################
# 
########################################################################

import numpy as np
import matplotlib.pyplot as plt

from pev_photons.utils.support import prefix, resource_dir
from pev_photons.utils.support import fig_dir, plot_setter, plot_style

if __name__ == "__main__":

    sens = np.load(prefix+'/systematics/sens_by_years.npy')
    years = np.arange(1.,6.,1)
    colors = plt.rcParams['axes.color_cycle']

    plt.style.use(plot_style)
    fig, ax = plt.subplots()

    sens = sens*1e9
    ax.plot(years, sens, label='Sensitivity')
    ax.plot(years, sens[0]*(1/years),
            label='1/T', ls='--', color=colors[2])
    ax.plot(years, sens[0]*(1/np.sqrt(years)),
            label='1/sqrt(T)', ls=':', color=colors[2])

    ax.set_xlabel('Years of Livetime')
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_ylabel(r'E$^2\frac{d\Phi}{dE}$ [TeV cm$^{-2}$ s$^{-1}$]')
    ax.legend()
    fig.tight_layout()
    plt.savefig(fig_dir+'systematics/sens_by_years.pdf')
    plt.close()
