#!/usr/bin/env python

########################################################################
# Make the subdirectories to store data files at the desired directory
########################################################################

import os

from pev_photons.support import prefix

def make_file_dirs(dir_list):
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    for directory in dir_list:
        if not os.path.exists(prefix+directory):
            os.makedirs(prefix+directory)

if __name__ == "__main__":
    dir_list = ['all_sky', 'datasets', 'event_selection',
                'galactic_plane', 'performance_checks',
                'TeVCat']

    make_file_dirs(dir_list)
