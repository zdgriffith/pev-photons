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
from skylab.ps_injector import PointSourceInjector

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

    dec_bins = np.arange(-1., -0.799, 0.01)
    energy_bins = [np.linspace(5.5,8.5,30), dec_bins]

    # Initialization of multi-year LLH object.
    psllh = MultiPointSourceLLH(ncpu=20)
    tot_mc = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        livetime = livetimes(year)*1.157*10**-5  # Convert seconds to days.
        exp = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        exp['dec'] = np.arcsin(exp['sinDec'])
        mc  = np.load(args.prefix+'/datasets/'+year+'_mc_ps.npy')
        mc['dec'] = np.arcsin(mc['sinDec'])

        llh_model[year] = EnergyLLH(twodim_bins=energy_bins,
                                    twodim_range=[[5.5,8.5],[-1,-0.8]],
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

    dec_list = np.radians(np.linspace(-84.,-54.,10))
    for alpha in [2.0,2.7]:
        sens = list()
        disc = list()
        for j, dec in enumerate(dec_list):
            inj = PointSourceInjector(alpha,
                                      sinDec_bandwidth=np.sin(np.radians(2)))
            inj.fill(dec, psllh.exp, tot_mc, psllh.livetime)
            result = psllh.weighted_sensitivity([0.5, 2.87e-7], [0.9, 0.5],
                                                inj=inj,
                                                eps=1.e-2,
                                                n_bckg=10000,
                                                n_iter=1000,
                                                src_ra=np.pi, src_dec=dec)
            sens.append(result[0]["flux"][0])
            disc.append(result[0]["flux"][1])
            print(sens)

        np.save('/data/user/zgriffith/pev_photons/all_sky/sens_alpha_%s.npy' % alpha, sens)
        np.save('/data/user/zgriffith/pev_photons/all_sky/disc_alpha_%s.npy' % alpha, disc)
