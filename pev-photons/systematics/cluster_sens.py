#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster evaluating the sensitivity for a fine
# grid (0.1 degrees) in declination.
########################################################################

import argparse
import os

from pev-photons.utils.support import prefix, resource_dir, dag_dir
from pev-photons.utils.cluster_support import DagMaker

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Sensitivity evaluation on the cluster.',
                          formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running a test job off the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument("--systematic", help='Systematic to test.')
    p.add_argument("--year", help='Data year.')
    args = p.parse_args()

    dag_maker = DagMaker(name='ps_sensitivity', temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    indices = [2.0] # each of the spectral indices to submit
    dec_bounds = [-85, -53.4] # the range in declination to test
    static_args = {'systematic': args.systematic, 'year': args.year}
    iters = {'index': indices,
             'dec': range(int((dec_bounds[1] - dec_bounds[0])*10))}

    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'sens_on_cluster.py'),
                          submit_file=os.path.join(resource_dir, 'basic.submit'),
                          static_args=static_args,
                          iters=iters, test=args.test, prefix=prefix)
    os.system(ex)
