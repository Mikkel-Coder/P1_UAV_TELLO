from machine import Pin, UART

#Import utime library to implement delay
import utime, time

class GPS_Class:
    """
    Class for returning coordinate position of the GPS module
    """

    def __init__(self):
    
        # ---------- Store GPS Coordinates ---------- 
        self.latitude = ""
        self.longitude = ""
        
        # ---------- Store the status of satellite is fixed or not ---------- 
        self.FIX_STATUS = False
        
        # ---------- Used to Store NMEA Sentences ---------- 
        self.buff = bytearray(255)
        self.TIMEOUT = False

        # ---------- GPS Module UART Connection ---------- 
        self.gps_module = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

    
    def getPositionData(self) -> None:
        """ Retrieves GPS coordinates, sorts them and saves latitude and longitude. """
        #run while loop to get gps data or terminate while loop after 5 seconds timeout
        timeout = time.time() + 5
        
        while True:
            self.buff = str(self.gps_module.readline())
            parts = self.buff.split(',')
            
            if parts[0] == "b'$GPGGA":
                if parts[2] and parts[3] and parts[4] and parts[5]:
                    #print("Latitude    : " + parts[2])
                    #print("N/S         : " + parts[3])
                    #print("Longitude   : " + parts[4])
                    #print("E/W         : " + parts[5])
                    
                    self.latitude = self.convertToDigree(parts[2])

                    # parts[3] contain 'N' or 'S'
                    if parts[3] == 'S':
                        self.latitude = -self.latitude

                    self.longitude = self.convertToDigree(parts[4])

                    # parts[5] contain 'E' or 'W'
                    if parts[5] == 'W':
                        self.longitude = -self.longitude

                    self.FIX_STATUS = True
                    break 
                    
            if time.time() > timeout:
                self.TIMEOUT = True
                break
            
            utime.sleep_ms(100)
            
    def convertToDigree(self,RawDegrees: float) -> float:
        """
        Converts raw latitude or longitude to decimaldegrees.
        
        Inputs:
        ---
        - RawDegress: latitude or longitude.

        Returns:
        ---
        - Converted degrees.
        """

        RawAsFloat = float(RawDegrees)
        firstdigits = int(RawAsFloat / 100) # degrees
        nexttwodigits = RawAsFloat - float(firstdigits * 100) # minutes
        Converted = float(firstdigits + nexttwodigits / 60)

        return Converted
        

    def getcoords(self) ->  float | bool:
        """
        Get GPS coordinates.

        Returns:
        ---
        - float of latitude and a float longitude.
        - False if timeout.

        """
        self.getPositionData()

        #if gps data is found then print it on lcd
        if self.FIX_STATUS == True:
            self.FIX_STATUS = False
            return self.latitude, self.longitude
            
        if self.TIMEOUT == True:
            self.TIMEOUT = False
            return False
    

if __name__ == "__main__":
    getgps = GPS_Class()
    while True:
        print(getgps.getcoords())