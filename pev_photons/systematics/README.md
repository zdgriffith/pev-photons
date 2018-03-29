# template

The scripts used to evaluate systematic uncertainties for the analysis sensitivity

## Hadronic Interaction Models

* coarse_sens.py
    : evaluates the point source sensitivity as a function of declination
* plot_sens.py
    : plots the point source sensitivity as a function of declination
* prob_dists.py
    : plots the random forest score distributions for each interaction model
* feature_dists.py
    : plots the distributions of llh_ratio and in-ice charge for each interaction model
* template_builder.py
    : a template building implementation with manually constructed input datasets
* sensitivity_test.py, inj_trials.py, cluster_inj_trials.py, sens_fit.py
    : template sensitivity comparison (see template section)
* interaction_model_test.py
    : passing fraction comparison

## In-Ice Charge
* gamma_charge_test.py
    : compares the passing fraction for systematic variations in deposited charge

## Snow Systematics
* snow_height_sens.py
    : compares the sensitivity when using MC with snow heights from before, during, or after data year.
* lambda_check.py
    : compares S125 distributions for different values of lambda in Laputop
