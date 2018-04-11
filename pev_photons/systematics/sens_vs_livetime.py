#!/usr/bin/env python

########################################################################
# Calculate sensitivity as a function of declination.
########################################################################

import argparse
import numpy as np
import logging

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH
from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH

from skylab.ps_injector import PointSourceInjector
from pev_photons.utils.support import prefix

logging.basicConfig(filename='scan.log', filemode='w', level=logging.INFO)
logging.getLogger("skylab.ps_llh.PointSourceLLH").setLevel(logging.INFO)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Calculate sensitivity as a function of declination.',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ncpu", type=int, default=1,
                    help="Number of cores to run on.")
    p.add_argument("--seed", type=int, default=1,
                   help='rng seed')
    args = p.parse_args()

    
    dataset = 'GammaRays5yr_PointSrc'
    llh_args = {}
    llh_args['ncpu'] = args.ncpu
    llh_args['mode'] = 'box'
    llh_args['delta_ang'] = np.radians(4.0)
    llh = MultiPointSourceLLH(seed=args.seed, ncpu=args.ncpu)

    dec = np.radians(-60.)
    index = 2.0

    years = ['2011', '2012', '2013', '2014', '2015']
    sens = np.zeros(5)
    for i, year in enumerate(years): 
        season = 'IC86.'+year
        exp, mc, livetime = Datasets[dataset].season(season)
        energy_bins = Datasets[dataset].energy_bins(season)
        energy_range = [energy_bins[0], energy_bins[-1]]
        sinDec_bins = Datasets[dataset].sinDec_bins(season)
        sinDec_range = [sinDec_bins[0], sinDec_bins[-1]]

        llh_model = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                              twodim_range=[energy_range, sinDec_range],
                              sinDec_bins=sinDec_bins,
                              sinDec_range=sinDec_range)

        llh_year = PointSourceLLH(exp, mc, livetime, llh_model, **llh_args)
        llh.add_sample(year, llh_year)

        inj= PointSourceInjector(index, E0=10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))
        inj.fill(dec, llh.exp, llh.mc, llh.livetime)
        result = llh.weighted_sensitivity([0.5], [0.9],
                                          inj=inj,
                                          eps=1.e-2,
                                          n_bckg=10000,
                                          n_iter=1000,
                                          src_ra=np.pi, src_dec=dec)
        sens[i] += result[0]['flux'][0]

        np.save(prefix+'systematics/sens_by_years.npy', sens)
