import numpy as np
import pandas as pd
import time
import pickle


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




# example of answer from Pico W
ans = """[(b'TELLO-gr155', b'``\x1f[K\xea', 7, -31, 5, 7), (b'ZyXEL', b'\x00\x19\xcbYu\xde', 13, -50, 3, 5), (b'AAU-1x', b'l1\x0e\xba\n\xa0', 11, -56, 5, 2), (b'AAU-1-DAY', b'l1\x0e\xba\n\xa1', 11, -56, 5, 2), (b'eduroam', b'l1\x0e\xba\n\xa4', 11, -55, 5, 3), (b'AAU', b'l1\x0e\xba\n\xa6', 11, -56, 0, 2), (b'Bear', b'\xc2+\xf9\xcay\x07', 11, -64, 5, 2), (b'linksys', b'\x00\x14\xbf\x8a\xa3,', 11, -85, 5, 1), (b'', b'l1\x0e\xba\n\xa5', 11, -57, 0, 1), (b'', b'l1\x0e\xba\x11\x85', 1, -67, 0, 1), (b'AAU', b'l1\x0e\xba\x11\x86', 1, -69, 0, 1), (b'eduroam', b'<Q\x0e\x13\xfd\x84', 1, -72, 5, 1), (b'AAU', b'<Q\x0e\x13\xfd\x86', 1, -74, 0, 1), (b'MiR_202303313', b'\x08U1>\xea\x0c', 5, -69, 7, 3), (b'AAU', b'l1\x0e\xe0ff', 6, -78, 0, 2), (b'', b'<Q\x0e\t>\xe5', 6, -76, 0, 1), (b'eduroam', b'l1\x0e\xe1\x0fd', 6, -73, 5, 1), (b'AAU', b'l1\x0e\xe1\x0ff', 6, -74, 0, 1), (b'AAU-1x', b'l1\x0e\xf3U\xe0', 6, -73, 5, 1), (b'AAU-1-DAY', b'l1\x0e\xf3U\xe1', 6, -74, 5, 2), (b'eduroam', b'l1\x0e\xf3U\xe4', 6, -72, 5, 1), (b'AAU', b'l1\x0e\xf3U\xe6', 6, -74, 0, 1), (b'AAU', b'<Q\x0e\t>\xe6', 6, -73, 0, 1)], ('57.014699', '9.987020')"""

data = handle_answer(ans, "b'AAU-1-DAY'")

print('Pickling raw scan data (client.scan_lst)...')
hour, minute, second = time.localtime()[3:6]
file = open(f'pickled_raw_data', 'wb')
# dumping info
pickle.dump(data, file)
file.close

time.sleep(5)

file = open('pickled_raw_data', 'rb')

data = pickle.load(file)

file.close()
print(data)
