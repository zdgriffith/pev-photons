import socket

from .cluster_support import DagMaker
from .support import prefix, dag_dir, resource_dir

if 'submit' not in socket.gethostname():
    from .skymap import PolarSkyMap
    from .load_datasets import load_dataset, load_systematic_dataset
    from .support import fig_dir, plot_style, plot_setter, ps_map, plasma_map
    from .gamma_ray_survival import apply_absorption
