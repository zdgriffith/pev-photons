#!/usr/bin/env python

########################################################################
# Count Event Numbers
########################################################################

import argparse
import numpy as np

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='Count events',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--prefix', type=str,
                   default='/data/user/zgriffith/pev_photons/',
                   help='The base directory for file storing.')
    args = p.parse_args()

    years = ['2011', '2012', '2013', '2014','2015']
    for i, year in enumerate(years): 
        ps = np.load(args.prefix+'/datasets/'+year+'_exp_ps.npy')
        print('PS = %s' % len(ps['logE']))
        gal = np.load(args.prefix+'/datasets/'+year+'_exp_diffuse.npy')
        print('Gal = %s' % len(gal['logE']))
