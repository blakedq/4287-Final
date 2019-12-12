
import signal
import time
import poplib
import timeit
import sys
from io import StringIO
import zmq
import argparse
import subprocess

'''
input a json(dictionary) from arguement and output the result json
input keys are: id, timeout, code, input
output keys are: status, exec_time, output, error_msg
'''

import socket


class Executor():
    def __init__(self, args):
        super().__init__()
        self.masterIp = args.masterIp
        self.masterPort = args.port
        self.recvPort = 8088
        self.sendPort = 8087
        self.netInterface = args.netInterface

        self.reciever = zmq.Context().instance().socket(zmq.PULL)
        self.reciever.setsockopt(zmq.LINGER, -1)
        self.reciever.setsockopt(zmq.SNDHWM, 0)
        
        self.sender = zmq.Context().instance().socket(zmq.PUSH)
        self.sender.setsockopt(zmq.LINGER, -1)

        self.ip = '127.0.0.1'
        
    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    
    def parse_ip(self):
        cmd = "ifconfig " + self.netInterface +  "| grep 'inet' | cut -d: -f2 | awk '{ print $2}'"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        output = str(output, 'utf-8').replace('\n', '')
        print('get ip err', err)
        print('ip addr:', output)
        return output

    def init_service(self):
        # self.ip = self.get_ip()

        self.ip = self.parse_ip()

        self.reciever.bind("tcp://*:" + str(self.recvPort))
        self.sender.bind("tcp://*:" + str(self.sendPort))  

        init_sender = zmq.Context().instance().socket(zmq.PUSH)
        init_sender.setsockopt(zmq.LINGER, -1)
        init_sender.connect("tcp://" + self.masterIp + ":" + str(self.masterPort))
        init_sender.send_string(self.ip + ":" + str(self.sendPort))

        print('service initialized!')

    def execution(self, codeInfo):

        print('codeinfo:')
        print(codeInfo)
        
        def sigHandler(signum, frame):
            # print('handler')
            raise Exception("timout")
        
        signal.signal(signal.SIGALRM, sigHandler)

        codeId = codeInfo['id']
        timeLimit = codeInfo['timeout']
        pyCode = codeInfo['code']
        userInput = codeInfo['input']

        execTime = -1

        old_stdout = sys.stdout
        old_stdin = sys.stdin

        mystdout = StringIO()
        mystdin = StringIO()
        sys.stdout = mystdout
        sys.stdin = mystdin
        mystdin.write(userInput)

        retVal = None

        try:
            # startPoint = time.time()
            # exec(pyCode)
            # execTime = time.time() - startPoint

            signal.alarm(timeLimit)
            execTime = timeit.timeit(pyCode, number=1)
            signal.alarm(0)

            sys.stdout = old_stdout
            sys.stdin = old_stdin
            retVal = {'status': 'success', 'exec_time': execTime, 'output':mystdout.getvalue(), 'error_msg':''}
        except SyntaxError as err:
            signal.alarm(0)
            sys.stdout = old_stdout
            sys.stdin = old_stdin
            # print('sytax err')
            # print(err)
            retVal = {'status': 'syntax error', 'exec_time': execTime, 'output':mystdout.getvalue(), 'error_msg': '*** syntax error:\n' + str(err)}
        except Exception as exc:
            signal.alarm(0)
            sys.stdout = old_stdout
            sys.stdin = old_stdin
            if (exc == 'timeout'):
                retVal = {'status': 'timout', 'exec_time': timeLimit, 'output':mystdout.getvalue(), 'error_msg': '*** execution timeout!'}
            else:
                retVal = {'status': 'runtime error', 'exec_time': execTime, 'output':mystdout.getvalue(), 'error_msg': '*** runtime error:\n' + str(exc)}
        
        # print('mystdout:', mystdout.getvalue())
            
        return retVal

    def start_service(self):
        self.init_service()

        while True:
            arg = self.reciever.recv()
            try:
                arg = eval(arg)
                print(arg)
                arg['id']
                arg['timeout']
                arg['code']
                arg['input']
                res = self.execution(arg)
                print("res:\n", res)

                self.sender.send_string(str(res))

            except NameError as err:
                print('invalid arguments')
                print(err)
            except KeyError:
                print('wrong json content')


def parseCmdLineArgs ():
    parser = argparse.ArgumentParser ()

    # add optional arguments
    parser.add_argument ("-n", "--netInterface", type=str, help="network interface in use")
    parser.add_argument ("-m", "--masterIp", type=str, help="master ip address")
    parser.add_argument ("-p", "--port", type=int, help="master listening port")
    
    args = parser.parse_args()

    return args

def main():
    parsed_args = parseCmdLineArgs()

    exc = Executor(parsed_args)
    exc.start_service()


if __name__ == "__main__":
    main()