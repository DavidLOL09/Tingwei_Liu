import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from NuRadioReco.modules.io import NuRadioRecoio
import NuRadioReco.modules.templateDirectionFitter
import os
from NuRadioReco.utilities import units
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco
from NuRadioReco.framework.parameters import channelParameters as chp
templateDirectionFitter = NuRadioReco.modules.templateDirectionFitter.templateDirectionFitter()
templateDirectionFitter.begin()
from NuRadioReco.detector import detector 
json_file_origin=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json'
det=detector.Detector(json_filename=json_file_origin)
from scipy.stats import binned_statistic_2d
import scipy
import pandas as pd
def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir

def hist_check(statistic_result,abins,rbins,weights):

    nx = len(abins) - 1
    ny = len(rbins) - 1
    binnumber = statistic_result.binnumber
    ic(len(binnumber),len(weights))
    ic(np.size(statistic_result.binnumber),scipy.stats.mode(statistic_result.binnumber,keepdims = True))

    weights_std_matrix = statistic_result.statistic
    ic("--- Standard Deviation of Weights Inside Each Bin ---")
    ic(np.round(weights_std_matrix*1000000, 3))  
    ic(abins,rbins)
    # 3. 构建一个大 List 矩阵，用来存放每个网格的对象
    # 初始化一个 nx * ny 的空列表矩阵
    grid_objects = [[[] for _ in range(ny)] for _ in range(nx)]

    # 4. 核心：遍历每一个原始对象，根据 binnumber 将其塞进对应的网格 List 中
    # ⚠️ 注意：SciPy 的 binnumber 是展平的一维索引，且包含了边缘溢出区间，需要做如下转换：
    for idx, bin_idx in enumerate(binnumber):
        # 将一维的 bin_idx 还原为网格的 (i, j) 坐标
        # 减 1 是因为 SciPy 把小于最小值的数据放在了 index=0
        i = (bin_idx // (ny + 2)) - 1
        j = (bin_idx % (ny + 2)) - 1
        
        # 排除掉超出你定义的网格范围之外的“溢出点”
        if 0 <= i < nx and 0 <= j < ny:
            grid_objects[i][j].append(weights[idx])
    # ic(f'check1{np.sum(weights)}')
    uniqueness = np.array([])
    for i in range(0,len(grid_objects)):
        zen = grid_objects[i]
        for j in range(0,len(zen)):
            # print(np.mean(zen[j]),end=' ')
            ic(i,j)
            if i==6 and j == 5:
                ic(len(zen[j]))
                ic(np.mean(zen[j]), np.max(zen[j]),np.min(zen[j]), np.std(zen[j]),np.sum(zen[j]))
                fig,ax = plt.subplots(1,1,figsize = (8,5))
                ax.hist(zen[j])
                # plt.show()
            ic(len(np.unique(zen[j])))
            uniqueness = np.concatenate((uniqueness,zen[j]))
            ic('---------------------')
        print()
    ic(len(uniqueness))
    ic(len(grid_objects),len(grid_objects[0]))
    unique = np.unique(uniqueness)
    ic(len(unique))


def plot_with_weights(azimuth_list,zenith_list,weights,ax):
    weights = np.array(weights)
    weights_mask = weights >= 0
    sin2Val = np.linspace(0,(np.sin(np.deg2rad(85)))**2 , 7)   #Bin edges evenly spaces in sin^2(angle) in radians
    sin2Val = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,(np.sin(np.deg2rad(85)))**2]
    # else:
    #     sin2Val = np.linspace(0,1,11)
    rbins = np.rad2deg(np.arcsin(np.sqrt(sin2Val)))
    ic(rbins)
    abins = np.linspace(0, 2*np.pi, 13)
    hist, _, _ = np.histogram2d(azimuth_list, np.rad2deg(zenith_list), bins=(abins, rbins), weights=weights[weights_mask])
    ic(hist)
    statistic_result = binned_statistic_2d(
        azimuth_list, np.rad2deg(zenith_list), 
        values=weights, 
        statistic='std', 
        bins=[abins, rbins]
    )
    hist_check(statistic_result,abins,rbins,weights)
    A, R = np.meshgrid(abins, rbins)
    pm=ax.pcolormesh(A, R, hist.T, norm=matplotlib.colors.LogNorm(), zorder=0)
    ax.figure.colorbar(pm,ax=ax)


# def get_weights(ax:plt.axes,readARIANNAData:NuRadioReco.modules.io):
def get_weights(input_path,ax:plt.axes):
    direct=[]
    weights=[]
    # for evt in readARIANNAData.get_events():
    #     stn=evt.get_station(51)
    #     # zen = stn.get_parameter(stnp.zenith)/units.rad
    #     # azi = stn.get_parameter(stnp.azimuth)/units.rad
    #     sim_stn = stn.get_sim_station()
    #     zen = sim_stn[NuRadioReco.framework.parameters.stationParameters.zenith]/units.rad
    #     azi = sim_stn[NuRadioReco.framework.parameters.stationParameters.azimuth]/units.rad
    #     direct.append([zen,azi])
    #     weights.append(evt.get_parameter(evtp.event_rate))

    zen,azi,weights = excel_reader(input_path,if_weights=True)
    zen = np.deg2rad(zen)
    # for i,iz in enumerate(zen):
    #     direct.append([zen[i],azi[i]])
    direct  = np.array(direct)
    weights = np.array(weights)
    weights = weights/np.sum(weights)
    # zen = direct[:,0]
    # azi = direct[:,1]
    # ic(zen[6],azi[6])
    # ic(np.sum(weights))
    plot_with_weights(azi,zen,weights,ax)

def annotate_scatter(ax,x,y,labels):
    for xi, yi, txt in zip(x, y, labels):
        ax.annotate(
            txt,                 # text to draw
            xy=(xi, yi),         # point to annotate
            xytext=(5, 5),       # (dx, dy) offset in points
            textcoords='offset points',
            fontsize=40, weight='bold',
            ha='left', va='bottom'
        )

import ToolsPac
from icecream import ic
def direction_plot_detect(ax:plt.axes,name:str,readARIANNAData:NuRadioReco.modules.io,zorder,color='r',alfa=1):
    direct=[]
    Iden=[]
    pass_Ratio=[]
    for evt in readARIANNAData.get_events():
        stn = evt.get_station(51)
        # zen = stn.get_parameter(stnp.zenith)/units.deg
        # azi = stn.get_parameter(stnp.azimuth)/units.rad
        sim_stn = stn.get_sim_station()
        zen = sim_stn[NuRadioReco.framework.parameters.stationParameters.zenith]/units.deg
        azi = sim_stn[NuRadioReco.framework.parameters.stationParameters.azimuth]/units.rad
        pass_Ratio.append(zen)
        # if zen>89:
        #     continue
        # if zen<=5:
        #     for chn_id in [4,5,6]:
        #         chn=stn.get_channel(chn_id)
        #         Xmax=chn[chp.cr_xcorrelations]['cr_ref_xcorr_time']
        #         # if Xmax!=0:
        #         #     chn[chp.cr_xcorrelations]['cr_ref_xcorr_time']
        #         ic(Xmax)
        #     # ic(ToolsPac.get_id_info(evt))
        #     time=stn.get_station_time().datetime
        #     det.update(time)
        #     templateDirectionFitter.run(evt,stn,det,channels_to_use=[4,5,6], cosmic_ray=True)
        #     ic(zen)
        #     exit()
        Iden.append(f'R{evt.get_run_number()}E{evt.get_id()}')
        direct.append([zen,azi])
    # ax.set_title('Direct')
    ax.set_rlim(0,85)
    direct=np.array(direct)
    zen=direct[:,0]
    azi=direct[:,1]
    # if len(zen)<10000:
    #     al=0.5
    # else:
    #     al=0.1
    # annotate_scatter(ax,azi,zen,Iden)
    ax.scatter(azi,zen,s=40,alpha=alfa,zorder=zorder,color=color)
    # ax.legend(fontsize=20)

def excel_reader(input_file,upper_lim=85,lower_lim=0,if_weights=False):
    df = pd.read_excel(input_file)
    zen = np.array(df['zen'])
    azi = np.array(df['azi'])
    result_z = []
    result_a = []
    for iz,z in enumerate(zen):
        if z>upper_lim or z<lower_lim:
            continue
        result_z.append(z)
        result_a.append(azi[iz])

    if if_weights:
        weights = np.array(df['weights'])
        result_w = []
        for iz,z in enumerate(zen):
            if z>upper_lim or z<lower_lim:
                continue
            result_w.append(weights[iz])
        return result_z,result_a,result_w
    else:
        return result_z,result_a

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
sim='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/new_phase_algorithm'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_cluster'
# candi = '/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/zen_test'
# candi='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/direct_New_Temp/Trig'
# raw_goso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw'
# raw_ngoso='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
# raw='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate'
# direct_Scattering(Xcorr,'X',sig,'X_335sig',Ratio,'X_335sig_Ratio',Zen,'X_335sig_Ratio_Zen',
#                X_sim,sig_sim,Ratio_sim,Zen_sim)
# direct_Scattering(candiR12,'candiR12',candiR10,'candiR10',candiR8,'candiR8',candiR6,'candiR6',
#                sim_Zen,sim_Zen,sim_Zen,sim_Zen)
fig,ax = plt.subplots(1,1,figsize=(8,8),layout='constrained',subplot_kw={'projection': 'polar'})
# Reader_candi = NuRadioRecoio.NuRadioRecoio(get_input(candi))
# direction_plot_detect(ax,'Trig',Reader_candi,2,color='red',alfa=1)

# Reader_raw=NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(candi))
# direction_plot_detect(ax,'Trig',Reader_raw,1,color='red')

# sim_Reader = NuRadioRecoio.NuRadioRecoio(get_input(sim))
# get_weights(ax,sim_Reader)

get_weights('/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify/sim_direct.xlsx',ax)

ax.tick_params(axis='x', labelsize=20)
# ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.set_rlabel_position(165)  

# plt.savefig('/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Direction_NewDirect.png')
plt.show()






        
    

