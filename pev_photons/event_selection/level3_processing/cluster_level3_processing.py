#!/usr/bin/env python 
import argparse
import os
import sys
import re
import glob

from pev_photons.utils.support import prefix

def getL2GCD(config):
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

    p = argparse.ArgumentParser(description='Level3 processing of simulation files.',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--dataset', help='Simulation dataset to run over')
    p.add_argument('--year', help='Detector year.')
    p.add_argument('--n', type=int, default=800,
                   help='Number of files to run per batch')
    p.add_argument('--test', action='store_true', default=False,
                   help='Option for running test off cluster')
    p.add_argument('--maxjobs', default='1200',
                   help='max jobs running on cluster')
    p.add_argument('--rm_old', action='store_true', default=False,
                   help='Remove old dag files?')
    args = p.parse_args()

    if args.test:
        args.n = 2 
    else:
        dag_name = prefix+'dagman/'+args.dataset+'_level3_processing.dag'
        ex = 'condor_submit_dag -f -maxjobs '+args.maxjobs+' '+dag_name

        if args.rm_old:
            print('Deleting '+dag_name[:-4]+' files...')
            os.system('rm '+dag_name[:-4]+'*')
        dag = open(dag_name, "w+")

    script = os.path.join(os.getcwd(), 'level3_processing.py')

    # Get config and simulation files
    config = 'IC86.' + args.year
    L2_GCD = getL2GCD(config)
    L3_GCD = '/data/user/zgriffith/Level3/GCDs/IT_'+args.year+'_GCD.i3.gz' 
    files = glob.glob('/data/sim/IceTop/2012/filtered/CORSIKA-ice-top/%s/level2/*/L*' % args.dataset)
    print(len(files))
    
    outDir = prefix+'datasets/level3/%s/' % args.dataset

    # Split into batches
    batches = [files[i:i+args.n] for i in range(0, len(files), args.n)]

    print(len(batches))
    SnowFactor = {'IC79': 2.1, 'IC86.2011':2.25,
                  'IC86.2012':2.25, 'IC86.2013':2.3,
                  'IC86.2014':2.3, 'IC86.2015':2.3}

    for k, batch in enumerate(batches):

        # Name outfile
        start = re.split('\.', batch[0])[-3][-6:]
        end   = re.split('\.', batch[-1])[-3][-6:]
        out = '%s/%s' % (outDir, args.dataset)
        out += '_part%s-%s.i3.gz' % (start, end)

        #print out

        batch = ' '.join(batch)
        arg  = '%s ' % batch
        arg += '--isMC --dataset %s ' % args.dataset 
        arg += '--det %s ' % config
        arg += '--snow-lambda %s ' % SnowFactor[config]
        arg += '--L2-gcdfile %s --L3-gcdfile %s ' % (L2_GCD, L3_GCD)
        arg += '--waveforms '
        arg += '--do-inice ' #Get InIce Pulses
        arg += '-o %s ' % out #Outfile name

        if args.test:
            cmd = 'python '+script
            ex  = ' '.join([cmd, arg])
            if k == 5:
                break
        else:
            arg  = script+' '+arg
            dag.write("JOB " + str(k) + " /data/user/zgriffith/dagman/new_icerec.submit\n")
            dag.write("VARS " + str(k) + " ARGS=\"" + arg + "\"\n")

    os.system(ex)
