"""
Demo Flask application to test the operation of Flask with socket.io



===================

Updated 22 August 2023

+ Upgraded code to Python 3
+ Used Python3 SocketIO implementation
+ Updated CDN Javascript and CSS sources

"""




# Start with a basic flask app webpage.
#from gevent import monkey
#monkey.patch_all()

import eventlet
eventlet.monkey_patch()

async_mode = "eventlet"

from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
import time
from time import sleep
from threading import Thread, Event
import subprocess
import shlex



__author__ = 'slynn'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode="eventlet", logger=True, engineio_logger=True)


#Time generator thread
thread = Thread()
thread_stop_event = Event()

def SignalDataServer():
    """
    Generate a time string  every half second and emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    #Continuous output of date and time
    print("Serving Signal Data")
    continuity_errors = "0" 
    siglevel = ''
    snrlevel = ''
    dBm = -99.9
    snrdB = 0.1
    maxdBm = -99
    maxSNR = 5
    sigcount = 0
    snrcount = 0
    command = 'sh ./sigdata2.sh'
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)    
    while not thread_stop_event.isSet():
        output = process.stdout.readline()
        if output:
            output = output.decode()
            if ") Signal=" in output :
                sigcount = sigcount + 1
                if sigcount > 3 :
                    siglevel = output.split(') Signal=')[1].strip().split()[0]
                    print('level',siglevel)
                    dBm = float(siglevel.split('dBm')[0])
            if "C/N= " in output :
                snrlevel = output.split('C/N= ')[1].strip().split()[0]
                print('snrlevel =',snrlevel)
                snrdB = float(snrlevel.split('dB')[0])
            if "CONTINUITY errors: " in output:
                continuity_errors = output.split('CONTINUITY errors:')[1].strip().split()[0]
                print('continuity errors =',continuity_errors)
            if dBm > maxdBm :
                maxdBm = dBm
            if snrdB > maxSNR :
                maxSNR = snrdB
        
        if (snrlevel != '') and (siglevel != '') : 
            SignalData = 'Signal strength: ' + siglevel + '<br>  SNR: ' + snrlevel +'<br>'+ \
'Maximum  Signal: ' + str(maxdBm) + ' dBm\n' + ' SNR: ' + \
str(maxSNR) + ' dB<br>' + 'Continuity Count (10 minutes): ' + continuity_errors
            print(SignalData)
            socketio.emit('newdata', {'SignalData': SignalData}, namespace='/test')
            snrlevel = ''
            siglevel = ''
            continuity_errors = ''
            socketio.sleep(1)
#    subprocess.Popen.kill(process)


@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
#    return render_template('index.html')

#def content(): 
    with open('static/analysis.txt', 'r') as f: 
        return render_template('index.html', 
text=f.read()) 

@socketio.on('connect', namespace='/test')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

    #Start the time generator thread only if the thread has not been started before.
    if not thread.is_alive():
        print("Starting Thread")
        thread = socketio.start_background_task(SignalDataServer)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
 

if __name__ == '__main__':
#    socketio.run(app,host='192.168.1.210',port=5000)
    socketio.run(app,host='0.0.0.0',port=8088)
