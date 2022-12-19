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