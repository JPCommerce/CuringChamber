import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import datetime
import time

#Note: for some reason GPIO status = True is off/low and False is on/high

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

count = 0

print 'Starting Loop'
while (count < 10):
    h,t = dht.read_retry(dht.DHT22, 4)
    t = t*(9/5)+51 #temperature calibration correction of 17 degrees
    h = h+4        #humidity correction of 6%
    dmt = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    print 'Date/Time: ' ,dmt
    print 'Temp: {0:0.1f}*F Humidity: {1:0.1f}%'.format(t,h)
    time.sleep(10)
    count = count + 1
    
print 'Loop complete\n'
GPIO.cleanup()

import RPi.GPIO as GPIO
import Adafruit_DHT as dht
import datetime
import time

#Note: for some reason GPIO status = True is off/low and False is on/high

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

#setup GPIO device pins and test for 30 seconds
GPIO.setup(26, GPIO.OUT) #GPIO 26 used for Refrigeration #Maps to Relay4
GPIO.setup(19, GPIO.OUT) #GPIO 19 used for Humidifier #Maps to Realy 3
GPIO.setup(13, GPIO.OUT) #GPIO 13 used for Dehumidifier #Maps to Realy 2 
GPIO.setup(6, GPIO.OUT)  #GPIO 6 used for Heater #Maps to Realy 1
print 'GPIO pins 26(cooler), 19(humidifier), 13(dehumidifier), & 6(Heater) setup'
GPIO.output(26, False)  
GPIO.output(19, False)
GPIO.output(13, False)
GPIO.output(6, False)
time.sleep(30)
print 'GPIO controlled device tested for 30 seconds. If a device did not switch on there may be an issue.'

#turn off all devices
GPIO.output(26, True)  #commenting this out will leave the refrigerator on until the do check the temperature
GPIO.output(19, True)
GPIO.output(13, True)
GPIO.output(6, True)
print 'GPIO controlled devices switched off.'

#setup and test LED warning lights
GPIO.setup(21, GPIO.OUT) #High Temp Warning (Orange)
GPIO.setup(20, GPIO.OUT) #Low Temp Warning (Blue)
GPIO.setup(16, GPIO.OUT) #High Humidity Warning (Green)
GPIO.setup(12, GPIO.OUT) #Low Humidity Warning (Yellow)
time.sleep(5)
GPIO.output(21, True)
GPIO.output(20, True)
GPIO.output(16, True)
GPIO.output(12, True)


dmt = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
statusCooler = True
statusDehumidifier = True
statusHumidifier = True
statusHeater = True

count = 0
while (count < 10):
    h,t = dht.read_retry(dht.DHT22, 4)
    t = t*(9/5)+51 #temperature calibration correction of 17 degrees
    h = h+3        #humidity correction of 6%
    print 'Date/Time: ' ,dmt
    print 'Temp: {0:0.1f}*C Humidity: {1:0.1f}%'.format(t,h)

    #check for high temp and take action if required.
    if t > 56:
        print 'High temp condition exists: {0:0.1f}'.format(t)
        if statusCooler == False:
            if statusHeater == True:
                print 'Cooler already on and heater off, no action taken.'
            else:
                print 'Cooler already on deactivating heater.'
                GPIO.output(6, True)
                statusHeater = True
        else:
            GPIO.output(26, False)
            statusCooler = False
            if statusHeater == True:
                print 'Cooler activated and heater off.'
            else:
                print 'Cooler activated, deactivating heater.'
                GPIO.output(6, True)
                statusHeater = True

    #check for low temp and take action if required
    if t < 50:
        print 'Low temp condition exist: {0:0.1f}'.format(t)
        if statusCooler == True:
            print 'Cooler already off, no action taken.'
        else:
            statusCooler = True
            print 'Deactivating cooler.'
            GPIO.output(26, True)

    #check for extreme low temp and pulse heater until temperature is optimal
    if t < 45:
        while (t < 55):
            print 'Extreme low temp exists, pusling heater for 5 seconds.'
            GPIO.output(6, False)
            time.sleep(5)
            GPIO.output(6, True)
            time.sleep(5)
            h,t = dht.read_retry(dht.DHT22, 4)
            t = t*(9/5)+49 #temperature calibration correction of 17 degrees
            h = h+6        #humidity correction of 6%

        print 'Extreme low temp condition rectified.'             
            

    #check for high humidity and take action if required
    if h > 72:
        print 'High humidity condition exists: {0:0.1f}'.format(h)
        if statusDehumidifier == False:       
            if statusHumidifier == True:
                print 'dehumidifier already active and humidifier already off, no action taken.'
            else:
                print 'dehumidifier already active and humidifier deactivated.'
                GPIO.output(19, True)
                statusHumidifier = True
        else:
            GPIO.output(13, False)
            statusDehumidifier = False
            if statusHumidifier == True:
                print 'dehumidifier activated and verified humidifier is off.'
            else:
                print 'dehumidifier activated and humidifier deactivated.'
                GPIO.output(19, True)
                statusHumidifier = True

    #check for low humidity and take action if required
    if h < 68:
        print 'Low humidity condition exists: {0:0.1f}'.format(h)
        if statusDehumidifier == True:
            print 'dehumidifier already off.'
        else:
            print 'dehumidifier deactivated.'
            GPIO.output(13, True)
            statusDehumidifier = True

    #check for extreme low humidity
    if h < 60:
        print 'Extreme low humidity condition exists, pulsing humidifier for 30 seconds until optimal humidity achieved.'
        while (h < 70):
            print 'Extreme low humidity exists, pusling humidifier for 30 seconds.'
            GPIO.output(19, False)
            time.sleep(30)
            GPIO.output(19, True)
            time.sleep(10)
            h,t = dht.read_retry(dht.DHT22, 4)
            t = t*(9/5)+49 #temperature calibration correction of 17 degrees
            h = h+6        #humidity correction of 6%

        print 'Extreme low humidity condition rectified.' 

    time.sleep(10)
    count = count + 1
    
print 'Loop complete\n'
GPIO.cleanup()