.. _setup:

:github_url: https://github.com/zdgriffith/pev_photons

******
Set Up
******

Currently you must run these scripts on a cobalt testbed or a submitter node.

-------------------------
Accessing the Environment
-------------------------

To make it easy to reproduce the results, I have created a virtual environment which is accessible on the cobalts. The virtual environment was installed using the python from the py2-v2 CVMFS environment: ``/cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_6_x86_64/bin/python``.

Simply run

.. code-block:: bash

    source enter_environment.sh

in ``pev_photons`` to activate the environment. Alternatively, if on an EL7 machine, use:

.. code-block:: bash

    source enter_environment.sh el_7

Note this redefines your python path, leaving the environment with ``deactivate`` will reset the python path to what it was before entering the environment. This will also add ``pev_photons`` to your python path.

To following package versions are necessary:

============  =======
Package       Version     
============  =======
astropy       2.0.3
basemap       1.0.7
healpy        1.8.6
matplotlib    1.4.3
numpy         1.13.3
pandas        0.18.1
scikit-learn  0.17.1
scipy         0.15.1
skylab        2.0.2
============  =======

You can create your own virtual environment with these packages using ``exact_environment.txt`` in ``pev_photons``.  Within a freshly made virtual environment:

.. code-block:: bash

    pip install -r exact_environment.txt

If you go this route, make sure ``pev_photons`` is in your python path before proceeding.

----------------------
Setting the File Paths 
----------------------

The file ``pev_photons/utils/support.py`` has two paths that should be changed to the location you want to store the files:

1.  ``prefix`` defines the base directory where generated data files should be stored.
2.  ``fig_dir`` defines the base directory where generated plots should be stored.

Change these paths to your personal directories.  Then, run:

.. code-block:: bash

    python pev_photons/make_directories.py

This makes the directory and all the subdirectories necessary in both the plot and data file locations if they don't already exist.
