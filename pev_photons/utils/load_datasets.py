#!/usr/bin/env python

########################################################################
# Functions for loading Skylab objects.
########################################################################

import numpy as np

from skylab.datasets import Datasets
from skylab.llh_models import EnergyLLH
from skylab.template import Template
from skylab.template_llh import TemplateLLH, MultiTemplateLLH
from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH

from .support import prefix
from .gamma_ray_survival import apply_source_absorption

def load_dataset(name, ncpu=1, seed=1, alpha=2.0, template_name=None,
                 absorption=False, llh_args={'scramble':False}, model_args={}):
    """ Creates a MultiTemplateLLH object from the final cut level gamma-ray
    analysis event files

    Parameters
    ----------
    name : string
        Describes the event selection used for the desired dataset.
        Allowed entries: "point_source", "galactic_plane", "HESE"

    ncpu: int
        The number of cores to use.
    seed: int
        The random number seed.
    alpha: float
        The spectral index to fix to in the template likelihood.

    Returns
    ----------
    psllh : MultiTemplateLLH instance

    """

    if name in ['point_source']:
        dataset = 'GammaRays5yr_PointSrc'
    elif name in ['galactic_plane', 'HESE']:
        dataset = 'GammaRays5yr_GalPlane'
    else:
        raise(ValueError, 'Name must be one of "point_source", "HESE", "galactic_plane".')

    llh_args['ncpu'] = ncpu

    years = ['2011', '2012', '2013', '2014', '2015']

    if name == 'point_source':
        llh = MultiPointSourceLLH(seed=seed, ncpu=ncpu)
        llh_args['mode'] = 'box'
        llh_args['delta_ang'] = np.radians(4.0)
    else:
        llh = MultiTemplateLLH(seed=seed, ncpu=ncpu)
        model_args['bounds'] = [alpha, alpha]
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
        if absorption:
            mc['ow'] *= apply_source_absorption(mc['trueE']*10**-3, absorption)

        if name == 'point_source':
            llh_year = PointSourceLLH(exp, mc, livetime, llh_model, **llh_args)
        else:
            template = Template((prefix+'/template/'+year+
                                 '/'+template_name+'_exp.npy'), reduced=True)
            llh_year = TemplateLLH(exp, mc, livetime, llh_model,
                                   template=template, **llh_args)

        llh.add_sample(year, llh_year)

    return llh

def load_systematic_dataset(name, systematic, year='2012', index=3.0,
                            seed=1, ncpu=1, llh_args={'scramble':False},
                            model_args={}):
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

    sel = {'point_source':'ps', 'galactic_plane':'diffuse'}
    livetimes = {'2011': 26673776., '2012': 25569773.,
                 '2013': 27769791., '2014': 28139667.,
                 '2015': 28097975.}

    mc = np.load(prefix+'/datasets/systematics/skylab/{}/{}_mc_{}.npy'.format(year, systematic, sel[name]))
    if 'standard_Laputop' in systematic:
        dataset = 'GammaRays5yr_PointSrc'
        exp, dump, full_livetime = Datasets[dataset].season('IC86.'+year)
        livetime = 2626947.0*1.157*10**-5
        exp = np.random.choice(exp, int(len(exp)*(livetime/full_livetime)))
        mc = np.load(prefix+'/datasets/systematics/skylab/{}/Laputop_mc_{}.npy'.format(year, sel[name]))
    elif 'Laputop' in systematic:
        exp = np.load(prefix+'/datasets/systematics/skylab/{}/{}_exp_{}.npy'.format(year, systematic, sel[name]))
        livetime = 2626947.0*1.157*10**-5 # days
    else:
        exp = np.load(prefix+'/resources/datasets/{}_exp_{}.npy'.format(year, sel[name]))
        livetime = livetimes[year]*1.157*10**-5 # days

    llh_args['ncpu'] = ncpu
    llh_args['seed'] = seed
    if name == 'point_source':
        llh_args['mode'] = 'box'
        llh_args['delta_ang'] = np.radians(4.0)
    else:
        model_args['bounds'] = [index, index]
        model_args['fix_index'] = True

    energy_bins = np.linspace(5.7, 8, 24)
    energy_range = [energy_bins[0], energy_bins[-1]]
    sinDec_bins = np.linspace(-1., -0.8, 21)
    sinDec_range = [sinDec_bins[0], sinDec_bins[-1]]

    llh_model = EnergyLLH(twodim_bins=[energy_bins, sinDec_bins],
                          twodim_range=[energy_range, sinDec_range],
                          sinDec_bins=sinDec_bins,
                          allow_empty=True,
                          sinDec_range=sinDec_range, **model_args)

    if name == 'point_source':
        llh = PointSourceLLH(exp, mc, livetime, llh_model, **llh_args)
        return exp, mc, livetime, llh
    else:
        template = Template((prefix+'/template/'+year+
                             '/'+systematic+'_exp.npy'), reduced=True)
        llh = TemplateLLH(exp, mc, livetime, llh_model,
                          template=template, **llh_args)
        return exp, mc, livetime, llh, template
