#!/usr/bin/env python

########################################################################
# Comparison of S125 for different lambdas
########################################################################

import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from pev-photons.utils.support import prefix, resource_dir, fig_dir, plot_setter, plot_style

def plot_s125(true_E, log_S125, label, E_bins=np.arange(5.7,8.0,0.1)):
    bin_medians, bin_edges, n = stats.binned_statistic(true_E, log_S125,
                                                       statistic='median',
                                                       bins=E_bins)
    line = ax0.step(bin_edges, np.append(bin_medians[0], bin_medians),
                    label=label)

    return 10**np.append(bin_medians[0], bin_medians), line[0]

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Comparison of S125 for different lambdas',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', help='MC year')
    args = p.parse_args()

    year_to_dataset = {'2011':'12622', '2012':'12533',
                       '2013':'12612', '2014':'12613', '2015':'12614'}
    year_to_lambda  = {'2011':2.1, '2012':2.25,
                       '2013':2.25, '2014':2.3, '2015':2.3}
    # Plotting set up
    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    fig, (ax0, ax1) = plt.subplots(2, 1, gridspec_kw={'height_ratios':[3, 1]})

    comp = []
    lines = []
    E_bins = np.arange(5.7,8.0,0.1)
    f = pd.read_hdf(prefix+'datasets/'+year_to_dataset[args.year]+'.hdf5')
    recos = ['LaputopLambdaDown', 'Laputop', 'LaputopLambdaUp']
    labels = np.array([-0.2,0,0.2])+year_to_lambda[args.year]

    for i, reco in enumerate(recos):
        f_cut = f[f[reco+'_quality_cut']==True]
        
        vals, line = plot_s125(np.log10(f_cut['MC_energy']), f_cut[reco+'_log10_s125'],
                               '$\lambda$ = %.2f' % labels[i])
        comp.append(vals)
        lines.append(line)

    for i, c in enumerate(comp):
        ratio = c/comp[1] 
        ax1.step(E_bins, ratio, color=lines[i].get_color())

    ax0.set_xticklabels([])
    ax0.set_xlim([5.7, 8])
    ax0.set_ylim([-0.5, 2])
    ax0.legend(loc='lower right')
    ax0.set_ylabel(r'log10(S$_{125}$)')
    ax0.set_title('Gamma-rays, {} Snow Heights'.format(args.year))

    ax1.set_xlim([5.7, 8])
    ax1.set_ylim([0.85,1.15])
    ax1.grid(b=True, color='grey')
    ax1.set_xlabel(r'log10(E$_{\textrm{\textsc{mc}}}$/GeV)')
    ax1.set_ylabel(r'Ratio to nominal', fontsize=14)

    plt.savefig(fig_dir+'systematics/lambda_check_{}.pdf'.format(args.year))
    plt.close()
