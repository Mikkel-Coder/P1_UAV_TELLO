import math
import pandas as pd
import numpy as np


def length_splitter(n:int, step:float, safe_dist:int, override_auto_step=False) -> np.array and int:
    """Takes a length of n, a step and a safetydistance to remove from both ends of n. If n divided by step has a remainder, the variable step
    will be automatically reduced to eliminate the remainder. Override_auto_step = True will lock the step as it is input.
    Override_auto_step is False by default, which is recommended to ensure equal spacing. Returns an array of n-coordinates"""
    
    left_of_n = n - safe_dist * 2 # subtracting by safe_dist "on both sides of the line" aka two times
    
    if override_auto_step == False:
        div_rounded_up = math.ceil(left_of_n / step) # division after safe_dist is subtracted. Then rounded up. This insures that the step will get
        # smaller later on
        new_step = left_of_n / div_rounded_up # by doing this, the new_step is a smaller length than step, giving us just one more datapoint and removing
        # the possibility of leaving an uneven space left towards the boundary set by safe_dist.
        step = new_step # assigns the newly found step

    amount_of_steps = int(left_of_n / step)
    
    if override_auto_step: # If for some reason it is more important to have integer steps, this loop will create an array with the values between 0
        # and the end of the line (left_of_n)
        n_coordinates = np.array(0) # creating the array
        for i in range(amount_of_steps):
            append_val = np.array((i + 1) * step) # the value to be appended to the array
            n_coordinates = np.append(n_coordinates, append_val)
    else:
        n_coordinates = np.linspace(start=0, stop=left_of_n, num=amount_of_steps + 1)

    return n_coordinates, step




x = 640 # cm
y = 520 # cm
# z = 150 # cm - bruges ikke endnu
sd = 20 # cm
step_dist = 50 # cm


x_coords, x_step_dist = length_splitter(n=x, step=step_dist, safe_dist=sd, override_auto_step=False)
print(f"x_coords: {x_coords}, and x_step_dist: {x_step_dist}")

y_coords, y_step_dist = length_splitter(n=y, step=step_dist, safe_dist=sd, override_auto_step=False)
print(f"y_coords: {y_coords}, and y_step_dist: {y_step_dist}")

"""
Noter til funktionen og overvejelser:
- Virker som den skal
- tænker ikke at errorhandling er nødvendig, hvis fx x=20 / step_dist=50 kommer zero division, hvilket ikke dur.
- evt er der ikke behov for mere end "amount_of_steps" og "step", da arrays kan laves af disse.
- Arrays kan evt bruges til visualiseringen som punkter i koordinatsystem
"""