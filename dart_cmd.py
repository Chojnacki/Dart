#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 10 17:20:55 2017

@author: chojnaal
"""

import time
import dart as d
import random
#import vRazor

#dart = d.Dart()

coef = 10

def setHeading(dart, head):
    headOk = False
    tolerance = 5
    
    if head > 180:
        head = 180
    if head < -180:
        head = -180
    
    speed = 50
    while not headOk:
        headMes = dart.get_angles()
#        headMes = dart.get_angles() + 2 * coef * random.random() - coef
#        print(headMes)
        headErr = head - headMes
        
        if abs(headErr) < tolerance:
            headOk = True
            dart.motor(0,'left')
            dart.motor(0,'right')
        else:
            if (headErr > 0 and headErr < 180) or headErr < -180: #Turn left
                dart.motor(speed,'left', -1)
                dart.motor(speed,'right', 1)
            
            else: #Turn right
                dart.motor(speed,'left', 1)
                dart.motor(speed,'right', -1)
    
            time.sleep(0.1)



def setHeadingProp(dart, head, alpha = 2):
    headOk = False
    tolerance = 5
    
    if head > 180:
        head = 180
    if head < -180:
        head = -180
    
    maxSpeed = 130
    while not headOk:
        headMes = dart.get_angles()
#        headMes = dart.get_angles() + 2 * coef * random.random() - coef
#        print(headMes)
        headErr = head - headMes
        
        if (-180 < headErr < 180):
            delta = abs(headErr)
        else:
            delta = abs(headErr) - 180

        speed = delta * alpha
        if speed > maxSpeed:
            speed = maxSpeed
        
        if abs(headErr) < tolerance:
            headOk = True
            dart.motor(0,'left')
            dart.motor(0,'right')
        else:
            if (headErr > 0 and headErr < 180) or headErr < -180: #Turn left
                dart.motor(speed,'left', -1)
                dart.motor(speed,'right', 1)
            
            else: #Turn right
                dart.motor(speed,'left', 1)
                dart.motor(speed,'right', -1)
    
            time.sleep(0.1)
    print('fin set heading')
            
def giveHeadingProp(dart, head, alpha = 1.95):
    tolerance = 1
    
    if head > 180:
        head = 180
    if head < -180:
        head = -180
    
    maxSpeed = 130
    headMes = dart.get_angles()
    headErr = head - headMes
    
    if (-180 < headErr < 180):
        delta = abs(headErr)
    else:
        delta = abs(headErr) - 180

    speed = delta * alpha
    if speed > maxSpeed:
        speed = maxSpeed
    
    if abs(headErr) < tolerance:
        return 0, None
    else:
        if (headErr > 0 and headErr < 180) or headErr < -180:
            return speed, 'left'
        
        else: #Turn right
            return speed, 'right'
            
def goDartHeading(dart, head, speed, duration):
    setHeading(dart, head)
    t0 = time.time()
    t1 = time.time()
    while t1 - t0 < duration:
        left_speed = speed
        right_speed = speed
        turnSpeed, direction = giveHeadingProp(dart, head, speed/20)
#        print(turnSpeed)
        if direction:
            if direction == 'left':
                left_speed -= turnSpeed
                right_speed += turnSpeed
            elif direction == 'right':
                left_speed += turnSpeed
                right_speed -= turnSpeed
#        print(left_speed,right_speed)
        dart.motor(left_speed,'left')
        dart.motor(right_speed,'right')
                
        t1 = time.time()
        
    dart.motor(0,'left')
    dart.motor(0,'right')
#    dart.stop()
    print('fin heading')

def goLineOdo (dart, speed, duration):
    t0 = 0
    t1 = 0
    t0 = time.time()
    
    while t1-t0 <= duration:
        
        dart.motor(speed, 'left')
        dart.motor(speed, 'right')
        
        leftOdo = dart.get_odometers()[0]
        rightOdo = dart.get_odometers()[1]
        errOdo = abs(leftOdo-rightOdo)
        
        if errOdo < 6:
            time.sleep(0.2)
            
        else:
            if leftOdo > rightOdo:
                dart.motor(speed-7, 'left')
            else:
                dart.motor(speed-7, 'right')
        print(errOdo)        
        t1=time.time()          

if __name__ == "__main__":
    myDart = d.Dart()
    time.sleep(1)
#    t1 = time.time()
#    t2 = time.time()
#    while t2-t1<2:
#        setHeading(myDart, 180)
#        t2 = time.time()
    
#    setHeadingProp(myDart, 180, 1.92)
    goDartHeading(myDart, 90, 100, 3.5)
    goDartHeading(myDart, -90, 100, 7)
    goDartHeading(myDart, 90, 100, 3.5)
#    print(myDart.get_angles())

    time.sleep(2) # example do nothing for 2 seconds

    myDart.stop()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    