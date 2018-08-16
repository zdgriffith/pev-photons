#!/usr/bin/env python 

########################################################################
# Submit a dagman to the cluster for Level 3 processing of IceTop Data.
########################################################################

import argparse
import os
import glob

from pev_photons.utils.support import prefix, resource_dir, dag_dir
from pev_photons.utils.cluster_support import DagMaker

def getL2GCD(config):
    """ Retrieve the Level 2 GCD filename for simulation
    for the given detector configuration.
    """
    base = '/data/sim/sim-new/downloads/GCD/GeoCalibDetectorStatus'
    gcd_dict = {
                'IC86.2011': base+'_IC86.55697_corrected_V3_NovSnow.i3.gz',
                'IC86.2012': base+'_2012.56063_V1_OctSnow.i3.gz',
                'IC86.2013': base+'_2013.56429_V1_OctSnow.i3.gz',
                'IC86.2014': base+'_2014.56784_V0_NovSnow.i3.gz',
                'IC86.2015': base+'_2015.57161_V0_OctSnow.i3.gz',
               }

    return gcd_dict[config]

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Level3 processing of IceTop data.',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--dataset', help='The simulation dataset to process.')
    p.add_argument('--year', help='The detector year.')
    p.add_argument('--n', type=int, default=800,
                   help='Number of files to run per batch.')
    args = p.parse_args()

    dag_maker = DagMaker(name='level3_processing', temp_dir=dag_dir)
    if args.rm_old:
        dag_maker.remove_old(prefix=prefix)

    bool_args = ['isMC', 'waveforms', 'do_inice']

    # Get config and simulation files
    config = 'IC86.' + args.year
    L2_GCD = getL2GCD(config)
    L3_GCD = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
    static_args = {'dataset': args.dataset, 'detector': config,
                   'L2_gcdfile': L2_GCD, 'L3_gcdfile': L3_GCD}

    files = glob.glob('/data/sim/IceTop/2012/filtered/CORSIKA-ice-top/%s/level2/*/L*' % args.dataset)
    batches = [files[i:i+args.n] for i in range(0, len(files), args.n)]
    iters = {'input_files': batches}

    ex = dag_maker.submit(script=os.path.join(os.getcwd(), 'level3_processing.py'),
                          static_args=static_args, bool_args=bool_args, iters=iters,
                          submit_file=os.path.join(resource_dir, 'icerec.submit'),
                          test=args.test, prefix=prefix)
    os.system(ex)
