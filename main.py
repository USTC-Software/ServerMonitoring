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
    check()
    return json.dumps(dataPOST)

def monitor():
    while True:
        udp_socket.send(getInfo())
        print("sended")
        time.sleep(1)


def check():
    global dataTS, dataPOST
    for data in dataTS:
        last_update_time_ori = data['time']
        last_update_time = datetime.datetime.fromtimestamp(last_update_time_ori)
        now_time = datetime.datetime.fromtimestamp(time.time())
        if (last_update_time - now_time).second >= 10:
            dataPOST[data['id']] = {"status":"down"}
        else:
            dataPOST[data['id']] = data


def receiver(threadName, delay):
    global dataTS
    while True:
        data_str = udp_socket.recv()
        print("received")
        data = json.loads(data_str)
        dataTS[data['id']] = data


if config['role'] == 'collector':
    monitor()
elif config['role'] == 'server':
    udp_socket.init_recv()
    thread.start_new_thread(receiver, ("receiver", 1, ))
    run(host='localhost', port=8077, reloader=True)