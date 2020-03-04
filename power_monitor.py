import time
from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.VoltageInput import *

voltage = 0
current = 0


def on_new_voltage_reading(self, voltage_update):
    global voltage
    voltage = voltage_update


def on_new_current_reading(self, current_update):
    global current
    current = current_update * 75.85973 - 37.76251


def main():
    global current, voltage

    voltage_sensor = VoltageInput()
    current_sensor = VoltageRatioInput()

    voltage_sensor.setHubPort(0)
    voltage_sensor.setIsHubPortDevice(False)
    voltage_sensor.setOnVoltageChangeHandler(on_new_voltage_reading)

    current_sensor.setHubPort(1)
    current_sensor.setIsHubPortDevice(True)
    current_sensor.setOnVoltageRatioChangeHandler(on_new_current_reading)


    #voltage_sensor.openWaitForAttachment(1000)
    current_sensor.openWaitForAttachment(1000)

    file = open("power_data.txt", "a")

    try:
        while True:
            time.sleep(0.05)
            message = "voltage: %f ; current: %f ; power: %f" % (voltage, current, voltage * current)
            print(message)
            file.write(message + "\n")

    except KeyboardInterrupt:
        print("Ending Program")
    file.close()
    voltage_sensor.close()
    current_sensor.close()


main()
