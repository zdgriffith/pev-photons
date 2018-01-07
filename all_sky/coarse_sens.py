#!/usr/bin/env python

########################################################################
# Calculate sensitivity as a function of declination.
########################################################################

import argparse
import numpy as np
import logging

from skylab.ps_injector import PointSourceInjector
from pev_photons.load_datasets import load_ps_dataset
from pev_photons.support import prefix

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

    # Initialization of multi-year LLH object.
    ps_llh = load_ps_dataset(args)

    dec_list = np.radians(np.linspace(-84.,-54.,10))
    for index in [2.0,2.7]:
        inj= PointSourceInjector(index, E0=10**6,
                                 sinDec_bandwidth=np.sin(np.radians(2)))

        sens = np.zeros(len(dec_list))
        disc = np.zeros(len(dec_list))
        for j, dec in enumerate(dec_list):
            inj.fill(dec, ps_llh.exp, ps_llh.mc, ps_llh.livetime)
            result = ps_llh.weighted_sensitivity([0.5, 2.87e-7], [0.9, 0.5],
                                                 inj=inj,
                                                 eps=1.e-2,
                                                 n_bckg=10000,
                                                 n_iter=1000,
                                                 src_ra=np.pi, src_dec=dec)
            sens[j] = result[0]["flux"][0]
            disc[j] = result[0]["flux"][1]

            np.save(prefix+'all_sky/sens_index_%s.npy' % index, sens)
            np.save(prefix+'all_sky/disc_index_%s.npy' % index, disc)
