from sys import stdin, stdout
from math import *
import RPi.GPIO as GPIO
import time
import requests

# ang1, ang2, ang3, ang4 -> angle of long rod, angle of small rod, angle of base, angle of string
# EVERYTHING IS IN METRES

#webaddress = 'http://192.168.0.101:8000/coordinates'
webaddress = 'http://192.168.2.48:8000/coordinates'
x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur = 0.0, 0.0, 0.0, 0.0, 90.0, 0.0, 0.0
len1, len2 = 0.985, 0.40
heightBase, heightFunnel = 0.135, 0.43
depthFin = 1.3
angArmCur, angArmFin = 0.0, 0.0
angBigArmFin = 0.0
angScoop = 0.0
heightOrg = 1.015
global angBase
angBase = 0.0
testAng, testDist, angArmSoil, angBigArmSoil = 0.0, 0.0, 0.0, 0.0
clawAng = 0

print("Start Arm Movement")

def get():
    r = requests.get(webaddress)
    data = r.json()

    x = float(data['coordinates']['x'])
    y = float(data['coordinates']['y'])
    angBaseFin = float(data['coordinates']['xyang'])
    distFin = float(data['coordinates']['xydist'])
    angBaseCur = float(data['coordinates']['Bang'])
    distCur = float(data['coordinates']['Bdist'])
    depthCur = float(data['coordinates']['depth'])
    testAng = float(data['coordinates']['Tang'])
    testDist = float(data['coordinates']['Tdist'])
    clawAng = float(data['coordinates']['Gang'])

    print(x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, testAng, testDist, clawAng)
    distFin -= 0.15
    distSoil = testDist
    distSoil -= 0.15
    temp = distSoil
    distSoil = sqrt(distSoil ** 2 + (heightBase - heightFunnel) ** 2)
    distFin = sqrt(distFin ** 2 + heightBase ** 2)
    angArmSoil = acos((pow(len1, 2) + pow(len2, 2) - pow(distSoil, 2)) / (2 * len1 * len2))
    angBigArmSoil = acos((pow(len1, 2) + pow(distSoil,2) - pow(len2, 2)) / (2 * len1 * distSoil))
    angArmFin = acos((pow(len1, 2) + pow(len2, 2) - pow(distFin, 2)) / (2 * len1 * len2))
    angBigArmFin = acos((pow(len1, 2) + pow(distFin,2) - pow(len2, 2)) / (2 * len1 * distFin))
    angBigArmSoil += acos(temp / distSoil)
    angArmFin *= 180.0 / pi
    angArmFin += 3
    angArmSoil *= 180.0 / pi
    angArmSoil -= 6
    
    #angArmFin -= 10.0
    
    #print("b", angArmFin)
    #return(angArmFin)
    
    return x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, angArmFin, angBigArmFin, testAng, angArmSoil, angBigArmSoil, clawAng


def Move360(angCur, angFin):
    if angCur < angFin:
        continuous.ChangeDutyCycle(7.53)
        time.sleep(0.05)
        print("a")
    else:
        continuous.ChangeDutyCycle(6.58)
        time.sleep(0.05)
        print("b")

def Move180(servo, angCur, angFin, interval, tm):
    if servo == base:
        global angBase
        if angCur > angFin:
            angBase -= interval
            servo.ChangeDutyCycle(angBase / 18.0 + 2.5)
            time.sleep(tm)
        else:
            angBase += interval
            servo.ChangeDutyCycle(angBase / 18.0 + 2.5)
            time.sleep(tm)
        return angBase
    if angCur > angFin:
        angCur -= interval
        servo.ChangeDutyCycle(angCur / 18.0 + 2.5)
        time.sleep(tm)
    else:
        angCur += interval
        servo.ChangeDutyCycle(angCur / 18.0 + 2.5)
        time.sleep(tm)
    return angCur

GPIO.setmode(GPIO.BOARD)

# Set-up Servos
pin_continuousservo = 11  # GPIO 17 #6.93 keeps it steady
pin_bigservo = 12  # GPIO 18
pin_clawservo = 13  # GPIO 27
pin_baseservo = 38  # GPIO 20

pin_bottomSwitch = 15
pin_topSwitch = 23 # GPIO 11

try:
    GPIO.setup(pin_continuousservo, GPIO.OUT)  # continuous servo
    GPIO.setup(pin_bigservo, GPIO.OUT)  # big servo
    GPIO.setup(pin_clawservo, GPIO.OUT)  # claw servo
    GPIO.setup(pin_baseservo, GPIO.OUT)  # base servo

    GPIO.setup(pin_bottomSwitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_topSwitch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    continuous = GPIO.PWM(pin_continuousservo, 50)
    big = GPIO.PWM(pin_bigservo, 50)
    claw = GPIO.PWM(pin_clawservo, 50)
    base = GPIO.PWM(pin_baseservo, 50)

    # set servos to default
    big.start(0.0)  # ninety degrees #23 degree difference
    claw.start(0.0)  # ninety degrees
    base.start(0.0)  # ninety degrees
    continuous.start(0)

    angBase = 110

    #x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, _ = get()
    #if angBaseCur > angBaseFin:
    #    angBase = 120.0
    
    #base.ChangeDutyCycle(12.5)
    #time.sleep(5)
    #print("life is life")
    #for i in range(300):
       	#print(angBase)
        #angBase = Move180(base, angBaseCur, angBaseFin, 0.2, 0.05)
    #print("wut")
    #time.sleep(100) 
    #continuous.ChangeDutyCycle(6.43)
    #time.sleep(2)
    
    state = False
    while True:
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, _, testAng, _, _, _ = get()
        angBaseFin *= (-0.44*sin(angBaseFin/180*pi*2)+1)
        angBaseFin -= 4
        angBase = Move180(base, angBaseCur, angBaseFin, 0.2, 0.01)
        print(angBase, angBaseFin, angBaseCur)
        time.sleep(0.05)
        if (state == True):
            if (abs(angBaseCur-angBaseFin) <= 0.75):
                break
            else:
                state = False
        elif (abs(angBaseCur-angBaseFin) <= 0.75):
            state = True
    
    #base.ChangeDutyCycle(11.8)
    #time.sleep(5)
    
    base.ChangeDutyCycle(0.0)
    time.sleep(2)
    

    #print("hooray!")
    
    #base.stop()

    #print("hooray!x2")

    time.sleep(2)

    x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, angBigArmFin, _, _, _, _, = get()

    heightFin = len1*sin(angBigArmFin)+0.37
    print(heightFin)
           
    while (depthCur > heightFin):
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, angBigArmFin, _, _, _, _ = get()
        print(depthCur, heightFin)
        Move360(depthCur, heightFin)
    
    continuous.ChangeDutyCycle(6.93)
    time.sleep(1.0)
    
    print("bob")
    print(clawAng, angBaseFin)
    
    state = False
    while True:
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, _, _, _, _, clawAng = get()
        if clawAng < 0.1:
            break
        angBase = Move180(base, clawAng, angBaseFin, 0.2, 0.1)
        print(angBase, clawAng, angBaseFin)
        time.sleep(0.05)
        if (state == True):
            if (abs(clawAng - angBaseFin) <= 0.5):
                break
            else:
                state = False
        elif (abs(clawAng - angBaseFin) <= 0.5):
            state = True
            
    base.ChangeDutyCycle(0.0)
    time.sleep(1)
    
    x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, angArmFin, _, _, _, _, _ = get()
    print("dist", distFin)
    print("angArmFin", angArmFin)

    angArmFin = ((angArmFin+6)-24.154)/1.1769

    while(abs(angArmCur-angArmFin) >= 0.2):
        angArmCur = Move180(big, angArmCur, angArmFin, 0.2, 0.01)
    
    Move360(2.0, 1.0)
    time.sleep(5.0)
    
    continuous.ChangeDutyCycle(0.0)
    time.sleep(2)

    claw.ChangeDutyCycle(2.5)
    time.sleep(2)
    
    claw.ChangeDutyCycle(0.0)
    
    while (depthCur < 0.95):
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, angBigArmFin, _, _, _, _ = get()
        print(depthCur, 0.95)
        Move360(depthCur, 0.95)
    
    continuous.ChangeDutyCycle(6.93)
    time.sleep(2)
    
    print("tada")
    
    state = False
    while True:
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, _, testAng, _, _, _ = get()
        testAng *= (-0.20*sin(testAng/180*pi*2)+1)
        testAng -= 4
        angBase = Move180(base, angBaseCur, testAng, 0.2, 0.1)
        print(angBase, testAng, angBaseCur)
        time.sleep(0.05)
        if (state == True):
            if (abs(angBaseCur-testAng) <= 0.75):
                break
            else:
                state = False
        elif (abs(angBaseCur-testAng) <= 0.75):
            state = True
    
    base.ChangeDutyCycle(0.0)
    time.sleep(2)
    
    x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, angArmFin, _, testAng, angArmSoil, angBigArmSoil, _ = get()
    print("dist", distFin)
    print("angArmSoil", angArmSoil)

    angArmSoil = (angArmSoil-24.154)/1.1769

    while(abs(angArmCur-angArmSoil) >= 0.2):
        angArmCur = Move180(big, angArmCur, angArmSoil, 0.2, 0.01)

    print("hooray!x2")
    
    #big.ChangeDutyCycle(6.93)
    time.sleep(2)
    
    x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, angBigArmFin, testAng, angArmSoil, angBigArmSoil, _ = get()
    print("a", angBigArmSoil)
    heightSoil = len1*sin(angBigArmSoil) + 0.3
    print(depthCur, heightSoil)

    while (depthCur > heightSoil):
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, angBigArmFin, testAng, angArmSoil, angBigArmSoil, _ = get()
        print("qq", depthCur, heightSoil)
        Move360(depthCur, heightSoil)
    
    print("bob")
    continuous.ChangeDutyCycle(6.93)
    time.sleep(1.0)
    
    state = False
    while True:
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, angArmFin, _, testAng, angArmSoil, angBigArmSoil, clawAng = get()
        if clawAng < 0.1:
            break
        angBase = Move180(base, clawAng, testAng, 0.2, 0.03)
        print(angBase, clawAng, testAng)
        time.sleep(0.05)
        if (state == True):
            if (abs(clawAng - testAng) <= 0.5):
                break
            else:
                state = False
        elif (abs(clawAng - testAng) <= 0.5):
            state = True

    base.ChangeDutyCycle(0.0)
    time.sleep(1)
    
    Move360(2.0, 1.0)
    time.sleep(0.3)
    
    continuous.ChangeDutyCycle(6.93)
    time.sleep(2)
    
    #claw = GPIO.PWM(pin_clawservo, 50)
    #claw.start(0.0)
    claw.ChangeDutyCycle(12.5)
    time.sleep(2)
    
    claw.ChangeDutyCycle(0.0)
    
    print("hmmm")
    
    while (depthCur < 0.95):
        x, y, angBaseFin, distFin, angBaseCur, distCur, depthCur, _, angBigArmFin, _, _, _, _ = get()
        print(depthCur, 0.95)
        Move360(depthCur, 0.95)
    
    continuous.ChangeDutyCycle(0.0)
#continuous.ChangeDutyCycle(7.5)
#time.sleep(2)
    
    GPIO.cleanup()
    
except KeyboardInterrupt:
    base.stop()
    claw.stop()
    continuous.stop()
    big.stop()
    print("stop")
    GPIO.cleanup()

#while True:
#    get()
#    print(x, y, angBaseFin, distFin, angBaseCur, distFin, depthCur)
#    time.sleep(1)

# while True:
#     get()
#     angBaseCur = Move180(base, angBaseCur, angBaseFin)
#     if (abs(angBaseCur-angBaseFin) < 0.2):
#         break
#
# get()

#angArmFin1 = get()
#angArmFin1 = 180-13.0
#time.sleep(5)

#while (abs(angArmCur-angArmFin) >= 0.1):
#    print(angArmCur)
#    angArmCur = Move180(big, angArmCur, angArmFin)
#big.ChangeDutyCycle(7.5)
