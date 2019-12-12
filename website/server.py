
from flask import Flask, request, Response, render_template, send_from_directory, jsonify
from execution import Execute
from subprocess import Popen, PIPE
from multiprocessing import Process, Manager


app = Flask(__name__, template_folder='.')

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

    return_dict = Manager().dict()
    p = Process(target=Execute, args=(data, return_dict))
    p.start()
    p.join()
    # print('output:')
    # print(output)

    print('res\n', return_dict['res'])
    
    return jsonify(return_dict['res'])

app.run(host='0.0.0.0', port=8888)

