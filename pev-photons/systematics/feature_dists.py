#!/usr/bin/env python

########################################################################
# feature distributions comparion of interaction models
########################################################################


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pev-photons.utils.support import prefix, resource_dir, fig_dir, plot_setter, plot_style

if __name__ == "__main__":

    gammas = pd.read_hdf(prefix+'datasets/systematics/2012_sybll_quality.hdf5')
    qgs = pd.read_hdf(prefix+'datasets/systematics/2012_qgs_quality.hdf5')

    #feature = 'llh_ratio'
    feature = 'charges'

    if feature == 'llh_ratio':
        bins = np.arange(-10,10,0.5)
    elif feature == 'charges':
        bins = np.arange(-0.5,4.5,0.1)

    fig, (ax0, ax1) = plt.subplots(2, 1)

    labels = ['SYBLL', 'QGS-Jet']
    
    colors = plt.rcParams['axes.color_cycle']
    for i,df in enumerate([gammas, qgs]):
        if feature == 'charges':
            df = df[df['laputop_ic'] < 1]

        mask = np.greater(np.log10(df['primary_E']),6.2) & np.less(np.log10(df['primary_E']),6.3)

        if feature == 'charges':
            x = np.ma.log10(df[mask][feature].values)
            x = x.filled(0)
        else:
            x = df[mask][feature]

        ax0.hist(x, alpha=0.5, lw=1.5, color=colors[i],
                 bins=bins, normed=True, label=labels[i])

        ax1.hist(x, alpha=1, lw=2, color=colors[i],
                 cumulative=True, histtype='step',
                 bins=bins, normed=True, label=labels[i])

    if feature == 'llh_ratio':
        ax0.set_xticklabels([])
        ax0.set_xlim([-7.5,7.5])
        ax0.set_title('6.0 $<$ log10($E_{MC}$/GeV) $<$ 6.1')

        ax1.set_xlabel('LLH Ratio')
        ax1.set_xlim([-7.5,7.5])
        ax1.set_ylim([0,1])
    else:
        ax0.set_xticklabels([])
        ax0.set_xlim([0,4])
        ax0.set_yscale('log')
        ax0.set_title('6.2 $<$ log10($E_{MC}$/GeV) $<$ 6.3 | $C_{IC}$ $<$ 1.0')

        ax1.set_xlabel('log10(InIce Charge) [PE]')
        ax1.set_xlim([0,4])
        ax1.set_ylim([0.7,1])

    ax0.set_ylabel('Norm. Prob.')
    ax1.set_ylabel('CDF')

    ax0.legend(loc='upper right')
    plt.savefig(fig_dir+'event_selection/{}.png'.format(feature))
