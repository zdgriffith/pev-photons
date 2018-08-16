#!/usr/bin/env python

########################################################################
# Calculate sensitivity as a function of declination.
########################################################################

import argparse
import numpy as np
import logging

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH
from skylab.ps_llh import PointSourceLLH

from skylab.ps_injector import PointSourceInjector
from pev_photons.utils.load_datasets import load_systematic_dataset
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

    dec = np.radians(-60.)
    index = 2.0
    
    years = {'2011': ['2011', '2012'],
             '2012': ['2011', '2012', '2013'],
             '2013': ['2012', '2013', '2014'],
             '2014': ['2013', '2014', '2015'],
             '2015': ['2014', '2015']}


    dataset = 'GammaRays5yr_PointSrc'

    llh_args = {}
    llh_args['ncpu'] = args.ncpu
    llh_args['mode'] = 'box'
    llh_args['delta_ang'] = np.radians(4.0)

    for i, year in enumerate(years.keys()):
        exp, mc, livetime = Datasets[dataset].season('IC86.'+year)
        energy_bins = Datasets[dataset].energy_bins('IC86.'+year)
        energy_range = [energy_bins[0], energy_bins[-1]]
        sinDec_bins = Datasets[dataset].sinDec_bins('IC86.'+year)
        sinDec_range = [sinDec_bins[0], sinDec_bins[-1]]
        llh_model = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                              twodim_range=[energy_range, sinDec_range],
                              sinDec_bins=sinDec_bins,
                              sinDec_range=sinDec_range)

        for snow_year in years[year]:
            print(snow_year)
            snow_exp, snow_mc, snow_livetime = Datasets[dataset].season('IC86.'+snow_year)
            ps_llh = PointSourceLLH(exp, snow_mc, livetime, llh_model, **llh_args)
            inj= PointSourceInjector(index, E0=10**6,
                                     sinDec_bandwidth=np.sin(np.radians(2)))
            inj.fill(dec, exp, snow_mc, livetime)
            result = ps_llh.weighted_sensitivity([0.5, 2.87e-7], [0.9, 0.5],
                                                 inj=inj,
                                                 eps=1.e-2,
                                                 n_bckg=10000,
                                                 n_iter=1000,
                                                 src_ra=np.pi, src_dec=dec)
            np.save(prefix+'systematics/{}_sens_{}_snow.npy'.format(year, snow_year), result[0]["flux"][0])
            np.save(prefix+'systematics/{}_disc_{}_snow.npy'.format(year, snow_year), result[0]["flux"][1])
