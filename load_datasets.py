#!/usr/bin/env python

########################################################################
# Functions for loading Skylab objects.
########################################################################

import numpy as np

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH

def load_ps_dataset(args):
    from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH

    ps_llh = MultiPointSourceLLH(ncpu=args.ncpu, seed=args.seed)

    years = ['2011', '2012', '2013', '2014', '2015']

    for i, year in enumerate(years): 
        name = 'IC86.'+year
        exp, mc, livetime = Datasets['GammaRays5yr_PointSrc'].season(name)
        energy_bins = Datasets['GammaRays5yr_PointSrc'].energy_bins(name)
        energy_range = [energy_bins[0], energy_bins[-1]]
        sinDec_bins = Datasets['GammaRays5yr_PointSrc'].sinDec_bins(name)
        sinDec_range = [sinDec_bins[0], sinDec_bins[-1]]

        llh_model = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                              twodim_range=[energy_range, sinDec_range],
                              sinDec_bins=sinDec_bins,
                              sinDec_range=sinDec_range)

        year_psllh = PointSourceLLH(exp, mc, livetime,
                                    ncpu=args.ncpu,
                                    mode='box',
                                    scramble=True,
                                    llh_model=llh_model,
                                    delta_ang=np.radians(10*0.4))

        ps_llh.add_sample(year, year_psllh)

    return ps_llh

def load_gp_dataset(args):
    from skylab.template import Template
    from skylab.template_llh import TemplateLLH, MultiTemplateLLH

    years = ['2011', '2012', '2013', '2014', '2015']

    for i, year in enumerate(years): 
        name = 'IC86.'+year
        exp, mc, livetime = Datasets['GammaRays5yr_GalPlane'].season(name)
        energy_bins = Datasets['GammaRays5yr_GalPlane'].energy_bins(name)
        energy_range = [energy_bins[0], energy_bins[-1]]
        sinDec_bins = Datasets['GammaRays5yr_GalPlane'].sinDec_bins(name)
        sinDec_range = [sinDec_bins[0], sinDec_bins[-1]]

        template = Template((args.prefix+'/galactic_plane/'+year+
                             '/'+args.name+'_exp.npy'), reduced=True)

        llh_model[year] = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                                    twodim_range=[energy_range, sinDec_range],
                                    bounds=[args.alpha, args.alpha],
                                    fix_index=True,
                                    sinDec_bins=sinDec_bins,
                                    sinDec_range=sinDec_range)

        year_llh = TemplateLLH(exp, mc, livetime,
                               scramble=False,
                               llh_model=llh_model[year],
                               ncpu=args.ncpu,
                               template=template)

        template_llh.add_sample(year, year_llh)

    return template_llh
