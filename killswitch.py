from djitellopy import Tello
import atexit, time


tello = Tello() 


def kill_switch():
    """Kills the drone at exit if it is still flying """
    if tello.is_flying == True: #checks if the tello drone is flying
        while tello.send_control_command("emergency") == False: 
            #.send_control_command - sends control command to Tello and wait for its reponse
            #'emergency' - stops all motors immediately
            #as long as the command has not gone through it will continue to try
            pass
        tello.is_flying = False # the API ends and the program quits
atexit.register(kill_switch) 
#register the function to be executed at termination
#to trigger press ctl + c


tello.connect() #connect to drone
tello.is_flying = True #sets the drone to flying
tello.takeoff() #the drone automatically takesoff
time.sleep(1) #adds delay in the execution of a program
#sleep is used to increase accuracy, as the drone sometimes 
#skips past a command and does not fully finish if 
#not given proper time.
tello.land() #the drone lands