# Import library for serial communication
import serial
# Import library for using/processing system time
import time
# Import selenium for web automation
import selenium
# Import library to make web requests
import requests

# GLOBAL VARS

global ser

global Serial_Commands
Serial_Commands = {
    'forward': 0b00010000,
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
        'x': Serial_Commands['stop']
    }

global Old_Commands
Old_Commands = " "

# FUNCTIONS

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
    Function: Gets file log.html, and returns the newest command
    Parameters: None
    Returns: char commands
    GetCommand()
'''
def GetCommand():
    global Old_Commands
    string = ""
    commands = "n"
    s = requests.get("https://connection-robertoruano.c9users.io/PHP/log.html")
    string = str(s.content)
    if len(string)>len(Old_Commands):
        character_numbers = len(Old_Commands)-len(string)
        Old_Commands = string
        commands = Old_Commands.strip()[-1]
        SendMessage(ser,chr(Key_Commands[commands] + Speed_Modes['level_0']))
        return commands
    s = requests.get("https://connection-robertoruano.c9users.io/PHP/log.html")
    string = str(s.content)
    return commands

if __name__ == '__main__':
    while 1:
        print GetCommand()