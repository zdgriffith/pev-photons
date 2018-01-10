# TeVCat

Scripts for analysis of TeVCat (HESS) sources with the 5-year gamma-ray dataset

## Individual Source Tests

* individual_ts.py
    : calculates the true TS for each HESS source
* hess_ts_to_pvalue.py
    : converts HESS TS values to p-values using bg trials at the declination of the source
* hess_sensitivities.py
    : calculates the sensitivity to each HESS source's declination and spectral index 

## All sky scan map in HESS source region

* plot_HESS_region.py
    : plots a rectangular region of the sky centered on the galactic plane using healpix, with sources marked with dots and lines to labels of the sources.

## HESS catalog stacking test

* stacking_test.py
    : stacked likelihood test for all H.E.S.S. sources considered. This saves the best fit TS, n_sources, and spectral index.
* cluster_stacking_trials.py
    : run background trials for the stacking test on the cluster.
* plot_stacking_trials.py
    : plots the background trial TS distribution

## HESS J1427-608

* plot_hessJ1427.py
    : plots the SED of HESS J1427-608 and IceCube's 5-year upper limit

# Miscellaneous

* gamma_ray_survival.py
    : Plots the survival function(s) for gamma rays 
