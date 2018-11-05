#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster for calculating all sky trials
########################################################################

import argparse
import os

from pev_photons import utils

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Calculate HESS sensitivities for a given energy cut off.'
        )
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    dag_maker = utils.DagMaker(name='hess_cut_offs', temp_dir=utils.dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=utils.prefix)

    #iters = {'source': range(15), 'Ecut':range(100, 10100, 100)}
    #iters = {'source': [0,1,3,4,5,6,8,9,10,11,12,13,14,15], 'Ecut':range(100, 10100, 100)}
    #iters = {'source': [0,1,3,4,5,6,8,9,10,11,12,13,14,15], 'Ecut':range(10100, 20100, 100)}
    iters = {'source': [1,5], 'Ecut':range(20100, 30100, 100)}
    #iters = {'source': [13], 'Ecut':range(1000, 10100, 100)}
    #iters = {'source': [3, 5, 10], 'Ecut':range(950, 1350, 10)}

    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'hess_cut_off.py'),
                          iters=iters,
                          submit_file=os.path.join(utils.resource_dir, 'py2v3.submit'),
                          test=args.test, prefix=utils.prefix)
    os.system(ex)
