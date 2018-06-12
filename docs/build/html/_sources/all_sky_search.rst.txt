.. _all_sky_search:

**************
All-Sky Search
**************

The following scripts reproduce the section of the analysis which searches the entire sky for point sources of gamma rays.  All scripts are within the ``pev_photons/all_sky`` directory.

------------
All-Sky Scan
------------

The first step is to scan the entire sky for point sources:

.. code-block:: bash

    python all_sky_scan.py --ncpu *desired_ncpu*

This produces the file ``{prefix}/all_sky/skymap.npy``, which is a healpy map of the test statistic for a point source at each pixel in the field of view.

To convert from test statistics to p-values, it is necessary to know the test statistic distribution for a ensemble of background trials at each declination.  For a healpix map of n_side=512, the all-sky scan has 342 unique declination values over the analysis field of view.  On the cluster, we evaluated 100,000 trials for each declination in the scan.  To do this yourself, **on submitter**, excecute the following:

.. code-block:: bash

   python cluster_dec_trials.py

This will store the results in ``{prefix}/all_sky/dec_trials``.  A healpy map of pre-trial p-values can be constructed with:

.. code-block:: bash

   python ts_to_p_value.py

You can skip creating the background trials yourself by adding the ``--use_original_trials`` argument.

Finally, to plot the all-sky scan in a South Polar projection (figure 8 in the paper), run:

.. code-block:: bash

   python plot_p_value.py


.. figure:: _static/all_sky_scan.png
   :scale: 50 %
   :alt: all sky scan

   All-sky likelihood scan pre-trial p-values shown projected from the south pole in equatorial units.  The right ascension is labeled along the figure axes, with the interior text denoting declination bands.  The green circle highlights the hottest spot in the scan.  The Galactic plane region (:math:`<` 5 :math:`^{\circ}` in Galactic latitude) is also shown.

-------
Hotspot
-------

To find the hottest spot in your all-sky scan, run:

.. code-block:: bash

   python get_hotspot.py

which stores the direction and fit information in ``{prefix}/all_sky/hotspot.npy``. The output should match:

Plot the result compared to a distribution of hottest spot test statistics from background all-sky-scan trials using:

.. code-block:: bash

   python plot_trials.py

This produces the following plot:


.. figure:: _static/all_sky_trials.png
   :scale: 50 %
   :alt: all sky trials 

   The highest test statistic found in the all-sky scan compared to the ensemble of hottest spot test statistics for background (right-ascension scrambled) trials.

