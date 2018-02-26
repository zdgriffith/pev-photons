#!/usr/bin/env/python

########################################################################
# Calculate the p-value, optionally plot trials
########################################################################

import argparse
import numpy as np
import numpy.lib.recfunctions
import matplotlib.pyplot as plt
from scipy.stats import chi2
from glob import glob

from pev_photons.utils.support import prefix, plot_style, fig_dir, plot_setter

def plot_trials(args, bg_trials, n_trials, true_TS):

    plt.style.use(plot_style)
    colors = plt.rcParams['axes.color_cycle']

    #Plot the background trials scrambled in right ascension
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
        plt.axvline(x=true_TS, color=colors[4], label='Observed TS', lw=4)

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
    plt.savefig(fig_dir+'template/'+args.name+'_bg_trials.pdf')
    plt.close()

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot scrambled trials.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--name', type = str, default='fermi_pi0',
                   help='name of the template')
    p.add_argument('--plot_trials', action='store_true', default=False,
                   help='if True, plot TS distribution.')
    p.add_argument('--chi2_ndf', type=int, nargs='*',
                   help='chi2 ndf values to plot')
    p.add_argument('--bin_width', type=float, default=0.2,
                   help='width of bin in TS space')
    p.add_argument('--only_bg', action='store_true', default=False,
                   help='if True, do not plot true TS.')
    p.add_argument('--use_original_trials', action='store_true', default=False,
                   help='Use the original background trials rather those you generated on your own.')
    args = p.parse_args()

    #Load in scrambled trials
    if args.use_original_trials:
        job_list = glob('/data/user/zgriffith/pev_photons/template/trials/'+args.name+'/*.npy') 
    else:
        job_list = glob(prefix+'/template/trials/'+args.name+'/*.npy') 
    bg_trials = []
    for job in job_list:
        job_ts = np.load(job)
        bg_trials.extend(job_ts)
    n_trials = float(len(bg_trials))

    #Calculate true result p-value
    fit_result = np.load(prefix+'/template/'+args.name+'_fit_result.npy')
    true_TS  = fit_result['TS']

    p_value = np.sum(np.greater(bg_trials, fit_result['TS']))/n_trials
    print("p-value: %.4f" % p_value)
    
    #Save to fit result
    if "p_value" not in fit_result.dtype.fields:
        fit_result = numpy.lib.recfunctions.append_fields(fit_result,
                                                          names="p_value",
                                                          data=[p_value],
                                                          dtypes=np.float,
                                                          usemask=False)
        np.save(prefix+'/template/'+args.name+'_fit_result.npy',
                fit_result)

    #Plot if desired
    if args.plot_trials:
        plot_trials(args, bg_trials, n_trials, fit_result['TS'])
