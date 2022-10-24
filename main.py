from djitellopy import Tello
import atexit, time


tello = Tello()


def kill_switch():
    """Kills the drone at exit"""
    while tello.send_control_command("emergency") == False: # Internal method with return
        pass


atexit.register(kill_switch)


tello.connect()
tello.takeoff()
print('tryk nu!!')
time.sleep(8)
