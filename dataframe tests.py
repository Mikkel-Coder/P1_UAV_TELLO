import pandas as pd
import pickle

"""scan_results = {
        'SSID' : [b'AAU-1-DAY', b'AAU-1-DAY'],
        'bSSID' : [b"b'l1\\x0e\\xe1\\x0fa'", b"b'l1\\x0e\\xba\\n\\xa1'"],
        'RSSI' : [-76.0, -66.0],
        'coordinates' : [(57.01477, 9.98668), (57.01477, 9.98668)]
    }


df = pd.DataFrame(scan_results)
# print(df)
df.reset_index(inplace=True, drop=True)
# df.drop(columns='index')

index_bssid = 0
selected_bSSID = df['bSSID'][index_bssid]

search_data = df.loc[df['bSSID'] == selected_bSSID]

print(df)
print(' ')
print(df['bSSID'])
print(' ')
print(selected_bSSID)
print(' ')
print(search_data)"""


import numpy as np


def decimaldegrees_to_cm(coords_tuple1, coords_tuple2):

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


if __name__ == '__main__':
    file = open('pickled_raw_data_9_43_58_perfect', 'rb')

    df = pickle.load(file)

    file.close()
    
    pd.set_option('display.max_columns', 10)
    print(df)
    pd.reset_option('all')

    # coords = df['coordinates']
    coords = [(57.01361, 9.992627), (57.01363, 9.992627), (57.01365, 9.992627), (57.01367, 9.992627), (57.01369, 9.992627), (57.013709999999996, 9.992627), (57.013729999999995, 9.992627), (57.013749999999995, 9.992627), (57.013769999999994, 9.992627)]
    dist_list = [0] # starts with 0 as the first datapoint is at x = 0 on the x-axis
    for i in range(len(coords) - 1):
        dist_btwn_points = decimaldegrees_to_cm(coords[i], coords[i + 1])
        dist_list.append(dist_btwn_points)
    print(dist_list)

