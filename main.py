from djitellopy import Tello
import atexit, time


tello = Tello()


def kill_switch():
    """Kills the drone at exit if it is still flying """
    if tello.is_flying == True:
        while tello.send_control_command("emergency") == False: # Internal method with return
            pass
        tello.is_flying = False # So that the API ends and the program quits
    



atexit.register(kill_switch)


tello.connect()
tello.is_flying = True
tello.takeoff()
print('tryk nu!!')
time.sleep(1)
tello.land()
