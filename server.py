from flask import Flask, jsonify, send_file
from flask_cors import CORS

#import _thread
import threading
from random import randint
from random import seed

import atexit

from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *

app = Flask(__name__)
CORS(app)

current = None
voltage = None
power = None
seed(1)

'''
currentThread = None
voltageThread = None
powerThread = None

threads = [currentThread, voltageThread, powerThread]
'''

voltageCh = None
currentCh = None

@app.route('/', methods=['GET'])
def getIndex():
    return render_template("index.html")

@app.route('/getVals', methods=['GET'])
def getIandV():
    global current, voltage, power
    while (power == None):
        while (voltage == None):
            while (current == None):
                pass
    
    return jsonify({"current": current,"voltage": voltage, "power": power})

'''
def getCurrentVal(ch):
    global current
    while True:
        current = ch.getCurrent()
        
def getVoltageVal(ch):
    global voltage
    while True:
        voltage = ch.getVoltage()
   
'''

def currentChangeHandler(self, current_update):
    global current
    current = current_update * 75.85973 - 37.76251

def voltageChangeHandler(self, voltage_update):
    global voltage
    voltage = voltage_update
        
def calculatePower():
    global current, voltage, power
    while True:
        power = current * voltage
        
        
def exitHandler():
    global voltageCh, currentCh
    global powerThread
    
    if voltageCh is not None:
        voltageCh.close()
    
    if currentCh is not None:
        currentCh.close()
    
    if powerThread is not None:
        powerThread.join()
    '''
    for thread in threads:
        if thread is not None:
            thread.join()

    '''
    
if __name__ == "__main__":
    #_thread.start_new_thread(doThreading, ())
    
    try:
        # voltage channel initialization
        voltageCh = VoltageInput()
        voltageCh.setHubPort(0)
        voltageCh.setIsHubPortDevice(False)
        voltageCh.setOnVoltageChangeHandler(voltageChangeHandler)
        
        
        # current channel initialization
        currentCh = VoltageRatioInput()
        currentCh.setHubPort(1)
        currentCh.setIsHubPortDevice(True)
        currentCh.setOnVoltageRatioChangeHandler(currentChangeHandler)
        
        currentCh.openWaitForAttachment(1000)

    except PhidgetException as PE:
        print("Phidget Exception:\n{0}".format(PE))
        
    while True:
        power = current * voltage
    
    '''
    currentThread = threading.Thread(target = getCurrentVal, args = (currentCh))
    voltageThread = threading.Thread(target = getVoltageVal, args = (voltageCh))
    
    for thread in threads:
        if thread is not None:
            thread.start()
    '''
    
    powerThread   = threading.Thread(target = calculatePower, args = ())
    if powerThread is not None:
        powerThread.start()
        
    atexit.register(exitHandler)
    app.run(threaded=True, debug=True, host='0.0.0.0')




