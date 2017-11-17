#!/usr/bin/env python

########################################################################
## Submit a dagman to the cluster for galactic plane background trials.
########################################################################

import os
import sys
import argparse as ap

if __name__ == "__main__":

    p = ap.ArgumentParser(description='Submit trials to the cluster.',
                          formatter_class=ap.RawDescriptionHelpFormatter)
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster.')
    p.add_argument('--nJobs', type=int, default=4,
                   help='The number of jobs to submit.')
    p.add_argument('--nTrials', type=int, default=25000,
                   help='The number of trials run per job.')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--rescue', action='store_true', default=False,
                   help='Option for submitting the rescue file.')
    args = p.parse_args()

    script = ('/home/zgriffith/photon_analysis/'
              'pev_photons/all_sky/one_dec_ts.py')

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = ('/data/user/zgriffith/dagman/myJobs/'
                    +'ps_dec_trials.dag')
        ex       = ('condor_submit_dag -f -maxjobs '
                    + args.maxjobs + ' ' + dag_name)

        if args.rescue:
            os.system(ex)
            sys.exit()

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")
    
    index = 0 
    unique_decs = 342 # For Nside = 512
    for dec_i in range(unique_decs):
        for job in range(args.nJobs):
            arg  = ' --job %s --dec_i %s' % (job, dec_i)
            arg += ' --n_trials %s ' % (args.nTrials)
            if args.test:
                ex  = ' '.join([cmd, arg])
            else:
                arg = script+arg
                dag.write(('JOB ' + str(index)
                           + ' /data/user/zgriffith/dagman/OneJob.submit\n'))
                dag.write('VARS ' + str(index) + " ARGS=\"" + arg + "\"\n")
            index += 1
    os.system(ex)
