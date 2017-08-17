#!/usr/bin/env/python

import argparse, glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chi2
import matplotlib as mpl
plt.style.use('stefan')
colors = mpl.rcParams['axes.color_cycle']
from support_functions import get_fig_dir, plot_setter
fig_dir = get_fig_dir()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='plot scrambled trials',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/TeVCat/',
                   help    = 'base directory for file storing')
    p.add_argument('--chi2_ndf', dest='chi2_ndf', type = int, nargs='*',
                   help = 'chi2 ndf values to plot')
    p.add_argument('--bin_width', dest='bin_width', type = float,
                   default = 0.2,
                   help = 'width of bin in TS space')
    args = p.parse_args()

    stack_true = np.load(args.prefix+'/stacking_TS.npy') # observed TS
    job_list   = glob.glob(args.prefix+'/stacking_trials/*') # background trials

    bg_trials = []
    for job in job_list:
        job_ts = np.load(job)
        bg_trials.extend(job_ts)

    Ntrials   = float(len(bg_trials))

    print("Fraction of trials above 0: %.2f" % (np.sum(np.greater(bg_trials,0))/Ntrials))

    #Plot chi2 distributions for each degree of freedom given
    if args.chi2_ndf != None:
        for df in args.chi2_ndf:
            x = np.linspace(0.1, chi2.ppf(0.9999, df), 1000)
            plt.plot(x, chi2.pdf(x, df)*Ntrials*args.bin_width*0.5, label='$\chi^2$ N$_{DOF}$ = %s', alpha = 0.75)

    c_rgb = (215/256.,25/256.,28/256., 0.5)
    plt.hist(bg_trials, bins = np.arange(0,15,args.bin_width), label = 'Scrambled Trials', histtype= 'stepfilled', edgecolor = 'none', color = c_rgb)

    #Plot the observed TS
    plt.axvline(x=stack_true, color = colors[4], label = 'Observed TS', lw = 4)

    p_value = np.sum(np.greater(bg_trials, stack_true))/Ntrials
    print("p-value: %.4f" % p_value)

    plt.title(r'Stacked H.E.S.S. Sources Correlation. p-value = %.4f' % p_value)

    plt.axvline(x=np.percentile(bg_trials,68), label = '1 $\sigma$', ls='--', color = 'k', lw = 2)
    plt.axvline(x=np.percentile(bg_trials,95), label = '2 $\sigma$', ls='-.', color = 'k', lw = 2)
    plt.axvline(x=np.percentile(bg_trials,99.7), label = '3 $\sigma$', ls=':', color = 'k', lw = 2)

    plt.xlabel('Test Statistic', fontweight = 'bold')
    plt.ylabel('Trials', fontweight = 'bold')
    plt.yscale('log')
    l = plt.legend(loc=0, fontsize = 18, prop={'weight':'bold'})
    plot_setter(plt.gca(), l)
    plt.xlim([0,20])
    plt.ylim([0.5,Ntrials])
    plt.tight_layout()
    plt.text(14,1.5, 'IceCube Preliminary', color = 'r', fontsize=14) #For unpublished results
    plt.savefig(fig_dir+'stacking_trials.pdf')
    plt.close()
