import PySimpleGUI as sg
import matplotlib 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
import numpy as np
import pandas as pd
import time
import pickle

# own files
from client import Client
from pathfinder import length_splitter, path
from gps_visualisation import create_map, create_circles, save_and_show_map


def amount_of_scans(command_str):
    amt_scans = 1 # starts at 1 because of the takeoff command
    command_list = command_str.split(',')
    for command in command_list:
        if 'forward' in command: # a scan before each forward command
            amt_scans += 1
    return amt_scans


def handle_answer(answer, search_ssid):

    answer = answer.split(',')
    for i in range(len(answer)):
        try:
            answer[i] = answer[i].strip(" )(]['") # removes annoying characters from the string. The measured data is still intact
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
    # print(answer)

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
    search_data.reset_index(inplace=True, drop=True)

    return search_data


def decimaldegrees_to_km(coords_tuple1, coords_tuple2):

    R = 6371 # earth's radius in km.
    
    # latitudes
    lat1 = np.radians(coords_tuple1[0])
    lat2 = np.radians(coords_tuple2[0])

    # longitudes
    long1 = np.radians(coords_tuple1[1])
    long2 = np.radians(coords_tuple2[1])

    lat_calc = ( np.sin( (lat2 - lat1) / 2) ) **2

    long_calc = (np.sin( (long2 - long1) / 2)) **2

    calc = np.sqrt( lat_calc + np.cos(lat1) * np.cos(lat2) * long_calc )

    d = 2 * R * np.arcsin(calc) # in km

    return d * 1000 * 100 # ganges til centimeter


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


def make_fig(df, step_dist):
   
   # The following has been outcommented due to poor GPS data
    """coords = df['coordinates']
    dist_list = [0] # starts with 0 as the first datapoint is at x = 0 on the x-axis
    for i in range(len(coords) - 1):
        dist_btwn_points = decimaldegrees_to_km(coords[i], coords[i + 1])
        dist_list.append(dist_btwn_points)"""

    dist_list = []
    for i in range(len(df['RSSI'])):
        dist_list.append(int(i*step_dist))

    fig, ax = plt.subplots()
    ax.plot(dist_list, df['RSSI'], ".", label="data") # plots x as distance from first measurement and y as RSSI

    x_data = dist_list
    x_data[0] = float(x_data[1] * 0.05) # x_data[0] will always be 0, but log(0) throws an error due to it being impossible.
    # print("This is x_data right before log:", x_data)
    # Therefore we cheat a little by making it 10% of the next x_value
    y_data = df['RSSI']
    # Taking log of x values
    xlog_data =  (-1) * np.log(x_data)

    # print(x_data, xlog_data, y_data)
    a, b = np.polyfit(xlog_data, y_data, 1)
    # print(xlog_data)
    # print(a, b)
    y = a * xlog_data + b
    # print(y)
    ax.plot(x_data, y, '--', label="log fit")

    ax.grid(True)
    ax.set_xlabel('distance (cm) from first measurement')
    ax.set_ylabel('signal strength RSSI (dBm)')
    ax.set_title(f"Graph of signalstrength of accespoint: {df['bSSID'].iloc[0]}")
    ax.legend()
    fig.tight_layout() # makes it not overlap, if possible
    plt.close()

    return(fig)


def gui():
    """Creates the GUI itself. Error-handles and calls other functions when needed"""
    # Creates the layout with inputboxes and such
    sg.theme('GreenMono')

    layout = [ 
            [sg.Text('Length and Width is the length and width of the Manhatten grid to fly in. Step distance is the distance between each cross-section in the grid')],
            [sg.Text('Write the name of the WiFi which you want to analyze in "Choose SSID to plot:". If you choose "Fitted graph" in "Choose graph variant",')],
            [sg.Text('the drone will fly in a straight line of given "length".')],
            [sg.Text('Length (cm):'), sg.Input(400, key = '-x-')],
            [sg.Text('Width (cm):'), sg.Input(100, key = '-y-')],
            [sg.Text('Step distance (20-500 cm):'), sg.Input(50, key = '-step_dist-')], 
            # [sg.Text('Safety distance to boundaries in cm:'), sg.Input(0, key = '-sd-')],
            [sg.Text('Choose SSID to plot:'), sg.Input("Marcus - iPhone", key = '-search_ssid-')],
            [sg.Text('Choose graph variant:'), sg.Combo(['Heatmap', 'Fitted graph'], size=(20,1), readonly=True, default_value='Fitted graph', key = '-variant-')],
            [sg.Text("[Optional] choose pickled dataframe to plot: "), sg.FileBrowse('load pickle', key = '-file-')],
            [sg.Button('1: Generate command list for drone'), sg.Button('2: Connect to drone'), sg.Button('3: Send command list'), sg.Button('[Optional] plot loaded pickle')],
            [sg.Canvas(key = '-graph-')]]     
 

    # creates the window using the layout from above
    window = sg.Window('P1 UAV wifi probe visualization',
                        layout = layout,
                        finalize = True,
                        element_justification='right')

    fig_gui = None

    while True:
        event, values = window.read()
        
        if event == '1: Generate command list for drone':
            
            try: # Error handling
                # defining variables
                x = int(values['-x-'])
                y = int(values['-y-'])
                step_dist = int(values['-step_dist-'])
                # sd = int(values['-sd-'])
                search_ssid = f"b'{values['-search_ssid-']}'"
                graph_type = str(values['-variant-'])
                print(x, y, step_dist, search_ssid, graph_type)

                msg = path(x=x, y=y, step_dist=step_dist, sd=0)

                if graph_type == 'Fitted graph':
                    first_turn = 0
                    for i in range(len(msg)):
                        if msg[i:i+5] == 'cw 90':
                            first_turn = i
                            break
                    # cuts of the rest of the list, making the drone only fly in a straight line
                    msg = msg[:first_turn]
                    msg = msg + "land"

                print(msg)
                client = Client(msg=msg)
                time.sleep(1)
        
            except Exception as e:
                sg.Popup(f"Error in input: {e}") # creates pop-up that tells the user what is wrong, if an error occurs.
                client.close() # tries to close the client
        
        if event == '2: Connect to drone':
            time.sleep(0.5)
            try: # Error handling
                # connecting to the Pico
                client.sock_connect()
                time.sleep(1)
        
            except Exception as e:
                sg.Popup(f"Error in connecting to PicoW server: {e}") # creates pop-up that tells the user what is wrong, if an error is found.
                client.close()

        
        if event == '3: Send command list':
            
            try: # Error handling
                print('Sending command list: ', client.cmd_lst)

                # finds out how many times to recieve data. If miscounted, client.recv_scan() will be stuck forever
                scan_amount = amount_of_scans(client.cmd_lst)
                print('amount of scans to conduct: ', scan_amount)

                scan_num = 0
                while scan_num < scan_amount:
                    print(scan_num)
                    if scan_num == 0:
                        ans = client.send_cmd_list() # send_cmd_list returns the first scan from the Pico W.
                        # print("ANSWER FROM SERVER: ", ans)
                        if ans == 'keepalive':
                            client.send_keepalive()
                        else:
                            ans_df = handle_answer(answer=ans, search_ssid=search_ssid) # returns RSSI and coords of specified ssid
                            index_bssid = 0
                            specific_bssid = ans_df['bSSID'][index_bssid]
                            ans_df = ans_df.loc[ans_df['bSSID'] == specific_bssid]

                            # print(ans_df)

                        scan_num += 1

                    elif scan_num > 0:
                        ans = client.recv_scan() # the scans are saved in an attribute of 'client' called scan_lst

                        if ans == 'keepalive':
                            client.send_keepalive()
                            print('received:', ans)
                        
                        else:
                            df = handle_answer(answer=ans, search_ssid=search_ssid)
                            # print(df)

                            df = df.loc[df['bSSID'] == specific_bssid]
                            
                            ans_df = pd.concat([ans_df, df], ignore_index=True)
                            # print(ans_df)

                            if graph_type == 'Heatmap' and scan_num == scan_amount: # Only makes 'heatmap' if all the data has been collected
                                map_obj = create_map()

                                map_obj = create_circles(map_obj=map_obj, RSSI_lst=ans_df['RSSI'], coords=ans_df['coordinates'], radius=0.5)

                                save_and_show_map(map_obj=map_obj)

                            if graph_type == 'Fitted graph' and scan_num == scan_amount: # If there are more than 3 datapoints (0,1,2), a graph is plotted
                                if fig_gui != None:
                                    delete_fig(fig_gui)

                                start = time.time()
                                fig = make_fig(ans_df, step_dist=step_dist) # makes a figure with the values
                                fig_gui = draw_figure(window['-graph-'].TKCanvas, fig) # draws said figure on the GUI
                                stop = time.time()
                                print('time it takes to plot: ', stop - start)
                            scan_num += 1

                print(ans_df)
                # print(client.scan_lst)

                print('Pickling raw scan data (ans_df)...')
                hour, minute, second = time.localtime()[3:6]
                file = open(f'pickled_raw_data_{hour}_{minute}_{second}', 'wb')
                # dumping info
                pickle.dump(ans_df, file)
                file.close()
                print('done pickling')
                    
        
            except KeyboardInterrupt as e:
                sg.Popup(f"Error in connecting to PicoW server: {e}") # creates pop-up that tells the user what is wrong, if an error is found.

                print('Pickling raw scan data (ans_df)...')
                hour, minute, second = time.localtime()[3:6]
                file = open(f'pickled_raw_data_{hour}_{minute}_{second}', 'wb')
                # dumping info
                pickle.dump(ans_df, file)
                file.close
                print('done pickling')
                client.close()
        
        if event == '[Optional] plot loaded pickle':
            if fig_gui != None:
                delete_fig(fig_gui)

            file = open(values['-file-'], 'rb')
            df = pickle.load(file)
            file.close()
            
            step_dist = int(values['-step_dist-'])

            fig = make_fig(df, step_dist=step_dist) # makes a figure with the values
            fig_gui = draw_figure(window['-graph-'].TKCanvas, fig)

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
