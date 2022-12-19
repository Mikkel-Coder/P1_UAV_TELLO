import folium
import webbrowser

def create_map(location=(57.01477, 9.98668), zoom_start=19, max_zoom=24) -> object:
    """
    Creates a empty folium.Map object.

    Inputs:
    ---
    - location: A tuple or list of coordinates.
    - zoom_start: The zoom level when created.
    - max_zoom: The max zoom level.
    
    Returns:
    ---
    - map_obj which is a folium.Map object.
    """

    map_obj = folium.Map(location=location, zoom_start=zoom_start, max_zoom=max_zoom)
    
    return map_obj


def create_circles(map_obj:object, RSSI_lst:list, coords:list or tuple, radius=0.5) -> object:
    """
    Creates circles of a specified radius on the map_obj. The colour of the circles
    is determined by the RSSI value of the given coordinates coords.
    They are colourcoded in strength in order (red, orange, yellow, green, blue, purple)
    
    Inputs:
    ---
    - map_obj: A folium object to plot in.
    - RSSI_lst: A list of RSSI values to be ploted in the map.
    - coords: The location for the RSSI values to be plotted at.
    - radius: The radius of the circles to be plotted in meters.
    
    Returns:
    ---
    - A map_obj with plotted RSSI values.
    """

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


def save_and_show_map(map_obj:object, name = 'gps_vis') -> None:
    """
    Saves a folium map object in html with a given name.

    Inputs:
    ---
    - map_obj: A folium map object to be saved.
    - name: The name of the html file to be saved.

    Returns:
    ---
    - None
    """
    map_obj.save(f'{name}.html')
    webbrowser.open('gps_vis.html')


if __name__ == '__main__':
    map_obj = create_map(location=(57.013610, 9.992627))

    RSSI_lst = [-22, -26, -40, -42, -49, -63, -60, -64, -61]

    coords = [
    (57.013610, 9.992627)
    ]
    two_m_in_coorddecimals = 0.00002
    for i in range(len(RSSI_lst)-1):
        lat = coords[i][0] + two_m_in_coorddecimals
        coords.append((lat, coords[i][1]))

    map_obj = create_circles(map_obj=map_obj, RSSI_lst=RSSI_lst, coords=coords)

    save_and_show_map(map_obj=map_obj)