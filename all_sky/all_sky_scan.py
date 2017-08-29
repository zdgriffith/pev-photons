#!/usr/bin/env python

import argparse
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('mystyle')
import matplotlib as mpl
import pandas as pd
colors = mpl.rcParams['axes.color_cycle']

from support_pandas import get_fig_dir, livetimes
fig_dir = get_fig_dir()

from skylab import psLLH
from skylab.psLLH import PointSourceLLH,MultiPointSourceLLH
from skylab.ps_injector import PointSourceInjector
from skylab.ps_model import ClassicLLH, EnergyLLH

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    p.add_argument('--outFile', dest='outFile', type = str,
                   default = 'all_sky/skymap.npy',
                   help    = 'file name')
    args = p.parse_args()

    dec_bins    = np.arange(-1., -0.799, 0.01)
    energy_bins = [np.linspace(5.5,8.5,30), dec_bins]

    #Initialization of multi-year LLH object
    psllh = MultiPointSourceLLH(ncpu      = 20,
                                mode      = 'box',
                                delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                                nside     = 128
                                )
    tot_mc    = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']

    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp      = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        mc       = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')

        llh_model[year] = EnergyLLH(twodim_bins  = energy_bins,
                                    twodim_range = [[5.5,8.5],[-1,-0.8]],
                                    sinDec_bins  = dec_bins, sinDec_range=[-1,-0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                               scramble  = False,
                               ncpu      = 20,
                               llh_model = llh_model[year],
                               mode      = 'box',
                               delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                               nside     = 128,
                               )
        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    for i, scan in enumerate(psllh.all_sky_scan(
                                decRange=[np.radians(-85.),np.arcsin(-0.8)])):
        if i > 0:
            m = scan[0]['TS']
            break

    #Stores the skymap in a standard directory
    np.save(args.prefix+args.outFile, m)
