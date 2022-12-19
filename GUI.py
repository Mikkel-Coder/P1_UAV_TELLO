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


def amount_of_scans(command_str: str) -> int:
    """
    The amount of scans to be conducted.

    Inputs:
    ---
    - command_str as the list to count the amount of scans.

    Returns:
    ---
    - The amount of scans.
    """

    amt_scans = 1 # starts at 1 because a scan is made after the takeoff command
    command_list = command_str.split(',')

    for command in command_list:
        if 'forward' in command:
            amt_scans += 1

    return amt_scans


def handle_answer(answer: str, search_ssid: str) -> object:
    """
    Sorts scan results from type string to a DataFrame containing relevant data in form of SSID, bSSID, RSSI and coordinates of a specific SSID
    
    Inputs:
    ---
    - answer: The answer that the Pico W sends. This function is only called if the answer is a scan with coordinates.

    Returns:
    ---
    - A DataFrame with the searched ssid input from GUI.
    """

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

    for item in range(len(answer)):
        try:
            if type(answer[item]) == float and type(answer[item + 1]) == str: # if the current item is a float and the next is a string
                # then this is where the tuples should be seperate

                scan = tuple(answer[start : item + 1]) # saves results from 'start' to seperationpoint (after float, before string)
                scan_results['SSID'].append(scan[0] + "'")                
                scan_results['bSSID'].append((scan[1] + "'").encode('utf-8'))
                scan_results['RSSI'].append(scan[-3])
                scan_results['coordinates'].append(coords)
                start += item - start + 1 # start is updated
                # ap += 1 # ap key is counted up 1 for the next accespoint

        except Exception:
            pass

    df = pd.DataFrame(scan_results)
    search_data = df.loc[df['SSID'] == search_ssid]
    search_data.reset_index(inplace=True, drop=True)

    return search_data


def draw_figure(canvas, figure) -> object:
    """Draws figure on canvas for GUI"""
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def delete_fig(fig) -> None:
    """Deletes figure from plot"""
    fig.get_tk_widget().forget()
    plt.close('all')


def make_fig(df: object, step_dist: int) -> object:
    """
    Creates a log fit plot and plots raw RSSI data as points.
   
    Inputs:
    ---
    - df: The given DataFrame to plot.
    - step_dist: Distance between measurements in centimeters (cm).

    Returns:
    ---
    - fig: A matplotlib.pyplot object.
    """

    # Create a list of x values to be plotted 
    stop = (len(df['RSSI']) - 1) * step_dist
    nums = len(df['RSSI'])
    dist_list = np.linspace(start=0, stop=int(stop), num=int(nums))

    # Real messurements plotted as dots
    fig, ax = plt.subplots()
    ax.plot(dist_list, df['RSSI'], ".", label="data") # plots x as distance from first measurement and y as RSSI

    x_data = dist_list
    x_data[0] = float(x_data[1] * 0.05) # x_data[0] will always be 0, but log(0) throws an error due to it being impossible.

    y_data = df['RSSI']
    # Taking log of x values
    xlog_data = np.log(x_data)

    # utilises np.polyfit as least squares method 
    a, b = np.polyfit(xlog_data, y_data, 1)

    y = a * xlog_data + b

    # Logfit plotted as a line
    ax.plot(x_data, y, '--', label="log fit")

    # layout
    ax.grid(True)
    ax.set_xlabel('distance (cm) from first measurement')
    ax.set_ylabel('signal strength RSSI (dBm)')
    ax.set_title(f"Graph of signalstrength of accespoint: {df['bSSID'].iloc[0]}")
    ax.legend()
    fig.tight_layout() # makes it not overlap, if possible

    return fig


def pickle_data(ans_df: object) -> None:
    """
    Saves an DataFram in a pickle. 

    Inputs:
    ---
    - ans_df: The DataFrame to be saved.
    """
    
    print('Pickling raw scan data (ans_df)...')
    hour, minute, second = time.localtime()[3:6]
    
    with open(f'pickled_raw_data_{hour}_{minute}_{second}', 'wb') as file:
        pickle.dump(ans_df, file) # dump info
        
    print('done pickling')


def gui() -> None:
    """Creates the GUI itself. Error-handles and calls other functions when needed"""

    sg.theme('GreenMono')

    layout = [ 
            [sg.Text('Length and Width is the length and width of the Manhatten grid to fly in. Step distance is the distance between each cross-section in the grid')],
            [sg.Text('Write the name of the Wi-Fi which you want to analyze in "Choose SSID to plot:". If you choose "Fitted graph" in "Choose graph variant",')],
            [sg.Text('the drone will fly in a straight line of given "length".')],
            [sg.Text('Length (cm):'), sg.Input(400, key = '-x-')],
            [sg.Text('Width (cm):'), sg.Input(100, key = '-y-')],
            [sg.Text('Step distance (20-500 cm):'), sg.Input(50, key = '-step_dist-')],
            [sg.Text('Choose SSID to plot:'), sg.Input("Marcus - iPhone", key = '-search_ssid-')],
            [sg.Text('Choose graph variant:'), sg.Combo(['RSSI map', 'Fitted graph'], size=(20,1), readonly=True, default_value='Fitted graph', key = '-variant-')],
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
            try:
                x = int(values['-x-'])
                y = int(values['-y-'])
                step_dist = int(values['-step_dist-'])
                search_ssid = f"b'{values['-search_ssid-']}'"
                graph_type = str(values['-variant-'])
                print(x, y, step_dist, search_ssid, graph_type)

                msg = path(x=x, y=y, step_dist=step_dist)

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
                sg.Popup(f"Error in input: {e}") # creates pop-up that tells the user what is wrong, if an error occurs
                client.close() # tries to close the client
        
        if event == '2: Connect to drone':
            time.sleep(0.5)
            try:
                # connecting to the Pico
                client.sock_connect()
                time.sleep(1)
        
            except Exception as e:
                sg.Popup(f"Error in connecting to PicoW server: {e}")
                client.close()

        
        if event == '3: Send command list':
            try:
                print('Sending command list: ', client.cmd_lst)

                # finds out how many times to recieve data
                scan_amount = amount_of_scans(client.cmd_lst)
                print('amount of scans to conduct: ', scan_amount)

                scan_num = 0
                while scan_num < scan_amount:
                    if scan_num == 0:
                        ans = client.send_cmd_list()
                        
                        if ans == 'keepalive':
                            client.send_keepalive()

                        else:
                            ans_df = handle_answer(answer=ans, search_ssid=search_ssid) # returns RSSI and coords of specified ssid
                            index_bssid = 0
                            specific_bssid = ans_df['bSSID'][index_bssid]
                            ans_df = ans_df.loc[ans_df['bSSID'] == specific_bssid]

                        scan_num += 1

                    elif scan_num > 0:
                        ans = client.recv_scan() # the scans are saved in an attribute of 'client' called scan_lst

                        if ans == 'keepalive':
                            client.send_keepalive()
                            # print('received:', ans)
                        
                        else:
                            df = handle_answer(answer=ans, search_ssid=search_ssid)
                            df = df.loc[df['bSSID'] == specific_bssid]
                            ans_df = pd.concat([ans_df, df], ignore_index=True)
                            # print(ans_df)

                            if graph_type == 'RSSI map' and scan_num == scan_amount: # Only makes 'RSSI map' if all the data has been collected
                                map_obj = create_map()
                                map_obj = create_circles(map_obj=map_obj, RSSI_lst=ans_df['RSSI'], coords=ans_df['coordinates'], radius=0.5)
                                save_and_show_map(map_obj=map_obj)

                            if graph_type == 'Fitted graph' and scan_num == scan_amount:
                                if fig_gui != None:
                                    delete_fig(fig_gui)

                                fig = make_fig(ans_df, step_dist=step_dist) # makes a figure with the values
                                fig_gui = draw_figure(window['-graph-'].TKCanvas, fig) # draws said figure on the GUI

                            scan_num += 1

                print(ans_df)
                # print(client.scan_lst)
                pickle_data(ans_df)
                client.close()       
        
            except Exception as e:
                sg.Popup(f"Error in connecting to PicoW server: {e}")
                pickle_data(ans_df)
                client.close()

        if event == '[Optional] plot loaded pickle':
            if fig_gui != None:
                delete_fig(fig_gui)

            with open(values['-file-'], 'rb') as file:
                df = pickle.load(file)
            
            step_dist = int(values['-step_dist-'])

            fig = make_fig(df, step_dist=step_dist) # makes a figure with the values
            fig_gui = draw_figure(window['-graph-'].TKCanvas, fig)


        # if the window is closed, break out of the while-loop, ending the script
        if event == sg.WIN_CLOSED:
            try:
                client.close() # close the socket as the last thing after the closebutton is pressed pressed. This is the kill-switch!
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
