#!/usr/bin/env python

########################################################################
# Plot the effective area for gamma rays compared to protons
########################################################################

import argparse
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

import dashi
from support_pandas import cut_maker, get_fig_dir

dashi.visual()
plt.style.use('stefan')
fig_dir = get_fig_dir()
colors = mpl.rcParams['axes.color_cycle']

def effective_area(E, label, fname, w, args, index):

    weights = []
    for i in E:
        if i < 6:
            weights.append(np.pi*800**2) 
        elif i<7 and i> 6:
            weights.append(np.pi*1100**2) 
        else:
            if 'Protons' in label:
                weights.append(np.pi*1700**2) 
            else:
                weights.append(np.pi*1400**2) 

    bins = np.arange(5,8.1,args.Ebin_width)
    E_hist= dashi.factory.hist1d(E, bins,
                                 weights=np.array(weights)*w**-1)
    error_hist = dashi.factory.hist1d(E, bins,
                                      weights=w**-1*np.array(weights)**2)

    events = np.load('/data/user/zgriffith/sim_files/'+fname+'_events.npy')
    n_gen = events[:].astype('float')

    if 'Protons' in label:
        factor = 1.971
    else:
        factor = 1

    area  = factor*E_hist.bincontent/n_gen
    error = np.sqrt(error_hist.bincontent)/n_gen
    
    #Plot bins unless told not to
    if not args.noBins:
        ax0.errorbar(E_hist.bincenters, np.array(area),
                     xerr=args.Ebin_width/2., yerr=error,
                     label=label, color=colors[index],
                     capsize=0, capthick=2, lw=2,
                     fmt='o', marker='o', ms=0)

    return area, E_hist.binedges

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Plot a skymap',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='base directory for file storing')
    p.add_argument('--outFile', type=str,
                   default='effective_area_proton_comp.png',
                   help='file name')
    p.add_argument('--noBins', action='store_true',
                   default = False, help='if True, do not plot bins')
    p.add_argument('--Ebin_width', type=float,
                   default=0.1, help='log(E/GeV) bin size')
    args = p.parse_args()

    labels = ['2012 Gamma Rays', '2012 Protons']

    left = 0.15
    width = 0.8
    ax0 = plt.axes([left, 0.36, width, 0.6])
    ax1 = plt.axes([left, 0.14, width, 0.19])

    cut_args = {'standard':1, 'laputop_it':1}

    comp = []
    for i, fname in enumerate(['12533', '12360']):
        f = cut_maker(fname, cut_args)
        w = np.ones(len(f['Nstations']))
            
        vals, bins = effective_area(np.log10(f['primary_E']), labels[i],
                                    fname, w, args, i)
        comp.append(np.array(vals))

    for i, c in enumerate(comp):
        ratio = c/comp[0] 
        ax1.step(bins,np.append(ratio[0],ratio), color = colors[i])

    ax1.set_xlim([5.7,8])
    ax1.set_ylim([0.2,2])
    ax1.grid(b=True, color='grey', linestyle='dashed', alpha=1)
    ax1.set_xlabel(r'log(E$_{\textrm{true}}$/GeV)', fontsize=14)
    ax1.set_ylabel('Ratio to Gammas', fontsize=14)
    ax0.xaxis.set_visible(False)
    ax0.set_xlim([5.7,8])
    ax0.set_ylabel('Effective Area (m$^2$)', fontsize=14)
    ax0.legend(loc='lower right')
    plt.savefig(fig_dir+args.outFile, facecolor='none', dpi=300)
    plt.close()
