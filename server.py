from flask import Flask, jsonify
from flask_cors import CORS

#import _thread
import threading
from random import randint
from random import seed

import atexit

from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.CurrentInput import *

app = Flask(__name__)
CORS(app)

current = None
voltage = None
power = None
seed(1)

currentThread = None
voltageThread = None
powerThread = None

voltageCh = None
currentCh = None

threads = [currentThread, voltageThread, powerThread]

@app.route('/getVals', methods=['GET'])
def getIandV():
    global current, voltage, power
    while (power == None):
        while (voltage == None):
            while (current == None):
                pass
    
    return jsonify({"current": current,"voltage": voltage, "power": power})

def getCurrentVal(ch):
    global current
    while True:
        current = ch.getCurrent()
        
def getVoltageVal(ch):
    global voltage
    while True:
        voltage = ch.getVoltage()
        
def calculatePower():
    global current, voltage, power
    while True:
        power = current * voltage
        
        
def exitHandler():
    global threads, voltageCh, currentCh
    
    if voltageCh is not None:
        voltageCh.close()
    
    if currentCh is not None:
        currentCh.close()
    
    for thread in threads:
        if thread is not None:
            thread.join()

if __name__ == "__main__":
    #_thread.start_new_thread(doThreading, ())
    voltageCh = VoltageInput()
    voltageCh.openWaitForAttachment(1000)
    
    currentCh = CurrentInput()
    currentCh.openWaitForAttachment(1000)
    
    currentThread = threading.Thread(target = getCurrentVal, args = (currentCh))
    voltageThread = threading.Thread(target = getVoltageVal, args = (voltageCh))
    powerThread   = threading.Thread(target = calculatePower, args = ())
    for thread in threads:
        if thread is not None:
            thread.start()
            
    atexit.register(exitHandler)
    app.run(threaded=True, debug=True, host='0.0.0.0')




