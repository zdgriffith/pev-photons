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
            description='Check Sensitivity for Different Cut Options',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', dest='year', type = str,
            help='Year', default = '2012')
    p.add_argument('--option', dest='option', type = str,
            help='Add on to file name', default = '/')
    p.add_argument('--alpha', dest='alpha', type = float,
            help='Spectral Index for training', default = 2.0)
    p.add_argument('--k', dest='k', type = int,
            default = 5, help='Total cross val folds')
    args = p.parse_args()

    pf = '/data/user/zgriffith/datasets/'

    dec_bins    = np.arange(-1., -0.799, 0.01)
    energy_bins = [np.linspace(5.5,8.5,30), dec_bins]

    psllh = MultiPointSourceLLH(ncpu      = 20,
                                mode      = 'box',
                                delta_ang = np.radians(10*0.4), #Recommended ~10 times ang_res
                                nside     = 128
                                )
    tot_mc    = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        livetime    = livetimes(year)*1.157*10**-5  #Seconds to Days
        exp = np.load('/data/user/zgriffith/datasets/'+year+'_exp_ps.npy')
        exp = exp[(exp['sinDec']<-0.8)&(np.degrees(np.arcsin(exp['sinDec']))>-85.)]
        mc  = np.load('/data/user/zgriffith/datasets/'+year+'_mc_ps.npy')
        mc  = mc[(mc['sinDec']<-0.8)&(np.degrees(np.arcsin(mc['sinDec']))>-85.)]
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

    np.save('/data/user/zgriffith/original_results/skymap.npy', m)
