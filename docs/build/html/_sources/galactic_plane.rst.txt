.. _galactic_plane:

**************
Galactic Plane
**************

The following scripts reproduce the section of the analysis which searches for diffuse emission from the galactic plane.  All scripts are within the ``pev_photons/template`` directory.

---------------------
Template Construction
---------------------

To construct the template objects for each year of data, run:

.. code-block:: bash

    python template_builder.py --year all

This creates a structured numpy array ``{prefix}/template/{year}/fermi_pi0_exp.npy`` with all the fields required by the template method.

To plot the Fermi :math:`\pi^0` template convolved with detector acceptance (Figure 12 in the paper), execute:

.. code-block:: bash

    python plot_template_x_acc.py

.. figure:: _static/fermi_pi0_x_acc.png
   :scale: 50 %
   :alt: Fermi pi0 template convolved with detector acceptance

   **Figure 12**:  The Fermi-LAT :math:`\pi^0` decay spatial template multiplied by the detector acceptance for the data year 2012. 

-----------------
Template Analysis
-----------------

To run the likelihood test with the Fermi :math:`\pi^0` template, execute:

.. code-block:: bash

    python run_gp_analysis.py

This creates the structured numpy array ``{prefix}/template/fermi_pi0_fit_result.npy``, which includes the test statistic and :math:`n_s` values from the fit.

To produce a background trial test statistic ensemble, **on submitter**, run:

.. code-block:: bash

    python cluster_bg_trials.py

The 10,000 trials produced are stored in ``{prefix}/template/trials/fermi_pi0``.  Then the p-value can be calculated via:

.. code-block:: bash

    python p_value_calc.py

This adds the p-value to the fit results file created earlier.  To skip generating your own trials, add the ``--use-original-trials`` option.  Your result should match the following table:

.. list-table:: Fermi Template Fit Result 
   :widths: auto
   :header-rows: 1

   * - Test Statistic
     - p-value 
     - :math:`n_s` 
   * - 0.22
     - 0.276
     - 150.70
