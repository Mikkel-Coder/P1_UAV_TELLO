from djitellopy import tello
import time

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

time.sleep(3)
# drone.send_command_with_return("wifi gr155 wordpass")
