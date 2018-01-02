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
    p.add_argument('--nJobs', type=int, default=50,
                   help='The number of jobs to submit.')
    p.add_argument('--nTrials', type=int, default=200,
                   help='The number of trials run per job.')
    p.add_argument('--name', type=str, default='fermi_pi0',
                   help='Name of the template.')
    p.add_argument('--maxjobs', type=str, default='1200',
                   help='Max jobs running on the cluster.')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--rescue', action='store_true', default=False,
                   help='Option for submitting the rescue file.')
    args = p.parse_args()

    script = ('/home/zgriffith/photon_analysis/'
              'pev_photons/galactic_plane/sens_to_cluster.py')

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = ('/data/user/zgriffith/dagman/myJobs/'
                    + args.name+'_sens_trials_.dag')
        ex       = ('condor_submit_dag -f -maxjobs '
                    + args.maxjobs + ' ' + dag_name)

        if args.rescue:
            os.system(ex)
            sys.exit()

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")
    
    # Range, intervals of injected events best found through a course
    # run on sensitivity_test.py first. 
    inj_list =[20.,   98.,  176.,  254.,  332.,  410.,
               488.,  566.,  644., 722.,  800.]
    index = 0 
    for n_inj in inj_list:
        for job in range(args.nJobs):
            arg  = ' --job %s --n_inj %s' % (index, n_inj)
            arg += ' --n_trials %s --name %s' % (args.nTrials, args.name)
            if args.test:
                ex  = ' '.join([cmd, arg])
            else:
                arg = script+arg
                dag.write(('JOB ' + str(index)
                           + ' /data/user/zgriffith/dagman/four_gigs.submit\n'))
                dag.write('VARS ' + str(index) + " ARGS=\"" + arg + "\"\n")
            index += 1
    os.system(ex)
