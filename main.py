import datetime
import thread
from config import config
from status import load_stat
import json
import udp_socket
import time
from mole import route, run, static_file, error,get, post, put, delete, Mole
from mole.template import template
from mole import request
from mole import response

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


@route('/')
def index():
    global thread_flag, dataPOST
    if thread_flag:
        thread_flag = False
        udp_socket.init_recv()
        thread.start_new_thread(receiver, ("receiver", 1, ))
    check()
    return json.dumps(dataPOST)

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
            dataPOST[data['id']] = {"status": "down"}
        else:
            dataPOST[data['id']] = data


def receiver(threadName, delay):
    global dataTS
    while True:
        data_str = udp_socket.recv()
        #print(data_str)
        data = json.loads(data_str)
        dataTS[data['id']] = data
        #print 'dataTS:', json.dumps(dataTS)


if __name__ == "__main__":
    if config['role'] == 'collector':
        monitor()
    elif config['role'] == 'server':
        #udp_socket.init_recv()
        #thread.start_new_thread(receiver, ("receiver", 1, ))
        run(host='localhost', port=8077, reloader=True)