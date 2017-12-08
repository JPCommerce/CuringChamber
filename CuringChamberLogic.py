#------------------------------------------------------------------------------
# Description: This script will validate temperature / humidity
#              and control devices accordingly.
# Author: James Pederson
# Date Create: 12/8/2017
# Modifications:
#------------------------------------------------------------------------------

# importations
import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import datetime
import time

# Note: for some reason GPIO status = True is off/low and False is on/high

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

# setup GPIO device pins and test for 30 seconds
GPIO.setup(26, GPIO.OUT)  # GPIO 26 used for Refrigeration #Maps to Relay4
GPIO.setup(19, GPIO.OUT)  # GPIO 19 used for Humidifier #Maps to Realy 3
GPIO.setup(13, GPIO.OUT)  # GPIO 13 used for Dehumidifier #Maps to Realy 2
GPIO.setup(6, GPIO.OUT)  # GPIO 6 used for Heater #Maps to Realy 1
# turn off all devices
GPIO.output(26, True)
GPIO.output(19, True)
GPIO.output(13, True)
GPIO.output(6, True)
print('Testing: \n')
print('GPIO Pin 26 - Relay 4: Cooler')
GPIO.output(26, False)
time.sleep(5)
GPIO.output(26, True)
print('GPIO Pin 19 - Relay 3: Humidifier')
GPIO.output(19, False)
time.sleep(5)
GPIO.output(19, True)
print('GPIO Pin 13 - Relay 2: Dehumidifier')
GPIO.output(13, False)
time.sleep(5)
GPIO.output(13, True)
print('GPIO Pin 06 - Relay 1: Heater\n')
GPIO.output(6, False)
time.sleep(5)
GPIO.output(6, True)

# setup and test LED warning lights
GPIO.setup(21, GPIO.OUT)  # High Temp Warning (Orange)
GPIO.setup(20, GPIO.OUT)  # Low Temp Warning (Blue)
GPIO.setup(16, GPIO.OUT)  # High Humidity Warning (Green)
GPIO.setup(12, GPIO.OUT)  # Low Humidity Warning (Yellow)
GPIO.output(21, False)
GPIO.output(20, False)
GPIO.output(16, False)
GPIO.output(12, False)
time.sleep(5)
GPIO.output(21, True)
GPIO.output(20, True)
GPIO.output(16, True)
GPIO.output(12, True)

# set time and relay status to determine if devices are on or off
dmt = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
statusCooler = True
statusDehumidifier = True
statusHumidifier = True
statusHeater = True

#function definitions:
# Title: get_temp
# Type: function
# return type: float
# Description: uses the Adafruit_DHT code to determine
#              temperature value from DHT22 sensor


def get_temp():
    tempOffset = 19  # temperature calibration correction
    h, t = dht.read_retry(dht.DHT22, 4)
    t = t * (9 / 5) + 32 + tempOffset
    return t

# Title: get_humidity
# Type: function
# return type: float
# Description: uses the Adafruit_DHT code to determine
#              humidity value from DHT22 sensor


def get_humidity():
    humidityOffset = 4  # humidity calibration correction
    h, t = dht.read_retry(dht.DHT22, 4)
    h = h + humidityOffset
    return h

# initialize loop counter and start loop
count = 0
while (count < 10):
    t = get_temp()
    h = get_humidity()
    print(('Date/Time: ', dmt))
    print(('Temp: {0:0.1f}*C Humidity: {1:0.1f}%'.format(t, h)))

    # check for high temp and take action if required.
    if t > 56:
        print(('High temp condition exists: {0:0.1f}'.format(t)))
        if statusCooler is False:
            if statusHeater is True:
                print('Cooler already on and heater off, no action taken.')
            else:
                print('Cooler already on deactivating heater.')
                GPIO.output(6, True)
                statusHeater = True
        else:
            GPIO.output(26, False)
            statusCooler = False
            if statusHeater is True:
                print('Cooler activated and heater off.')
            else:
                print('Cooler activated, deactivating heater.')
                GPIO.output(6, True)
                statusHeater = True

    # check for low temp and take action if required
    if t < 50:
        print(('Low temp condition exist: {0:0.1f}'.format(t)))
        if statusCooler is True:
            print('Cooler already off, no action taken.')
        else:
            statusCooler = True
            print('Deactivating cooler.')
            GPIO.output(26, True)

    # check for extreme low temp and pulse heater until temperature is optimal
    if t < 45:
        heatCount = 0
        while (t < 55 and heatCount < 10):
            print('Extreme low temp exists, pusling heater for 5 seconds.')
            GPIO.output(6, False)
            time.sleep(5)
            GPIO.output(6, True)
            time.sleep(5)
            t = get_temp()
            heatCount = heatCount + 1

        if heatCount < 9:
            print('Extreme low temp condition rectified.')
        else:
            print('Heater cycled 10 times, will cycle again if needed.')

    # check for high humidity and take action if required
    if h > 72:
        print(('High humidity condition exists: {0:0.1f}'.format(h)))
        if statusDehumidifier is False:
            if statusHumidifier is True:
                print('dehumidifier active/humidifier off, no action taken.')
            else:
                print('dehumidifier already active and humidifier deactivated.')
                GPIO.output(19, True)
                statusHumidifier = True
        else:
            GPIO.output(13, False)
            statusDehumidifier = False
            if statusHumidifier is True:
                print('dehumidifier activated and verified humidifier is off.')
            else:
                print('dehumidifier activated and humidifier deactivated.')
                GPIO.output(19, True)
                statusHumidifier = True

    # check for low humidity and take action if required
    if h < 68:
        print(('Low humidity condition exists: {0:0.1f}'.format(h)))
        if statusDehumidifier is True:
            print('dehumidifier already off.')
        else:
            print('dehumidifier deactivated.')
            GPIO.output(13, True)
            statusDehumidifier = True

    # check for extreme low humidity
    if h < 60:
        humidCount = 0
        while (h < 70 and humidCount < 10):
            print('Extreme low humidity, pusling humidifier for 30 seconds.')
            GPIO.output(19, False)
            time.sleep(30)
            GPIO.output(19, True)
            time.sleep(10)
            h = get_humidity()
            humidCount = humidCount + 1

        if humidCount < 9:
            print('Extreme low humidity condition rectified.')
        else:
            print('Humidifier cycled 10 times, will cycle again if needed.')

    time.sleep(10)
    count = count + 1

print('Loop complete/n')
GPIO.cleanup()

