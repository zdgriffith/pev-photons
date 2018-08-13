
# coding: utf-8

# In[70]:


#load libraries
import numpy as np
get_ipython().magic(u'matplotlib inline')
from matplotlib import pyplot as plt
import cPickle as pkl
from matplotlib.colors import LogNorm
import tables,os
from matplotlib.ticker import MultipleLocator


# In[2]:


def load_pkl(tfile):
    f=open(tfile)
    h1=pkl.load(f)
    n1=pkl.load(f)
    h2=pkl.load(f)
    n2=pkl.load(f)
    xe=pkl.load(f)
    ye=pkl.load(f)
    f.close()
    return h1,h2,n1,n2,xe,ye


# In[3]:


#path on cobalt: 
#picklefile : /data/user/hpandya/gamma_combined_scripts/resources/
#h5file: /data/user/zgriffith/Level3/new_processing/IC86.2012_data/
root_path = '../../../ApJ_heatmaps/'
tfile=root_path+'12533_2012GammaSim_BurnSample_2012.pickle'
h5file=root_path+'Run00121841_0.hdf5'


# In[4]:


h={}
N={}
h['cr'],h['gamma'],N['cr'],N['gamma'],xe,ye=load_pkl(tfile)


# In[89]:


templates=h['gamma'].keys()
ebins=h['gamma'][templates[0]].keys()
zenbins=h['gamma'][templates[0]][ebins[0]].keys()

print ebins
print ''
print zenbins
template='q_r'
ebin = ebins[9]
zenbin = zenbins[2]
print ebin, zenbin

xlabels={}
xlabels['q_r']='Log(Tank Charge/ VEM)'
ylabels={}
ylabels['q_r']='Log(Lateral Distance/ m)'

vmax=1.25e-3
vmin=1e-6
#cmap='coolwarm'
cmap='Spectral_r'
#cmap='nipy_spectral'


# In[90]:


def plot_2d_hist(hist,xedges,yedges,
                xlim,ylim,
                xlabel='',ylabel='',title='',cmap='coolwarm',
                vmin=1e-1,vmax=1e-5,same_plot=False,alpha=1.0):

    hist=hist.T
    hist=np.ma.masked_where(hist==0,hist)
    #label='nentries: %i'%np.sum(hist)

    if not same_plot:
        plt.figure()#dpi=320)
    plt.pcolormesh(xedges,yedges,hist,alpha=alpha,
                   cmap=cmap,norm=LogNorm(vmin=vmin,vmax=vmax))
    #cbar=plt.colorbar()
    #plt.scatter([2.0],[2],color=None,s=0,label=label)
    #plt.legend()
    plt.xlim(xlim)
    plt.ylim(ylim)
    #plt.xlabel(xlabel)
    #plt.ylabel(ylabel)
    #plt.title(title)
    return plt


# In[7]:


def get_events(s125_low=0.3,
               s125_high=0.4,
               zen_low=0.85,
               zen_high=0.9,
               h5file='../../../ApJ_heatmaps/Run00121841_0.hdf5'):

    g=tables.open_file(h5file)

    slc_charge=np.log10(g.root.IceTopLaputopSeededSelectedSLC.cols.charge[:])
    slc_time=np.log10(g.root.IceTopLaputopSeededSelectedSLC.cols.time[:])
    slc_x=g.root.IceTopLaputopSeededSelectedSLC.cols.x[:]
    slc_y=g.root.IceTopLaputopSeededSelectedSLC.cols.y[:]
    slc_r = np.log10(np.sqrt( slc_x**2.0 + slc_y**2.0 ))
    slc_start=g.root.__I3Index__.IceTopLaputopSeededSelectedSLC.cols.start[:]
    slc_stop=g.root.__I3Index__.IceTopLaputopSeededSelectedSLC.cols.stop[:]

    hlc_charge=np.log10(g.root.IceTopHLCSeedRTPulses_Laputop.cols.charge[:])
    hlc_time=np.log10(g.root.IceTopHLCSeedRTPulses_Laputop.cols.time[:])
    hlc_x=g.root.IceTopHLCSeedRTPulses_Laputop.cols.x[:]
    hlc_y=g.root.IceTopHLCSeedRTPulses_Laputop.cols.y[:]
    hlc_r = np.log10(np.sqrt( hlc_x**2.0 + hlc_y**2.0 ))
    hlc_start=g.root.__I3Index__.IceTopHLCSeedRTPulses_Laputop.cols.start[:]
    hlc_stop=g.root.__I3Index__.IceTopHLCSeedRTPulses_Laputop.cols.stop[:]

    logs125=np.log10(g.root.LaputopParams.cols.s125[:])
    coszen=np.cos(g.root.Laputop.cols.zenith[:])
    run = g.root.I3EventHeader.cols.Run[:]
    eventid=g.root.I3EventHeader.cols.Event[:]

    t_=[]
    q_=[]
    r_=[]
    eventid_=[]
    run_=[]
    logs125_=[]
    coszen_=[]
    
    for i in range(len(logs125)):
        if logs125[i]<s125_low or logs125[i]>=s125_high:
            continue
        if coszen[i]<zen_low or coszen[i]>=zen_high:
            continue

        ht=hlc_time[hlc_start[i]:hlc_stop[i]]
        hq=hlc_charge[hlc_start[i]:hlc_stop[i]]
        hr=hlc_r[hlc_start[i]:hlc_stop[i]]

        st=slc_time[slc_start[i]:slc_stop[i]]
        sq=slc_charge[slc_start[i]:slc_stop[i]]
        sr=slc_r[slc_start[i]:slc_stop[i]]

        t=np.concatenate((ht,st))
        r=np.concatenate((hr,sr))
        q=np.concatenate((hq,sq))
        t_.append(t)
        r_.append(r)
        q_.append(q)
        logs125_.append(logs125[i])
        coszen_.append(coszen[i])
        run_.append(run[i])
        eventid_.append(eventid[i])
        
    return q_,t_,r_,run_,eventid_,logs125_,coszen_


# In[8]:


def get_scatter(eventno,q,t,r,run,eventid,logs125,coszen):
    xvar=eval(template[-1])
    xvar=xvar[eventno]
    yvar=eval(template[0])
    yvar=yvar[eventno]
    event,xedges,yedges=np.histogram2d(xvar,yvar,bins=[xe[template],ye[template]])

    xcenters=(xedges[:-1]+xedges[1:])/2.0
    ycenters=(yedges[:-1]+yedges[1:])/2.0

    xscatter=[]
    yscatter=[]
    zscatter=[]
    for r,row in enumerate(event):
        for c,element in enumerate(row):
            if element!=0:
                xscatter.append(xcenters[r])
                yscatter.append(ycenters[c])
                zscatter.append(element)
    xscatter=np.array(xscatter)
    yscatter=np.array(yscatter)
    zscatter=np.array(zscatter)

    return xscatter,yscatter,zscatter,eventid[eventno],run[eventno],logs125[eventno],coszen[eventno]


# In[88]:


#make plots
q,t,r,rung,eventidg,logs125g,coszeng=get_events(s125_low = float(ebin)-0.1, 
                 s125_high = float(ebin),
                 zen_low = float(zenbin)-0.05,
                 zen_high = float(zenbin),
                 h5file=h5file)
#for cmap in ['PiYG','PRGn','coolwarm','coolwarm_r','Spectral_r',
#             'Spectral','nipy_spectral','PRGn','PiYG',
#            'jet','PiYG_r','PRGn_r','viridis','viridis_r',
#             'plasma','inferno','inferno_r','plasma_r','YlGnBu','YlGnBu_r']:
for cmap in ['coolwarm']:
    for eventno in [12]:
        xscatter,yscatter,zscatter,eventid,run,logs125,coszen=get_scatter(eventno,q,t,r,
                                                                          rung,eventidg,logs125g,coszeng)
        for prim in ['cr','gamma']:
            print cmap
            plt.figure(figsize=(16,10))
            plot_2d_hist(hist= h[prim][template][ebin][zenbin]/ np.sum(h[prim][template][ebin][zenbin]), 
                         xedges= xe[template],
                         yedges= ye[template],
                         xlim = [xe[template][0],xe[template][-1]],
                         ylim = [ye[template][0],ye[template][-1]],
                         xlabel=xlabels[template],
                         ylabel=ylabels[template],
                         title=prim+ebin+zenbin,
                         cmap=cmap,
                         same_plot=True,
                         vmin=vmin,
                         vmax=vmax)
            cbar=plt.colorbar()
            cbar.ax.tick_params(labelsize=20,length=6)
            cbar.set_label('Probability',fontsize=22)

            plt.scatter(xscatter,yscatter,
                        s=zscatter*50,marker='s',
                        facecolor='none',edgecolor='k',
                        lw=1.,alpha=0.65,
                        label='Sample CR Event')
            
            boxheight=0.2
            plt.plot([2.2,3.2],[boxheight,boxheight],ls='--',color='k',alpha=0.65,lw=1.)
            plt.plot([2.2,3.2],[-1.*boxheight,-1.0*boxheight],ls='--',color='k',alpha=0.65,lw=1.)
            plt.plot([2.2,2.2],[-1.*boxheight,boxheight],ls='--',color='k',alpha=0.65,lw=1.)
            plt.plot([3.2,3.2],[-1.*boxheight,boxheight],ls='--',color='k',alpha=0.65,lw=1.)
            
            plt.xlabel(xlabels[template],fontsize=24)
            plt.ylabel(ylabels[template],fontsize=24)
            plt.legend(fontsize=20)
            plt.axes().yaxis.set_minor_locator(MultipleLocator(0.1))
            plt.axes().xaxis.set_minor_locator(MultipleLocator(0.1))
            
            plt.tick_params(axis='both', which='minor', length=5)
            plt.tick_params(axis='both', which='major', labelsize=20,length=10)
            #ax=plt.gca()
            #ax.set_facecolor('gainsboro')
            tag='../../../plots/LLHR_%s_%s_S125'%(os.path.basename(tfile).replace('.','_'),template)
            plt.savefig(tag+'_%s_Zen_%s_Run_%i_Event_%i_%s_%i_%s.png'%(ebin,zenbin,run,eventid,prim,eventno,cmap),
                        bbox_inches='tight',dpi=180)
            plt.close()

