import folium
import webbrowser


def create_map(location=(57.01477, 9.98668), zoom_start=19, max_zoom=24):

    map_obj = folium.Map(location=location, zoom_start=zoom_start, max_zoom=max_zoom)
    
    return map_obj


def create_circles(map_obj, RSSI_lst, coords, radius=0.5):

    for i in range(len(RSSI_lst)):
        if RSSI_lst[i] > -25:
            folium.Circle(location=coords[i], radius=radius, fill=True, color='red').add_to(map_obj)
        elif RSSI_lst[i] > -35:
            folium.Circle(location=coords[i], radius=radius, fill=True, color='orange').add_to(map_obj)
        elif RSSI_lst[i] > -45:
            folium.Circle(location=coords[i], radius=radius, fill=True, color='yellow').add_to(map_obj)
        elif RSSI_lst[i] > -55:
            folium.Circle(location=coords[i], radius=radius, fill=True, color='green').add_to(map_obj)
        elif RSSI_lst[i] > -65:
            folium.Circle(location=coords[i], radius=radius, fill=True, color='blue').add_to(map_obj)
        elif RSSI_lst[i] > -75:
            folium.Circle(location=coords[i], radius=radius, fill=True, color='purple').add_to(map_obj)

    return map_obj


def save_and_show_map(map_obj):
    
    map_obj.save('gps_vis.html')
    webbrowser.open('gps_vis.html')


if __name__ == '__main__':

    """RSSI_lst = [-10]
    coords = [(57.01477, 9.98668),
    (57.01477, 9.98668),
    (57.01478, 9.986689),
    (57.0148, 9.986696),
    (57.01482, 9.986692),
    (57.01482, 9.98668),
    (57.01483, 9.986672),
    (57.01483, 9.986675),
    (57.01485, 9.986667),
    (57.01487, 9.986642),
    (57.01489, 9.986627),
    (57.01488, 9.986616),
    (57.01487, 9.986593),
    (57.01487, 9.986569),
    (57.01486, 9.986564),
    (57.01485, 9.986564),
    (57.01485, 9.98656),
    (57.01484, 9.986581),
    (57.01483, 9.986573),
    (57.01483, 9.986568),
    (57.01482, 9.986568),
    (57.01482, 9.986576),
    (57.0148, 9.986568),
    (57.01479, 9.986573),
    (57.0148, 9.986586),
    (57.0148, 9.9866),
    (57.0148, 9.9866),
    (57.01478, 9.986589),
    (57.01478, 9.986581),
    (57.01478, 9.986573),
    (57.01479, 9.986587),
    (57.01479, 9.986577),
    (57.01478, 9.986576),
    (57.01478, 9.986563),
    (57.01478, 9.986563),
    (57.01477, 9.98656),
    (57.01477, 9.986555),
    (57.01477, 9.986547),
    (57.01474, 9.986513),
    (57.01471, 9.986475),
    (57.01471, 9.98645),
    (57.0147, 9.986436),
    (57.0147, 9.986404),
    (57.01469, 9.986373),
    (57.0147, 9.98636),
    (57.01469, 9.986348),
    (57.01468, 9.986333),
    (57.01468, 9.986316),
    (57.01468, 9.986298),
    (57.01468, 9.986288),
    (57.01468, 9.986277),
    (57.01468, 9.986265),
    (57.01468, 9.98626),
    (57.01469, 9.986242),
    (57.0147, 9.986238),
    (57.0147, 9.986221),
    (57.0147, 9.986228),
    (57.0147, 9.986213),
    (57.01471, 9.986208),
    (57.01473, 9.986197),
    (57.01477, 9.986195),
    (57.01477, 9.9862),
    (57.01477, 9.986193),
    (57.01477, 9.986197),
    (57.01477, 9.986192),
    (57.01477, 9.986203),
    (57.01477, 9.986186),
    (57.01476, 9.986186),
    (57.01476, 9.986188),
    (57.01474, 9.986199),
    (57.01474, 9.986199),
    (57.01473, 9.986211),
    (57.01473, 9.986209),
    (57.01473, 9.986203),
    (57.01473, 9.9862),
    (57.01474, 9.986193),
    (57.01473, 9.9862),
    (57.01473, 9.986201),
    (57.01473, 9.986217),
    (57.01473, 9.98623),
    (57.01472, 9.986239),
    (57.01471, 9.986248),
    (57.01471, 9.98626),
    (57.01471, 9.986271),
    (57.0147, 9.986278),
    (57.0147, 9.986282)]

    coords2 = [(57.01477, 9.98668)]

    add_coords = 0.00002
    for i in range(len(coords)-1):
        RSSI_lst.append(random.randint(-80, -10))
        coords2.append((coords2[i][0] + add_coords, coords2[i][1] + add_coords*2))
    #print(RSSI_lst)

    add = max(RSSI_lst)
    for i in range(len(RSSI_lst)):
        # RSSI_lst[i] = RSSI_lst[i] + (add * -1) + 100
        pass

    #print(RSSI_lst)
    #print(min(RSSI_lst))

    lats_longs_weight = []
    for i in range(len(RSSI_lst)):
        if i % 1 == 0:
        #if i < 1:
            lats_longs_weight.append([round(coords[i][0], 5), round(coords[i][1], 5), RSSI_lst[i]])

    # print(lats_longs_weight)

    gradient_dict = {
        0.4:'blue',
        0.5:'green',
        0.7:'yellow',
        1:'red'
    }

    # HeatMap(lats_longs_weight, blur=1, radius=4, gradient=gradient_dict, min_opacity=0.5).add_to(map_obj)"""


    map_obj = create_map(location=(57.013610, 9.992627))

    RSSI_lst = [-22, -26, -40, -42, -49, -63, -60, -64, -61]

    coords = [
    (57.013610, 9.992627)
    ]
    two_m_in_coorddecimals = 0.00002
    for i in range(len(RSSI_lst)-1):
        lat = coords[i][0] + two_m_in_coorddecimals
        # print(lat)
        coords.append((lat, coords[i][1]))


    print(coords)
    map_obj = create_circles(map_obj=map_obj, RSSI_lst=RSSI_lst, coords=coords)

    save_and_show_map(map_obj=map_obj)