"""

+ Upgraded code to Python 3
+ Used Python3 SocketIO implementation
+ Updated CDN Javascript and CSS sources

"""
import gevent
# gevent.monkey_patch()
# from gevent.pywsgi import WGSIServer

async_mode = "gevent"

from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
import time
from time import sleep
# from eventlet import sleep
from threading import Thread, Event
import subprocess
import shlex

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

#turn the flask app into a socketio app
socketio = SocketIO(app, async_mode="gevent", logger=True, engineio_logger=True, threaded=True)


#Signal data server thread
thread = Thread()
thread_stop_event = Event()

# Add sleep to prevent conflict with /dev/dvb/adapter1 when restarting
# socketio.sleep(5)


def SignalDataServer():
    #Continuous output of signal data
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
    pid49_rate = ''
    pid65_rate = ''
    pid81_rate = ''
    command = 'sh ../sigdata3.sh'
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)    
    while not thread_stop_event.is_set():
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
            if ("   49  " in output) & ("bps " in output):
                pid49_rate = output.split(' p/s ')[1].strip().split()[0] + ' ' + \
                             output.split(' p/s ')[1].strip().split()[1] 
                print('PID 49 rate =',pid49_rate)
            if ("   65  " in output) & ("bps " in output):
                pid65_rate = output.split(' p/s ')[1].strip().split()[0] + ' ' + \
                             output.split(' p/s ')[1].strip().split()[1]
                print('PID 65 rate =',pid65_rate)
            if ("   81  " in output) & ("bps " in output):
                pid81_rate = output.split(' p/s ')[1].strip().split()[0] + ' ' + \
                             output.split(' p/s ')[1].strip().split()[1] 
                print('PID 81 rate =',pid81_rate)
        
        if (snrlevel != '') and (siglevel != '') : 
            SignalData = 'Signal strength: ' + siglevel + '<br>  SNR: ' + snrlevel +'<br>'+ \
'Maximum  Signal: ' + str(maxdBm) + ' dBm\n' + ' SNR: ' + \
str(maxSNR) + ' dB<br>' + 'Continuity Count (5 minutes): ' + continuity_errors + '<br>' \
+ 'PID 49 rate: ' + pid49_rate + '<br>' + 'PID 65 rate: ' + pid65_rate + '<br>' \
+ 'PID 81 rate: ' + pid81_rate
            print(SignalData)
            socketio.sleep(1)
            socketio.emit('newdata', {'SignalData': SignalData}, namespace='/test')
            snrlevel = ''
            siglevel = ''
            continuity_errors = ''
#            socketio.sleep(1)
           
#    thread_event.clear()
#    thread = None

@app.route('/')
def index():
    #only by sending this page first will the client be connected to the socketio instance
#    eventlet.sleep(1)
    with open('static/analysis.txt', 'r') as f: 
        return render_template('index.html', 
text=f.read()) 

thread = socketio.start_background_task(SignalDataServer)

#@socketio.on('connect', namespace='/test')
@socketio.on('connect')
def test_connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')

#Start the signal server thread only if the thread has not been started before.
#    eventlet.sleep(1)
#    if not thread.is_alive():
#        print("Starting Thread")

#thread = socketio.start_background_task(SignalDataServer)

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')
#    with thread_lock:
#        if thread is not None:
#            thread.join()
#            thread = None
 

if __name__ == '__main__':

    socketio.run(app,host='0.0.0.0',port=8088)

gevent.wait()