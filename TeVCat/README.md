# TeVCat

Scripts for analysis of TeVCat (HESS) sources with the 5-year gamma-ray dataset

cluster_submit.py:  Submit a dagman to the cluster for stacking background trials.
cutoff_calculator.py:  For each HESS source, calculate the minimum cut-off energy matching a sensitivity
gamma_ray_survival.py:  Plots the survival function(s) for gamma rays 
hess_sensitivities.py:  Calculates the sensitivity to each HESS source's declination and spectral index 
individual_ts.py:  Calculates the true TS for each HESS source
map_w_srcs.py:  plots simple crosses on top of zoomed in skymap with basemap
plot_hessJ1427.py:  plots the SED of HESS J1427-608 and IceCube's 5-year upper limit
plot_HESS_region.py:  plots a rectangular region of the sky centered on the galactic plane using healpix, with sources marked with dots and lines to labels of the sources.
plot_stacking_trials.py:  plots the background trial TS distribution
sensitivity.py:  Plots the sensitivity and discovery potential as a function of declination, with HESS source fluxes extrapolated
stacking_test.py:  runs the likelihood test of the HESS sources as a stacked catalog
