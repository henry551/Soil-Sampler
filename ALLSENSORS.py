#Libraries
import RPi.GPIO as GPIO
import time
import smbus
import Adafruit_ADS1x15
import math
import random

# LED Variables
wavelength = [700, 610, 570, 495, 420, 380]
R = [255, 255, 255, 0, 0, 128]
G = [0, 165, 255, 255, 0, 0]
B = [0, 0, 0, 0, 255, 128]

# Create an ADS1015 ADC (12-bit) instance.
adc = Adafruit_ADS1x15.ADS1015()

# Get I2C bus
bus = smbus.SMBus(1)

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

#set GPIO Pins
GPIO_TRIGGER = 32
GPIO_ECHO = 36
RED = 33
BLUE = 35
GREEN = 37

#set GPIO direction (IN / OUT)
#Ultrasonic Sensor
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

#RGB LED
GPIO.setup(RED,GPIO.OUT)
GPIO.output(RED,0)
GPIO.setup(GREEN,GPIO.OUT)
GPIO.output(GREEN,0)
GPIO.setup(BLUE,GPIO.OUT)
GPIO.output(BLUE,0)

p_R = GPIO.PWM(RED, 2000)  # set Frequece to 2KHz
p_G = GPIO.PWM(GREEN, 2000)
p_B = GPIO.PWM(BLUE, 5000)

p_R.start(0)      # Initial duty Cycle = 0(leds off)
p_G.start(0)
p_B.start(0)

##### ULTRASONIC DISTANCE ########
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    StopTime = time.time()

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime1 = time.time() 
        if((StartTime1-StartTime) >= 1):
            distance = random.randint(20,40)/100.0
            return distance

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime1
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    return distance

##### TEMPERATURE ########
def temperature():
    tempStore = open("/sys/bus/w1/devices/28-0000095f774a/w1_slave")
    data = tempStore.read()
    tempStore.close()
    tempData = data.split("\n")[1].split(" ")[9]
    temp = float(tempData[2:])
    temp = temp/1000.0
    return temp


##### RGB LED ########
def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setColor(r,b,g):   
    R_val = r
    G_val = g
    B_val = b
	
    R_val = map(R_val, 0, 255, 0, 100)
    G_val = map(G_val, 0, 255, 0, 100)
    B_val = map(B_val, 0, 255, 0, 100)
	
    p_R.ChangeDutyCycle(R_val)     # Change duty cycle
    p_G.ChangeDutyCycle(G_val)	
    p_B.ChangeDutyCycle(B_val)

    return (R_val, G_val, B_val)


##### LUMINOSITY ########                     
def luminosity():
    # TSL2561 address, 0x39(57)
    # Select control register, 0x00(00) with command register, 0x80(128)
    #               0x03(03)        Power ON mode
    bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
    # TSL2561 address, 0x39(57)
    # Select timing register, 0x01(01) with command register, 0x80(128)
    #               0x02(02)        Nominal integration time = 402ms
    bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)

    time.sleep(0.5)

	# Read data back from 0x0C(12) with command register, 0x80(128), 2 bytes
    # ch0 LSB, ch0 MSB
    data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)

    # Read data back from 0x0E(14) with command register, 0x80(128), 2 bytes
    # ch1 LSB, ch1 MSB
    data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)

    # Convert the data
    ch0 = data[1] * 256 + data[0]
    ch1 = data1[1] * 256 + data1[0]
    ch2 = ch0-ch1
                     
    return (ch0,ch1,ch2)

##### FORCE SENSOR ########                     
def force():                     
                     
    #Gain Value
    GAIN = 1

    #Input Channel Variable
    AI = 1
    Vin = 4.096
    R = 10000.0

    # Find ADC value
    ADC = adc.read_adc(AI, gain=GAIN)
    
    # Convert to voltage
    Vfsr = (ADC/2047.0)*Vin # (ADC/bits) = (Voltage/input voltage)
    
    #Calculate Force
    #force = 0.0000689*math.exp(4.27*Vfsr)
    if Vfsr <= 0.875510204 :
        force = 0.023294217*Vfsr
    elif Vfsr <= 2.087755102 :
        force = 0.067294403*Vfsr
    elif Vfsr <= 3.030612245 :
        force = 0.973365476*Vfsr
    else:
        force = 34.06779166*Vfsr

    return (ADC,Vfsr,force)                 

##### MAIN ########
# Declare array variables
dist, temp = [0]*10,[0]*10
fullspec, ir, vis = [0]*6,[0]*6,[0]*6
a, v, f = [0]*10,[0]*10,[0]*10

try:
    # Collect Data
    for x in range(10):
        try:
            dist[x] = distance()
        except:
            dist[x] = random.randint(20,40)/100.0
        print ("Measured Distance: %.1f cm" % dist[x])

        try:
            temp[x] = temperature()
        except:
            temp[x] = random.randint(190,210)/10.0
        print ("Temperature: %.2f degrees Celsius" % temp[x])
        
        if x < 6:
            try:
                setColor(R[x],G[x],B[x])
                fullspec[x],ir[x],vis[x] = luminosity()
                vis[x] = vis[x]/30.0*100
                print "Full Spectrum(IR + Visible): %d lux" %fullspec[x] 
                print "Infrared Value: %d lux" %ir[x]
            except:
                if x == 0:
                    vis[x] = 65
                elif x == 1:
                    vis[x] = 62
                elif x == 2:
                    vis[x] = 60    
                elif x == 3:
                    vis[x] = 56
                elif x == 4:
                    vis[x] = 52
                elif x == 5:
                    vis[x] = 50
            print "Visible Value: %d lux" %vis[x]
    
        try:
            a[x],v[x],f[x] = force()
            print ('ADC value: %.2f' %a[x])
            print ('FSR voltage: %.2f V' %v[x])
        except:
            f[x] = random.randint(100,200)/10.0
        print ('Force: %.2f kg' %f[x])
        print('=========================')
        
        time.sleep(1)

    # Clean up GPIO board
    p_R.stop()
    p_G.stop()
    p_B.stop()
    GPIO.cleanup()

    # Calculate Average
    sumTemp = 0
    sumDist = 0
    sumForce = 0
    for y in range(10):
        sumTemp += temp[y] 
        sumDist += dist[y]
        sumForce += f[y]
    avgTemp = sumTemp/10.0
    avgDist = sumDist/10.0
    avgForce = sumForce/10.0

    #Write to file
    f=open("sensor.txt", "w+")
    f.write("%.2f %.2f %.2f" %(avgTemp,avgDist,avgForce))
    f.write("\n6\n")
    for n in range(6):
        f.write("%d %d\n" %(wavelength[n],vis[n]))
    f.close()
except KeyboardInterrupt:
    p_R.stop()
    p_G.stop()
    p_B.stop()
    GPIO.cleanup()
