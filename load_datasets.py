#!/usr/bin/env python

########################################################################
# Functions for loading Skylab objects.
########################################################################

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH

def load_gp_dataset(args):
    from skylab.template import Template
    from skylab.template_llh import TemplateLLH, MultiTemplateLLH

    sinDec_range = [-1, -0.8]
    energy_range = [5.7, 8.0]

    template_llh = MultiTemplateLLH(ncpu=args.ncpu)
    template_years = dict()
    exp_years = dict()
    mc_years = dict()
    lt_years = dict()
    llh_model = dict()

    years = ['2011', '2012', '2013', '2014','2015']

    for i, year in enumerate(years): 
        name = 'IC86.'+year
        exp, mc, livetime = Datasets['GammaRays5yr_GalPlane'].season(name)
        sinDec_bins = Datasets['GammaRays5yr_GalPlane'].sinDec_bins(name)
        energy_bins = Datasets['GammaRays5yr_GalPlane'].energy_bins(name)
        lt_years[i] = livetime 
        mc_years[i] = mc 
        exp_years[i] = exp

        template = Template((args.prefix+'/galactic_plane/'+year+
                             '/'+args.name+'_exp.npy'), reduced=True)
        template_years[i] = template

        llh_model[year] = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                                    twodim_range=[energy_range, sinDec_range],
                                    seed=1,
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

    return template_llh, exp_years, mc_years, lt_years
