import numpy as np
from matplotlib import pyplot as plt
from env.env.envs import factory
import feather
import os
from pyat.pyat.env import Box, Beam
from pyat.pyat.readwrite import read_arrivals_asc
import pickle

'''
Description:

Author: Hunter Akins
'''

feather.read_dataframe('/home/hunter/research/code/internalwaves/IW/config/strat.fthr')

builder = factory.create('deepwater')
dw_env = builder()

iw_root = '/home/hunter/research/code/internalwaves/IW/data/'
prof_dir = 'sound_prof_1/'

"""
Source-receiver parameters
"""
freq = 100
zs = 500
dz = 100 # 100 meter spacing between array elements
zr = np.arange(100, 1000+dz, dz)
dw_env.add_source_params(freq, zs, zr)
field_dz = 10
field_zmax =  5000
dr = 50*1e3
rmax = 550*1e3
dw_env.add_field_params(field_dz, field_zmax, dr, rmax)

""" 
Bellhop, beam set up
"""

run_type = 'A' # arrivals (I for shd file)
nbeams = 100
alpha = np.linspace(-20,20, 100) # launch angles/num rays
box = Box(5500, 550) # max depth, max range (m, km) to compute rays
deltas=0 # auto choose ray step size
beam = Beam(RunType=run_type, Nbeams=nbeams, alpha=alpha,box=box,deltas=deltas)
dir_name =os.getcwd() + '/at_files/' # where to put the bellhop files

"""
arrivals is the list of all arrival information
each element is a list of lists of lists
the first level separates by time (so arrivals[0] is arrival info for time 0, etc.) (Time within a static internal wave field! So within each "time" there is a static IW field, but there are arrival times within it)
within a given time snapshot, it lineates by depth and range (indexed the same)
so arr = arrivals[0] is the set of arrival lists for all depth and range stuff for
time 0
Then arr[i] is the arrival list item for receiver position i//num_ranges depth and i%num_ranges range (it's more clear if you just look at the loops I use to extract
the data
Okay finally, arr[i] is the arrival list, so it contains amp, delay, src_ang, rec_ang, num_top_bnc, num_bot_bnc
time steps are 900 seconds so total sim time is 900*101 seconds = 25 hours
"""

arrivals = []
num_runs = 101
for i in range(num_runs):
    iw_file = 'run-' + str(i).zfill(3) + '.fthr'

    iw_name = iw_root + prof_dir + iw_file
    df = feather.read_dataframe(iw_name)
    print('Time step', df['t'])
    if i == 2:
        sys.exit(0)
    iw_name = iw_root + prof_dir + iw_file
    dw_env.add_iw_field(iw_name)

    dw_env.run_model('bellhop', dir_name, 'dw_ray', beam=beam, zr_flag=True, zr_range_flag=False)

    ssp = dw_env.cw

    arrs, pos = read_arrivals_asc(dir_name + 'dw_ray.arr')
    arrivals.append(arrs)

with open('pickles/sound_prof1.pickle', 'wb') as f:
    pickle.dump([arrivals, pos], f)
     
#for i in range(len(zr)):
#    for j in range(num_ranges):
#        arr = arrivals[i*num_ranges + j]

