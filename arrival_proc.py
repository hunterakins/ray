import numpy as np
from matplotlib import pyplot as plt
import pickle
from pyat.pyat.env import Arrival, Arrivals
import os

"""
Description:
arrivals is the list of all arrival information
each element is a list of lists of lists
the first level separates by time (so arrivals[0] is arrival info for time 0, etc.)
within a given time snapshot, it lineates a nested level for various sources, and then within that level by depth and range (indexed the same)
so arr = arrivals[0] is the set of arrivals for all depth and range stuff for every source for
time 0
Then arr = arr[i] is the arrival associated with the ith source position
Then arr[i] is the arrival list item for receiver position i//num_ranges depth and i%num_ranges range (it's more clear if you just look at the loops I use to extract
the data
Okay finally, arr[i] is an arrivals object, so it contains amp, delay, src_ang, rec_ang, num_top_bnc, num_bot_bnc

Author: Hunter Akins
"""


def index_to_pos(i, pos):
    """
    Take index i to tuple that is range and depth (meters)
    Input - 
    i - integer
    index
    pos - Pos object (pyat env)
    """
    r = pos.r.range
    z = pos.r.depth
    num_ranges = len(r)
    depth_index = i//num_ranges
    range_index = i%num_ranges
    return z[depth_index], r[range_index]*1e-3


if __name__ == '__main__':
    with open('pickles/sound_prof1.pickle', 'rb') as f:
        thing = pickle.load(f)
        pos_obj = thing[-1] # position obj
        thing = thing[0] # arrival list thing
        num_times = len(thing) # each time is a spec. IW field
        arrivals_list = []
        for time in range(num_times):
            tmp_list = []
            pos_list = thing[time]
            new_pos_list = [0]*len(pos_list) # create new list of arrival objects in stead of the lists
            for pos in range(len(pos_list)):
                arr_list = pos_list[pos]
                arrs = Arrivals([Arrival(x) for x in arr_list])
                new_pos_list[pos] = arrs
            arrivals_list.append(new_pos_list)
            

    for i in range(len(pos_list)):
        depth, ran = index_to_pos(i, pos_obj)
        print(depth, ran)
        for time in range(num_times):
            first_pos = arrivals_list[time][i]
            fig = plt.figure()
            if time == 0:
                ymin, ymax, vals = first_pos.plot_cir()
            else:
                _, _, _ = first_pos.plot_cir(vals)
            plt.ylim([ymin, ymax])
            pic_name = 'pics/' + str(time).zfill(3) + '.png'
            plt.xlabel('Arrival time (s)')
            plt.ylabel('Arrival amplitude')
            plt.title('Channel impulse response')
            plt.savefig(pic_name)
            plt.close()
        vid_name = 'z_{:.2f}_r_{:.2f}.mp4'.format(depth, ran)
        print('VID NAME', vid_name)
        os.system('cd pics && ffmpeg -r 10 -f image2 -s 1920x1080 -i %03d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p ' + vid_name)
        os.system('cd pics && rm *.png')
 
            
            
