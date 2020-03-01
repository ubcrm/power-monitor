import time
from Phidget22.Devices.DigitalOutput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.Devices.CurrentInput import *

voltage = 0
current = 0


def on_new_voltage_reading(self, voltage_update):
    global voltage
    voltage = voltage_update


def on_new_current_reading(self, current_update):
    global current
    current = current_update


def main():
    global current, voltage

    voltage_sensor = VoltageRatioInput()
    current_sensor = CurrentInput()

    voltage_sensor.setHubPort(0)
    voltage_sensor.setIsHubPortDevice(False)
    voltage_sensor.setOnVoltageRatioChangeHandler(on_new_voltage_reading)

    current_sensor.setHubPort(1)
    current_sensor.setIsHubPortDevice(False)
    current_sensor.setOnCurrentChangeHandler(on_new_current_reading)

    voltage_sensor.openWaitForAttachment(1000)
    current_sensor.openWaitForAttachment(1000)

    try:
        while True:
            time.sleep(0.15)
            print("voltage: %f ; current: %f ; power: %f" % (voltage, current, voltage * current))

    except KeyboardInterrupt:
        print("Ending Program")

    voltage_sensor.close()
    current_sensor.close()


main()
