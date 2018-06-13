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

Note that this requires the unique declination background trials produce in the ``all_sky`` section.  Add ``--use_original_trials`` to use the trials we generated instead.

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
