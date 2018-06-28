#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster evaluating the sensitivity for a fine
# grid (0.1 degrees) in declination.
########################################################################

import argparse
import os

from pev_photons.utils.support import prefix, resource_dir, dag_dir
from pev_photons.utils.cluster_support import DagMaker

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Sensitivity evaluation on the cluster.',
                          formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running a test job off the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    dag_maker = DagMaker(name='ps_sensitivity', temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    indices = [2.0, 2.7] # each of the spectral indices to submit
    dec_bounds = [-85, -53.4] # the range in declination to test
    iters = {'index': indices,
             'dec': range(int((dec_bounds[1] - dec_bounds[0])*10))}

    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'sens_on_cluster.py'),
                          submit_file=os.path.join(resource_dir, 'basic.submit'),
                          iters=iters, test=args.test, prefix=prefix)
    os.system(ex)
