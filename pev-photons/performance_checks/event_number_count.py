#!/usr/bin/env python

########################################################################
# Count Event Numbers
########################################################################

import numpy as np

from pev-photons.utils.support import prefix

if __name__ == "__main__":

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        ps = np.load(prefix+'/datasets/'+year+'_exp_ps.npy')
        print('PS = %s' % len(ps['logE']))
        gal = np.load(prefix+'/datasets/'+year+'_exp_diffuse.npy')
        print('Gal = %s' % len(gal['logE']))
