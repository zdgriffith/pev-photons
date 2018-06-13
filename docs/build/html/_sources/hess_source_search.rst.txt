.. _hess_source_search:

************************
H.E.S.S. Source Searches
************************

Gamma-ray point sources observed by `H.E.S.S. <https://www.mpi-hd.mpg.de/hfm/HESS/>`_ at TeV energies are candidate targets for this analysis.  The scripts used to test for correlation with these sources are within the ``pev_photons/TeVCat`` directory.

-----------------------
Individual Source Tests
-----------------------

To fit each H.E.S.S. source location indiviually, run:

.. code-block:: bash

    python individual_ts.py

This produces the file ``{prefix}/TeVCat/hess_sources_fit_results.npy``, which stores the TS, :math:`n_s`, and :math:`\gamma` for each source location.  Convert these test statistics to pre-trial p-values with:

.. code-block:: bash

    python hess_ts_to_pvalue.py

Note that this requires the unique declination background trials produce in the ``all_sky`` section.  Add ``--use_original_trials`` to use the trials we generated instead.  Finally, to calculate the sensitivity to each H.E.S.S. source at 1 PeV, given an unbroken power law with the best fit spectral index from H.E.S.S. data, run:

.. code-block:: bash

    python hess_sensitivities.py --ncpu *desired_ncpu*

Combining the information from this section should give you results consistent with the following table:

.. list-table:: Individual H.E.S.S. Source Fit Results
   :widths: auto
   :header-rows: 1

   * - Source
     - :math:`\delta` [:math:`^{\circ}`]
     - :math:`\alpha` [:math:`^{\circ}`]
     - pre-trial p-value 
     - :math:`n_s` 
     - :math:`\gamma`
     - Sens. at 1 PeV (x :math:`10^{-20}`)
   * - HESS J1356-645
     - 209.00
     - -64.50
     - ...
     - 0.0
     - ...
     - 3.72
   * - HESS J1507-622
     - 226.72
     - -62.35
     - 0.29
     - 2.5
     - 1.3
     - 4.75
   * - SNR G292.2-00.5
     - 169.75
     - -61.40
     - 0.30
     - 10.0
     - 4.0
     - 8.97
   * - Kookaburra (Rabbit)
     - 214.52
     - -60.98
     - 0.31
     - 3.7
     - 1.8
     - 4.96
   * - HESS J1458-608
     - 224.54
     - -60.87
     - 0.22
     - 9.1
     - 2.4
     - 1.88
   * - HESS J1427-608
     - 216.97
     - -60.85
     - 0.07
     - 25.9
     - 3.2
     - 12.10
   * - Kookaburra (PWN)
     - 215.04
     - -60.76
     - 0.49
     - 1.8
     - 2.2
     - 4.31

-------------
Stacking Test
-------------

Run the stacked likelihood test for all H.E.S.S. source combined by executing:

.. code-block:: bash

    python all_sky_scan.py --ncpu *desired_ncpu*

The results are stored in ``{prefix}/TeVCat/stacking_fit_result.npy``.  It should match the following table:

.. list-table:: H.E.S.S. Catalog Stacking Result
   :widths: auto
   :header-rows: 1

   * - Test Statistic
     - p-value 
     - :math:`n_s` 
     - :math:`\gamma`
   * - 1.74
     - 0.08
     - 65.23
     - 3.66
