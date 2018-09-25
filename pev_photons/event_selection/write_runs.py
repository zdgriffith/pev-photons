#!/usr/bin/env python
import argparse
import os
import glob
import json
import re
import numpy as np

from pev_photons import utils

def clean_files(runFile, fileList):
    """Remove runs marked as bad from the file list."""

    goodRunList = []
    with open(runFile, 'r') as f:
        for line in f.readlines():
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

    goodRunList.sort()
    cleanList = []
    for fname in fileList:
        run_st = fname.find('Run') + 3
        run = fname[run_st:run_st+8]
        if run in goodRunList:
            cleanList.append(fname)
    return cleanList

def get_data_files(year, burn_sample=False):
    """Return a list of run files for the given year."""

    if year == '2011':
        file_list = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/IC86.%s/*/*/*/*.i3.bz2' % year)
    else:
        file_list = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*.i3.bz2' % year)
    file_list.sort()

    if burn_sample:
        return clean_files(utils.prefix+'/resources/run_files/burn_runs_%s.txt' % year,
                           file_list)
    else:
        return clean_files(utils.prefix+'/resources/run_files/non_burn_runs_%s.txt' % year,
                           file_list)

def get_gcd_files(year, run_files):
    """Return a list of gcd files for the given year."""
    gcd_files = glob.glob('/data/ana/CosmicRay/IceTop_level3/exp/test_data/IC86.%s/*/*/*/*_GCD.i3.gz' % args.year)
    gcd_dict = {}
    for fname in run_files:
        if fname in gcd_dict.keys():
            continue
        run = re.split('\_', os.path.basename(fname))[3]
        gcd_dict[run] = [gcd for gcd in gcd_files if run in gcd][0]
    return gcd_dict

if __name__ == "__main__":

    p = argparse.ArgumentParser(description='Write a list of run and GCD files.',
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', help='Detector year.')
    p.add_argument('--burn_sample', action='store_true', default=False,
                   help='Burn sample runs?')
    args = p.parse_args()

    run_files = get_data_files(args.year, burn_sample=args.burn_sample)
    if args.burn_sample:
        np.savetxt(utils.prefix+'resources/run_files/{}_burn_run_files.txt'.format(args.year),
                   run_files, fmt='%s')
    else:
        np.savetxt(utils.prefix+'resources/run_files/{}_good_run_files.txt'.format(args.year),
                   run_files, fmt='%s')

    gcd_dict = get_gcd_files(args.year, run_files)

    if args.burn_sample:
        gcd_name = utils.prefix+'resources/run_files/{}_burn_gcd_files.json'.format(args.year)
    else:
        gcd_name = utils.prefix+'resources/run_files/{}_gcd_files.json'.format(args.year)
    with open(gcd_name, 'w') as f:
        json.dump(gcd_dict, f)
