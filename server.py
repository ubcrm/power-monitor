import time
import requests
import threading
import atexit
import json
import urllib

from flask import Flask, jsonify
from flask_cors import CORS

from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.VoltageInput import *

app = Flask(__name__)
CORS(app)

voltage = 0
current = 0
startTime = time.time()
serverUpdateThread = None

url = "http://power-monitor-phidgets.herokuapp.com/updateVals"
headers = {
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
            time.sleep(0.5)
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
    global voltage, current, startTime, headers
    while (True):
        try:
            jsonData = json.dumps({'current': current, 'voltage':voltage, 'power':voltage * current, 'time':time.time() - startTime}).encode("utf-8")
            req = urllib.request.Request(url, jsonData, headers)
            req.add_header('Content-Length', len(jsonData))
            res = urllib.request.urlopen(req)
            print(res)
        except Exception as e:
            print(e)
            pass

    return 0

def on_new_voltage_reading(self, voltage_update):
    global voltage
    voltage = voltage_update


def on_new_current_reading(self, current_update):
    global current
    current = current_update * 75.85973 - 37.76251

def exit_handler(voltage_sensor, current_sensor):
    global current, voltage, serverUpdateThread
    serverUpdateThread.join()

    if voltage_sensor is not None:
        voltage_sensor.close()
        
    if current_sensor is not None:
        current_sensor.close()

def main():
    global current, voltage, app, serverUpdateThread
    
    voltage_sensor = None
    current_sensor = None
    serverUpdateThread = StoppableThread(target=updateWebServer)

    try:
        voltage_sensor = VoltageInput()
        current_sensor = VoltageRatioInput()

        voltage_sensor.setHubPort(0)
        voltage_sensor.setIsHubPortDevice(False)
        voltage_sensor.setOnVoltageChangeHandler(on_new_voltage_reading)

        current_sensor.setHubPort(1)
        current_sensor.setIsHubPortDevice(True)
        current_sensor.setOnVoltageRatioChangeHandler(on_new_current_reading)

        current_sensor.openWaitForAttachment(1000)
        
        serverUpdateThread.start()

        atexit.register(exit_handler)
        app.run(host='0.0.0.0')
        voltage_sensor.close()
        current_sensor.close()
        
    except PhidgetException as e:
        print(e)
        exit_handler(voltage_sensor, current_sensor)
        
    except KeyboardInterrupt as key:
        print(key)
        exit_handler(voltage_sensor, current_sensor)

    #voltage_sensor.openWaitForAttachment(1000)
    

    #file = open("power_data.txt", "a")

    #try:
    #    while True:
    #        time.sleep(0.05)
    #        message = "voltage: %f ; current: %f ; power: %f" % (voltage, current, voltage * current)
    #        print(message)
    #        file.write(message + "\n")
    #
    #except KeyboardInterrupt:
    #    print("Ending Program")
    #file.close()
    
    

main()