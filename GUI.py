import PySimpleGUI as sg
import matplotlib 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
import numpy as np
import pandas as pd
from client import Client
from pathfinder import length_splitter, path
import time
import pickle


def amount_of_scans(command_str):
    amt_scans = 1 # 1 because of the takeoff command.
    command_list = command_str.split(',')
    for command in command_list:
        if 'forward' in command: # a scan before each forward command
            amt_scans += 1
    return amt_scans


def handle_answer(answer, search_ssid):

    answer = answer.split(' ')
    for i in range(len(answer)):
        try:
            answer[i] = answer[i].strip(" ,)(]['") # removes annoying characters from the string. The measured data is still intact
            answer[i] = float(answer[i]) # converts to float if possible
        except Exception:
            pass

    coords = tuple(answer[-2:]) # coords are secured
    del answer[-2:] # coords removed from OG list

    # every AP's scanresult is 5 or 6 parts long, so making a loop to save them to individual tuples in a dictionary
    scan_results = {
        'SSID' : [],
        'bSSID' : [],
        'RSSI' : [],
        'coordinates' : []
    }
    start = 0 # first index to save into the tuple of each accespoint

    for item in range(len(answer)):
        try:
            
            if type(answer[item]) == float and type(answer[item + 1]) == str: # if the current item is a float and the next is a string
                # then this is where the tuples should be seperate

                scan = tuple(answer[start : item + 1]) # saves results from 'start' to seperationpoint (after float, before string)
                scan_results['SSID'].append(scan[0] + "'")                
                scan_results['bSSID'].append((scan[1] + "'").encode('utf-8')) # gets bssid, but doesnt work currently. The formats are completely broken??
                scan_results['RSSI'].append(scan[-3])
                scan_results['coordinates'].append(coords)
                start += item - start + 1 # start is updated
                # ap += 1 # ap key is counted up 1 for the next accespoint
        except Exception:
            pass

    # print(scan_results, len(scan_results['SSID']), len(scan_results['RSSI']))
    # print(coords)
    df = pd.DataFrame(scan_results)
    search_data = df.loc[df['SSID'] == search_ssid]

    return search_data


def draw_figure(canvas, figure):
    """Draws figure on canvas for GUI"""
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def delete_fig(fig):
    """Deletes figure from plot"""
    fig.get_tk_widget().forget()
    plt.close('all')


def make_fig(df):
   
    fig, ax = plt.subplots()
    ax.plot(df['RSSI'], ".", label="data") # plots x as distance from first measurement and y as RSSI

    """x_data = np.array(df.index)
    x_data[0] = x_data[1] * 0.1 # x_data[0] will always be 0, but log(0) throws an error due to it being impossible.
    # Therefore we cheat a little by making it 10% of the next x_value
    y_data = df['RSSI']
    # Taking log of x values
    xlog_data =  (-1) * np.log(x_data)
    a, b = np.polyfit(xlog_data, y_data, 1)
    # print(xlog_data)
    # print(a, b)
    y = a * xlog_data + b
    # print(y)
    ax.plot(x_data, y, '--', label="log fit")"""

    ax.grid(True)
    ax.set_xlabel('distance (cm) from first measurement')
    ax.set_ylabel('signal strength RSSI (dBm)')
    ax.set_title(f"Graph of signalstrength of accespoint: {df['bssid'].iloc[0]}")
    ax.legend()
    fig.tight_layout() # makes it not overlap, if possible
    plt.close()


    return(fig)


def gui():
    """Creates the GUI itself. Error-handles and calls other functions when needed"""
    # Creates the layout with inputboxes and such

    layout = [[sg.Text('Length (cm):'), sg.Input(100, key = '-x-'),sg.Text('Width (cm):'), sg.Input(100, key = '-y-')],
            [sg.Text('Step distance (20-500 cm):'), sg.Input(50, key = '-step_dist-'), sg.Text('Safety distance to boundaries in cm:'), sg.Input(0, key = '-sd-')],

            [sg.Text('Choose SSID to plot:'), sg.Input("AAU-1-DAY", key = '-search_ssid-'),
            sg.Text('Choose graph variant:'), sg.Combo(['Heatmap', 'Fitted graph'], size=(20,1), readonly=True, default_value='Heatmap', key = '-variant-')],
            [sg.Button('1: Generate command list for drone'), sg.Button('2: Connect to drone'), sg.Button('3: Send command list')],
            [sg.Canvas(key = '-graph-')]]        

    # creates the window using the layout from above
    window = sg.Window('P1 UAV wifi probe visualization',
                        layout = layout,
                        finalize = True,
                        element_justification='center')

    fig_gui = None

    while True:
        event, values = window.read()
        
        if event == '1: Generate command list for drone':
            
            try: # Error handling
                # defining variables
                x = int(values['-x-'])
                y = int(values['-y-'])
                step_dist = int(values['-step_dist-'])
                sd = int(values['-sd-'])
                search_ssid = f"b'{values['-search_ssid-']}'"
                graph_type = str(values['-variant-'])
                print(x, y, step_dist, sd, search_ssid, graph_type)

                msg = path(x=x, y=y, step_dist=step_dist, sd=sd)
                print(msg)
                client = Client(msg=msg)
                time.sleep(1)
        
            except Exception as e:
                sg.Popup(f"Error in input: {e}") # creates pop-up that tells the user what is wrong, if an error occurs.
                client.close() # tries to close the client
        
        if event == '2: Connect to drone':
            time.sleep(1)
            try: # Error handling
                # connecting to the Pico
                client.sock_connect()
                time.sleep(2)
        
            except Exception as e:
                sg.Popup(f"Error in connecting to PicoW server: {e}") # creates pop-up that tells the user what is wrong, if an error is found.
                client.close()

        
        if event == '3: Send command list':
            if fig_gui != None:
                delete_fig(fig_gui) # if there is a figure on the GUI already then delete it when a new one is about to be created
            
            try: # Error handling
                print('Sending command list: ', client.cmd_lst)

                
                ans = client.send_cmd_list() # send_cmd_list returns the first scan from the Pico W.
                
                df = handle_answer(answer=ans, search_ssid=search_ssid) # returns RSSI and coords of specified ssid

                # finds out how many times to recieve data. If miscounted, client.recv_scan() will be stuck forever
                scan_amount = amount_of_scans(client.cmd_lst)
                print('amount of scans to conduct: ', scan_amount)
                for scan_num in range(scan_amount):
                    ans = client.recv_scan() # the scans are saved in an attribute of 'client' called scan_lst
                    df = handle_answer(answer=ans, search_ssid=search_ssid)
                
                print(client.scan_lst)

                print('Pickling raw scan data (client.scan_lst)...')
                hour, minute, second = time.localtime()[3:6]
                file = open(f'pickled_raw_data_{hour}_{minute}_{second}', 'wb')
                # dumping info
                pickle.dump(client.scan_lst, file)
                file.close()
                print('done pickling')

                """
                Write graphing code in here or above. Gør data til dataframe der gemmes til csv mellem hver scanning. Så kan data reddes.
                """
                
        
            except Exception as e:
                sg.Popup(f"Error in connecting to PicoW server: {e}") # creates pop-up that tells the user what is wrong, if an error is found.

                print('Pickling raw scan data (client.scan_lst)...')
                hour, minute, second = time.localtime()[3:6]
                file = open(f'pickled_raw_data_{hour}_{minute}_{second}', 'wb')
                # dumping info
                pickle.dump(client.scan_lst, file)
                file.close
                print('done pickling')
                client.close()
        

        # if the window is closed, break out of the while-loop, ending the script
        if event == sg.WIN_CLOSED:
            try:
                client.close()    # close the socket as the last thing after the closebutton is pressed pressed. This is the kill-switch!
                print('closing socket')
            except UnboundLocalError as e:
                print('UnboundLocalError: ', e)
                print('There was no socket to close.')
            break
        
    plt.close('all')
    window.close()

if __name__ == '__main__':
    try:
        gui()
    except KeyboardInterrupt as e:
        print('KeyboardInterrupt: ', e)

# fig = make_fig() # makes a figure with the values
# fig_gui = draw_figure(window['-graph-'].TKCanvas, fig) # draws said figure on the GUI