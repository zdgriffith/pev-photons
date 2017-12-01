#!/usr/bin/env python

########################################################################
# Calculates the TS for the hottest spot
########################################################################

import argparse
import numpy as np
import pandas as pd

from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import ClassicLLH, EnergyLLH
from skylab.datasets import Datasets

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Test hotspot',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', dest='prefix', type = str,
                   default = '/data/user/zgriffith/pev_photons/',
                   help    = 'base directory for file storing')
    args = p.parse_args()

    #Initialization of multi-year LLH object
    psllh = MultiPointSourceLLH(ncpu=20)
    tot_mc    = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        name = 'IC86.'+year
        exp, mc, livetime = Datasets['GammaRays5yr_PointSrc'].season(name)
        sinDec_bins = Datasets['GammaRays5yr_PointSrc'].sinDec_bins(name)
        energy_bins = Datasets['GammaRays5yr_PointSrc'].energy_bins(name)

        llh_model[year] = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                                    sinDec_bins=sinDec_bins,
                                    twodim_range=[[5.7, 8], [-1, -0.8]],
                                    sinDec_range=[-1, -0.8])

        year_psllh = PointSourceLLH(exp, mc, livetime,
                                    scramble=False,
                                    ncpu=20,
                                    llh_model=llh_model[year],
                                    mode='box',
                                    delta_ang=np.radians(10*0.4))
        psllh.add_sample(year, year_psllh)
        tot_mc[i] = mc 

    #20.2740533246
    dec = -73.4039433
    ra =  148.42541436
    a = psllh.fit_source(np.radians(ra),np.radians(dec), scramble = False)
    print(a)
