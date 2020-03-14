from flask import Flask, jsonify, send_file, render_template
from flask_cors import CORS

#import _thread
import threading

import atexit
import time

from Phidget22.Phidget import *
from Phidget22.Devices.VoltageInput import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *

app = Flask(__name__)
CORS(app)

current = 0
voltage = 0
power = 0

powerThread = None

'''
currentThread = None
voltageThread = None
powerThread = None

threads = [currentThread, voltageThread, powerThread]
'''

voltageCh = None
currentCh = None

# @app.route('/', methods=['GET'])
# def getIndex():
#     return render_template("index.html")

@app.route('/getVals', methods=['GET'])
def getIandV():
    global current, voltage, power
    # while (power == None):
    #     while (voltage == None):
    #         while (current == None):
    #             pass
    
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
        
def calculatePower(run_event):
    global current, voltage, power
    # while True:
    #     power = current * voltage

    while run_event.is_set():
        try:
            # time.sleep(0.5)
            power = current * voltage
            # print("power is {0}, current is {1}, voltage is {2}".format(power, current, voltage))
        except KeyboardInterrupt:
            break
        except:
            break
        
        
def exitHandler(run_event):
    global voltageCh
    global currentCh
    global powerThread

    run_event.clear()

    stopThread = 1
    
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
    
    run_event = threading.Event()
    run_event.set()

    try:
        # voltage channel initialization
        voltageCh = VoltageInput()
        voltageCh.setHubPort(0)
        voltageCh.setIsHubPortDevice(False)
        voltageCh.setOnVoltageChangeHandler(voltageChangeHandler)
        
        voltageCh.openWaitForAttachment(2000)
        
        # current channel initialization
        currentCh = VoltageRatioInput()
        currentCh.setHubPort(1)
        currentCh.setIsHubPortDevice(True)
        currentCh.setOnVoltageRatioChangeHandler(currentChangeHandler)
        
        currentCh.openWaitForAttachment(2000)

        powerThread  = threading.Thread(target = calculatePower, args=(run_event,))
        if powerThread is not None:
            powerThread.start()
            
        atexit.register(exitHandler, run_event)
        app.run(threaded=True, debug=True, host='0.0.0.0')

    except PhidgetException as PE:
        print("Phidget Exception:\n{0}".format(PE))
        exitHandler(run_event)

    except KeyboardInterrupt:
        print("keyboard interrupt")
        exitHandler(run_event)

    except Exception as e:
        print("Unknown exception:\n{0}".format(e))
        exitHandler(run_event)
    




