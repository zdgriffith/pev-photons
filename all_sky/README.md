# all_sky

The scripts used to produce the all-sky-scan and related results.

## Producing the all sky scan

* all_sky_scan.py
    : perform an unbinned LLH test over each point of a grid in the sky, creating a TS map
* one_dec_ts.py
    : calculate the TS for random trials at a given declination.
* cluster_dec_trials.py
    : submit one_dec_ts.py on the cluster 
* ts_to_pvalue.py
    : convert a TS map to a pre-trial p-value map using the TS ensembles produced by cluster_dec_trials.py
* plot_p_value.py
    : plot the pre-trial p-value map

## Hotspot

* get_hotspot.py
    : get hotspot from TS map and save information.
* plot_trials.py
    : plot hotspot TS and background trials TS ensemble.
* plot_hotspot_events.py
    : scatterplot of events in region around hotspot.

## Sensitivity Calculation

* sens_on_cluster.py
    : Calculate sensitivity and discovery potential for a given declination and spectral index.
* cluster_sens.py
    : Submit sens_on_cluster.py for a grid of 0.1 degrees in declination and indices 2.0 and 2.7 to the cluster.
* coarse_sens.py
    : Calculate sensitivity and discovery potential every 3 degrees.
* plot_sens.py
    : Plot sensitivity and discovery potential as a function of declination with projected HESS fluxes.

## Fitted spectral index systematics test
* spectral_index_fit_test.py
    : Functions to test the behavior of the fitted spectral index.
* plot_spectral_test.py
    : Plotting functions for output from spectra_index_fit_test.py
