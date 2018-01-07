#!/usr/bin/env python

########################################################################
# Combine HDF Files
########################################################################

import numpy as np
import argparse, sys, tables, file_functions
import time, glob
import pandas as pd

from pev_photons.support import prefix

def combine_hdfs(file_list, outFile):

    err = 0
    dataframe_dict = {}
    for i, fname in enumerate(file_list):
        print(i)
        f = {}
        try:
            store = pd.HDFStore(fname)
        except:
            print('error, skipping')
            err += 1
            continue
        f['laputop_E'] = store.select('Laputop_E').value
        store.close()

        for key in f.keys():
            if i == 0:
                dataframe_dict[key] = f[key].tolist()
            else:
                dataframe_dict[key] += f[key].tolist()

    df = pd.DataFrame.from_dict(dataframe_dict)
    df.to_hdf(outFile, 'dataframe', mode='w')

if __name__ == "__main__":

    p = argparse.ArgumentParser(
            description='Combine HDF files',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--year', default='2012', help='Analyis Year')
    args = p.parse_args()
    
    file_list = glob.glob(prefix+'datasets/quality_energies/'+args.year+'/Run*.hdf5')
    outFile = prefix+'datasets/quality_energies/'+args.year+'.hdf5'

    combine_hdfs(file_list, outFile)
