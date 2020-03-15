import time
import requests
import threading
import atexit
import json
import urllib
from random import randint
from random import seed
from retrying import retry
from datetime import datetime

from flask import Flask, jsonify
#from flask_cors import CORS

from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.VoltageInput import *

app = Flask(__name__)
#CORS(app)
seed(1)

voltage = 0
current = 0
startTime = time.time()
serverUpdateThread = None
s = requests.Session()

sessionFile = None

hadPhidgetException = False

url = "http://power-monitor-phidgets.herokuapp.com/updateVals"
header = {
    "Content-Type" : "application/json"
}


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(StoppableThread,self).join(*args, **kwargs)

    def run(self):
        while not self._stop_event.is_set():
            print("Still running!")
            time.sleep(0.15)
            updateWebServer()
        print("stopped!")

# @app.route('/getVals', methods=['GET'])
# def getValues():
#     global voltage, current, startTime
#     return jsonify({'current': current, 'voltage':voltage, 'power':voltage * current, 'time':time.time() - startTime})

# @app.route('/setTime', methods=['GET'])
# def resetTime():
#     global startTime
#     startTime = time.time()
#     return "OK"

def updateWebServer():
    global voltage, current, startTime, headers, app, url, s
    
    try:
        jsonData = {'current': current, 'voltage': voltage,
                    'power': current * voltage, 'time':time.time() - startTime}
        res = s.post(url, data=json.dumps(jsonData), headers=header)
        
        print(res.text)
        if res.text.split(" ")[1] == "true":
            print('reseting start time')
            startTime = time.time()
            
    except Exception as e:
        print(e)
        pass

def on_new_voltage_reading(self, voltage_update):
    global voltage, current, sessionFile
    voltage = voltage_update
    if sessionFile is not None:
        power = voltage * current
        sessionFile.write(str(power) + " W " + str(datetime.now()))


def on_new_current_reading(self, current_update):
    global current, voltage, sessionFile
    current = current_update * 75.85973 - 37.76251
    if sessionFile is not None:
        power = voltage * current
        sessionFile.write(str(power) + " W " + str(datetime.now()))

def exit_handler(voltage_sensor, current_sensor):
    global current, voltage, serverUpdateThread, sessionFile
    serverUpdateThread.join()

    if voltage_sensor is not None:
        voltage_sensor.close()
        
    if current_sensor is not None:
        current_sensor.close()

    if sessionFile is not None:
        sessionFile.close()
        
def retry_if_phidgets_exception():
    global hadPhidgetException
    return hadPhidgetException

@retry(retry_on_result=retry_if_phidgets_exception)
def main():
    global current, voltage, app, serverUpdateThread, hadPhidgetException, sessionFile
    
    hadPhidgetException = False
    
    voltage_sensor = None
    current_sensor = None
    serverUpdateThread = StoppableThread()
    
    sessionNum = 0
    
    with open("numSessions.txt", "r+") as numSessionsFile:
        sessionNum = int(numSessionsFile.read()) + 1
        print(sessionNum)
        numSessionsFile.seek(0)
        numSessionsFile.write(str(sessionNum))
        numSessionsFile.truncate()
        numSessionsFile.close()
        
    timestamp = datetime.now()
    sessionFile = open("Sessions/session"+ str(sessionNum)
                       + "_" + str(timestamp.month) + "-" + str(timestamp.day)
                       + "_" + str(timestamp.hour) + "-" + str(timestamp.minute) + "-" + str(timestamp.second) + ".txt", "w+")
    
    
    print("Session File created")

    try:
        voltage_sensor = VoltageInput()
        current_sensor = VoltageRatioInput()

        voltage_sensor.setHubPort(0)
        voltage_sensor.setIsHubPortDevice(False)
        voltage_sensor.setOnVoltageChangeHandler(on_new_voltage_reading)

        current_sensor.setHubPort(1)
        current_sensor.setIsHubPortDevice(True)
        current_sensor.setOnVoltageRatioChangeHandler(on_new_current_reading)

        voltage_sensor.openWaitForAttachment(1000)
        current_sensor.openWaitForAttachment(1000)
        
        serverUpdateThread.start()

        atexit.register(exit_handler)
        app.run(host='0.0.0.0')
        voltage_sensor.close()
        current_sensor.close()
        
    except PhidgetException as e:
        print(e)
        hadPhidgetException = True
        exit_handler(voltage_sensor, current_sensor)
        
    except KeyboardInterrupt as key:
        print(key)
        exit_handler(voltage_sensor, current_sensor)
        
    except IOError as e:
        print(e)
        exit_handler(voltage_sensor, current_sensor)
    
if __name__ == '__main__':
    main()