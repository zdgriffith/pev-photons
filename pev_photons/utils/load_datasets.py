#!/usr/bin/env python

########################################################################
# Functions for loading Skylab objects.
########################################################################

import numpy as np

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH

from pev_photons.utils.support import prefix

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

    if name in ['point_source', 'high_galactic_lat']:
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

def load_systematic_dataset(name, model, args, year='2012', reco_test=False,
                            llh_args={'scramble':False}, model_args={}):
    """ Creates a MultiTemplateLLH object from the final cut level gamma-ray
    analysis event files

    Parameters
    ----------
    name : string which describes the event selection used for the desired dataset
           Allowed entries: "point_source", "galactic_plane"

    model : either hadronic interaction model (sybll, qgs) or type of
            reconstruction (e.g. LaputopLambdaUp, LaputopLambdaDown)

    args : Namespace object with argparse arguments from the parent script.
           Needs to include:
               ncpu  : number of cores to use.
               seed  : random number seed.
               alpha : spectral index to fix to in the template likelihood

    Returns
    ----------
    psllh : MultiTemplateLLH instance

    """

    if reco_test == True:
        if name == 'point_source':
            exp = np.load(prefix+'/datasets/systematics/skylab/{}_data_{}_ps.npy'.format(year, model))
            mc = np.load(prefix+'/datasets/systematics/skylab/{}_mc_{}_ps.npy'.format(year, model))
        elif name in ['galactic_plane', 'HESE']:
            exp = np.load(prefix+'/datasets/systematics/skylab/{}_data_{}_gal.npy'.format(year, model))
            mc = np.load(prefix+'/datasets/systematics/skylab/{}_mc_{}_gal.npy'.format(year, model))
        else:
            raise(ValueError, 'Name must be one of "point_source", "HESE", "galactic_plane".')
    else:
        if name == 'point_source':
            exp = np.load(prefix+'/resources/datasets/{}_exp_ps.npy'.format(year))
            mc = np.load(prefix+'/datasets/systematics/{}_{}_ps.npy'.format(year, model))
        elif name in ['galactic_plane', 'HESE']:
            exp = np.load(prefix+'/resources/datasets/{}_exp_diffuse.npy'.format(year))
            mc = np.load(prefix+'/datasets/systematics/{}_{}_gal.npy'.format(year, model))
        else:
            raise(ValueError, 'Name must be one of "point_source", "HESE", "galactic_plane".')

    llh_args['ncpu'] = args.ncpu
    llh_args['seed'] = args.seed

    if name == 'point_source':
        llh_args['mode'] = 'box'
        llh_args['delta_ang'] = np.radians(4.0)
    else:
        model_args['bounds'] = [args.alpha, args.alpha]
        model_args['fix_index'] = True

    livetimes = {'2011': 26673776.,
                 '2012': 25569773.,
                 '2013': 27769791.,
                 '2014': 28139667.,
                 '2015': 28097975.}

    if reco_test == True:
        livetime = 0.05*livetimes[year]*1.157*10**-5 # days
    else:
        livetime = livetimes[year]*1.157*10**-5 # days

    energy_bins = np.linspace(5.7, 8, 24)
    energy_range = [energy_bins[0], energy_bins[-1]]
    sinDec_bins = np.linspace(-1., -0.8, 21)
    sinDec_range = [sinDec_bins[0], sinDec_bins[-1]]

    llh_model = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                          twodim_range=[energy_range, sinDec_range],
                          sinDec_bins=sinDec_bins,
                          sinDec_range=sinDec_range, **model_args)

    if name == 'point_source':
        llh = PointSourceLLH(exp, mc, livetime, llh_model, **llh_args)
        return exp, mc, livetime, llh
    else:
        template = Template((prefix+'/template/'+year+
                             '/'+model+'_exp.npy'), reduced=True)
        llh = TemplateLLH(exp, mc, livetime, llh_model,
                          template=template, **llh_args) 
        return exp, mc, livetime, llh, template
