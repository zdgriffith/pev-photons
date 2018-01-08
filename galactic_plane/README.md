# galactic_plane

The scripts related to the galactic plane component of the gamma-ray analysis.

## Constructing the Templates

* template_builder.py
    : Build template maps for use in Skylab. (Credit: Josh Wood)
* plot_skymap.py
    : Plot the template map convolved with detector acceptance in a South Pole projection.

## Template Analysis

* run_gp_analysis.py
    : produces the fitted TS and n_sources for the correlation with the given template.
* cluster_bg_trials.py (run on submitter)
    : produces scrambled background trials on the cluster.
* plot_trials.py : plots the background trial ensemble compared to result, yields p-value.

## Sensitivity Calculation

* sensitivity_test.py
    : runs a coarse sensitivity test.
* cluster_sens_trials.py
    : produces 10000 trials for each injection point in range.
* sens_fit.py
    Calculates sensitivity from trials produced by cluster_sens_trials.py
