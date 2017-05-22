#!/usr/bin/python
# -*- coding: utf-8 -*-

# Second Year ENSTA Bretagne SPID Project
#    D : Brian Detourbet
#    A : Elouan Autret
#    A : Fahad Al Shaik
#    R : Corentin Rifflart
#    R : Clément Rodde
#    T : Rémi Terrien

# Code modified in May 2016, by BenBlop (small changes to conform with
#  new DART)

# Code modified in May 2017, by BenBlop (big changes to adapt to Irvin's
# drivers and to communicate with V-REP using sockets

# student starting code

import os
import time
import math
import struct
import sys

def high_low_int(high_byte, low_byte):
    '''
    Convert low and low and high byte to int
    '''
    return (high_byte << 8) + low_byte

def high_byte(integer):
    '''
    Get the high byte from a int
    '''
    return integer >> 8


def low_byte(integer):
    '''
    Get the low byte from a int
    '''
    return integer & 0xFF

class Dart():
    def __init__(self):

        
        # test if on real robot, if yes load the drivers
#        if os.access("/var/www/daarrt.conf", os.F_OK) :
        if os.access("/sys/class/gpio/gpio266", os.F_OK) :
            print ("Real DART is being created")

            # Import modules
            from drivers.trex import TrexIO
            from drivers.sonars import SonarsIO
            from drivers.razor import RazorIO
            from drivers.rear_odo import RearOdos

            self.__trex = TrexIO()
            self.__sonars = SonarsIO()
            self.__razor = RazorIO()
            self.__rear_odos = RearOdos()
            self.__trex.command["use_pid"] = 0 # 1
            self.tolerance = 5
            self.minSpeed = 50

        # if not create virtual drivers for the robot running in V-REP
        else :
            print ("Virtual DART is being created")

            import threading

            import socket
            import sys
            import struct
            import time
 
            # socket connection to V-REP
            self.__HOST = 'localhost'  # IP of the sockect
            self.__PORT = 30100 # port (set similarly in v-rep)
            self.minSpeed = 50

            self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print ('Socket created')

            # bind socket to local host and port
            try:
                # prevent to wait for  timeout for reusing the socket after crash
                # from :  http://stackoverflow.com/questions/29217502/socket-error-address-already-in-use
                self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.__s.bind((self.__HOST, self.__PORT))
            except socket.error as msg:
                print (msg)
                sys.exit()
            print ('Socket bind completed')
             
            # start listening on socket
            self.__s.listen(10)
            print ('Socket now listening')

            # reset variables 
            self.__vMotorLeft =  0.0
            self.__vMotorRight = 0.0
            self.__vEncoderLeft = 0
            self.__vEncoderRight = 0
            self.__vSonarLeft = 0.0
            self.__vSonarRight = 0.0
            self.__vSonarFront = 0.0
            self.__vSonarRear = 0.0
            self.__vHeading =  0.0

            # initiate communication thread with V-Rep
            self.__simulation_alive = True
            a = self.__s
            vrep = threading.Thread(target=self.vrep_com_socket,args=(a,))
            vrep.start()

            # start virtual drivers 
            import vDaarrt.modules.vTrex as vTrex
            import vDaarrt.modules.vSonar as vSonar
            import vDaarrt.modules.vRazor as vRazor

            self.__trex = vTrex.vTrex()
            self.__razor = vRazor.vRazorIO()
            self.__sonars = vSonar.vSonar(self)



    @property
    def s(self):
        return self.__s

    @property
    def vMotorLeft(self):
        return self.__vMotorLeft

    @property
    def vMotorRight(self):
        return self.__vMotorRight

    @property
    def vSonarFront(self):
        return self.__vSonarFront

    @property
    def vSonarRear(self):
        return self.__vSonarRear

    @property
    def vSonarLeft(self):
        return self.__vSonarLeft

    @property
    def vSonarRight(self):
        return self.__vSonarRight

    @property
    def vEncoderLeft(self):
        return self.__vEncoderLeft

    @property
    def vEncoderRight(self):
        return self.__vEncoderRight

    @property
    def simulation_alive(self):
        return self.__simulation_alive

    @property
    def vHeading(self):
        return self.__vHeading

    @property
    def angles(self):
        return self.__razor.angles 
    
    def vrep_com_socket(vdart,s):
        print (s)
        RECV_BUFFER = 4096 # buffer size 
        while True:
            #wait to accept a connection - blocking call
            conn, addr =  s.accept()
            print ('Connected with ' + addr[0] + ':' + str(addr[1]))
            #print (conn)

            while True:
                #print ("socket read",conn)
                data = conn.recv(RECV_BUFFER)
                #print (len(data))
                hd0,hd1,sz,lft,vSonarFront, vSonarRear,vSonarLeft, vSonarRight, vEncoderLeft, vEncoderRight, vHeading, simulationTime = struct.unpack('<ccHHffffffff',data)
                #print (hd0,hd1,sz,lft,vSonarFront, vSonarRear,vSonarLeft, vSonarRight, vEncoderLeft, vEncoderRight, vHeading, simulationTime)

                #print (vEncoderLeft, vEncoderRight, vHeading)

                vdart.vrep_update_sim_param (vEncoderLeft,vEncoderRight,vSonarLeft,vSonarRight,vSonarFront,vSonarRear,vHeading)

                vMotorLeft = vdart.vMotorLeft
                vMotorRight = vdart.vMotorRight

                strSend = struct.pack('<BBHHff',data[0],data[1],8,0,vMotorLeft,vMotorRight)
                conn.send(strSend)
                if not vdart.simulation_alive:
                    break
                time.sleep(0.010)

            if not vdart.simulation_alive:
                break



    def vrep_update_sim_param (self,vEncoderLeft,vEncoderRight,vSonarLeft,vSonarRight,vSonarFront,vSonarRear,vHeading):
        self.__vEncoderLeft = vEncoderLeft
        self.__vEncoderRight = vEncoderRight
        self.__vSonarLeft = vSonarLeft
        self.__vSonarRight = vSonarRight
        self.__vSonarFront = vSonarFront
        self.__vSonarRear = vSonarRear
        self.__trex.status["left_encoder"] = vEncoderLeft
        self.__trex.status["right_encoder"] = vEncoderRight
        self.__vMotorLeft = self.__trex.command["left_motor_speed"]
        self.__vMotorRight = self.__trex.command["right_motor_speed"]
        self.__vHeading = vHeading

    # insert here your functions to control the robot using motors, sonars
    #  encoders and heading
    
    # ...
    def rotation(self,speed = 50, sens = 1, duration = 1):
        """
        sens = 1 -> sens horaire
        sens = -1 -> sens anti-horaire
        """
        t1 = time.time()
        t0= time.time()
    
        
        while t1-t0 <= duration:
            
            speed = speed % 250
            self.__trex.command ['left_motor_speed'] = speed * sens
            self.__trex.command ['right_motor_speed'] = -speed * sens
            self.__trex.i2c_write()
            t1 = time.time()
        
        self.motor(0,'left')
        self.motor(0,'right')
            

    def ligne_droite(self,speed = 50, sens = 1):
        speed = speed % 250
        self.__trex.command['left_motor_speed'] = speed * sens
        self.__trex.command['right_motor_speed'] = speed * sens
        self.__trex.i2c_write()
    
    def get_odometers(self):
        """
        renvoie la valeur de gauche puis de droite
        """
        left = self.__trex.status['left_encoder']
        right = self.__trex.status['right_encoder']
        self.__trex.i2c_read()
        return left,right
        
    def get_sonar(self,sonar_name):
        return self.__sonars.get_distance(sonar_name)
    
    def motor(self, speed, side, sens = 1):
        if speed < self.minSpeed and speed != 0:  #définition d'une vitesse minimale
            speed = self.minSpeed
        speed = int(speed)
        if side == 'left':
            self.__trex.command['left_motor_speed'] = speed * sens
        if side == 'right':
            self.__trex.command['right_motor_speed'] = speed * sens
        self.__trex.i2c_write()

    
    
    def get_angles(self):
        return - self.__razor.angles[0]

#    @property
#    def get_angles(self):
#        return - self.__razor.angles[0]

    def stop(self):
        print ("Game Over")
        # stop the connection to the simulator
        self.__simulation_alive = False
        # add a command to stop the motors
        # ...
        self.motor(0,'left')
        self.motor(0,'right')
        
    def setHeading(self, head):
#        print('setheading')
        headOk = False
        
        if head > 180:
            head = 180
        if head < -180:
            head = -180
        
        speed = 50
        while not headOk:
            headMes = self.get_angles()
#            print(headMes)
    #        headMes = self.get_angles() + 2 * coef * random.random() - coef
    #        print(headMes)
            headErr = head - headMes
            
            if abs(headErr) < self.tolerance:
                headOk = True
                self.motor(0,'left')
                self.motor(0,'right')
            else:
                if (headErr > 0 and headErr < 180) or headErr < -180: #Turn left
                    self.motor(speed,'left', -1)
                    self.motor(speed,'right', 1)
                
                else: #Turn right
                    self.motor(speed,'left', 1)
                    self.motor(speed,'right', -1)
        
                time.sleep(0.1)
    
    
    
    def setHeadingProp(self, head, alpha = 1.2):
#        print('setHeadingProp')
        headOk = False
        
        if head > 180:
            head = 180
        if head < -180:
            head = -180
        
        maxSpeed = 130
        while not headOk:
            headMes = self.get_angles()
    #        headMes = self.get_angles() + 2 * coef * random.random() - coef
    #        print(headMes)
            headErr = head - headMes
#            print('head',head)
#            print('headMes',headMes)
#            print('ERREUR',headErr)
            
            if (-180 < headErr < 180):
                delta = abs(headErr)
            else:
                delta = abs(headErr) - 180
    
            speed = delta * alpha
            if speed > maxSpeed:
                speed = maxSpeed
            if abs(headErr) < self.tolerance:
#                print('lmqksdfjqlmsdkfjqsdlmkfjqslmdkfjqmsldkfjqslmdf')
                headOk = True
                self.motor(0,'left')
                self.motor(0,'right')
            else:
                if (headErr > 0 and headErr < 180) or headErr < -180: #Turn left
                    self.motor(speed,'left', -1)
                    self.motor(speed,'right', 1)
                
                else: #Turn right
                    self.motor(speed,'left', 1)
                    self.motor(speed,'right', -1)
        
                time.sleep(0.1)
#        print('fin set heading')
                
    def giveHeadingProp(self, head, alpha = 1.95):
#        print('giveHeadingProp')
        
        if head > 180:
            head = 180
        if head < -180:
            head = -180
        
        maxSpeed = 130
        headMes = self.get_angles()
#        print(headMes)
        headErr = head - headMes
        
        if (-180 < headErr < 180):
            delta = abs(headErr)
        else:
            delta = abs(headErr) - 180
    
        speed = delta * alpha
        if speed > maxSpeed:
            speed = maxSpeed
        
        if abs(headErr) < self.tolerance:
            return 0, None
        else:
            if (headErr > 0 and headErr < 180) or headErr < -180:
                return speed, 'left'
            
            else: #Turn right
                return speed, 'right'
                
    def goDartHeading(self, head, speed, duration):
#        print('goDartHeading')
        self.setHeadingProp(head)
        t0 = time.time()
        t1 = time.time()
        while t1 - t0 < duration:
            left_speed = speed
            right_speed = speed
            turnSpeed, direction = self.giveHeadingProp(head, speed/20)
    #        print(turnSpeed)
            if direction:
                if direction == 'left':
                    left_speed -= turnSpeed
                    right_speed += turnSpeed
                elif direction == 'right':
                    left_speed += turnSpeed
                    right_speed -= turnSpeed
    #        print(left_speed,right_speed)
            self.motor(left_speed,'left')
            self.motor(right_speed,'right')
                    
            t1 = time.time()
            
        self.motor(0,'left')
        self.motor(0,'right')
    #    self.stop()
#        print('fin heading')

        

    def goLineOdo (self, speed, duration):
        t0 = 0
        t1 = 0
        t0 = time.time()
        
        while t1-t0 <= duration:
            
            self.motor(speed, 'left')
            self.motor(speed, 'right')
            
            leftOdo = self.get_odometers()[0]
            rightOdo = self.get_odometers()[1]
            errOdo = abs(leftOdo-rightOdo)
            
            if errOdo < 6:
                time.sleep(0.2)
                
            else:
                if leftOdo > rightOdo:
                    self.motor(speed-7, 'left')
                else:
                    self.motor(speed-7, 'right')
#            print(errOdo)        
            t1=time.time()    
            
    def goLineEmpirique (self, speed, duration):
        t0 = 0
        t1 = 0
        t0 = time.time()
        
        correction = 16*speed/40
        while t1-t0 <= duration:
            
            self.motor(speed+correction, 'left')
            self.motor(speed, 'right')
                  
            t1=time.time()    

    def obstcleAVoid(self,d = 0.5):
#        print(self.get_sonar('front'))        
        if self.get_sonar('front')<=d:
            self.motor(0,'left')
            self.motor(0,'right')
#            time.sleep(0.1)
            if self.get_sonar('right')<=d/2 and self.get_sonar('left')>=d/2:
#                self.rotation(90,-1,1.45)
                print('Left')
                return 'Left'
            elif self.get_sonar('left')<=d/2 and self.get_sonar('right')>=d/2:
#                self.rotation(90,1,1.45)
                print('Right')
                return 'Right'
            else:
#                self.rotation(90,1,1.45)
                print('DefaultCase')
                return 'Right'
        return False
      
       
        
if __name__ == "__main__":
    myDart = Dart()
    myDart.tolerance = 2
    time.sleep(1)

#    myDart.goDartHeading( 180, 40, 1)
#    myDart.goDartHeading( 90, 40, 1)
#    myDart.goDartHeading( 0, 40, 1)
#    myDart.goDartHeading( -90, 40, 1)
#    myDart.goDartHeading( -180, 40, 1)

#    myDart.goLineEmpirique(40, 3)
#     
#    myDart.rotation(90, 1, 2)
    
    time.sleep(1)
#    myDart = Dart()
    time.sleep(1)
    
    myDart.stop()
    time.sleep(1)
