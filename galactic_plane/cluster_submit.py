#!/usr/bin/env python

import os, sys, argparse

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Run test trials on cluster',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', dest='test', action='store_true',
            default=False,
            help='Option for running test off cluster')
    p.add_argument('--nJobs', dest='nJobs', type=int,
            default='100',
            help='max jobs running on cluster')
    p.add_argument('--nTrials', dest='nTrials', type=int,
            default='10',
            help='max jobs running on cluster')
    p.add_argument('--name', dest='name', type = str,
                   default = 'fermi_pi0',
                   help    = 'name of the template')
    p.add_argument('--maxjobs', dest='maxjobs',
            default='1200',
            help='max jobs running on cluster')
    p.add_argument('--rm_old', dest='rm_old', action='store_true',
            default=False,
            help='Remove old dag files?')
    p.add_argument('--rescue', dest='rescue', action='store_true',
            default=False,
            help='Option for submitting rescue file')
    args = p.parse_args()

    script = "/home/zgriffith/photon_analysis/pev_photons/galactic_plane/run_trials.py"

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = '/data/user/zgriffith/dagman/myJobs/'+args.name+'_trials.dag'
        ex       = 'condor_submit_dag -f -maxjobs ' +args.maxjobs+' '+dag_name

        if args.rescue:
            os.system(ex)
            sys.exit()

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")

    index = 0
    for job in range(args.nJobs):
        arg  = ' --runTrial --job %s --nTrials %s --name %s' % (job, args.nTrials, args.name)
        if args.test:
            ex  = ' '.join([cmd, arg])
        else:
            arg = script+arg
            dag.write("JOB " + str(index) + " /data/user/zgriffith/dagman/OneJob.submit\n")
            dag.write("VARS " + str(index) + " ARGS=\"" + arg + "\"\n")
        index += 1
    os.system(ex)
