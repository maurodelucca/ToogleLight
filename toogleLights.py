#!/usr/bin/env python

"""
Python source code - replace this with a description of the code and write the code below this text.
"""

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import unirest, json, time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

bridgeUrl = "http://192.168.11.124/api"
userId = "/2923e94030a763af3c09ed9029714b9f"

# Lights: Id Bridge Hue, Pin Button, Pin LED, Name
lights = {
        (1, 14, 12, "Entrada"),
        (2, 15, 16, "Pieza Papas"),
        (3, 18, 21, "Pieza Agustin")
        }

# Current all light's state
global currLightsState 

def updateAllLightsState():
    global currLightsState
    url = bridgeUrl + userId + "/lights"
    response = unirest.get(url, headers={ "Accept": "application/json" })
    currLightsState = response.body

def isLightOn(lightId):
    return currLightsState[str(lightId)]['state']['on']

def isLightReachable(lightId):
    return currLightsState[str(lightId)]['state']['reachable']

def setNewLightState(lightId, newState):
    url = bridgeUrl + userId + "/lights/" + str(lightId) + "/state"
    response = unirest.put(url, headers={ "Accept": "application/json" }, 
            params=json.dumps({ 
                "on": newState, 
                "bri": 254 
                })
            )

def toogleLight(lightId):
    if isLightReachable(lightId):
        currState = isLightOn(lightId)
        setNewLightState(lightId, not currState)
        return True
    else:
        return False

if __name__ == "__main__":
    # Setup lights
    for light in lights:
        GPIO.setup(light[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(light[1], GPIO.FALLING, bouncetime = 200)
        GPIO.setup(light[2], GPIO.OUT, initial=GPIO.LOW)

    try:
        while True:
            # Update lights status
            updateAllLightsState()

            for light in lights:
                try:
                    # Check if button was pressed
                    if GPIO.event_detected(light[1]):
                        if not toogleLight(light[0]):
                            # Informing of error during setting, probably led not reachable
                            for i in range(3):
                                time.sleep(0.1)
                                GPIO.output(light[2], GPIO.HIGH)
                                time.sleep(0.1)
                                GPIO.output(light[2], GPIO.LOW)
                    
                    # Update Light/LED status
                    GPIO.output(light[2], isLightReachable(light[0]) and isLightOn(light[0]))
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print e
                    pass

            time.sleep(0.5)
    except KeyboardInterrupt:
        print "Closing..."

    GPIO.cleanup()

