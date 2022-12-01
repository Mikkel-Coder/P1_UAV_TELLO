from djitellopy import Tello
import atexit
from time import sleep


tello = Tello()


def kill_switch():
    """Kills the drone at exit if it is still flying"""
    if tello.is_flying == True: # the drone 'is flying' once takeoff is finished or simply if tello.is_flying is set to True
        # Internal method with return
        while tello.send_control_command("emergency") == False:
            pass
        tello.is_flying = False
        

atexit.register(kill_switch)


tello.connect()
print(f"Tello battery life: {tello.get_battery()}%")

tello.is_flying = True
tello.takeoff()
sleep(0.5)
print("tryk nu!")

tello.land()