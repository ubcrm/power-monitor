from flask import Flask, jsonify
from flask_cors import CORS

import _thread
from random import randint
from random import seed

app = Flask(__name__)
CORS(app)

currentVal = None
voltageVal = None
powerVal = None
seed(1)

@app.route('/getVals', methods=['GET'])
def getIandV():
    global currentVal, voltageVal, powerVal
    while (powerVal == None):
        while (voltageVal == None):
            while (currentVal == None):
                pass

    while (powerVal is not currentVal * voltageVal):
        pass
    
    return jsonify({"current": currentVal,"voltage": voltageVal, "power": powerVal})


def getPhidgetValues():
    global currentVal, voltageVal, powerVal

    # change these values to get from phidget code
    currentVal = randint(0, 10)
    voltageVal = randint(0, 10)
    powerVal = currentVal * voltageVal

def doThreading():
    while True:
        getPhidgetValues()

if __name__ == "__main__":
    _thread.start_new_thread(doThreading, ())
    print("thread started")
    app.run(threaded=True, debug=True, host='0.0.0.0')




