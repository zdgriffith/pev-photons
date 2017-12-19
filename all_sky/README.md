# all_sky

The scripts used to produce the all-sky-scan and related results.

## Producing the all sky scan

* all_sky_scan.py
*: perform an unbinned LLH test over each point of a grid in the sky, creating a TS map
* one_dec_ts.py
*: calculate the TS for random trials at a given declination.
* cluster_dec_trials.py
*: submit one_dec_ts.py on the cluster 
* ts_to_pvalue.py
*: convert a TS map to a pre-trial p-value map using the TS ensembles produced by cluster_dec_trials.py
* plot_p_value.py
*: plot the pre-trial p-value map
