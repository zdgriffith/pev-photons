#!/usr/bin/env python

########################################################################
# get the total livetime for a systematics set
########################################################################

import numpy as np

from pev_photons.utils.support import resource_dir

if __name__ == "__main__":

    table = np.loadtxt(resource_dir+'run_files/non_burn_runs_2012.txt', dtype='str')
    runs = np.loadtxt(resource_dir+'run_files/2012_systematic_run_files.txt', dtype='str')
    runs = [run.split('/')[-2][5:] for run in runs]
    print(np.sum(table.T[4][np.array([run in runs for run in table.T[0]])].astype('float')))
