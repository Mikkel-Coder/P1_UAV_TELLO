from djitellopy import tello

# From pc wifi hotspot
# SSID = 'gr155'
# PASS = '123456789gr155'
# drone = tello.Tello()
# drone.connect()
# drone.send_command_with_return(f"ap {SSID} {PASS}")


drone = tello.Tello('192.168.4.1')
drone.connect()
print(drone.get_battery())
