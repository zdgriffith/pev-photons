#!/bin/bash

# This script will load the environment the analysis results were produced with.
# The photon_env virtual environment has the following packages installed:
# argparse == 1.1
# basemap == 1.0.7
# numpy == 1.13.3
# scipy == 0.15.1
# matplotlib == 1.4.3
# pandas == 0.18.1
# healpy == 1.8.6
# basemap == 1.0.7 
# 
# dashi == 0.1
# skylab release version 2.2:
# (http://code.icecube.wisc.edu/svn/sandbox/skylab/skylab_stable_v2-02)

# TO USE: Run "source enter_environment.sh" 

eval `/cvmfs/icecube.opensciencegrid.org/py2-v2/setup.sh`
source /data/user/zgriffith/pev_photons/resources/photon_env/bin/activate
#source /data/user/zgriffith/pev_photons/resources/mpl_2_env/bin/activate
export PYTHONPATH=$PYTHONPATH:"$(pwd)"
