# Import library to use system functions
import sys
# Import library to parse '.ini' files
import ConfigParser
# Import library for getting and configuring time strings
from time import gmtime, strftime
# Import library for reading networks and configuring current network
import wifi
# Import library for reading json data from .json files
import json
# Import library for serial communication
import serial
# Import library for using/processing system time
import time
# Import selenium for web automation
import selenium
# Import library to make web requests
import requests
# Import library used for managing .log files
import logging
# Import library used to extract, format and print stack traces
import traceback

import webbrowser

import os

from threading import Timer,Thread,Event

import urllib2

#############
# GLOBAL VARS
#############

global Log_File
Log_File = "telebot_error.log"

global ser

global Wireless_Interface
Wireless_Interface = "wlan0"

global Serial_Commands
Serial_Commands = {
    'forward': 0b00010000,
    'backward': 0b00100000,
    'right': 0b00110000,
    'left': 0b01000000,
    'clockwise': 0b01010000,
    'anti_clockwise': 0b01100000,
    'stop': 0b10000000,
    'sensor_0': 0b10010000,
    'sensor_1': 0b10100000,
    'sensor_2': 0b10110000,
    'sensor_3': 0b11000000,
    'sensor_4': 0b11010000,
    'sensor_5': 0b11100000,
    'battery': 0b10000000
}

global Speed_Modes
Speed_Modes = {
    'level_0': 0,
    'level_1': 1,
    'level_2': 2,
    'level_3': 3,
    'level_4': 4,
    'level_5': 5,
    'level_6': 6,
    'level_7': 7,
    'level_8': 8,
    'level_9': 9,
    'level_10': 10,
    'level_11': 11,
    'level_12': 12,
    'level_13': 13,
    'level_14': 14,
    'level_15': 15,
}

global Key_Commands
Key_Commands = {
        'w': Serial_Commands['forward'],
        's': Serial_Commands['stop'],
        'a': Serial_Commands['left'],
        'd': Serial_Commands['right'],
        'q': Serial_Commands['anti_clockwise'],
        'e': Serial_Commands['clockwise'],
        'x': Serial_Commands['backward']
    }

global Speed
Speed = "level_0"

global Old_Commands
Old_Commands = " "

global Robot_ID
global Robot_Password
Robot_ID = Robot_Password = "robot01"

global InCall
InCall = False

global JSON_File 
JSON_File = "/var/www/html/data.json"

#############
# FUNCTIONS
#############

############
# CHROMIUM
############

def StartGUI():
    robot_gui = "localhost/robot_gui.php"
    os.system("sudo su -c \"chromium-browser '" + robot_gui + "' --start-fullscreen\" -s /bin/sh pi &")
    # Full command:
    # sudo su -c "chromium-browser 'localhost/robot_gui.php' --start-fullscreen" -s /bin/sh pi &
    return robot_gui

def PlaceCall():
    robot_login = "https://connection-robertoruano.c9users.io/robot_login.php?username=" + Robot_ID + "&pswrd=" + Robot_Password
    os.system("sudo su -c \"chromium-browser '" + robot_login + "' --start-fullscreen\" -s /bin/sh pi &")
    # Full command:
    # sudo su -c "chromium-browser 'https://connection-robertoruano.c9users.io/robot_login.php?username=robot01&pswrd=robot01' --start-fullscreen" -s /bin/sh pi &
    return robot_login

def KillChromium():
    os.system("killall chromium-browser")
    return None

############
# LOGGING
############

def ErrorLog(message):
	log = strftime(" %d-%m-%Y %H:%M:%S -> ", gmtime()) + str(message)
	print "[ERROR] " + log
	#logging.basicConfig(filename = Log_File, level = logging.DEBUG)
	#logging.warning(log)
	return None

def DebugLog(message):
	log = strftime(" %d-%m-%Y %H:%M:%S -> ", gmtime()) + str(message)
	print "[DEBUG] " + log
	#logging.basicConfig(filename = Log_File, level = logging.DEBUG)
	#logging.debug(log)
	return None
    
def InfoLog(message):
	log = strftime(" %d-%m-%Y %H:%M:%S -> ", gmtime()) + str(message)
	print "[INFO] " + log
	#logging.basicConfig(filename = Log_File, level = logging.DEBUG)
	#logging.info(log)
	return None

############
# SERIAL
############

''' 
    Function: Starts a serial object at 9600 baud rate with default 
              settings
    Parameters: None
    Returns: Serial object ser
    StartSerial()
'''
def StartSerial():
    ser = serial.Serial(
      port="/dev/ttyS0",
      baudrate = 9600,
      parity = serial.PARITY_NONE,
      stopbits = serial.STOPBITS_ONE,
      bytesize = serial.EIGHTBITS,
      timeout = 1
    )
    return ser

# Initialize ser as Serial object
ser = StartSerial()

''' 
    Function: Sends a message to specified serial object
    Parameters: Serial ser, String message
    Returns: boolean True when done
    SendMessage(ser, "hello")
'''
def SendMessage(ser, message):
    ser.write(message)
    return True

''' 
    Function: Gets a message at specified Serial object
    Parameters: Serial ser
    Returns: String serial_message
    GetsMessage(ser)
'''
def GetMessage(ser):
    serial_message = ser.readline()
    return serial_message

''' 
    Function: Gets battery status from the serial data
    Parameters: None
    Returns: int battery_value
    GetBattery()
''' 
def GetBattery():
    SendMessage(ser, chr(Serial_Commands["battery"]))
    robot_battery = GetMessage(ser)
    InfoLog("Battery read at: " + str(robot_battery) + "%")
    SetBattery(robot_battery)
    return 15

def GetSensor():
    SendMessage(ser, chr(Serial_Commands["sensor_0"]))
    sensor_data = GetMessage(ser)
    InfoLog("Sensor 0 read at: " + str(sensor_data) + "%")
    SetSensor(sensor_data)
    return 15

############
# REQUESTS
############

def SetBattery(battery):
    r = requests.get("https://connection-robertoruano.c9users.io/PHP/set_battery.php?battery=" + str(battery))
    if r.status_code is 200:
        InfoLog("Succesfully set battery in web app")
        return True
    else:
        ErrorLog("Failed setting battery in web app with error code: " + string(r.status_code))
        return False

def SetSensor(sensor):
    r = requests.get("https://connection-robertoruano.c9users.io/PHP/set_sensor.php?sensor=" + str(sensor))
    if r.status_code is 200:
        InfoLog("Succesfully set sensor in web app")
        return True
    else:
        ErrorLog("Failed setting sensor in web app with error code: " + string(r.status_code))
        return False

def GetCall():
    global InCall
    s = requests.get("https://connection-robertoruano.c9users.io/PHP/call.html")
    string = str(s.content)
    if "calling" in string:
        InfoLog("Received call")
        InCall = True
        KillChromium()
        PlaceCall()
        return True
    else:
        InfoLog("No new call")
        InCall = False
        return False

def DropCall():
    global InCall
    InCall = False
    s = requests.get("https://connection-robertoruano.c9users.io/PHP/call.html")
    string = str(s.content)
    if "none" in string:
        SendMessage(ser, chr(Serial_Commands["stop"]))
        InfoLog("Dropped call")
        InCall = False
        KillChromium()
        StartGUI()
        return False
    else:
        InfoLog("Still in call")
        InCall = True
        return True

''' 
    Function: Gets file log.html, and returns the newest command
    Parameters: None
    Returns: char commands
    GetCommand()
'''
def GetCommand():
    global Old_Commands
    string = ""
    commands = "n"
    try:
        s = requests.get("https://connection-robertoruano.c9users.io/PHP/log.html")
        string = str(s.content)
        if len(string)>len(Old_Commands):
            character_numbers = len(Old_Commands)-len(string)
            Old_Commands = string
            commands = Old_Commands.strip()[-1]
            SendMessage(ser,chr(Key_Commands[commands] + Speed_Modes[Speed]))
            InfoLog("Read and sent command: " +  commands)
            return commands
        s = requests.get("https://connection-robertoruano.c9users.io/PHP/log.html")
        string = str(s.content)
        InfoLog("No new command")
        return commands
    except(KeyError):
        ErrorLog("Exception: KeyError in GetCommand")
        return commands

############
# INT. CONF.
############

''' 
    Function: Reads a .ini file and returns a dictionary
    Parameters: string ini_file, string section to be read
    Returns: dictionary with 'option': 'option value'
    GetIniFile("settings.ini", "settings_example")
''' 
def GetIniFile(ini_file, section):
    dict1 = {}
    config = ConfigParser.ConfigParser()
    config.read(str(ini_file))
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

''' 
    Function: Wrapper for GetIniFile and assigns the options
              /values read to the corresponding global variables
    Parameters: string ini_file, string section to be read
    Returns: None
    GetSettings("settings.ini", "settings_example")
''' 
def GetSettings(ini_file, section):
    settings = GetIniFile("robot.ini", "robot")
    Robot_Number = settings["robot_number"]
    WiFi = settings["wifi"]
    WiFi_Password = settings["wifi_password"]
    print Robot_Number
    return None

''' 
    Function: Gets current date and time
    Parameters: None
    Returns: string "day-month-year hour:minute:second"
    GetDate()
''' 
def GetDate():
    return strftime("%d-%m-%Y %H:%M:%S", gmtime())

''' 
    Function: Gets available WiFi networks
    Parameters: str interface (to use for scanning)
    Returns: list of strings with available SSID's
    ScanWifi()
''' 
def ScanWifi():
    interface = Wireless_Interface
    # Scan networks & generate a list of Cells
    networks = wifi.Cell.all(interface)
    # Declare list to hold SSID names, and fill it
    SSID_List = list()
    for network in networks:
        SSID_List.append(str(network.ssid) + ', ' + str(network.encryption_type) 
                         + ', ' + str(network.quality))
    # Return list with SSID strings
    InfoLog("Scanned networks: " + str(SSID_List))
    return SSID_List

''' 
    Function: Changes the settings screen variables to display all
              available wifi networks in the options_wifi container
    Parameters: str original_json_string (to modify)
    Returns: str modified_json_string (adds WiFi networks)
    ChangeSettings(settings_json)
''' 
def ChangeSettings(settings_json):
    #print settings_json
    test = settings_json.split("\"insertion\"")
    #print "Split str: " + str(test[0]) + str(test[1])
    SSID_List = ScanWifi()
    test = ''
    for ssid in SSID_List:
        ssid = '\"' + ssid + '\"'
        test = test + ',' + ssid
    json_string = settings_json.split("\"insertion\"")
    settings_json = json_string[0] + test[1:len(test)] + json_string[1]
    return settings_json

''' 
    Function: Connects to specified WiFi network using specified pwd
    Parameters: str interface (to connect with), str ssid (to connect to), 
                str password (to use)
    Returns: None
    ChangeWifi("Some_Network", "password")
''' 
def ChangeWifi(interface, ssid, password):
    cell = Cell.all(interface)[0]
    scheme = Scheme.for_cell(interface, 'robot_connection', ssid, password)
    scheme.save()
    scheme.activate()
    return None

def InternetOn():
    try:
        urllib2.urlopen('https://google.com', timeout=1)
        return True
    except urllib2.URLError as err: 
        return False

############
# JSON
############

def GetJSON(file):
    with open(file) as json_file:  
        settings = json.load(json_file)
        return settings

def UpdateGUI(file):
    with open(file) as json_file:  
        settings = json.load(json_file)
        settings["battery"] = GetBattery()
        InfoLog("Battery read and set at: " + str(settings["battery"]))
        settings["Internet"] = str(InternetOn())
        InfoLog("Internet works: " + settings["Internet"])
        DebugLog(settings)
        with open(file,'w') as json_file:
            json.dump(settings,json_file)

############
# PERIODIC
############

# This should be called every 1/3 of a second
def start_settings():
    robot_number_label = 'Robot: ' + GetIniFile("robot.ini","robot")["robot_number"]
    date = GetDate()
    Robot_ID = Robot_Password = "robot01"

# This should be called every 2.5 minutes
def get_battery():
    Robot_Battery = GetBattery()
    Battery_Text = str(Robot_Battery) + '%'

# This should be called every 16.666 milliseconds = 1/60 seconds
def get_command():
    GetCommand()

# This should be called every 16.666 milliseconds = 1/60 seconds
def get_call():
    if InCall is False:
        GetCall()
    else:
        DropCall()

# This should be called every 5 seconds
def get_sensor():
	GetSensor()

# Should be called every 3 minutes
def update_gui():
    UpdateGUI(JSON_File)

############
# THREADING
############
class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()


   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

##################################
# MAIN
##################################
if __name__ == '__main__':

    #StartGUI()

    getting_command = perpetualTimer(1.0 / 60.0,get_command)
    getting_call = perpetualTimer(6.0 / 60.0,get_call)
    getting_gui = perpetualTimer(200.0,update_gui)
    getting_sensor = perpetualTimer(5.0,get_sensor)
    getting_battery = perpetualTimer(300.0,get_battery)

    getting_command.start()
    #getting_call.start()
    #getting_gui.start()
    #getting_battery.start()
    #getting_sensor.start()
