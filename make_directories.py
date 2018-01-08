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
    
    # All second level directories
    dir_list = ['all_sky', 'datasets', 'event_selection',
                'galactic_plane', 'performance_checks',
                'TeVCat']

    sub_dirs = dict()
    sub_dirs['all_sky'] = ['dec_trials', 'sens_jobs/index_2.0',
                           'sens_jobs/index_2.7']

    sub_dirs['galactic_plane'] = ['2011', '2012', '2013', '2014', '2015',
                                  'source_templates', 'trials', 'sens_trials']

    for directory in sub_dirs.keys():
        for sub_dir in sub_dirs[directory]:
            dir_list += [directory+'/'+sub_dir]

    make_file_dirs(dir_list)
