#!/usr/bin/env python

########################################################################
# Perform a scan over the entire FOV, evaluating the TS at each pixel.
########################################################################

import argparse
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

import logging

from support_pandas import get_fig_dir, livetimes
from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import ClassicLLH, EnergyLLH

logging.basicConfig(filename='scan.log', filemode='w', level=logging.INFO)
logging.getLogger("skylab.ps_llh.PointSourceLLH").setLevel(logging.INFO)

fig_dir = get_fig_dir()
plt.style.use('mystyle')
colors = matplotlib.rcParams['axes.color_cycle']

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Create an all sky TS map.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='The base directory for file storing.')
    p.add_argument('--outFile', type=str,
                   default='all_sky/skymap.npy',
                   help='The output file name.')
    args = p.parse_args()

    dec_bins = np.linspace(-1., -0.8, 21)
    energy_bins = [np.linspace(5.7,8,24), dec_bins]

    # Initialization of multi-year LLH object.
    psllh = MultiPointSourceLLH(ncpu=20)
    tot_mc = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  # Convert seconds to days.
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        mc  = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[[5.7,8],[-1,-0.8]],
                                    sinDec_bins=dec_bins,
                                    sinDec_range=[-1,-0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                                    ncpu=20,
                                    mode='box',
                                    scramble=False,
                                    llh_model=llh_model[year],
                                    delta_ang=np.radians(10*0.4))

        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    for i, scan in enumerate(psllh.all_sky_scan(nside=256, follow_up_factor=1)):
        if i > 0:
            m = scan[0]['TS']
            break

    # Stores the skymap in a standard directory.
    np.save(args.prefix+args.outFile, m)
