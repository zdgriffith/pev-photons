#!/usr/bin/env/python

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2

from utils.support import prefix, fig_dir, plot_setter, plot_style

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='plot scrambled trials',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--chi2_ndf', type = int, nargs='*',
                   help='chi2 ndf values to plot')
    p.add_argument('--bin_width', type=float, default=0.2,
                   help='width of bin in TS space')
    args = p.parse_args()

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    stack_true = np.load(prefix+'TeVCat/stacking_fit_result.npy')['TS']
    bg_trials = np.load(prefix+'TeVCat/stacking_trials.npy')
    n_trials = len(bg_trials)

    #Plot chi2 distributions for each degree of freedom given
    if args.chi2_ndf != None:
        for df in args.chi2_ndf:
            x = np.linspace(0.1, chi2.ppf(0.9999, df), 1000)
            plt.plot(x, chi2.pdf(x, df)*n_trials*args.bin_width*0.5,
                     label='$\chi^2$ N$_{DOF}$ = %s', alpha = 0.75)

    #Plot the histogram of background trials
    c_rgb = (215/256.,25/256.,28/256., 0.5)
    plt.hist(bg_trials, bins = np.arange(0,15,args.bin_width),
             label = 'Scrambled Trials', histtype= 'stepfilled',
             edgecolor = 'none', color = c_rgb)

    #Plot the observed TS
    plt.axvline(x=stack_true, color=colors[4],
                label='Observed TS', lw=4)

    p_value = np.sum(np.greater(bg_trials, stack_true))/float(n_trials)
    print("p-value: %.4f" % p_value)
    plt.title(r'Stacked H.E.S.S. Sources Correlation. p-value = %.4f' % p_value)

    #Plot significance lines
    plt.axvline(x=np.percentile(bg_trials,68), label='1 $\sigma$',
                                ls='--', color='k', lw=2)
    plt.axvline(x=np.percentile(bg_trials,95), label='2 $\sigma$',
                                ls='-.', color='k', lw=2)
    plt.axvline(x=np.percentile(bg_trials,99.7), label='3 $\sigma$',
                                ls=':', color='k', lw=2)

    #Preliminary result
    plt.text(14,1.5, 'IceCube Preliminary', color='r', fontsize=14)

    plt.xlabel('Test Statistic')
    plt.ylabel('Trials')
    plt.xlim([0,20])
    plt.ylim([0.5,n_trials])
    plt.yscale('log')
    l = plt.legend()
    plot_setter(plt.gca(), l)
    plt.tight_layout()
    plt.savefig(fig_dir+'TeVCat/stacking_trials.pdf')
    plt.close()
