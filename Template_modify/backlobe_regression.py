import sys
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation')
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
import pandas as pd
import polynomial_regression
poly_reger = polynomial_regression.polynomial_regression()
from NuRadioReco.modules.channelLengthAdjuster import channelLengthAdjuster
import numpy as np
from NuRadioReco.framework.parameters import showerParameters as shp
from NuRadioReco.utilities import units
from NuRadioReco.modules.channelStopFilter import channelStopFilter
channelStopFilter=channelStopFilter()
from NuRadioReco.framework.parameters import eventParameters as evtp
import NuRadioReco.utilities.fft as fft
import NuRadioReco.modules.channelBandPassFilter
import pandas as pd
channelBandPassFilter = NuRadioReco.modules.channelBandPassFilter.channelBandPassFilter()
import matplotlib
import datetime
import send2trash
import os
from FFT_cut import flatVolt_remove
# import plot_waveform
from pathlib import Path
savename = 'Tingwei_Stn51'
trigger_name = 'direct_LPDA_3of3_3.5sigma'
save_channels = [4, 5, 6]
station_id = 51
import matplotlib.pyplot as plt
import NuRadioReco.modules.channelResampler
import NuRadioReco.modules.channelStopFilter
channelStopFilter = NuRadioReco.modules.channelStopFilter.channelStopFilter()
channelResampler = NuRadioReco.modules.channelResampler.channelResampler()
channelResampler.begin()
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import astropy
from NuRadioReco.detector import detector
det = detector.Detector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation/station51_InfAir.json', assume_inf=False, antenna_by_depth=False)
det.update(astropy.time.Time('2018-1-1'))
channels_to_use=[4,5,6]
import ToolsPac

Vrms=(9.71+9.66+8.94)/3
input_det_nobacklobe    = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze/analyze_candi'
input_det_1backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze1/analyze_candi'
input_det_2backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze2/analyze_candi'
input_det_4backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze4/analyze_candi'


input_sim_nobacklobe    = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze/sim/Trig_335_Freqs_X_SNR'
input_sim_1backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze1/sim/Trig_335_Freqs_X_SNR'
input_sim_2backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_SNR'
input_sim_4backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze4/sim/Trig_335_Freqs_X_SNR'

input_sim = input_sim_2backlobe
input_det = input_det_2backlobe

# input_det = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'

# sim_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_sim))
# det_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det))

def get_plot_info_sim(reader:NuRadioReco.modules.io, if_weights = False):
    SNR_dic = []
    X_dic   = []
    weights = []
    for evt in reader.get_events():
        stn = evt.get_station(51)
        trace_up    = []
        for channel in stn.iter_channels(use_channels=[0,1,2,3,4,5,6,7]):
            trace_up.append(np.max(np.abs(channel.get_trace()/units.mV)))
        Xcorr=[] 
        for chn in [4,5,6]:  
            channel = stn.get_channel(chn)
            Xcorr.append(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])
        X_dic.append(np.max(Xcorr))
        SNR_dic.append(max(trace_up)/Vrms)
        if if_weights:
            weights.append(evt.get_parameter(evtp.event_rate))
    if if_weights:
        weights = np.array(weights)*(datetime.timedelta(days=31, seconds=8844)/datetime.timedelta(days=365))
        SNR_dic = np.array(SNR_dic)
        X_dic   = np.array(X_dic)
        return SNR_dic,X_dic,weights   
    else:
        SNR_dic = np.array(SNR_dic)
        X_dic   = np.array(X_dic) 
        return SNR_dic,X_dic 
    
def save_into_xlsx(SNR,Chi,filename,weights=np.array([])):
    if len(weights) == 0:
        data = {
            'SNR': SNR,
            'Chi': Chi
        }
    else:
        data = {
            'SNR': SNR,
            'Chi': Chi,
            'weights': weights
        }
    df = pd.DataFrame(data)
    df.to_excel(os.path.join('/Users/david/PycharmProjects/Demo1/Research/Repository',f'{filename}.xlsx'),index=False)

def excel_reader(input_file,if_weights=False):
    df = pd.read_excel(input_file)
    SNR = np.array(df['SNR'])
    Chi = np.array(df['Chi'])
    if if_weights:
        weights = np.array(df['weights'])
        return SNR,Chi,weights
    else:
        return SNR,Chi
    
def sim_plots(ax:plt.axes,SNR:np.array,chi:np.array,weights:np.array):
    SNR_bins = np.logspace(np.log10(np.min(SNR)), np.log10(np.max(SNR)), 101)
    X_bins=np.linspace(0,1,101)
    ax.set_xlim(3,900)
    ax.set_ylim(0.2,1)
    hist,_,_=np.histogram2d(SNR,chi,bins=(SNR_bins,X_bins),weights=weights)
    S,X=np.meshgrid(SNR_bins,X_bins)
    pm=ax.pcolormesh(S,X,hist.T,norm=matplotlib.colors.LogNorm(),zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    ax.set_xlabel(f'SNR',fontsize=40)
    ax.set_ylabel(fr'$\chi$',fontsize=40)

def Logeqs(k,b,x):
    return k*np.log10(x)+b
def SNR_cut_line(ax):
    x=np.linspace(1,1000,1001)
    # 2 backlope
    y1=np.full_like(x[x<6.566],0.46)

    x2=x[(x>6.566)&(x<8.32)]
    y2=Logeqs(k=0.86557,b=-0.24743,x=x2)

    x3=x[(x>8.32)&(x<8.822)]
    y3=Logeqs(k=0.62884,b=-0.02961,x=x3)

    x4=x[(x>8.822)&(x<11.306)]
    y4=Logeqs(k=1.37365,b=-0.73388,x=x4)
    
    x5=x[(x>11.306)&(x<14.541)]
    y5=Logeqs(k=0.48497,b=0.20218,x=x5)

    y6=np.full_like(x[x>14.541],0.766)
    y=np.concatenate((y1,y2,y3,y4,y5,y6))

    ax.plot(x,y,color='black',linestyle='--',zorder=3)

def SNR_cut(snr,chi):
    mask = []
    # 2 backlope
    for i in range(len(snr)):
        y = 0
        x = snr[i]
        if x<6.566:
            y = 0.46
        elif x>6.566 and x<8.32:
            y = Logeqs(k=0.86557,b=-0.24743,x=x)
        elif x>8.32 and x<8.822:
            y = Logeqs(k=0.62884,b=-0.02961,x=x)
        elif x>8.822 and x<11.306:
            y = Logeqs(k=1.37365,b=-0.73388,x=x)
        elif x>11.306 and x<14.541:
            y = Logeqs(k=0.48497,b=0.20218,x=x)
        else:
            y = 0.766
        mask.append(chi[i]>y)
    mask = np.array(mask)
    snr = snr*mask
    chi = chi*mask
    return snr[snr>0],chi[chi>0],mask


def func(k_lst,x_bin):
    # k_lst=[0,1,2,3]
    y = np.zeros_like(x_bin)
    for ik,k in enumerate(k_lst):
        ic(ik)
        y+= k*(x_bin**ik)
    return y

def zoom_x(x_lst:np.array):
    min = np.log10(np.min(x_lst))
    max = np.log10(np.max(x_lst))
    x_zoom = np.logspace(min,max,1000)
    return x_zoom

def get_distance(point1:np.array,point2:np.array):
    diff_vec = point1-point2
    return np.sqrt(np.dot(diff_vec,diff_vec))

def get_closest_dis(line:np.array,point_lst:np.array,index_output = False):
    min_lst = []
    index_lst = []
    for ie,ep in enumerate(point_lst):
        min = 10000
        index = 0
        for il,lp in enumerate(line):
            distance = get_distance(ep,lp)
            if distance<min:
                min = distance
                index = il
        min_lst.append(min)
        index_lst.append(index)
    min_lst = np.array(min_lst)
    index_lst = np.array(index_lst)
    if index_output:
        return min_lst,index_lst
    else:
        return min_lst



# SNR_dic,X_dic = get_plot_info_sim(det_reader)
# save_into_xlsx(SNR_dic,X_dic,'det_2backlobe_info')



# SNR_dic,X_dic,weights = get_plot_info_sim(sim_reader,if_weights=True)
# save_into_xlsx(SNR_dic,X_dic,'sim_2backlobe_info',weights)
backl_fact = 0
excel_sim = f'/Users/david/PycharmProjects/Demo1/Research/Repository/sim_{backl_fact}backlobe_info.xlsx'
excel_det = f'/Users/david/PycharmProjects/Demo1/Research/Repository/det_{backl_fact}backlobe_info.xlsx'
det_SNR,det_Chi = excel_reader(excel_det)
sim_SNR,sim_Chi,weights = excel_reader(excel_sim,if_weights=True)



# fig,ax = plt.subplots(figsize=(10,8))
# x_bins = np.linspace(0,0.5,1000)
# ax.hist(weights,x_bins)
# plt.show()
# exit()



x_list = np.log10(sim_SNR)
# ic(x_list)
y_list = sim_Chi
# ic(y_list)
# poly_reger = polynomial_regression.polynomial_regression()
# poly_reger.begin([0,1,2,3],x_list,y_list,regression='polynomial',demo_size=100,y_weights = weights*1000,zoom=True,descent='Normal',learningR=0.11)
# coeff,err,iteration,training_x = poly_reger.run()

backlobe_4 = np.array([ 0.51292512,  1.56144298, -0.88074515, -0.88302168])
backlobe_2 = np.array([ 0.55932826,  1.57243922, -0.82038923, -0.79672034])
backlobe_1 = np.array([ 0.57333255,  1.52189362, -0.77125602, -0.76775629])
backlobe_0 = np.array([ 0.57040368,  1.55095131, -0.78921136, -0.7895467 ])

if backl_fact == 0:
    coeff = backlobe_0
elif backl_fact == 1:
    coeff = backlobe_1
elif backl_fact == 2:
    coeff = backlobe_2
elif backl_fact == 4:
    coeff = backlobe_4






# ic(err)
# ic(iteration)
# coeff = np.array([ 0.6594515 ,  0.97801051, -0.3809382 , -0.59058307])
# x_bin = np.logspace(0.1,3,100)
x_bin = zoom_x(sim_SNR)

# y_exp = func(coeff,training_x[:,1])
y_exp = func(coeff,np.log10(np.logspace(0,1,1000)))
ic(coeff)
for isnr,snr in enumerate(x_bin):
    if abs(snr-26)<=1:
        ic(isnr,snr)
        y_exp[isnr:]=y_exp[isnr]
        break

line_points = np.column_stack((np.log10(x_bin), y_exp))
det_points  = np.column_stack((np.log10(det_SNR),det_Chi))
min_lst,index_lst = get_closest_dis(line_points,det_points,True)
line_points = line_points[index_lst]


fig,ax = plt.subplots(figsize=(10,8),layout='constrained')
sim_plots(ax,sim_SNR,sim_Chi,weights)
ax.set_xlim(3,1000)
# ax.set_ylim(0.2,1)
SNR_cut_line(ax)
pass_snr,pass_chi,passed_mask = SNR_cut(det_SNR,det_Chi)


ax.scatter(det_SNR,det_Chi,color='r',label=f'evt:{len(det_Chi)}\nstd:{np.mean(min_lst):5f}',alpha=0.5)

# ax.scatter(det_SNR,det_Chi,color='r',alpha=0.5)

ic(f'sample_size:{len(det_Chi)} \naverage Variance:{np.mean(min_lst):.8f} passed:{np.sum(passed_mask)}')
ax.plot(x_bin,y_exp,color='r')
ax.grid()
ax.set_ylim(0,1)
ax.set_xscale('log')
ax.tick_params(axis='x', labelsize=40)
ax.tick_params(axis='y', labelsize=40)

# for ip,point_det in enumerate(det_points):
#     point_exp = line_points[ip]
#     ax.plot([10**point_det[0],10**point_exp[0]],[point_det[1],point_exp[1]])


# plt.legend(fontsize=25)
plt.savefig(os.path.join('/Users/david/Desktop',f'{backl_fact}backlobe_regression.png'))
plt.show()
# ic(coeff)

# 4backlobe: coeff: np.array([ 0.51292512,  1.56144298, -0.88074515, -0.88302168])
# 2backlobe: coeff: np.array([ 0.55932826,  1.57243922, -0.82038923, -0.79672034])
# 1backlobe: coeff: np.array([ 0.57333255,  1.52189362, -0.77125602, -0.76775629])
# nobacklobe: coeff: np.array([ 0.57040368,  1.55095131, -0.78921136, -0.7895467 ])




