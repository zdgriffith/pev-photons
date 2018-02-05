# template

The scripts related to the template components of the gamma-ray analysis.

## Constructing the Templates

* template_builder.py
    : Build template maps for use in Skylab. (Credit: Josh Wood)
* plot_skymap.py
    : Plot the template map convolved with detector acceptance in a South Pole projection.

## Template Analysis

* run_template_analysis.py
    : produces the fitted TS and n_sources for the correlation with the given template.
* cluster_bg_trials.py (run on submitter)
    : produces scrambled background trials on the cluster.
* p_value_calc.py : calculates the p_value of the best-fit TS and saves to the fit result.

## Sensitivity Calculation

* sensitivity_test.py
    : runs a coarse sensitivity test.
* inj_trials.py
    : runs signal-injected trials and fits the TS for sensitivity calculation.
* cluster_inj_trials.py (run on submitter)
    : produces 10000 trials for each injection point in range using inj_trials.py
* sens_fit.py
    : Calculates sensitivity from trials produced by cluster_sens_trials.py
