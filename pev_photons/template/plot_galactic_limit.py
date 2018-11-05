#!/usr/bin/env python

########################################################################
# Isotropic limits compared to the best fit flux from HESE
########################################################################

import argparse
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import interpolate

from pev_photons import utils

def convert_limit(data):
    g = np.array([[1.66, 1.58, 1.63, 1.67, 1.63], np.full(5, 1.4)])
    a = np.array([[7860, 3550, 2200, 1430, 2120],
                  [20., 20., 13.4, 13.4, 13.4]])
    Z = np.array([1., 2., 7., 19.5, 26.])
    Y = np.array([4e6, 30e6])

    conversion = np.zeros(len(data))
    for j, data_j in enumerate(data):
        for i in range(2):
            conversion[j] += np.sum((a[i]*(data_j*1e3)**(-g[i]+1.)
                                    *1e-4*np.exp(-data_j*1e3/Z/Y[i])))
    return conversion

def plot_arrow(exp):
    for i, x_i in enumerate(exp['data'][0]):
        ax.plot(np.full(2, x_i),
                np.full(2, exp['data'][1][i])*[1,0.5],
                color=exp['color'], zorder=2)

    ax.scatter(exp['data'][0],exp['data'][1]*0.5,
               marker='v', color=exp['color'], s=40, zorder=2)
    ax.scatter(exp['data'][0],exp['data'][1], label=exp['label'],
               marker=exp['marker'], color=exp['color'], s=40, zorder=2)

def plot_limits(exp, key):
    if exp['convert']:
        exp['data'][1] *= convert_limit(exp['data'][0])

    if args.fermi_limit:
        exp['data'][1] *= fermi_ratio[key]

    exp['data'][1] *= 1e-3
    plot_arrow(exp)

def plot_data(exp, key):
    if args.fermi_limit:
        exp['data'][1] *= fermi_ratio[key]

    ax.errorbar(exp['data'][0], 1e-3*exp['data'][1]*(exp['data'][0]*1e3)**2,
                yerr=1e-3*exp['error']*(exp['data'][0]*1e3)**2,
                label=exp['label'], color=exp['color'],
                #marker=exp['marker'], s=40, zorder=2)
                markeredgewidth=0, capsize=0, elinewidth=2,
                lw=0, markersize=7,
                marker=exp['marker'], zorder=2)

def plot_range(exp):
    x = np.linspace(exp['E_min'], exp['E_max'], 100)
    y = exp['data'][1]*(exp['E_0']/x)**(3.0-2.0)
    ax.plot(x, y, ls='--', color=exp['color'], zorder=1)

def plot_flux_model(model):
    values = np.load(utils.resource_dir+model['name']+'.npy')

    if args.fermi_limit:
        for key in ['low', 'high']:
            values['flux_'+key] *= fermi_ratio['IC86']*1e-3

    ax.fill_between(values['energy'], values['flux_low'], values['flux_high'],
                    edgecolor=model['edgecolor'], color=model['color'],
                    alpha=model['alpha'], zorder=model['zorder'])
    p = plt.Rectangle((0, 0), 0, 0,
                      edgecolor=model['edgecolor'], facecolor=model['color'],
                      label=model['label'])
    ax.add_patch(p)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
            description='galactic plane limit',
            formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--fermi_limit', action='store_true', default=False,
                   help='If True, convert to angular integrated limit.')
    args = p.parse_args()

    plt.style.use(utils.plot_style)

    colors = plt.rcParams['axes.color_cycle']
    fig, ax = plt.subplots()
    ax.tick_params(axis='both', which='major', pad=10, labelsize=23)

    fermi_ratio = np.load(utils.resource_dir+'fermi_ratio_dict.npz')

    exp = {}
    exp['CASA-MIA'] = {'data':np.array([[140, 180, 310, 650, 1300],
                                        [3.4e-5 ,2.6e-5, 2.4e-5, 2.6e-5, 3.5e-5]]),
                      #'color':colors[1], 'marker':'D',
                      'color': 'magenta', 'marker': 'D',
                      'convert': True, 'label': 'CASA-MIA'}
    exp['IC40'] = {'data':np.array([[3e3], [1.2e-3]]),
                   #'color':'cyan', 'marker':'H',
                   'color': colors[1], 'marker': 'H',
                   'convert': True, 'label': 'IC-40 (1 year)'}
    exp['ARGO-YBJ'] = {'data':np.array([[0.390, 0.750, 1.640],
                                        [8.06e-12, 1.64e-12, 0.13e-12]]),
                      'error':np.array([1.49e-12, 0.43e-12, 0.05e-12]),
                      'color': 'green', 'marker': 'o',
                      'convert': False, 'label': 'ARGO-YBJ'}

    if args.fermi_limit:
        value = 1.044e-09
    else:
        value = 4.20419751853e-09 #((3.42e-22)*(2*10**6)**2)/(0.2*np.pi)

    exp['IC86'] = {'data':np.array([[2e3], [value]]),
                   #'color':colors[0], 'marker':'p',
                   'color':colors[0], 'marker':'p',
                   'E_0':2e3, 'E_min':0.683e3, 'E_max': 2.73e3,
                   'convert': False, 'label':'IC-86 (5 years)'}

    for key in exp:
        if not args.fermi_limit:
            exp[key]['label'] += ' ($|$b$|$ $<$ 5$^{\circ}$)'

        if key in ['ARGO-YBJ']:
            plot_data(exp[key], key)
        else:
            plot_limits(exp[key], key)

    plot_range(exp['IC86'])

    # Model prediction for flux emission over our entire FOV
    models = {}
    models['v_l_unatt'] = {'name':'vernetto_unattenuated',
                           'color':'none', 'edgecolor':'black', 'alpha':1.0,
                           'label':'Vernetto 2017 (Unatt.)',
                           'zorder':-1}
    models['v_l_att'] = {'name':'vernetto_attenuated',
                         'color':'lightgrey', 'edgecolor':'none', 'alpha':1.0,
                         'label':'Vernetto 2017 (Att.)',
                         'zorder':-2}
    for model in models:
        plot_flux_model(models[model])

    ax.set_xlim([0.1, 5e4])
    ax.set_ylim([1e-12, 5e-9])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'E$_\gamma$ [TeV]', fontsize=25)
    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), borderaxespad=0, ncol=3,
               frameon=True, loc='lower left', mode='expand', handletextpad=0.4)

    if args.fermi_limit:
        ax.set_ylabel(r'E$^2\Phi_{\large\textrm{template}}$ [cm${}^{-2}$s${}^{-1}$TeV]', fontsize=25)
        plt.savefig(utils.fig_dir+'template/fermi_integrated_limit.png')
        #plt.savefig(utils.fig_dir+'paper/fermi_integrated_limit.pdf', bbox_inches='tight')
        plt.savefig(utils.fig_dir+'paper/fermi_integrated_limit.eps', bbox_inches='tight')
    else:
        ax.set_ylabel(r'$E^2J_\gamma$ [cm$^{-2}$s$^{-1}$sr$^{-1}$TeV]')
        plt.savefig(utils.fig_dir+'template/per_str_limit.pdf')
    plt.close()
