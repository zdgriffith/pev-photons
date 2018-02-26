#!/usr/bin/env python

import re, os, sys, argparse, glob
from getGoodRuns import fileCleaner

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Run on my i3 files, write to hdf5',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', dest='year', default = '2012',
            help='Year to run over')
    p.add_argument('--dag', dest='dag',
            help='dag file')
    p.add_argument('-n', '--n', dest='n', type=int, default=200,
            help='Number of files to run per batch')
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

    # Default parameters            
    outDir   = '/data/user/zgriffith/pev_photons/datasets/quality_energies/'+args.year
    gcdFiles = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*_GCD.i3.gz' % args.year)

    dag_name    = '/data/user/zgriffith/dagman/myJobs/quality_E_%s.dag' % args.year
    goodRunList = '/data/user/zgriffith/pev_photons/run_files/non_burn_runs_%s.txt' % args.year

    if args.year == '2011':
        file_list   = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/IC86.%s/*/*/*/*.i3.bz2' % args.year)
    else:
        file_list   = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*.i3.bz2' % args.year)

    file_list.sort()
    files = fileCleaner(goodRunList, file_list)

    if args.test:
        args.n = 200 
    else:
        ex       = 'condor_submit_dag -f -maxjobs ' +args.maxjobs+' '+dag_name
        if args.rescue:
            os.system(ex)
            sys.exit()

        if args.rm_old:
            print('Deleting '+dag_name[:-4]+' files...')
            os.system('rm '+dag_name[:-4]+'*')
        dag = open(dag_name, "w+")

    # Split into batches
    batches = {}
    for file in files:
        run = re.split('\_', os.path.basename(file))[3]
        if run in batches:
            new_batch = 0
            for i in range(len(batches[run])):
                if len(batches[run][i]) < args.n:
                    batches[run][i].append(file)
                    new_batch += 1
            if new_batch == 0:
                batches[run].append([file])
        else:
            batches[run] = [[file]]

    print(sum([len(batches[i]) for i in batches.keys()]))
    script = "/home/zgriffith/pev_photons/event_selection/quality_energies.py"

    count = 0
    for k, key in enumerate(batches.keys()):

        for j, batch in enumerate(batches[key]):
            count += 1
        
            #batch = batch_num[j]
            run   = re.split('\_', os.path.basename(batch[0]))[3]
            gcd   = [gcdFile for gcdFile in gcdFiles if run in gcdFile][0]
            out  = '%s/' % outDir
            out += '%s_%s' % (run,j)

            out += '.hdf5'
            #print out
            if args.test:
                batch = ' '.join(batch)
            else:
                batch = ' '.join(batch)

            arg  = '%s -g %s ' % (batch, gcd)
            arg += '-o %s ' % out

            if args.test:
                cmd = 'python '+script
                ex  = ' '.join([cmd, arg])
                break
            else:
                arg  = script+ ' '+arg
                dag.write("JOB " + str(count) + " /data/user/zgriffith/dagman/new_icerec.submit\n")
                dag.write("VARS " + str(count) + " ARGS=\"" + arg + "\"\n")

    os.system(ex)
