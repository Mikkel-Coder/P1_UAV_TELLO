import PySimpleGUI as sg
import matplotlib 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
import numpy as np
import pandas as pd


def csv_to_df(file, search_ssid):
    """Takes the raw data and sorts it to find all data on a single bssid. Returns a dataframe of those bssid measurements"""
    data = pd.read_csv(file, sep=";") # reading the csv and splitting when there is a semicolon
    # print(data)
    search_data = data.loc[data['ssid'] == search_ssid] # making new df of only the same ssid's
    print(search_data)
    top_bssid = search_data['bssid'].iloc[1] # finds the first bssid to further look at
    print(f"searching by first bssid entry: {top_bssid}")
    top_bssid_df = search_data.loc[search_data['bssid'] == top_bssid] # making a new df of only same ssid's AND bssid's based on 'top_bssid'
    # print(top_bssid_df)
    return top_bssid_df

def calc_x_dist(y2, y1, speed):
    # to calc distance the formula is distance = speed x time. units need to be the same. meters/second from dronespeed, and seconds between measurements
    dist = (y2 - y1) * speed
    # print(dist)
    return dist * 100 # distance in centimeters

def dist_index_df(df, speed):
    """funktion der udregner hvordan x-aksen skal skalleres baseret på tid mellem målinger og hastighed af endelige df"""
    time_array = df['time'].to_numpy()
    distances = np.zeros_like(time_array)
    for i in range(len(time_array) - 1): # goes from index 1 - 19
        i = i + 1 # helps go from index 1 - 19
        distances[i] = calc_x_dist(time_array[i], time_array[i-1], speed) # places the distance between current index and the index - 1

    cum_distances = distances.cumsum() # makes the distances cumulative
    # print(cum_distances)
    return df.set_index(cum_distances) # sets the index of the dataframe to the distance from first measurement which is 0 meters


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

    x_data = np.array(df.index)
    x_data[0] = x_data[1] * 0.1 # x_data[0] will always be 0, but log(0) throws an error due to it being impossible.
    # Therefore we cheat a little by making it 10% of the next x_value
    y_data = df['RSSI']
    # Taking log of x values
    xlog_data =  (-1) * np.log(x_data)
    a, b = np.polyfit(xlog_data, y_data, 1)
    y = a * xlog_data + b
    ax.plot(x_data, y, '--', label="log fit")

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
    layout = [[sg.Text("GUI for csv wifi data")],
            [sg.Text('choose the .csv-file'), sg.FileBrowse(key = '-csv-')],
            [sg.Text('Choose SSID to plot:'), sg.Input("b'AAU-1-DAY'", key = '-search_ssid-')],
            [sg.Text('input drone-speed during measurements (m/s):'), sg.Input('2', key = '-speed-')],
            [sg.Button('Simulate and graph')],
            [sg.Canvas(key = '-graph-')]]

    # creates the window using the layout from above
    window = sg.Window('Monte Carlo simulator',
                        layout = layout,
                        finalize = True,
                        element_justification='center')

    fig_gui = None

    while True:
        event, values = window.read()
        
        if event == 'Simulate and graph':
            if fig_gui != None:
                delete_fig(fig_gui) # if there is a figure on the GUI already then delete it when a new one is about to be created
            
            try: # Error handling
                speed = float(values['-speed-'])
                search_ssid = str(values['-search_ssid-'])
                file = values['-csv-']

                # finds certain bssid - data from all measured data
                bssid_df = csv_to_df(file, search_ssid)
                # print(bssid_df)

                # gets a df with distance from first measurement as index.
                df = dist_index_df(bssid_df, speed) 
                print(df)
                
                fig = make_fig(df) # makes a figure with the values
                fig_gui = draw_figure(window['-graph-'].TKCanvas, fig) # draws said figure on the GUI
            except Exception as e:
                sg.Popup(f"Error in input: {e}") # creates pop-up that tells the user what is wrong, if an error is found.

        # if the window is closed, break out of the while-loop, ending the script
        if event == sg.WIN_CLOSED:
            break
        
    plt.close('all')
    window.close()

gui()
