
# coding: utf-8

# In[50]:

import sys
sys_path_ls = sys.path

my_paths = ['/home/kouz', '/home/kouz/.conda/envs/kouenv/lib/python37.zip', '/home/kouz/.conda/envs/kouenv/lib/python3.7', '/home/kouz/.conda/envs/kouenv/lib/python3.7/lib-dynload', '', '/home/kouz/.conda/envs/kouenv/lib/python3.7/site-packages', '/home/kouz/.conda/envs/kouenv/lib/python3.7/site-packages/IPython/extensions', '/home/kouz/.ipython']
# for p in my_paths:
    # if p not in sys_path_ls:
        # sys.path.insert(0, p)
sys.path.insert(0, '/home/kouz/.conda/envs/kouenv/lib/python3.7/site-packages/')

import threading
import urllib.request
import os
import simplejson
import csv
import json
import time
import datetime
import subprocess
import pandas as pd
from threading import *
from urllib.error import URLError
import numpy as np
from multiprocessing import Pool, current_process


# In[43]:

def filecount(): #start create or using exist filecount.txt for next step.
    global countlist
    path = datapath + '/filecount.txt'
    isExists = os.path.exists(path)
    if not isExists:
        file = open(path,'w')
        file.write(countlist)
        file.close()
        return True
    else:
        file = open(path,'r')
        tempstr = file.readlines()
        #print(tempstr[0])
        str = tempstr[0]
        str = str.lstrip('[')
        str = str.rstrip(']')
        templist = str.split(',')  
        i = 0
        for x in templist:
            countlist[i] = int(x)
            i+=1
        file.close()
        return False

def write_log(filepath):
    now=datetime.datetime.now()
    path = filepath+"log.txt"
    isExists = os.path.exists(path)
    if not isExists:
        file = open(path,'w')
        file.write(now.strftime('%Y-%m-%d %H:%M:%S'))
        file.write("\n")
        file.close()
        return True
    else:
        file = open(path,'a+')
        file.write(now.strftime('%Y-%m-%d %H:%M:%S'))
        file.write("\n")
        file.close()


def savecount(): #save the current file progress for next run. 
    global countlist
    path = datapath + '/filecount.txt'
    file = open(path, 'w')
    file.write(str(countlist))
    file.close()


def nestedlist2csv(list, out_file): #csv working part.
    with open(out_file, 'wb') as f:
        w = csv.writer(f)
        fieldnames=list[0].keys()  # solve the problem to automatically write the header
        w.writerow(fieldnames)
        for row in list:
            w.writerow(row.values())

def read_json(filename):             #read the json file downloaded by url link.
    return json.loads(open(filename).read())

def merge_dicts_to_df(list_of_dicts):
    v_list = list_of_dicts
    data = v_list[0]
    df_out = pd.DataFrame([data], columns=data.keys())
    if len(v_list) > 1:
        for i in range(1, len(v_list)):
            data = v_list[i]
            df_t = pd.DataFrame([data], columns=data.keys())
            df_out = pd.concat([df_out, df_t], axis=0, ignore_index=True, sort=False)
    return df_out

def write_csv(in_list, state, city, name, d_type, file_path):  #write the translated file into csv file formate. 
    df_out = merge_dicts_to_df(in_list)
    now=datetime.datetime.now()
    df_out['Download Time'] = now.strftime('%Y-%m-%d %H:%M:%S')
    time_stamp = now.strftime("%Y-%m-%d_%H:%M:%S")
    download_date = now.strftime("%Y-%m-%d")
    save_to_folder = file_path +'/'+state+'_'+city+'_'+ name+'_'+ d_type +'_' + download_date+'/'
    file_name = save_to_folder +state+'_'+city+'_'+ name+'_'+ d_type +'_'+ time_stamp+'.csv'
    if not os.path.exists(save_to_folder):
        os.makedirs(save_to_folder)
    df_out.to_csv(file_name, index=False)


def write_time(filename,targenemt):
    global row
    now=datetime.datetime.now()
    with open(filename,'r') as inputf:
        with open(targenemt,'w') as outputf:
            writer = csv.writer(outputf,lineterminator='\n')
            reader = csv.reader(inputf)

            all = []
            try:
                row = next(reader)
            except StopIteration:
                pass
            row.append('Download Time')
            all.append(row)

            for row in reader:
                row.append(now.strftime('%Y-%m-%d %H:%M:%S'))
                all.append(row)
            writer.writerows(all)
    os.remove(filename)
    time_stamp = now.strftime("%Y-%m-%d_%H:%M:%S")
    download_date = now.strftime("%Y-%m-%d")
    return download_date, time_stamp

def mkdir(path): #createing a file folder for the city if it does not exist. 
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False

def open_path(path):
    try:
        fd = open(path)
        return fd
    except FileNotFoundError:
        # TODO here
        # time.sleep(100)
        # fd = open(path)
        return

def find_data_dict(data_url):
    req = urllib.request.Request(data_url, headers = {"User-Agent": "Mozilla/5.0"})
    response = urllib.request.urlopen(req)
    html = response.read() # https://docs.python.org/3/howto/urllib2.html
    data_dict = json.loads(html.decode('utf-8'))
    return data_dict

def find_data_list(data_dict):
    if 'data' in data_dict.keys():
        sub_dict = data_dict['data']
        if sub_dict == None:
            return []
        elif 'bikes' in sub_dict.keys():
            return sub_dict['bikes']
        elif 'stations' in sub_dict.keys():
            return sub_dict['stations']
    elif 'bikes' in data_dict.keys():
        return data_dict['bikes']
        

def save_data(state, city, name, d_type, data_url, datapath = "/depot/cai161/data/Bike_Share_Data/GBFS_data/"):
        
    file_path = datapath + state + '/' + city + '/' + name + '/' + d_type
    mkdir(file_path)
    try:
        data_dict = find_data_dict(data_url)
    except:
        print('Error retrieving data from url for city {}, name {}'.format(city, name))
    try:
        in_list = find_data_list(data_dict)
    except:
        print('Error finding data list for city {}, name {}'.format(city, name))
    try:
        if len(in_list)==0:
            pass
        else:
            write_csv(in_list, state, city, name, d_type, file_path)
    except:
        print('Error saving data for city {}, name {}'.format(city, name))


# In[39]:

def split_df(df, sep = 10):
    df_list = []
    len_df = len(df)
    int_max = int(len_df/sep)
    for i in range(1, (int_max+1)):
        s_num = i * sep
        sub_df = df.iloc[(s_num-sep):s_num]
        df_list.append(sub_df)
    sub_df = df.iloc[(int_max*sep):len_df]
    df_list.append(sub_df)
    return df_list


# In[40]:




# In[48]:

def collect_from_df(df):
    starttime=time.time()
    while True:
        for i in range(len(df)):
            state = df['state'].iloc[i]
            city = df['city'].iloc[i]
            name = df['Name'].iloc[i]
            d_type = df['type'].iloc[i]
            data_url = df['URL'].iloc[i]
            save_data(state, city, name, d_type, data_url, datapath = "/depot/cai161/data/Bike_Share_Data/GBFS_data/")
        time.sleep(120.0 - ((time.time() - starttime) % 120.0))
    


# In[51]:

if __name__ == '__main__':
    # Read in the summary table
    d_all = pd.read_csv('/home/kouz/data_crawler/NABSA_data_url.csv')
    d_in = d_all[d_all['state']=='IN'].copy()
    d_in = d_in[['Name','state','city','StationURL']]
    d_in.columns = ['Name','state','city','URL']
    d_in = d_in.dropna(how='all', subset=['URL'])
    d_in['type'] = 'station'
    d_all = d_all.dropna(how='all', subset=['TripDataLink', 'BikeURL'])
    d_sta = d_all.copy()
    d_sta = d_sta[['Name','state','city','StationURL']]
    d_sta.columns = ['Name','state','city','URL']
    d_sta = d_sta.dropna(how='all', subset=['URL'])
    d_sta['type'] = 'station'
    d_bike = d_all.copy()
    d_bike = d_bike[['Name','state','city','BikeURL']]
    d_bike.columns = ['Name','state','city','URL']
    d_bike = d_bike.dropna(how='all', subset=['URL'])
    d_bike['type'] = 'bike'
    sta_df_ls = split_df(d_sta)
    bike_df_ls = split_df(d_bike)
    df_ls = sta_df_ls + bike_df_ls
    df_ls.append(d_in)

    n_jobs = 20    # You can change this based on your machine

    with Pool(n_jobs) as p:
        p.map(collect_from_df, df_ls)


