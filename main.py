from djitellopy import Tello
import atexit, time


tello = Tello()


def kill_switch():
    """Kills the drone at exit if it is still flying"""
    if tello.is_flying == True:
        # Internal method with return
        while tello.send_control_command("emergency") == False:
            pass


atexit.register(kill_switch)


tello.connect()
tello.takeoff()
print('tryk nu!!')
time.sleep(8)
tello.land()
