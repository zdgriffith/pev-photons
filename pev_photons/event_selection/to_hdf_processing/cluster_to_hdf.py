#!/usr/bin/env python 
import argparse
import os
import sys
import re
import glob
from datetime import datetime
startTime = datetime.now()

from pev_photons.utils.support import prefix, resource_dir, dag_dir

def fileCleaner(runFile, fileList, reverse = False):

    f = open(runFile, 'r')
    lines = f.readlines()
    goodRunList = []

    for line in lines:

        # Lines with run info need at least 6 parts
        line_info = line.split()
        try:
            test = int(line_info[0])
        except ValueError:
            continue
        # Make sure run is good
        if int(line_info[2]) == 1:
            run  = '00'+line_info[0]
            goodRunList.append(run)
    f.close()
    goodRunList.sort()
    cleanList = []
    for file in fileList:
        run_st = file.find('Run') + 3
        run = file[run_st:run_st+8]
        if reverse:
            if run not in goodRunList:
                cleanList.append(file)
        else:
            if run in goodRunList:
                cleanList.append(file)

    return cleanList


def write_job(script, batches, gcd_file, year,
              out_dir, out_name, dag_name,
              isMC=False, test=False, systematics=False, job=0):
    """Submit a dag file for Monte Carlo.

    Parameters
    ----------
    script : string
        Script which performs event processing.
    batches : array-like, shape = [batch_length, n_batches]
        Batches of event files, each corresponding
        to a job on the cluster.
    gcd_file : string
        The GCD file corresponding to the event files.
    out_dir : string
        The directory where the output files are written.
    out_name : name
        Name of the output file.
    isMC : boolean
        Flag for Monte Carlo simulation.
    test : boolean
        Flag for testing on Cobalt before submitting
        to the cluster.
    systematics : boolean
        Flag for running systematic processing on the events.

    """
    for i, batch in enumerate(batches):
        out = '{}/{}_{}.hdf5'.format(out_dir, out_name, i)
        arg = '{}'.format(' '.join(batch))
        arg += ' -g {} --year {} -o {}'.format(gcd_file, year, out)

        if isMC:
            arg += ' --isMC'
        if systematics:
            arg += ' --systematics'

        if test:
            cmd = 'python '+script
            ex  = ' '.join([cmd, arg])
            os.system(ex)
            sys.exit(str(datetime.now() - startTime))
            break
        else:
            arg = script+' '+arg
            dag.write('JOB {} {}/icerec.submit\n'.format(job, resource_dir))
            dag.write('VARS {} ARGS=\"{}\"\n'.format(job, arg))
            dag.write('VARS {} log_dir=\"{}/logs/{}\"\n'.format(job, dag_dir, dag_name))
            dag.write('VARS {} out_dir=\"{}/dagman/{}\"\n'.format(job, prefix, dag_name))
            job += 1
    return job


def get_data_batches(files, batch_length):
    """Construct batches for each run of data.
    
    Parameters
    ----------
    files : array-like, shape = [n_files]
        File containing events, where n_files
        is the number of files in the year.
    batch_length : int
        The number of files run over in one batch.

    Returns
    -------
    run_batches : dict of string -> array-like
        Batches grouped by run number.

    """
    run_batches = {}
    for fname in files:
        run = re.split('\_', os.path.basename(fname))[3]
        if run in run_batches:
            new_batch = 0
            for i in range(len(run_batches[run])):
                if len(run_batches[run][i]) < batch_length:
                    run_batches[run][i].append(fname)
                    new_batch += 1
            if new_batch == 0:
                run_batches[run].append([fname])
        else:
            run_batches[run] = [[fname]]
    return run_batches


def get_data_files(year):
    if year == '2011':
        file_list = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/IC86.%s/*/*/*/*.i3.bz2' % year)
    else:
        file_list = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*.i3.bz2' % year)
    file_list.sort()

    goodRunList = prefix+'run_files/burn_runs_%s.txt' % year
    return fileCleaner(goodRunList, file_list)


if __name__ == "__main__":

    p = argparse.ArgumentParser(description='analysis level processing of files',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', help='Detector year.')
    p.add_argument('--MC_dataset', default=None,
                   help='If simulation, the dataset to run over.')
    p.add_argument('--n', type=int, default=4,
                   help='Number of files to run per batch')
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', default='1200',
                   help='max jobs running on cluster')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    p.add_argument('--systematics', action='store_true', default=False,
                   help='Process with systematic reconstructions?')
    args = p.parse_args()

    script = os.path.join(os.getcwd(), 'to_hdf_processing.py')
    isMC = args.MC_dataset is not None

    if args.test:
        args.n = 2
        dag_name = ''
    else:
        if isMC:
            dag_name = args.MC_dataset+'_to_hdf'
        else:
            dag_name = args.year+'_to_hdf'

        if args.rm_old:
            print('Deleting '+dag_name+' files...')
            os.system('rm '+os.path.join(dag_dir, dag_name)+'*')

        dag_file = os.path.join(dag_dir, dag_name+'.dag')
        dag = open(dag_file, "w+")

    job = 0
    if isMC:
        if args.MC_dataset in ['12622', '12533', '12612', '12613', '12614']:
            files = glob.glob('/data/user/zgriffith/Level3/IT81_sim/%s/*.i3.gz' % args.MC_dataset)
            gcd_file = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
        elif args.MC_dataset in ['12360']:
            path = '/data/ana/CosmicRay/IceTop_level3/sim/IC86.2012/'
            files = glob.glob(os.path.join(path, '{}/*.i3.gz'.format(args.MC_dataset)))
            gcd_file = os.path.join(path, 'GCD/Level3_{}_GCD.i3.gz'.format(args.dataset))
        else:
            files = glob.glob(prefix+'datasets/level3/%s/*.i3.gz' % args.MC_dataset)
            gcd_file = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
        batches = [files[i:i+args.n] for i in range(0, len(files), args.n)]
        if args.systematics:
            out_dir = prefix+'datasets/systematics/%s/' % args.MC_dataset
        else:
            out_dir = prefix+'datasets/%s/' % args.MC_dataset
        write_job(script, batches, gcd_file, args.year, out_dir,
                  out_name=args.MC_dataset, dag_name=dag_name,
                  isMC=isMC, test=args.test, systematics=args.systematics)
    else:
        files = get_data_files(args.year)
        run_batches = get_data_batches(files, args.n)
        gcd_files = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*_GCD.i3.gz' % args.year)
        if args.systematics:
            out_dir = prefix+'/datasets/systematics/data/'+args.year
        else:
            out_dir = prefix+'/datasets/data/'+args.year
        for i, (run, batches) in enumerate(run_batches.iteritems()):
            gcd_file = [gcd for gcd in gcd_files if run in gcd][0]
            job = write_job(script, batches, gcd_file, args.year, out_dir,
                            out_name=run, dag_name=dag_name, test=args.test,
                            systematics=args.systematics, job=job)

    if not args.test:
        ex = 'condor_submit_dag -f -maxjobs {} {}'.format(args.maxjobs, dag_file)
        os.system(ex)
