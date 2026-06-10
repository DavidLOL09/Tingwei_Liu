import sys
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/')
sys.path.append('/Users/david/PycharmProjects/Demo1/Research/Repository/Simulation')
from NuRadioReco.modules.io import NuRadioRecoio
from icecream import ic
import pandas as pd
from collections import Counter
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
from scipy.signal import lombscargle
Vrms=(9.71+9.66+8.94)/3

input_det_nobacklobe    = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze/analyze_candi'
input_det_1backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze1/analyze_candi'
input_det_2backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze2/analyze_candi'
input_det_4backlobe     = '/Users/david/PycharmProjects/Demo1/Research/Repository/candidate_events/analyze4/analyze_candi'
input_det_candi         =   '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_SNR'

def Logeqs(k,b,x):
    return k*np.log10(x)+b
def SNR_cut(SNR,Xcorr):
    # 2 backlope
    x=SNR
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

    return Xcorr>y

def check_repeat(reader1,reader2):
    lst1 = []
    lst2 = []
    mask = []
    for evt in reader1.get_events():
        id = f'R{evt.get_run_number()}E{evt.get_id()}'
        lst1.append(id)
    for evt in reader2.get_events():
        id = f'R{evt.get_run_number()}E{evt.get_id()}'
        mask.append(id in lst1)
    return sum(mask)

def get_plot_info_sim(reader:NuRadioReco.modules.io, if_weights = False):
    SNR_dic = []
    X_dic   = []
    weights = []
    id = []
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
        id.append(f'R{evt.get_run_number()}E{evt.get_id()}')
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
        return SNR_dic,X_dic,id
    
# def period_check(time:np.array,unit,period):
#     time = np.round(time/unit)
#     counts = Counter(time)

#     # 2. Determine the range (from 1 to the maximum number in the array)
#     max_val = max(time)

#     # 3. Build the lists using list comprehensions
#     x = np.array(range(1, max_val + 1))
#     repeats = [counts[i] for i in x]
#     repeats = np.array(repeats)
#     repeats -= np.mean(repeats)
    
#     exp_y = np.cos(2 * np.pi * x / period)

#     # cross_correlation

#     for t in time:

        



def period_find(time:np.array):
    time = np.sort(time)
    y = np.ones(len(time))
    y -= np.mean(y)
    span = (time[-1]-time[0])
    # min_gap = 10
    f_min = 1.0 / span                  # ~0.0096 Hz for your data
    f_max = 60*f_min        # can't resolve periods shorter than 2x smallest gap
    n_freqs = 100
    freqs   = np.linspace(f_min, f_max, n_freqs)
    omegas  = 2 * np.pi * freqs
    power = lombscargle(time, y, omegas, normalize=True)
    ic(power)
    best_idx = np.argmax(power)
    best_f   = freqs[best_idx]
    best_T   = 1.0 / best_f
    fig, axes = plt.subplots(2, 1, figsize=(10, 7))

    # top: frequency domain
    axes[0].plot(freqs, power, color='steelblue', linewidth=1.2)
    axes[0].axvline(best_f, color='orange', linewidth=1.5, linestyle='--', label=f'peak f={best_f:.4f} Hz  (T={best_T:.1f}s)')
    axes[0].set_xlabel('Frequency (Hz)')
    axes[0].set_ylabel('Power (normalized)')
    axes[0].set_title('Lomb-Scargle Frequency Spectrum')
    axes[0].legend()
    axes[0].set_xlim(f_min, f_max)

    # bottom: period domain (same data, x-axis flipped to 1/f)
    # avoid 1/0 by skipping f=0
    T_axis = 1.0 / freqs
    axes[1].plot(T_axis, power, color='seagreen', linewidth=1.2)
    axes[1].axvline(best_T, color='orange', linewidth=1.5, linestyle='--', label=f'peak T={best_T:.1f}s')
    axes[1].set_xlabel('Period (seconds)')
    axes[1].set_ylabel('Power (normalized)')
    axes[1].set_title('Same spectrum — period domain view')
    axes[1].set_xlim(1.0 / f_max, 1.0 / f_min)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig('ls_spectrum.png', dpi=150)
    plt.show()

def weights_test(readARIANNAData:NuRadioReco.modules.io,det_directs):
    direct=[]
    weights=[]
    for evt in readARIANNAData.get_events():
        stn=evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.rad
        azi = stn.get_parameter(stnp.azimuth)/units.rad
        direct.append([zen,azi])
        weights.append(evt.get_parameter(evtp.event_rate))
    direct  = np.array(direct)
    weights = np.array(weights)
    zen = direct[:,0]
    azi = direct[:,1]
    plot_with_weights(azi,zen,weights,det_directs)

def get_even_zen_bin(start,stop,step):
    # start:deg
    # stop: deg
    s_min = 2 * np.pi * (1-np.cos(np.deg2rad(start)))
    s_max = 2 * np.pi * (1-np.cos(np.deg2rad(stop)))
    s = np.linspace(s_min,s_max,step)
    zbins = np.rad2deg(np.arccos(1-(s/(2 * np.pi))))
    return zbins

def excel_reader(input_file,upper_lim,lower_lim,if_weights=False):
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

def save_into_xlsx(zen,azi,filename,weights=np.array([])):
    if len(weights) == 0:
        data = {
            'zen': zen,
            'azi': azi
        }
    else:
        data = {
            'weights': weights,
            'zen': zen,
            'azi': azi
        }
    df = pd.DataFrame(data)
    df.to_excel(os.path.join('/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify',f'{filename}.xlsx'),index=False)

def generate_randome_evt(n_sample,rbins,abins,hist):
    prob_matrix = hist
    # ic(np.sum(prob_matrix))
    flat_probs = prob_matrix.ravel()
    flat_indices = np.arange(len(flat_probs))

    num_samples = n_sample
    sampled_flat = np.random.choice(flat_indices, size=num_samples, p=flat_probs)

    azimuth_bin_idx, zenith_bin_idx = np.unravel_index(sampled_flat, prob_matrix.shape)

    random_azimuths = np.random.uniform(abins[azimuth_bin_idx], abins[azimuth_bin_idx + 1])
    random_zeniths  = np.random.uniform(rbins[zenith_bin_idx], rbins[zenith_bin_idx + 1])

    return prob_matrix[azimuth_bin_idx,zenith_bin_idx],random_zeniths,random_azimuths

def plot_with_weights(azimuth_list,zenith_list,weights,det_direct,up_lim,lo_lim):
    weights = np.array(weights)
    azimuth_list = np.array(azimuth_list)
    zenith_list = np.array(zenith_list)
    zen_mask = zenith_list<np.deg2rad(85)
    ic(zen_mask)
    ic(np.shape(azimuth_list))
    weights_mask = weights >= 0
    weights = weights[zen_mask]
    weights = weights/np.sum(weights)
    ic(zen_mask)
    azimuth_list = azimuth_list[zen_mask]
    zenith_list = zenith_list[zen_mask]
    # sin2Val = np.linspace(0,(np.sin(np.deg2rad(85)))**2, 8)   #Bin edges evenly spaces in sin^2(angle) in radians
    # else:
    #     sin2Val = np.linspace(0,1,11)
    # rbins = np.rad2deg(np.arcsin(np.sqrt(sin2Val)))
    rbins = get_even_zen_bin(lo_lim,up_lim,7)
    abins = np.linspace(0, 2*np.pi, 10)
    hist, _, _ = np.histogram2d(azimuth_list, np.rad2deg(zenith_list), bins=(abins, rbins), weights=weights)

    # hist = np.zeros_like(hist)+1
    # for ib,box in enumerate(hist):
    #     if ib<6:
    #         hist[ib] = [0,0,0,0,0,0,0]

    norm_factor = np.sum(hist)
    ic(norm_factor)
    hist = hist/norm_factor
    sample_num = len(det_direct)
    ic(sample_num)
    ic(np.shape(det_direct))
    azi_bin_index_det = np.digitize(det_direct[:,0], abins) - 1
    zen_bin_index_det = np.digitize(det_direct[:,1], rbins) - 1
    ic(np.shape(azi_bin_index_det),np.shape(zen_bin_index_det))
    # ic(det_direct[1])
    hist_sorted = np.sort(hist.ravel())
    mu = np.sum(hist**2)*sample_num
    ic(mu)
    ic(np.shape(hist))
    ic(azi_bin_index_det,zen_bin_index_det)
    ic(np.max(det_direct[:,1]))
    det_prob = np.sum(hist[azi_bin_index_det,zen_bin_index_det])
    ic(det_prob)
    
    ic(np.shape(hist))
    prob_lst = []
    try_num = 10000
    for i in range(try_num): 
        random_evts,random_zen,random_azi = generate_randome_evt(sample_num,rbins,abins,hist)
        prob_lst.append(np.sum(random_evts))
    prob_lst = np.array(prob_lst)
    position = (det_prob-mu)/(np.std(prob_lst))
    ic(position)
    # ic(hist)
    ic(np.sum(hist))
    ic(np.mean(prob_lst))
    fig,ax = plt.subplots(1,1,figsize = (10,8))
    bins = np.linspace(np.min(prob_lst),np.max(prob_lst),int(100)+1)
    n,_,_ = ax.hist(prob_lst,bins) 
    ax.vlines(x=det_prob,ymin=0,ymax=np.max(n),color = 'r')
    fig,ax = plt.subplots(1,1,figsize=(8,8),layout='constrained',subplot_kw={'projection': 'polar'})
    hist, _, _ = np.histogram2d(azimuth_list, np.rad2deg(zenith_list), bins=(abins, rbins), weights=weights)
    A, R = np.meshgrid(abins, rbins)
    pm=ax.pcolormesh(A, R, hist.T, norm=matplotlib.colors.LogNorm(), zorder=0)
    ax.figure.colorbar(pm,ax=ax)
    ax.scatter(random_azi,random_zen)
    return position

    

def get_direction(reader:NuRadioReco.modules.io):
    direct = []
    for evt in reader.get_events():
        stn=evt.get_station(51)
        zen = stn.get_parameter(stnp.zenith)/units.deg
        azi = stn.get_parameter(stnp.azimuth)/units.rad  
        if zen>85 or zen<20:
            continue
        direct.append([azi,zen])
    return np.array(direct)





# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/test_sim'
input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/sim/Trig_335_Freqs_X_direct/new_phase_algorithm'
input_det = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_cluster'
# sim_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_path))
zen_lst = []
azi_lst = []
weights = []
# for evt in sim_reader.get_events():
#     stn = evt.get_station(51)
#     zen = stn.get_parameter(stnp.zenith)/units.deg
#     azi = stn.get_parameter(stnp.azimuth)/units.rad
#     if zen>85:
#         continue
#     zen_lst.append(zen)
#     azi_lst.append(azi)
#     weights.append(evt.get_parameter(evtp.event_rate))
# save_into_xlsx(zen_lst,azi_lst,'sim_direct',weights)

# det_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det))
# zen_lst = []
# azi_lst = []
# for evt in det_reader.get_events():
#     stn = evt.get_station(51)
#     zen = stn.get_parameter(stnp.zenith)/units.deg
#     azi = stn.get_parameter(stnp.azimuth)/units.rad 
#     if zen>85:
#         continue
#     zen_lst.append(zen)
#     azi_lst.append(azi)
# save_into_xlsx(zen_lst,azi_lst,'det_direct')   

input_det_xlsx='/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify/det_direct.xlsx'
input_sim_xlsx='/Users/david/PycharmProjects/Demo1/Research/Repository/Template_modify/sim_direct.xlsx'

lo_lim = 0
up_lim = 60
det_zen, det_azi = excel_reader(input_det_xlsx,up_lim,lo_lim)
sim_zen,sim_azi,weights = excel_reader(input_sim_xlsx,up_lim,lo_lim,True)
det_direct = []
for iz,zen in enumerate(det_zen):
    det_direct.append([det_azi[iz],det_zen[iz]])
# weights_test(sim_reader,det_direct)
position = plot_with_weights(sim_azi,np.deg2rad(sim_zen),weights,np.array(det_direct),up_lim,lo_lim)
# standard_D.append([lo_lim,up_lim,np.abs(position),len(det_direct)])
plt.show()
exit()
standard_D = []
# for lo in range(0,65):
# det_direct = get_direction(det_reader)
ic(lo)
lo_lim = lo
up_lim = lo+20
det_zen, det_azi = excel_reader(input_det_xlsx,up_lim,lo_lim)
sim_zen,sim_azi,weights = excel_reader(input_sim_xlsx,up_lim,lo_lim,True)
det_direct = []
for iz,zen in enumerate(det_zen):
    det_direct.append([det_azi[iz],det_zen[iz]])
# weights_test(sim_reader,det_direct)
position = plot_with_weights(sim_azi,np.deg2rad(sim_zen),weights,np.array(det_direct),up_lim,lo_lim)
standard_D.append([lo_lim,up_lim,position,len(det_direct)])

# standard_D = np.array(standard_D)
# ic(standard_D)
# ic(standard_D[:,2])
# fig,axes = plt.subplots(2,1,figsize = (10,8))
# ax = axes[0]
# ax.plot(standard_D[:,2])
# ax = axes[1]
# ax.plot(np.abs(standard_D[:,2]))
# plt.show()

# ic| len(candi_lst): 44

# input_path = '/Users/david/PycharmProjects/Demo1/Research/Repository/Analyze2/det/Trig_335_Freqs_X_direct/new_phase_algorithm'
# input_nongoso = '/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/raw_non_goso'
# reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_nongoso))
# time_lst = []
# for evt in reader.get_events():
#     stn = evt.get_station(51)
#     if stn.has_triggered():
#         time = stn.get_station_time().datetime
#         time = (time-datetime.datetime(2018,1,1,0,0,0))/datetime.timedelta(hours=1)
#         time_lst.append(time)
# time_lst = np.sort(np.array(time_lst))
# time_lst = time_lst-time_lst[0]
# ic(time_lst[0],time_lst[-1],len(time_lst))
# period_check(time_lst)


    
    
# det_reader_candi = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det_candi))
# ic(det_reader_candi.get_n_events())






# input_lst = [input_det_nobacklobe,input_det_1backlobe,input_det_2backlobe,input_det_4backlobe]
# for input_det in input_lst:
#     det_reader = NuRadioRecoio.NuRadioRecoio(ToolsPac.get_input(input_det))
#     snr,chi,id = get_plot_info_sim(det_reader)
#     passed_id = []
#     for s in range(len(snr)):
#         if SNR_cut(snr[s],chi[s]):
#             passed_id.append(id[s])
#     repeat_evt = []
#     for evt in det_reader_candi.get_events():
#         evt_id = f'R{evt.get_run_number()}E{evt.get_id()}'
#         if evt_id in passed_id:
#             repeat_evt.append(evt_id)
#     ic(len(repeat_evt))



