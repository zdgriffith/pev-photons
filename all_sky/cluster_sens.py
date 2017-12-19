#!/usr/bin/env python

import re, os, sys, argparse, dataFunctions
import glob
from math import ceil
import myGlobals as my
import random

if __name__ == "__main__":

    # Setup global path names
    my.setupGlobals(verbose=False)
    my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
            description='Mass runs on cluster',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--test', dest='test', action='store_true',
            default=False,
            help='Option for running test off cluster')
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

    script = "/home/zgriffith/photon_analysis/pev_photons/all_sky/sens_on_cluster.py"

    if args.test:
        cmd = 'python '+script 
    else:
        dag_name = '/data/user/zgriffith/dagman/myJobs/sens.dag'
        ex       = 'condor_submit_dag -f -maxjobs ' +args.maxjobs+' '+dag_name

        if args.rescue:
            os.system(ex)
            sys.exit()

        if args.rm_old:
            print('Deleting '+dag_name[:-3]+' files...')
            os.system('rm '+dag_name[:-3]+'*')

        dag = open(dag_name, "w+")

    dec_0 = -85
    dec_1 = -53.4

    counter = 0
    for index in [2.0,2.7]:
        for i in range(int((dec_1-dec_0)*10)):
            dec = dec_0+i/10.
            arg  = ' --dec %s' % dec
            arg += ' --index %s' % index
            if args.test:
                ex  = ' '.join([cmd, arg])
            else:
                arg = script+arg
                dag.write("JOB " + str(counter) + " /data/user/zgriffith/dagman/OneJob.submit\n")
                dag.write("VARS " + str(counter) + " ARGS=\"" + arg + "\"\n")
            counter += 1
    os.system(ex)
