# all_sky

The scripts used to produce the all-sky-scan and related results.

## Producing the all sky scan

* all_sky_scan.py
    : perform an unbinned LLH test over each point of a grid in the sky, creating a TS map.
* dec_list.py
    : create an array of unique declination values for a given Nside.
* one_dec_ts.py
    : calculate the TS for random trials at a given declination.
* cluster_dec_trials.py
    : submit one_dec_ts.py on the cluster.
* ts_to_p_value.py
    : convert a TS map to a pre-trial p-value map using the TS ensembles produced by cluster_dec_trials.py.
* plot_p_value.py
    : plot the pre-trial p-value map.
* cluster_all_sky_trials.py
    : submit all-sky trial jobs to the cluster.

## Hotspot

* get_hotspot.py
    : get hotspot from TS map and save information.
* plot_trials.py
    : plot hotspot TS and background trials TS ensemble.

## Sensitivity Calculation

* sens_on_cluster.py
    : Calculate sensitivity and discovery potential for a given declination and spectral index.
* cluster_sens.py
    : Submit sens_on_cluster.py for a grid of 0.1 degrees in declination and indices 2.0 and 2.7 to the cluster.
* coarse_sens.py
    : Calculate sensitivity and discovery potential every 3 degrees.
* plot_sens.py
    : Plot sensitivity and discovery potential as a function of declination with projected HESS fluxes.

* test_hese_track.py
    : Test for an excess at the location of the HESE track.
