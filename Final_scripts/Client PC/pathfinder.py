import numpy as np

def length_splitter(n:int, step:float, override_auto_step=False) -> float and int:
    """
    Takes a length of n and a step. If n divided by step has a remainder, the variable step
    will be automatically reduced to eliminate the remainder. Override_auto_step = True will lock the step as it is input.
    Override_auto_step is False by default, which is recommended to ensure equal spacing. Returns an a float step and the amount of steps on the line.
    
    Inputs:
    ---
    - n is a length in centimeters.
    - step is the distance between each point on line n in centimeters
    - override_auto_step will lock step to the input value if set to True

    Returns:
    ---
    - step
    - amount of steps is int(n / step)
    """
    
    if override_auto_step == False:
        div_rounded_up = np.ceil(n / step) # This insures that the step will get smaller later on
        # by doing this, the new_step is a smaller length than step, giving us just one more datapoint and removing
        # the possibility of leaving an uneven space left towards the boundary set by safe_dist.
        step = n / div_rounded_up # assigns the newly found step

    amount_of_steps = int(n / step)
    
    if override_auto_step: # If for some reason it is more important to have integer steps, this loop will create an array with the values between 0
        # and the end of the line (n)
        n_coordinates = np.array(0)
        for i in range(amount_of_steps):
            append_val = np.array((i + 1) * step)
            n_coordinates = np.append(n_coordinates, append_val)
    else:
        n_coordinates = np.linspace(start=0, stop=n, num=amount_of_steps + 1)

    return step, amount_of_steps


def path(x:int, y:int, step_dist:float) -> str:
    """
    Creates a 2D Manhattan grid command list for the drone to fly in. It returns said list.

    inputs:
    ---
    - x is a length in centimeters to be passed into length_splitter as n
    - y is a length in centimeters to be passed into length_splitter as n
    - step_dist is the distance between each point on line n in centimeters. Is passed into length_splitter as step
    
    Returns:
    ---
    - A string with the commands for the drone to fly in.
    """
    
    x_step_dist, x_amount_of_steps = length_splitter(n=x, step=step_dist, override_auto_step=False)
    y_step_dist, y_amount_of_steps = length_splitter(n=y, step=step_dist, override_auto_step=False)

    direction = 1 # direction = 1 means to turn Right (clockwise 90). 0 means Left (counterclockwise 90)
    cmd_list = "cmd_lst, command, takeoff,"

    for i in range(y_amount_of_steps + 1):
        if i == max(range(y_amount_of_steps + 1)):
            cmd_list += (f"forward {round(x_step_dist)},") * x_amount_of_steps + ("land")
            
        elif direction == 1: # turning right
            cmd_list += (f"forward {round(x_step_dist)},") * x_amount_of_steps + ("cw 90,") + (f"forward {round(y_step_dist)},") + ("cw 90,")
            direction = 0
            
        else: # turning left
            cmd_list += (f"forward {round(x_step_dist)},") * x_amount_of_steps + ("ccw 90,") + (f"forward {round(y_step_dist)},") + ("ccw 90,")
            direction = 1
            
    return cmd_list
