#!/usr/bin/env python

########################################################################
# Functions for loading Skylab objects.
########################################################################

import numpy as np

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH

from utils.support import prefix

from skylab.template import Template
from skylab.template_llh import TemplateLLH, MultiTemplateLLH
from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH

def load_dataset(name, args, llh_args={'scramble':False}, model_args={}):
    """ Creates a MultiTemplateLLH object from the final cut level gamma-ray
    analysis event files

    Parameters
    ----------
    name : string which describes the event selection used for the desired dataset
           Allowed entries: "point_source", "galactic_plane"

    args : Namespace object with argparse arguments from the parent script.
           Needs to include:
               ncpu  : number of cores to use.
               seed  : random number seed.
               alpha : spectral index to fix to in the template likelihood

    Returns
    ----------
    psllh : MultiTemplateLLH instance

    """

    if name == 'point_source':
        dataset = 'GammaRays5yr_PointSrc'
    elif name in ['galactic_plane', 'HESE']:
        dataset = 'GammaRays5yr_GalPlane'
    else:
        raise(ValueError, 'Name must be one of "point_source", "HESE", "galactic_plane".')

    llh_args['ncpu'] = args.ncpu

    years = ['2011', '2012', '2013', '2014', '2015']

    if name == 'point_source':
        llh = MultiPointSourceLLH(seed=args.seed, ncpu=args.ncpu)
        llh_args['mode'] = 'box'
        llh_args['delta_ang'] = np.radians(4.0)
    else:
        llh = MultiTemplateLLH(seed=args.seed, ncpu=args.ncpu)
        model_args['bounds'] = [args.alpha, args.alpha]
        model_args['fix_index'] = True

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
                              sinDec_range=sinDec_range, **model_args)

        if name == 'point_source':
            llh_year = PointSourceLLH(exp, mc, livetime, llh_model, **llh_args)
        else:
            template = Template((prefix+'/template/'+year+
                                 '/'+args.name+'_exp.npy'), reduced=True)
            llh_year = TemplateLLH(exp, mc, livetime, llh_model,
                                   template=template, **llh_args)

        llh.add_sample(year, llh_year)

    return llh
