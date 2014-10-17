import datetime
from config import config
from status import load_stat
import json
import udp_socket
import time


dataTS = {}
dataPOST = {}
thread_flag = True

def getInfo():
    load = load_stat()
    load['status'] = 'up'
    load['id'] = config['id']
    load['location'] = config['location']
    load['database_center'] = config['dc']
    load['node'] = config['node']
    #load['time'] = time.strftime("%Y/%M/%d-%H:%M:%S", time.localtime())
    load['time'] = time.time()
    return json.dumps(load)


def monitor():
    while True:
        udp_socket.send(getInfo())
        time.sleep(1)


def check():
    global dataTS, dataPOST
    for (i, data) in dataTS.items():
        last_update_time_ori = data['time']
        last_update_time = datetime.datetime.fromtimestamp(last_update_time_ori)
        now_time = datetime.datetime.fromtimestamp(time.time())

        if (now_time - last_update_time).seconds >= 30:
            dataPOST[data['id']]['status'] = "down"
        else:
            if not dataPOST.has_key(data['id']):
                dataPOST[data['id']] = {}
            if not dataPOST[data['id']].has_key("history"):
               dataPOST[data['id']]['history'] = {}
            history_old = dataPOST[data['id']]['history']
            dataPOST[data['id']] = data
            dataPOST[data['id']]['history'] = history_old
            dataPOST[data['id']]['history'][last_update_time.second % 24] = {}
            dataPOST[data['id']]['history'][last_update_time.second % 24]['load_1'] = data['lavg_1']
            dataPOST[data['id']]['history'][last_update_time.second % 24]['time'] = int(data['time']*1000)


def receiver():
    global dataTS
    while True:
        data_str = udp_socket.recv()
        #print(data_str)
        data = json.loads(data_str)
        dataTS[data['id']] = data
        check()
        json.dumps(dataPOST)
        fileHandle = open(config['json'], 'w')
        fileHandle.write(json.dumps(dataPOST))
        fileHandle.close()
        # print 'dataTS:', json.dumps(dataTS)


if __name__ == "__main__":
    if config['role'] == 'collector':
        monitor()
    elif config['role'] == 'server':
        udp_socket.init_recv()
        receiver()
