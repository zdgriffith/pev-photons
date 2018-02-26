#!/usr/bin/env python

########################################################################
# Make the subdirectories to store data files at the desired directory
########################################################################

import os

from pev_photons.utils.support import prefix, fig_dir

def make_file_dirs():
    # All second level directories
    dir_list = ['all_sky', 'datasets', 'event_selection',
                'template', 'performance_checks',
                'TeVCat', 'HESE', 'dagman']

    sub_dirs = dict()
    sub_dirs['all_sky'] = ['dec_trials', 'sens_jobs/index_2.0',
                           'sens_jobs/index_2.7', 'all_sky_trials']

    sub_dirs['template'] = ['2011', '2012', '2013', '2014', '2015',
                            'source_templates', 'trials', 'sens_trials']

    sub_dirs['HESE'] = ['2011', '2012', '2013', '2014', '2015',
                        'source_templates', 'trials', 'sens_trials']

    sub_dirs['dagman'] = ['logs']

    for directory in sub_dirs.keys():
        for sub_dir in sub_dirs[directory]:
            dir_list += [directory+'/'+sub_dir]

    if not os.path.exists(prefix):
        os.makedirs(prefix)

    for directory in dir_list:
        if not os.path.exists(prefix+directory):
            os.makedirs(prefix+directory)

def make_fig_dirs():
    # All second level directories
    dir_list = ['all_sky', 'event_selection',
                'template', 'performance_checks',
                'TeVCat', 'HESE', 'paper']

    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir)

    for directory in dir_list:
        if not os.path.exists(fig_dir+directory):
            os.makedirs(fig_dir+directory)
    

if __name__ == "__main__":
    if (    prefix == '/data/user/zgriffith/pev_photons/'
        or fig_dir == '/home/zgriffith/public_html/pev_photons/'
       ):
        raise Exception('You need to change the storage directories in support.py first!')

    make_file_dirs() 
    make_fig_dirs()
