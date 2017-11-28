#!/usr/bin/env python

########################################################################
# Perform a scan over the entire FOV, evaluating the TS at each pixel.
########################################################################

import healpy as hp
import argparse
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import logging

from dask import delayed
from dask.diagnostics import ProgressBar
from support_pandas import get_fig_dir, livetimes

from skylab.ps_llh import PointSourceLLH, MultiPointSourceLLH
from skylab.llh_models import ClassicLLH, EnergyLLH

logging.getLogger("skylab.ps_llh.PointSourceLLH").setLevel(logging.INFO)

fig_dir = get_fig_dir()
plt.style.use('mystyle')
colors = matplotlib.rcParams['axes.color_cycle']

def fill_map(vals, indices, npix):
    m = np.zeros(npix)
    m[indices] = vals
    return m
    
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

    dec_bins = np.linspace(-1., -0.8, 21)
    energy_bins = [np.linspace(5.7,8,24), dec_bins]

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
                                    twodim_range=[[5.7,8],[-1,-0.8]],
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

    nside = 512
    npix = hp.nside2npix(nside)
    m = np.zeros(npix)
    theta, ra = hp.pix2ang(nside, range(npix))
    dec = np.pi/2. - theta
    mask = np.less(np.sin(dec), -0.8)

    for pix in np.arange(npix)[mask]:
        m[pix] = psllh.fit_source(ra[pix],dec[pix], scramble = False)[0]

    np.save(args.prefix+'/all_sky/skymap_%s_manual.npy' % nside, m)
    '''
    np.save('/data/user/zgriffith/pev_photons/all_sky/manual_mask.npy', mask)

    ts = np.zeros(npix, dtype=np.float)
    xmin = np.zeros_like(ts, dtype=[(p, np.float) for p in psllh.params])
    xmin = np.array(zip(
        *[hp.get_interp_val(xmin[p], theta, ra) for p in psllh.params]),
        dtype=xmin.dtype)
    ts, xmin = psllh._scan(ra[mask], dec[mask], ts, xmin, mask)

    np.save(args.prefix+'/all_sky/skymap_%s_new.npy' % nside, ts)
    '''
