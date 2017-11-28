#!/usr/bin/env/python

########################################################################
# Plot background TS ensemble with observed TS.
########################################################################

import argparse
import glob
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import chi2

from support_functions import get_fig_dir, plot_setter

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='plot scrambled trials',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--chi2_ndf', type=int, nargs='*',
                   help='chi2 ndf values to plot')
    p.add_argument('--bin_width', type=float, default=0.5,
                   help='width of bin in TS space')
    args = p.parse_args()

    stack_true = 20.7
    job_list = glob.glob('/data/user/zgriffith/all_sky/full_*.npy')

    bg_trials = []
    for job in job_list:
        job_ts = np.load(job)
        if not np.any(np.equal(job_ts,0)):
            bg_trials.extend(job_ts)

    Ntrials = float(len(bg_trials))

    #Plot chi2 distributions for each degree of freedom given
    if args.chi2_ndf != None:
        for df in args.chi2_ndf:
            x = np.linspace(0.1, chi2.ppf(0.9999, df), 1000)
            plt.plot(x, chi2.pdf(x, df)*Ntrials*args.bin_width*0.5,
                     label='$\chi^2$ N$_{DOF}$ = %s', alpha=0.75)

    plt.hist(bg_trials, bins=np.arange(0,100,args.bin_width),
             label='Background Trials', histtype='stepfilled',
             edgecolor='none', color='grey')

    #Plot the observed TS
    plt.axvline(x=stack_true, color=colors[2],
                label='Observed', lw=3)

    p_value = np.sum(np.greater(bg_trials, stack_true))/Ntrials
    print("p-value: %.4f" % p_value)

    plt.axvline(x=np.percentile(bg_trials,68), label='1 $\sigma$',
                ls='--', color='k')
    plt.axvline(x=np.percentile(bg_trials,95), label='2 $\sigma$',
                ls='-.', color='k')
    plt.axvline(x=np.percentile(bg_trials,99.7), label='3 $\sigma$',
                ls=':', color='k')

    plt.xlabel('Test Statistic')
    plt.ylabel('Trials')
    plt.yscale('log')
    l = plt.legend(loc=0)
    plot_setter(plt.gca(), l)
    plt.xlim([0,50])
    plt.ylim([0.5,Ntrials])
    plt.tight_layout()
    plt.text(1, 3000, 'IceCube Preliminary', color = 'r', fontsize=14)
    plt.savefig(fig_dir+'all_sky_trials.pdf')
    plt.savefig('/home/zgriffith/public_html/paper/all_sky_trials.pdf')
    plt.close()
