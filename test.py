import matplotlib.pyplot as plt
import numpy as np
import datetime
from icecream import ic
time_A=datetime.timedelta(hours=1,seconds=3)
hour = datetime.timedelta(hours=1)
import random
from icecream import ic
import matplotlib.pyplot as plt
from NuRadioReco.utilities import templates
import numpy as np
template_path='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/templates_cr_station_51.pickle'
# template_path='/Users/david/PycharmProjects/Demo1/Research/2020cr_search/templates/'
import pickle
# import NuRadioMC.NuRadioReco.utilities.templates

# Create a sine wave
# x = np.linspace(0, 5.5 * np.pi, 1000)
# x1= np.linspace(5.5*np.pi,10*np.pi,1000)
# y = np.sin(x)
# y1= 0.5*np.sin(x1+np.pi/3)+0.5*np.sin(x1)
# x = np.concatenate((x, x1))
# y = np.concatenate((y, y1))
# # Plot
# plt.figure(figsize=(8, 4))
# plt.plot(x, y, label='sin(x)')
# # plt.plot(x1,y1,label='sin(x+3)')
# plt.title('Sine Wave')
# plt.xlabel('x')
# plt.ylabel('sin(x)')
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()

# {template_id:{ch_id:[chi_max,chi_phase]}}

# xcorrelations['{}_ref_xcorr'.format(ref_str)] = np.abs(xcorrs_ch).mean()
# xcorrelations['{}_ref_xcorr_all'.format(ref_str)] = np.abs(xcorrs_ch)
# xcorrelations['{}_ref_xcorr_max'.format(ref_str)] = np.abs(xcorrs_ch[np.argmax(np.abs(xcorrs_ch))])
# xcorrelations['{}_ref_xcorr_time'.format(ref_str)] = np.mean(xcorrpos_ch[np.argmax(np.abs(xcorrs_ch))]) * dt
# xcorrelations['{}_ref_xcorr_template'.format(ref_str)] = template_key[np.argmax(np.abs(xcorrs_ch))]
# channel[chp.cr_xcorrelations] = xcorrelations

with open(template_path, 'rb') as file:
    template = pickle.load(file)

def get_klog(arr1,arr2):
    k=(arr1[1]-arr2[1])/(np.log10(arr1[0])-np.log10(arr2[0]))
    b=arr1[1]-k*np.log10(arr1[0])
    return k,b

def test_logeqs(k,b,arr1):
    exp=k*np.log10(arr1[0])+b
    ic(exp)
    return exp==arr1[1]

arr1=[7,0.35] 
arr2=[10,0.46]
k,b=get_klog(arr1,arr2)
ic(k,b)
ic(test_logeqs(k,b,arr1))
# self.__cr_templates[station_id][0][zen_ref][az_ref]
# 'templates_cr_station_{}.pickle'.format(station_id))