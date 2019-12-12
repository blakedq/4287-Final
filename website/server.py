
from flask import Flask, request, Response, render_template, send_from_directory, jsonify
# from execution import Execute
from subprocess import Popen, PIPE
from multiprocessing import Process, Manager
from threading import Thread
import zmq

workers = []

def listenToWorkers(workerLst):
    init_reciever = zmq.Context().instance().socket(zmq.PULL)
    init_reciever.setsockopt(zmq.LINGER, -1)
    init_reciever.setsockopt(zmq.SNDHWM, 0)
    init_reciever.bind("tcp://*:8086")

    while True:
        workerAddr = init_reciever.recv_string()
        workerAddr = workerAddr.split(':')

        workerDict = {'ip': workerAddr[0], 'port': eval(workerAddr[1])}

        sender = zmq.Context().instance().socket(zmq.PUSH)
        sender.setsockopt(zmq.LINGER, -1)
        reciever = zmq.Context().instance().socket(zmq.PULL)
        reciever.setsockopt(zmq.LINGER, -1)
        reciever.setsockopt(zmq.SNDHWM, 0)

        workerDict['sender'] = sender
        workerDict['reciever'] = reciever
        workerDict['free'] = True

        workerLst.append(workerDict)
        print('new worker:\n', workerDict)

t = Thread(target=listenToWorkers, args=(workers, ))
t.start()


app = Flask(__name__, template_folder='.')

sender = zmq.Context().instance().socket(zmq.PUSH)
sender.setsockopt(zmq.LINGER, -1)
reciever = zmq.Context().instance().socket(zmq.PULL)
reciever.setsockopt(zmq.LINGER, -1)
reciever.setsockopt(zmq.SNDHWM, 0)

@app.route("/")
def index():
    print('return webpage')
    return render_template("website.html")


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('./js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('./css', path)


@app.route('/execute', methods=['POST'])
def getpost():
    content = request.get_json()
    data = request.json
    print("data is " + format(data))
    print(str(format(data)))

    print(workers)
    for worker in workers:
        if worker['free'] == False:
            continue
        
        worker['free'] = False
        sender = worker['sender']
        reciever = worker['reciever']
        sender.connect("tcp://" + worker['ip'] + ":" + str(worker['port'] + 1))
        sender.send_string(str(format(data)))

        reciever.connect("tcp://" + worker['ip'] + ":" + str(worker['port']))
        result = reciever.recv_string()
        print('recv:\n', result)
        worker['free'] = True

        return jsonify(eval(result))

    # return_dict = Manager().dict()
    # p = Process(target=Execute, args=(data, return_dict))
    # p.start()
    # p.join()
    # sender.connect("tcp://127.0.0.1:8088")
    # sender.send_string(str(format(data)))
    # reciever.connect("tcp://127.0.0.1:8087")
    # result = reciever.recv_string()
    # print('recv:\n', result)

    # print('out1put:')
    # print(output)

    # print('res\n', return_dict['res'])
    
    return jsonify({'status':'failed'})

app.run(host='0.0.0.0', port=8888)

