import os, time
import requests
import json, time
import numpy as np
import subprocess, glob

import pandas as pd
from multiprocessing import Process

headers = {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
     'Content-Type': 'application/x-www-form/urlencoded',
    'Connection': 'Keep-Alive',
    'Referer': 'https://instances.social/list',
}


suffix_api = '/api/v1/timelines/public'

DATSET_FOLDER = 'message/'



def fetch_server_meta(server):
    url = 'https://instances.social/list.json?q%5Busers%5D=&strict=false' 
    FOLD = 'daily_stats/'
    resp = requests.get(url, headers=headers)
    with open(FOLD + str(server) + '.json', 'w' ) as fp:
        json.dump(resp.json(), fp)


def get_config_from_file( f_name, server ):
    with open(f_name, 'r') as fp:
        s_dat = json.load(fp)

    if s_dat.get(server):
        return server, s_dat[server]['max'], s_dat[server]['crawled']
    fetch_server_meta(server)
    return server, 0, False

def write_status(folder, data, f_name):
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(folder +'/' + f_name + '.json', 'w' ) as fp:
        json.dump(data, fp)
    cmd = ['gzip', folder +'/' + f_name + '.json']
    subprocess.call(cmd)
    

def get_timeline_url( is_https_enabled, suffix_api, serv_url, last=0):
    if is_https_enabled:
        serv_url = 'https://' + serv_url
    else:
        serv_url = 'http://' + serv_url
    if last == 0:
        return serv_url + suffix_api, {'limit': 40}
    return serv_url + suffix_api, { 'max_id': last, 'limit': 40}



def update_config_from_file( f_name, server, max_v, crawled):
    with open(f_name, 'r') as fp:
        s_dat = json.load(fp)

    s_dat[server] = {}
    s_dat[server]['max'] = max_v
    s_dat[server]['crawled'] = crawled
    with open(f_name, 'w') as fp:
        json.dump(s_dat, fp)
    
    return True

def get_servers(serv_file, s, e):
    crawled_names = [] #['witches.town','mstdn.kemono-friends.info','mastodon.social', 'kirakiratter.com','mastodon.cloud', 'otajodon.com', 'gensokyo.cloud', 'ostatus.blessedgeeks.jp', 'kiminona.co', 'mstdn.nemsia.org', 'social.kimamass.com', 'mental.social', 'social.touha.me', 'ltch.fr', 'jojomonvr.com', 'glamdon.com', 'mastodon.minicube.net', 'don.ekesete.net', 'mastodon.partipirate.org', 'mstdn.toaruhetare.net', 'foresdon.jp', 'mastodon.mail.at', 'www.nekotodon.com', 'nishinomiya.in.net', 'social.apreslanu.it', 'tooting.intensifi.es', 'mikado-city.jp', 'mastodon.matrix.org', 'i.write.codethat.sucks', 'thinkers.ac', 'octodon.social', 'oc.todon.fr', 'gingadon.com', 'jeunesse.media', 'sldon.com', 'friloux.me', 'mstdnsrv.moe.hm', 'mastodon.cgx.me', 'nice.toote.rs', 'mastodon.roflcopter.fr', 'un.lobi.to', 'social.tchncs.de', 'status.dissidence.ovh', 'lfsr.net', 'mastodon.snowandtweet.jp'] 
    with open(serv_file, 'r') as fp:
        s_list = json.load(fp)
    top_ins = pd.DataFrame.from_records(s_list['instances']).sort_values('statuses', ascending=False).name.values
    ins  = []
    for ins_d in s_list['instances']:
        if ins_d['name'] in top_ins[s:e] and ins_d['name'] not in crawled_names:
            ins.append(ins_d)
    return ins#s_list['instances']

def populate_conf_file(conf_file, servers):
    conf = {}    
    for server in servers:
        serv_url = server['name']
        crawled = False
        all_fint = []
        all_fs = glob.glob(DATSET_FOLDER + '/' + serv_url +'/*json*')
        # print all_fs
        for f in all_fs:
            for j in f.split('/')[-1].split('.')[0].split('_'): 
                all_fint.append(int(j))
        if all_fs:
            last = min(all_fint)
            conf[serv_url] = {"max": last, "crawled": crawled}

    with open(conf_file, 'w') as fp:
        json.dump(conf, fp)




def main(arr_start, arr_end):
    servers = get_servers('./server_list.json', arr_start, arr_end)
# print servers
    conf_file = 'conf_'+ str(arr_start)+'_' + str(arr_end) +'.json'
    populate_conf_file(conf_file, servers)
    print 'total servers =', len(servers)


    lt = 30

    no_resp = []
    times = {}
# Done -- 3:4
# for server in servers[1:1]:
    # print ['addedAt']

    for server in servers:
        times[server['name']] = 0
    
    while True:
    #
            server = np.random.choice(servers)
        
            if server['up'] and server['name'] not in no_resp:
                serv_url = server['name']
                ssl_enabled = False
                if server['https_score'] > 0:
                    ssl_enabled = True
                serv_url, last, crawled = get_config_from_file(conf_file, serv_url)
                
                if not crawled:
                    url,params = get_timeline_url( ssl_enabled, suffix_api, serv_url, last )
                    # print url, params
                    resp = requests.get(url, params=params, headers=headers)
                    # print resp.json() 
                    resp_json = resp.json()
                                
                    
                    if not resp_json:
                        print server['name'], server['addedAt']
                        crawled = True
                        update_config_from_file(conf_file, serv_url, last, crawled)
                    else:
                        # print len(resp_json), resp_json[0]['created_at'], resp_json[-1]['created_at']
                        # print str(resp_json[0]['id']) + '_' + str(resp_json[-1]['id'])
                        f_name = str(resp_json[0]['id']) + '_' + str(resp_json[-1]['id'])
                        write_status( DATSET_FOLDER + '/' + serv_url, resp_json, f_name )
                        last = int(resp_json[-1]['id'])
                        update_config_from_file(conf_file, serv_url, last, crawled)
                        serv_url, last, crawled = get_config_from_file(conf_file, serv_url)
                    # time.sleep(0.2)
                else:
                    update_config_from_file(conf_file, serv_url, last, crawled)
        #except:
         #   print server['name']
          #  time.sleep(10)
           # times[server['name']] += 1
           # if times[server['name']] >= 5:
            #    no_resp.append(server['name'])
            #    times[server['name']] = 0
            #pass

main(1, 2)
