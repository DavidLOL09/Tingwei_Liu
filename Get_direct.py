import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from NuRadioReco.modules.io import NuRadioRecoio
import os
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco


def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
def plot_with_weights(azimuth_list,zenith_list,weights,ax):
    weights = np.array(weights)
    weights_mask = weights >= 0
    sin2Val = np.linspace(0,(np.sin(np.deg2rad(85)))**2 , 11)   #Bin edges evenly spaces in sin^2(angle) in radians
    # else:
    #     sin2Val = np.linspace(0,1,11)
    rbins = np.rad2deg(np.arcsin(np.sqrt(sin2Val)))
    abins = np.linspace(0, 2*np.pi, 61)
    hist, _, _ = np.histogram2d(azimuth_list, np.rad2deg(zenith_list), bins=(abins, rbins), weights=weights[weights_mask])
    A, R = np.meshgrid(abins, rbins)
    pm=ax.pcolormesh(A, R, hist.T, norm=matplotlib.colors.LogNorm(), zorder=0)
    ax.figure.colorbar(pm,ax=ax)


def get_weights(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io):
    direct=[]
    weights=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.rad
        azi = stn.get_parameter(stnp.azimuth)/units.rad
        direct.append([zen,azi])
        weights.append(evt.get_parameter(evtp.event_rate))
    direct  = np.array(direct)
    weights = np.array(weights)*31/365
    zen = direct[:,0]
    azi = direct[:,1]
    plot_with_weights(azi,zen,weights,ax)

def annotate_scatter(ax,x,y,labels):
    for xi, yi, txt in zip(x, y, labels):
        ax.annotate(
            txt,                 # text to draw
            xy=(xi, yi),         # point to annotate
            xytext=(5, 5),       # (dx, dy) offset in points
            textcoords='offset points',
            fontsize=9, weight='bold',
            ha='left', va='bottom'
        )


def direction_plot_detect(ax:plt.axes,name:str,readARIANNAData:NuRadioReco.modules.io,zorder,color='r',alfa=1):
    direct=[]
    Iden=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.deg
        azi = stn.get_parameter(stnp.azimuth)/units.rad
        Iden.append(f'R{evt.get_run_number()}E{evt.get_id()}')
        direct.append([zen,azi])
    # ax.set_title('Direct')
    ax.set_rlim(0,90)
    direct=np.array(direct)
    zen=direct[:,0]
    azi=direct[:,1]
    # if len(zen)<10000:
    #     al=0.5
    # else:
    #     al=0.1
    # annotate_scatter(ax,azi,zen,Iden)
    ax.scatter(azi,zen,s=20,alpha=alfa,zorder=zorder,color=color)
    ax.legend()


def direction_plot_sim_scatter(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io):
    direct=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        sim_stn = stn.get_sim_station()
        sim_zen = sim_stn[NuRadioReco.framework.parameters.stationParameters.zenith]/units.deg
        sim_azi = sim_stn[NuRadioReco.framework.parameters.stationParameters.azimuth]/units.rad
        direct.append([sim_zen,sim_azi])
    # ax.set_title(name)
    ax.set_rlim(0,90)
    direct=np.array(direct)
    zen=direct[:,0]
    azi=direct[:,1]
    if len(zen)<10000:
        al=0.5
    else:
        al=0.1
    ax.scatter(azi,zen,c='r',s=5,alpha=al,label=len(zen))
    ax.legend()

def direct_Scattering(path1,name1,
                   path2,name2,
                   path3,name3,
                   path4,name4,
                   sim1,sim2,sim3,sim4):
    fig,Axes = plt.subplots(2,2,figsize=(10,8),layout='constrained',subplot_kw={'projection': 'polar'})
    # Axes= fig.subplots(2,2,sharey=True)
    ax1 = Axes[0][0]
    ax2 = Axes[0][1]
    ax3 = Axes[1][0]
    ax4 = Axes[1][1]
    direction_plot_detect(path1,name1,ax1)
    direction_plot_detect(path2,name2,ax2)
    direction_plot_detect(path3,name3,ax3)
    direction_plot_detect(path4,name4,ax4)

    # direction_plot_sim_scatter(sim1,name1,ax1)
    # direction_plot_sim_scatter(sim2,name2,ax2)
    # direction_plot_sim_scatter(sim3,name3,ax3)
    # direction_plot_sim_scatter(sim4,name4,ax4)




    get_weights(sim1,name1,ax1)
    get_weights(sim2,name2,ax2)
    get_weights(sim3,name3,ax3)
    get_weights(sim4,name4,ax4)

    fig.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/plots/direction.png')
    plt.show()

# sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_bef_cut'
sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Trig_Freqs_X_SNR_with_direct'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output_Trig/Final_Candi'
# raw_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
# raw_ngoso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
raw='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
# direct_Scattering(Xcorr,'X',sig,'X_335sig',Ratio,'X_335sig_Ratio',Zen,'X_335sig_Ratio_Zen',
#                X_sim,sig_sim,Ratio_sim,Zen_sim)
# direct_Scattering(candiR12,'candiR12',candiR10,'candiR10',candiR8,'candiR8',candiR6,'candiR6',
#                sim_Zen,sim_Zen,sim_Zen,sim_Zen)
fig,ax = plt.subplots(1,1,figsize=(10,8),layout='constrained',subplot_kw={'projection': 'polar'})
Reader_candi = NuRadioRecoio.NuRadioRecoio(get_input(candi))
direction_plot_detect(ax,'Trig_Freqs_X_SNR_Zen',Reader_candi,2,color='red',alfa=1)

# Reader_raw=NuRadioRecoio.NuRadioRecoio(get_input(raw))
# direction_plot_detect(ax,'Trig',Reader_raw,1,color='grey',alfa=0.4)

sim_Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim))
get_weights(ax,sim_Reader)

ax.tick_params(axis='x', labelsize=20)
# ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.set_rlabel_position(165)  

plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Direction_32')
plt.show()






        
    



