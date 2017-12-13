#!/usr/bin/env/python

########################################################################
# Plot the TS distribution of background trials.
########################################################################

import argparse
import glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2

from support_functions import get_fig_dir, plot_setter

plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
fig_dir = get_fig_dir()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot scrambled trials.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--chi2_ndf', type=int, nargs='*',
                   help='chi2 ndf values to plot')
    p.add_argument('--bin_width', type=float, default=0.2,
                   help='width of bin in TS space')
    p.add_argument('--only_bg', action='store_true', default=False,
                   help='if True, do not plot true TS.')
    args = p.parse_args()

    #Plot the background trials scrambled in right ascension
    job_list = glob.glob(args.prefix+'/galactic_plane/trials/*') 
    bg_trials = []
    for job in job_list:
        job_ts = np.load(job)
        bg_trials.extend(job_ts)
    n_trials = float(len(bg_trials))

    c_rgb = (215/256.,25/256.,28/256., 0.5)
    plt.hist(bg_trials, bins=np.arange(0,15,args.bin_width),
             label='Scrambled Trials', histtype='stepfilled',
             edgecolor='none', color=c_rgb)

    #Plot chi2 distributions for each degree of freedom given.
    if args.chi2_ndf != None:
        for df in args.chi2_ndf:
            x = np.linspace(0.1, chi2.ppf(0.9999, df), 1000)
            plt.plot(x, chi2.pdf(x, df)*n_trials*args.bin_width*0.5,
                     label='$\chi^2$ N$_{DOF}$ = %s' % df, alpha = 0.75)

    #Plot the observed TS
    if not args.only_bg:
        true_TS  = np.load(args.prefix+'/galactic_plane/fermi_pi0_fit_result.npy')['TS']
        plt.axvline(x=true_TS, color=colors[4], label='Observed TS', lw=4)
        p_value = np.sum(np.greater(bg_trials, true_TS))/n_trials
        print("p-value: %.4f" % p_value)

    #Plot the lines denoting significance thresholds
    plt.axvline(x=np.percentile(bg_trials,68), label='1 $\sigma$',
                ls='--', color='k', lw=2)
    plt.axvline(x=np.percentile(bg_trials,95), label='2 $\sigma$',
                ls='-.', color='k', lw=2)
    plt.axvline(x=np.percentile(bg_trials,99.7), label='3 $\sigma$',
                ls=':', color='k', lw=2)

    plt.text(14, 1.5, 'IceCube Preliminary',
             color='r', fontsize=14)

    #Plot a legend with bold lines.
    l = plt.legend(loc=0, fontsize = 18, prop={'weight':'bold'})
    plot_setter(plt.gca(), l)

    plt.xlim([0,20])
    plt.ylim([0.5,n_trials])
    plt.yscale('log')
    plt.xlabel('Test Statistic', fontweight = 'bold')
    plt.ylabel('Trials', fontweight = 'bold')
    plt.tight_layout()
    plt.savefig(fig_dir+'bg_trials.pdf')
    plt.close()
