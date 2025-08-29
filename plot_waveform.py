import numpy as np
import NuRadioReco.utilities.units as units
from icecream import ic
from NuRadioReco.framework.parameters import stationParameters as stnp
from NuRadioReco.framework.parameters import channelParameters as chp
import datetime
import matplotlib.pyplot as plt
import NuRadioReco.modules.io.NuRadioRecoio as NuRadioRecoio
from NuRadioReco.detector import detector
from NuRadioReco.detector import generic_detector
import send2trash
goso=[242,243,247,249,256,260,263,264,266]
det = generic_detector.GenericDetector(json_filename=f'/Users/david/PycharmProjects/Demo1/Research/2020cr_search/data/station_51/Stn51_sim_inAir/station51.json', assume_inf=False, antenna_by_depth=True, default_station=51)
import os
import ToolsPac
import math
ic(NuRadioRecoio.__file__)
Vrms=(9.71+9.66+8.94)/3
det.update(datetime.datetime(2019, 1, 1))
files = []
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_bef_cut_no_Incorp/sim_bef_cut'
input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/Trig_rate/Trig_Freqs_X_SNR_Ratio_Zen'
candi='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_Template/front_back_sep/'
candidate_path=os.path.join(candi,'Waveform')
# input_path='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract'
output=candidate_path
# output='/Users/david/PycharmProjects/Demo1/Research/Repository/candi_waveform'
Zen_sim='/Users/david/PycharmProjects/Demo1/Research/Repository/sim_output/X_335sig_Ratio_zen'
# output='/Users/david/PycharmProjects/Demo1/Research/Repository/raw_output/extract'

bad_Bic=['R243E324','R243E1271','R243E1330','R243E314','R243E1811','R243E6','R243E327','R243E2']

try:
    os.makedirs(output)
except(FileExistsError):
    send2trash.send2trash(output)
    os.makedirs(output)
def space_angle(loc1,loc2):
    # A*B/|A||B|
    def Sph2Carti(dirct_sp):
        # dirct_sp:[zen,azi]
        zen=dirct_sp[0]
        azi=dirct_sp[1]
        z=np.cos(zen)
        x=np.sin(zen)*np.cos(azi)
        y=np.sin(zen)*np.sin(azi)
        return np.array([x,y,z])
    dir1=Sph2Carti(loc1)
    dir2=Sph2Carti(loc2)
    diff=np.acos(np.dot(dir1,dir2))
    return diff

def SNR_cut_line(SNR):
    # x=np.linspace(0,1000,1001)
    # k=0.3
    # y=k*np.log10(x[10:])+0.2
    # ax.plot(x[10:],y,color='blue',linestyle='--',zorder=3)
    # for i in np.linspace(0.4,1,7):
    #     ax.axhline(y=i,color='blue',linestyle='--',zorder=3)
    bins=np.logspace(0.5,2,11)
    for i in range(1,len(bins)):
        if SNR>=bins[i-1] and SNR<=bins[i]:
            return i
    return 'Nothing'


        # ax.axvline(x=i,color='blue',linestyle='--',zorder=3)
    


def get_input(input):
    input_dir=[]
    for i in os.listdir(input):
        if i.endswith('.nur'):
            input_dir.append(os.path.join(input,i))
    return input_dir
# strange='R3E89'
# candidate=['R256E13', 'R256E588', 'R256E628', 'R256E735', 'R256E736', 'R256E1973', 'R256E2152', 'R256E2177', 'R263E368', 'R263E734', 'R263E736', 'R263E762', 'R263E764', 'R266E7', 'R266E59', 'R266E60', 'R266E1236', 'R266E1423', 'R266E1517', 'R266E1990', 'R260E112', 'R249E9', 'R249E13', 'R249E251', 'R249E355', 'R249E394', 'R243E110', 'R243E531', 'R243E542', 'R243E555', 'R243E589', 'R243E590', 'R243E591', 'R243E995', 'R243E1064', 'R243E1120', 'R243E1126', 'R243E1142', 'R243E1270', 'R243E1403', 'R243E1441', 'R243E1447', 'R243E1460', 'R243E1720', 'R243E1823', 'R243E1848', 'R264E8', 'R264E17', 'R264E244', 'R264E466', 'R264E476', 'R264E483', 'R264E496', 'R247E818', 'R247E821', 'R247E1193', 'R247E1281', 'R247E1319', 'R247E1482', 'R247E1732']

# ic(get_input(candi))
# data=NuRadioRecoio.NuRadioRecoio(get_input(candi))
# data=NuRadioRecoio.NuRadioRecoio(get_input(Zen_sim))

# for evt in data.get_events():

def plot_wave(evt,temp_output='Nothing',filename=None,plt_close=False,suptitle=f'waveform'):
    stn = evt.get_station(51)
    run = evt.get_run_number()
    id = evt.get_id()
    trace_list=[]
    for i in range(8):
        chn=stn.get_channel(i)
        trace=chn.get_trace()/units.mV
        trace_list.append(np.max(np.abs(trace)))
    trace_max=np.max(np.array(trace_list))

    n_chns = 8
    if n_chns == 4:
        fig = plt.figure(figsize=(10, 8))
        axes = fig.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
    elif n_chns == 8:
        fig = plt.figure(figsize=(10, 8))
        axes = fig.subplots(nrows=4, ncols=2, sharex=True, sharey=True)

    for i in range(n_chns):
        chn = stn.get_channel(i)
        if i == 0:
            ax = axes[0, 0]
            color = '0.5'
            #antenna_type = 'downward LPDA'
            ax.set_ylabel('Amplitude (mV)')
        elif i == 1:
            ax = axes[0, 1]
            color = '0.5'
            #antenna_type = 'downward LPDA'
        elif i == 2:
            ax = axes[1, 0]
            color = '0.5'
            #antenna_type = 'downward LPDA'
            ax.set_ylabel('Amplitude (mV)')
        elif i == 3:
            ax = axes[1, 1]
            color = '0.5'
            #antenna_type = 'downward LPDA'
        elif i == 4:
            ax = axes[2, 0]
            color = 'green'
            #antenna_type = 'upward LPDA'
            channel = stn.get_channel(i)
            # X=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            time_delay=channel[chp.reflect_delay]/units.ns
            # ax.set_title(f'ref_Dlay:{time_delay:.3f}')
            ax.set_ylabel('Amplitude (mV)')
        elif i == 5:
            ax = axes[2, 1]
            color = 'blue'
            #antenna_type = 'upward LPDA'
            channel = stn.get_channel(i)
            # X=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            time_delay=channel[chp.reflect_delay]/units.ns
            # ax.set_title(f'ref_Dlay:{time_delay:.3f}')
            ax.set_ylabel('Amplitude (mV)')
        elif i == 6:
            ax = axes[3, 0]
            color = 'red'
            #antenna_type = 'upward LPDA'
            ax.set_ylabel('Amplitude (mV)')
            ax.set_xlabel('Time (ns)')
            channel = stn.get_channel(i)
            # X=np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr']))
            time_delay=channel[chp.reflect_delay]/units.ns
            # ax.set_title(f'ref_Dlay:{time_delay:.3f}')
            ax.set_ylabel('Amplitude (mV)')
        elif i == 7:
            ax = axes[3, 1]
            color = '0.5'
            #antenna_type = 'dipole'
            ax.set_xlabel('Time (ns)')
        time = chn.get_times()/units.ns
        amplitude = chn.get_trace()/units.mV
        max_index = np.argmax(amplitude)
        max = np.max(np.abs(amplitude))
        # ax.plot(time,np.full(256,5*Vrms),c='0.5')
        # ax.plot(time,-np.full(256,5*Vrms),c='0.5')
        # ax.set_title(f'channel{i}_max_amp:{max:.4f}')
        ax.plot(time, amplitude, color=color, lw=1)
        if i in [4,5,6]:
            # ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f} X:{100*X:.2g}')
            ax.set_title(f'frontlope of ch{i} A:{np.max(np.abs(amplitude)):.2f} T_Dlay:{time_delay:.3f}ns')
        elif i in [0,1,2]:
            ax.set_title(f'backlope of ch{i+4} A:{np.max(np.abs(amplitude)):.2f}')
        else:
            ax.set_title(f'A:{np.max(np.abs(amplitude)):.2f}')
        ax.grid()
    stn=evt.get_station(51)
    sim_stn = stn.get_sim_station()
    sim_zen = sim_stn[stnp.zenith]/units.deg
    sim_azi = sim_stn[stnp.azimuth]/units.deg
    suptitle=f'[{sim_zen:.2f},{sim_azi:.2f}]'



    Xcorr=[]     
    for i in [4,5,6]:
        channel = stn.get_channel(i)
        # Xcorr.append(np.max(np.abs(channel[chp.cr_xcorrelations]['cr_ref_xcorr'])))
    # Xcorr=np.max(Xcorr)
    id=evt.get_id()
    run=evt.get_run_number()
    evt_time=stn.get_station_time().datetime
    # zen=stn.get_parameter(stnp.zenith)/units.deg
    # azi=stn.get_parameter(stnp.azimuth)/units.deg
    # sim_stn = stn.get_sim_station()
    # sim_zen = sim_stn[stnp.zenith]/units.deg
    # sim_azi = sim_stn[stnp.azimuth]/units.deg
    # zen=np.rad2deg(zen)
    # azi=np.rad2deg(azi)
    SNR=trace_max/Vrms
    # sim_zen=np.rad2deg(sim_zen)
    # sim_azi=np.rad2deg(sim_azi)
    # fig.suptitle(f'U/D:{trace_up/trace_down:.1f} recon[{zen:.1f},{azi:.1f}] sim[{sim_zen:.1f},{sim_azi:.1f}]X:{np.max(Xcorr):.2f}')
    # region=SNR_cut_line(SNR)
    # fig.suptitle(f'recon[{zen:.1f},{azi:.1f}] X:{np.max(Xcorr):.2f} SNR:{SNR:.2f} Area:{region} T{evt_time}')
    # fig.suptitle(f'SNR:{SNR:.2f}, T{evt_time}, D:{zen:.3g},{azi:.3g}')
    fig.suptitle(suptitle)
    # plt.show()
    # temp_output=os.path.join(output,f'Region{region}')
    if temp_output is 'Nothing':
        plt.show()
        return 
    # temp_output=os.path.join(temp_output,f'Re{SNR_cut_line(SNR)}')
    if filename == None:
        filename=f'R{run}E{id}.png'
    else:
        filename=f'{filename}.png'
    try:
        # plt.savefig(os.path.join(temp_output,f'X{100*Xcorr:.2g}R{run}E{id}.png'))
        plt.savefig(os.path.join(temp_output,filename))
    except(FileNotFoundError):
        os.makedirs(temp_output)
        # plt.savefig(os.path.join(temp_output,f'X{100*Xcorr:.2g}R{run}E{id}.png'))
        plt.savefig(os.path.join(temp_output,filename))
    if plt_close:
        plt.close()
# for evt in data.get_events():
#     iden=ToolsPac.get_id_info(evt)
#     plot_wave(evt,temp_output=candidate_path)

# True
# 0.6955312335093126
# 1.9808323415339528 2.847941610816865

# R3E89
# ic| np.rad2deg(err): np.float64(94.31406177967368)
#     np.rad2deg(np.array([zen,azi])): array([ 81.6587646 , 280.86563437])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([ 32.8498, 169.3205])
# R6E40
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E61
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E120
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E241
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E328
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E357
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E477
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E486
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E525
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R6E771
# ic| np.rad2deg(err): np.float64(49.822010668801916)
#     np.rad2deg(np.array([zen,azi])): array([84.98370285, 85.34491115])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([55.7544, 41.7073])
# R4E966
# ic| np.rad2deg(err): np.float64(56.88943196519379)
#     np.rad2deg(np.array([zen,azi])): array([19.3154988 , 73.71677512])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([ 58.8772, 151.7986])
# R4E764
# ic| np.rad2deg(err): np.float64(59.49479862826895)
#     np.rad2deg(np.array([zen,azi])): array([ 61.2745762 , 109.80062177])
#     np.rad2deg(np.array([sim_zen,sim_azi])): array([36.5474, 33.2559])
# R266E1531