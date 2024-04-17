import serial
import time
import math

# Serial port configuration
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Function to send AT command and receive response
def send_command(command):
    ser.write((command + '\r\n').encode())
    time.sleep(1)
    response = ser.read(ser.inWaiting()).decode()
    return response.strip()

# Function to convert NMEA coordinates to decimal degrees
def nmea_to_decimal(nmea_coord):
    nmea_coord = str(nmea_coord)
    direction = 1 if nmea_coord[-1] in ['N', 'E'] else -1
    nmea_coord = nmea_coord[:-1]
    degrees = float(nmea_coord[:2])
    minutes = float(nmea_coord[2:4])
    seconds = float(nmea_coord[4:])
    
    decimal_degrees = (degrees + minutes / 60.0 + seconds / 3600.0) * direction
    return decimal_degrees

def parse_own(nmea_coord):
    nmea_coord = str(nmea_coord)
    direction_raw = nmea_coord[-1]
    nmea_coord = nmea_coord[:-1]
    
    # split to two
    split_by_period = nmea_coord.split(".")
    left_values, right_values = split_by_period[0], split_by_period[1]
    degrees, minutes = left_values[:-2], left_values[-2:]
    seconds = float(right_values) / 3600
    double_quote = '"'
    
    return f"{degrees}°{minutes}'{seconds}{double_quote} {direction_raw}"

def ddm_to_dd(dms_lat, dms_lon):
    # Function to convert DMS to DD
    def convert(degrees, minutes, seconds, direction):
        # Convert minutes to decimal and add to degrees
        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
        # If direction is South or West, make it negative
        if direction in ['S', 'W']:
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    # Split input strings based on known positions and convert to float/int
    lat_degrees = int(dms_lat[:2])
    lat_minutes = int(dms_lat[2:4])
    lat_seconds = float(dms_lat[4:9])
    lat_direction = dms_lat[-1]

    lon_degrees = int(dms_lon[:3])
    lon_minutes = int(dms_lon[3:5])
    lon_seconds = float(dms_lon[5:10])
    lon_direction = dms_lon[-1]

    # Convert DMS to DD
    lat_dd = convert(lat_degrees, lat_minutes, lat_seconds, lat_direction)
    lon_dd = convert(lon_degrees, lon_minutes, lon_seconds, lon_direction)

    return lat_dd, lon_dd

def dd_to_dms(lat_dd, lon_dd):
    # Function to convert DD to DMS
    def convert(decimal_degrees):
        # Obtain the degrees from the decimal degrees
        degrees = int(decimal_degrees)
        # Calculate the minutes from the remaining decimal
        remainder = abs(decimal_degrees - degrees)
        minutes = int(remainder * 60)
        # Calculate the seconds from the remaining decimal
        seconds = remainder * 60 - minutes
        return degrees, minutes, seconds
    
    # Convert latitude and longitude from DD to DMS
    lat_degrees, lat_minutes, lat_seconds = convert(lat_dd)
    lon_degrees, lon_minutes, lon_seconds = convert(lon_dd)

    # Format in human-readable DMS form with cardinal direction
    lat_hemisphere = 'N' if lat_dd >= 0 else 'S'
    lon_hemisphere = 'E' if lon_dd >= 0 else 'W'

    lat_dms = f"{abs(lat_degrees)}°{lat_minutes}'{lat_seconds:.2f}\"{lat_hemisphere}"
    lon_dms = f"{abs(lon_degrees)}°{lon_minutes}'{lon_seconds:.2f}\"{lon_hemisphere}"

    return lat_dms, lon_dms

# Function to retrieve GPS location
def retrieve_gps_location():
    # Enable GPS
    send_command('AT+GPS=1')

    # Retrieve GPS information
    response = send_command('AT+GPSRD=1')
    if response:
        gps_data = response.split(',')
        latitude_nmea = gps_data[2]
        longitude_nmea = gps_data[4]
        direct_latitude = gps_data[3]
        direct_longitude = gps_data[5]
        
        latitude_nmea = f"{latitude_nmea}{direct_latitude}"
        longitude_nmea = f"{longitude_nmea}{direct_longitude}"
        
        print(latitude_nmea, longitude_nmea)
    
        combined_lat, combined_long = ddm_to_dd(latitude_nmea, longitude_nmea)
        
        return combined_lat, combined_long
    else:
        return None, None