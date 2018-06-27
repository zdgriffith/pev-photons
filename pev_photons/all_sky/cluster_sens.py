#!/usr/bin/env python

########################################################################
# Submit a dagman to the cluster evaluating the sensitivity for a fine
# grid (0.1 degrees) in declination.
########################################################################

import argparse
import os
import sys
from itertools import product

from pev_photons.utils.support import prefix, resource_dir, dag_dir
from pev_photons.utils.cluster_support import DagMaker

def construct_dag(dag_maker, test=False):
    """ Construct a dag for point source sensitivity.

    Parameters
    ----------
    dag_maker : DagMaker instance
        Class instance that contains info for creating dag files.
    test : bool
        Denotes whether this is a test on a non-submitter node.

    Returns
    -------
    ex : str
        a bash executable to pass to os.system()
    """
    script = os.path.join(os.getcwd(), 'sens_on_cluster.py')
    dag_file = os.path.join(dag_maker.temp_dir, dag_maker.name+'.dag')
    indices = [2.0,2.7]
    dec_bounds = [-85, -53.4]
    decs = range(int((dec_bounds[1] - dec_bounds[0])*10))
    with open(dag_file, 'w+') as dag:
        for i, (dec, index) in enumerate(product(decs, indices)):
            arg  = ' --dec %s' % dec
            arg += ' --index %s' % index

            if test:
                return ' '.join(['python', cmd, arg])
            else:
                dag_maker.write(dag=dag, index=i, arg=script+arg,
                                submit_file=resource_dir+'basic.submit',
                                prefix=prefix) 
    return 'condor_submit_dag -f {}'.format(dag_file)

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Runs sensitivity evaluation on cluster',
                          formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    dag_maker = DagMaker(name='ps_sensitivity', temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    ex = construct_dag(dag_maker, test=args.test, nJobs=args.nJobs,
                       nTrials=args.nTrials)
    os.system(ex)
