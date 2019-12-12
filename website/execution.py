
import signal
import time
import poplib
import timeit
import sys
from io import StringIO

'''
input a json(dictionary) from arguement and output the result json
input keys are: id, timeout, code, input
output keys are: status, exec_time, output, error_msg
'''

def Execute(codeInfo, retDict = None):

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

    signal.alarm(timeLimit)

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
        execTime = timeit.timeit(pyCode, number=1)
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        retVal = {'status': 'success', 'exec_time': execTime, 'output':mystdout.getvalue(), 'error_msg':''}
    except SyntaxError as err:
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        # print('sytax err')
        # print(err)
        retVal = {'status': 'syntax error', 'exec_time': execTime, 'output':mystdout.getvalue(), 'error_msg': '*** syntax error:\n' + str(err)}
    except Exception as exc:
        sys.stdout = old_stdout
        sys.stdin = old_stdin
        if (exc == 'timeout'):
            retVal = {'status': 'timout', 'exec_time': timeLimit, 'output':mystdout.getvalue(), 'error_msg': '*** execution timeout!'}
        else:
            retVal = {'status': 'runtime error', 'exec_time': execTime, 'output':mystdout.getvalue(), 'error_msg': '*** runtime error:\n' + str(exc)}
    
    # print('mystdout:', mystdout.getvalue())

    if (not retDict is None):
        retDict['res'] = retVal
        
    return retVal



def main():
    if (len(sys.argv) < 2):
        print('need a json arguement!')
        exit(1)
    
    try:
        arg = sys.argv[1]
        print(arg)
        exit(1)
        arg['id']
        arg['timeout']
        arg['code']
        arg['input']
        print(Execute(arg))
    except NameError:
        print('invalid arguments')
    except KeyError:
        print('wrong json content')


if __name__ == "__main__":
    main()