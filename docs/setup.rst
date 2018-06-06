.. _setup:

:github_url: https://github.com/zdgriffith/pev_photons

******
Set Up
******

-------------------------
Accessing the Environment
-------------------------

To make it easy to replicate my environment, I have created and stored a virtual environment which is accessible on the cobalts. The virtual environment was installed using the python from the py2-v2 CVMFS environment: ``/cvmfs/icecube.opensciencegrid.org/py2-v2/RHEL_6_x86_64/bin/python``.

Simply run

.. code-block:: bash

    source enter_environment.sh

in pev_photons to activate the environment. Note this redefines your python path, leaving the environment with ``deactivate`` will reset the python path to what it was before entering the environment. This will also add pev_photons to your python path.
