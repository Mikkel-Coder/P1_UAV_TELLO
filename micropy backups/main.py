import machine
import utime

import time
import network
import ubinascii


led_pin = machine.Pin("LED", machine.Pin.OUT)

time_start = utime.time()

sleep_time = 0.1 # time between blinks
time_till_start = 3 # seconds before starting the actual script. Will take more like double this due to processing in the meantime and sleeping twice
n_cycles = int(time_till_start/ 2 / sleep_time) # deviding by 2 as there are 2 sleeps per cycle

for i in range(n_cycles):
    led_pin.value(1) # powers LED
    utime.sleep(sleep_time)
    led_pin.value(0)
    utime.sleep(sleep_time)

time_stop = utime.time()

time_taken = time_stop - time_start
print(f"time before measurements began was ~ {time_taken} seconds. {n_cycles} cycles of blinks were run")

led_pin.value(1) # powers LED after being done. Indicates the actual script is running now.

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# measuring
measurements = 10
measure_dict = {}
for i in range(measurements):
    measure_dict[i] = wlan.scan()
    #time.sleep(0.1)
    #print(f"måling nr: {i}")


# data handling
measured_router = 0
for i in range(measurements):
    for ap in measure_dict[i]:
        if ap[0] == bytes(b'AAU-1-DAY'):
            if measured_router == 0:
                measured_router = ap[1]
                print(f"found ap of same router: {ap[0]}, hex to ascii: {ap[1]}, and strength: {ap[3]}")
            elif ap[1] == measured_router:
                print(f"found ap of same router: {ap[0]}, hex to ascii: {ap[1]}, and strength: {ap[3]}")
                                
