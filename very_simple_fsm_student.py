import fsm
import time
import sys
import dart_cmd
import dart as d
import select

# use keyboard to control the fsm
#  w : event "Wait"
#  s : event "Stop"
#  g : event "Go" 

# global variables
f = fsm.fsm();  # finite state machine
timeout = 0.1

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def getKey():
    #tty.setcbreak(sys.stdin.fileno())
    c='s'
    cok=False
    if isData():
        c = sys.stdin.read(1)
        cok=True
    if str(c) == '\n':
        cok = False

    return cok,str(c)

user_dict = {"w":"Attendre","z":"Avancer","s":"Reculer","d":"TournerDroite","q":"TournerGauche"," ":"Arreter"}


if __name__== "__main__":
    myDart = d.Dart()
    myDart.tolerance = 2
    time.sleep(1)

    
 
    def wait():
#        print('test')
        myDart.motor(0,'left')
        myDart.motor(0,'right')
        newKey,val = getKey(); # check if key pressed
        event="Attendre" # define the default event
        if newKey:
            event = user_dict[val]
        return event 
 
    def forward(speed = 40):
#        dart.motor(speed,'left')
#        dart.motor(speed,'right')
        myDart.goLineEmpirique(speed, timeout)
        newKey,val = getKey(); # check if key pressed
        event="Avancer" # define the default event
        if newKey:
            event = user_dict[val]
        return event 

 
    def turnRight(angle = 90):
        
        myDart.rotation(speed = 80, sens = 1, duration = 1.15/3)
        
        
        # Code avec heading
#        angle_actuel = myDart.get_angles()
#        heading = angle_actuel - angle
#        myDart.setHeadingProp(heading)
        
        
        
        newKey,val = getKey(); # check if key pressed
        event="Attendre" # define the default event
        if newKey:
            event = user_dict[val]
        return event
 
    def turnLeft(angle = 90):
        
        
        myDart.rotation(speed = 80, sens = -1, duration = 1.15/3)
        
        
        # Code avec heading        
#        angle_actuel = myDart.get_angles()
#        heading = angle_actuel + angle
#        myDart.setHeadingProp(heading)
        
        
        
        

        newKey,val = getKey(); # check if key pressed
        event="Attendre" # define the default event
        if newKey:
            event = user_dict[val]
        return event   
        
    
    def turnRightStatic(angle = 90):
        
        myDart.rotation(speed = 80, sens = 1, duration = 1.15/2.1875)

        newKey,val = getKey(); # check if key pressed
        event="Attendre" # define the default event
        if newKey:
            event = user_dict[val]
        return event
 
    def turnLeftStatic(angle = 90):

        myDart.rotation(speed = 80, sens = -1, duration = 1.15/2.1875)

        newKey,val = getKey(); # check if key pressed
        event="Attendre" # define the default event
        if newKey:
            event = user_dict[val]
        return event  
    
 
    def backward(speed = 40):
#        dart.motor(-speed,'left')
#        dart.motor(-speed,'right')
        myDart.goLineEmpirique(-speed, timeout)
        newKey,val = getKey(); # check if key pressed
        event="Reculer" # define the default event
        if newKey:
            event = user_dict[val]
        return event 
    
    def end():
        pass


    
    
    # define the states
    f.add_state ("Idle")
    
    f.add_state ("Forward")
    
    f.add_state ("End")
    
    f.add_state ("Backward")
    
    f.add_state ("TournerGauche")
    
    f.add_state ("TournerDroite")

    
    # defines the events 
    f.add_event ("Attendre")
    f.add_event ("Avancer")
    f.add_event ("Reculer")
    f.add_event ("TournerDroite")
    f.add_event ("TournerGauche")
    f.add_event ("Arreter")
   
    # defines the transition matrix
    # current state, next state, event, action in next state
    
    f.add_transition ("Idle","Idle","Attendre",wait);
    f.add_transition ("Idle","Forward","Avancer",forward);
    f.add_transition ("Idle","TournerDroite","TournerDroite",turnRightStatic);
    f.add_transition ("Idle","TournerGauche","TournerGauche",turnLeftStatic);
    f.add_transition ("Idle","Backward","Reculer",backward);
    f.add_transition ("Idle","End","Arreter",end);


    f.add_transition ("Forward","Idle","Attendre",wait);
    f.add_transition ("Forward","Forward","Avancer",forward);
    f.add_transition ("Forward","TournerDroite","TournerDroite",turnRight);
    f.add_transition ("Forward","TournerGauche","TournerGauche",turnLeft);
    f.add_transition ("Forward","Backward","Reculer",backward);

    f.add_transition ("TournerDroite","Idle","Attendre",wait);
    f.add_transition ("TournerDroite","Forward","Avancer",forward);
    f.add_transition ("TournerDroite","TournerDroite","TournerDroite",turnRight);
    f.add_transition ("TournerDroite","TournerGauche","TournerGauche",turnLeft);
    f.add_transition ("TournerDroite","Backward","Reculer",backward);

    f.add_transition ("TournerGauche","Idle","Attendre",wait);
    f.add_transition ("TournerGauche","Forward","Avancer",forward);
    f.add_transition ("TournerGauche","TournerDroite","TournerDroite",turnRight);
    f.add_transition ("TournerGauche","TournerGauche","TournerGauche",turnLeft);
    f.add_transition ("TournerGauche","Backward","Reculer",backward);

    f.add_transition ("Backward","Idle","Attendre",wait);
    f.add_transition ("Backward","Forward","Avancer",forward);
    f.add_transition ("Backward","TournerDroite","TournerDroite",turnRight);
    f.add_transition ("Backward","TournerGauche","TournerGauche",turnLeft);
    f.add_transition ("Backward","Backward","Reculer",backward);


    # initial state
    f.set_state ("Idle") # ... replace with your initial state
    # first event
    f.set_event ("Attendre") # ...  replace with you first event 
    # end state
    end_state = "End" # ... replace  with your end state

    
            # fsm loop
    run = True   
    previousState = False
    while (run):
        avoid = myDart.obstcleAVoid()
        if (avoid == False): # si il n'y a plus d'obstacle mais qu'il y en avait avant, on avance
#            print(False)
            ######################################################################################
            if previousState:
#                print('etat avant l\'evitement',previousState)
                f.set_state("Forward")
                f.set_event("Avancer")
                previousState = False
            pass
        elif avoid == 'Right' and (f.curState != "Idle"):
#            print('evitement a droite')
            f.set_state("TournerDroite")
            f.set_event("TournerDroite")
            previousState = True
        elif avoid == 'Left' and (f.curState != "Idle"):
#            print('evitement a gauche')
            f.set_state("TournerGauche")
            f.set_event("TournerGauche")
            previousState = True
        time.sleep(timeout)
        funct = f.run () # function to be executed in the new state
        if f.curState != end_state:
            newEvent = funct() # new event when state action is finished
            if f.curEvent != newEvent:
                print ("New Event : ",newEvent)
            f.set_event(newEvent) # set new event for next transition
        else:
            funct()
            run = False
    
    

            
    print ("End of the programm")



