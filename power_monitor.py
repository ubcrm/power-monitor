import time

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

@app.route('/getVals', methods=['GET'])
def getValues():
    global voltage, current, startTime
    return jsonify({'current': current, 'voltage':voltage, 'power':voltage * current, 'time':time.time() - startTime})

@app.route('/setTime', methods=['GET'])
def resetTime():
    global startTime
    startTime = time.time()
    return "OK"

def on_new_voltage_reading(self, voltage_update):
    global voltage
    voltage = voltage_update


def on_new_current_reading(self, current_update):
    global current
    current = current_update * 75.85973 - 37.76251


def main():
    global current, voltage, app
    
    voltage_sensor = None
    current_sensor = None

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
        
        app.run(host='0.0.0.0')
        voltage_sensor.close()
        current_sensor.close()
        
    except PhidgetException as e:
        print(e)
        
    except KeyboardInterrupt as key:
        print(key)
        if voltage_sensor is not None:
            voltage_sensor.close()
            
        if current_sensor is not None:
            current_sensor.close()

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
