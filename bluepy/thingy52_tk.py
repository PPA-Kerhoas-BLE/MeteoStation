#! /usr/bin/python3

# http://wordsmakeworlds.com/programming-tutorials/bluetooth-control-with-python-and-an-arduino/
# http://fab.cba.mit.edu/classes/863.16/section.CBA/people/Williams/files/finalproj/ble.py
# http://fab.cba.mit.edu/classes/863.16/section.CBA/people/Williams/week13.html
# https://r0b0t.files.wordpress.com/2017/01/ostest11.pdf
# https://stackoverflow.com/questions/32807781/ble-subscribe-to-notification-using-gatttool-or-bluepy

from bluepy.btle import UUID, Peripheral, ADDR_TYPE_PUBLIC, DefaultDelegate
from tkinter import *
import argparse
import time
import struct
import binascii




#=======================================================================

def write_uint16(data, value, index):
    """ Write 16bit value into data string at index and return new string """
    data = data.decode('utf-8')  # This line is added to make sure both Python 2 and 3 works
    return '{}{:02x}{:02x}{}'.format(
                data[:index*4], 
                value & 0xFF, value >> 8, 
                data[index*4 + 4:])

def write_uint8(data, value, index):
    """ Write 8bit value into data string at index and return new string """
    data = data.decode('utf-8')  # This line is added to make sure both Python 2 and 3 works
    return '{}{:02x}{}'.format(
                data[:index*2], 
                value, 
                data[index*2 + 2:])

# Please see # Ref https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
# for more information on the UUIDs of the Services and Characteristics that are being used
def STM32_UUID(val):
    """ Adds base UUID and inserts value to return Nordic UUID """
    return UUID("0000%04X-0000-1000-8000-00805F9B34FB" % val)
# 0000181a-0000-1000-8000-00805f9b34fb
# Definition of all UUID used by Thingy

ENVIRONMENT_SERVICE_UUID = 0x181A
E_TEMPERATURE_CHAR_UUID = 0x2A6E
E_HUMIDITY_CHAR_UUID    = 0x2A6F

LIGHTSWITCH_SERVICE_UUID = 0xFF10
SWITCHLED_CHAR_UUID = 0xFF12
LEDSTATE_CHAR_UUID  = 0xFF11

#CCCD_UUID = 0x2902

CCCD_UUID = 0x2902

# Notification handles used in notification delegate
e_temperature_handle = None
e_humidity_handle = None
m_tap_handle = None

switchled_handle = None
ledstate_handle = None

ledstate = 0
data_temperature=0
data_humidity=0
data_state=0




#=======================================================================

class LightSwitchService():
    serviceUUID = STM32_UUID(LIGHTSWITCH_SERVICE_UUID )
    switchled_char_uuid = STM32_UUID(SWITCHLED_CHAR_UUID)
    ledstate_char_uuid = STM32_UUID(LEDSTATE_CHAR_UUID)
    
    def __init__(self, periph):
        self.periph = periph
        self.lightswitch_service = None
        self.switchled_char = None
        self.switchled_cccd = None
        self.ledstate_char = None
        self.ledstate_cccd = None
	
    def enable(self):
        """ Enables the class by finding the service and its characteristics. """
        global switchled_handle
        global ledstate_handle

        if self.lightswitch_service is None:
            self.lightswitch_service = self.periph.getServiceByUUID(self.serviceUUID)
        if self.switchled_char is None:
            self.switchled_char = self.lightswitch_service.getCharacteristics(self.switchled_char_uuid)[0]
            switchled_handle = self.switchled_char.getHandle()
         #   self.switchled_cccd = self.switchled_char.getDescriptors(forUUID=CCCD_UUID)[0]
        if self.ledstate_char is None:
            self.ledstate_char = self.lightswitch_service.getCharacteristics(self.ledstate_char_uuid)[0]
            ledstate_handle = self.ledstate_char.getHandle()
            self.ledstate_cccd = self.ledstate_char.getDescriptors(forUUID=CCCD_UUID)[0]


    def set_switchled_notification(self, state):
        if self.switchled_cccd is not None:
            if state == True:
                self.switchled_cccd.write(b"\x01\x00", True)
            else:
                self.switchled_cccd.write(b"\x00\x00", True)

    def set_ledstate_notification(self, state):
        if self.ledstate_cccd is not None:
            if state == True:
                self.ledstate_cccd.write(b"\x01\x00", True)
            else:
                self.ledstate_cccd.write(b"\x00\x00", True)
                
    def set_switch_led_on(self):
           self.switchled_char.write(b"\x01", True)             

    def set_switch_led_off(self):
           self.switchled_char.write(b"\x00", True)  

    def disable(self):
        set_switchled_notification(False)
        set_ledstate_notification(False)

#=======================================================================

class EnvironmentService():
    """
    Environment service module. Instance the class and enable to get access to the Environment interface.
    """
    serviceUUID =           STM32_UUID(ENVIRONMENT_SERVICE_UUID)
    temperature_char_uuid = STM32_UUID(E_TEMPERATURE_CHAR_UUID)
    humidity_char_uuid =    STM32_UUID(E_HUMIDITY_CHAR_UUID)


    def __init__(self, periph):
        self.periph = periph
        self.environment_service = None
        self.temperature_char = None
        self.temperature_cccd = None
        self.humidity_char = None
        self.humidity_cccd = None


    def enable(self):
        """ Enables the class by finding the service and its characteristics. """
        global e_temperature_handle
        global e_humidity_handle

        if self.environment_service is None:
            self.environment_service = self.periph.getServiceByUUID(self.serviceUUID)
        if self.temperature_char is None:
            self.temperature_char = self.environment_service.getCharacteristics(self.temperature_char_uuid)[0]
            e_temperature_handle = self.temperature_char.getHandle()
            self.temperature_cccd = self.temperature_char.getDescriptors(forUUID=CCCD_UUID)[0]
        if self.humidity_char is None:
            self.humidity_char = self.environment_service.getCharacteristics(self.humidity_char_uuid)[0]
            e_humidity_handle = self.humidity_char.getHandle()
            self.humidity_cccd = self.humidity_char.getDescriptors(forUUID=CCCD_UUID)[0]

    def set_temperature_notification(self, state):
        if self.temperature_cccd is not None:
            if state == True:
                print("temperature write")				
                self.temperature_cccd.write(b"\x01\x00", True)
            else:
                self.temperature_cccd.write(b"\x00\x00", True)

    def set_humidity_notification(self, state):
        if self.humidity_cccd is not None:
            if state == True:
                print("humidity write")
                self.humidity_cccd.write(b"\x01\x00", True)
            else:
                self.humidity_cccd.write(b"\x00\x00", True)

    def disable(self):
        set_temperature_notification(False)
        set_humidity_notification(False)


#=======================================================================

class MyDelegate(DefaultDelegate):
    
    def handleNotification(self, hnd, data):
        global data_temperature, data_humidity, data_state
        if (hnd == e_temperature_handle):
            teptep = binascii.b2a_hex(data)
            #print('Notification: Temp received:  {}.{} degCelcius'.format(self._str_to_int(teptep[:-2]), int(teptep[-2:], 16)))
            
            #print('Notification: Temp received:  {} degCelcius'.format(self._str_to_int(teptep[:-2]), 16))
            print("Notification: Temp received:" + str(data))
            data_temperature = data    
        elif (hnd == e_humidity_handle):
            teptep = binascii.b2a_hex(data)
            #print('Notification: Humidity received: {} %'.format(self._str_to_int(teptep)))  
            print("Notification: Humidity received:" + str(data))
            data_humidity = data
        elif (hnd == ledstate_handle):   
            data_state = data
    

    def _str_to_int(self, s):
        """ Transform hex str into int. """
        i = int(s, 16)
        if i >= 2**7:
            i -= 2**8
        return i    

#=======================================================================

class Thingy52(Peripheral):
    """
    Thingy:52 module. Instance the class and enable to get access to the Thingy:52 Sensors.
    The addr of your device has to be know, or can be found by using the hcitool command line 
    tool, for example. Call "> sudo hcitool lescan" and your Thingy's address should show up.
    """
    def __init__(self, addr):
        Peripheral.__init__(self, addr, addrType=ADDR_TYPE_PUBLIC)
        self.environment = EnvironmentService(self)
        self.lightswitch = LightSwitchService(self)

#=======================================================================

def askFordatas():
    thingy.waitForNotifications(args.t)
    strTemperature.set(str(data_temperature) + ' --- ' + time.ctime())
    strHumidity.set(str(data_humidity) + ' --- ' + time.ctime())   
    strLedState.set(str(data_state) + ' --- ' + time.ctime())
   
    ui.after(1,askFordatas)
    

def onPushSwitch():
    global ledstate
    if ledstate == 0:
        print("switch on")
        thingy.lightswitch.set_switch_led_on()
        ledstate = 1
    else:
        print("switch off")
        thingy.lightswitch.set_switch_led_off()
        ledstate = 0
        
#=======================================================================

if  __name__ == "__main__" :
    parser = argparse.ArgumentParser()
    parser.add_argument('mac_address', action='store', help='MAC address of BLE peripheral')
    parser.add_argument('-n', action='store', dest='count', default=0, type=int, help="Number of times to loop data")
    parser.add_argument('-t',action='store',type=float, default=2.0, help='time between polling')
    parser.add_argument('--temperature', action="store_true",default=False)
    parser.add_argument('--humidity', action="store_true",default=False)
    parser.add_argument('--keypress', action='store_true', default=False)
    parser.add_argument('--tap', action='store_true', default=False)
    parser.add_argument('--stepcnt', action='store_true', default=False)

    args = parser.parse_args()

    print('Connecting to ' + args.mac_address)
    thingy = Thingy52(args.mac_address)
    print('Connected...')
    thingy.setDelegate(MyDelegate())
    
    print('Enabling selected sensors...')
    
    thingy.environment.enable()
    thingy.environment.set_temperature_notification(True)
    thingy.environment.enable()
    thingy.environment.set_humidity_notification(True)       
    thingy.lightswitch.enable()
    thingy.lightswitch.set_ledstate_notification(True)    
    
    print('All requested sensors and notifications are enabled...')
    time.sleep(1.0)    
    
    #-------------------------------------------------------------------
    ui=Tk()
    ui.title("BLEIOT")
    ui.geometry("200x200")

    labelTemperature=Label(ui, text="Temperature", font=("Arial", 10), fg="black")
    labelTemperature.pack()
 
    strTemperature = StringVar()
    TemperatureEntry=Entry(ui, textvariable=strTemperature)
    TemperatureEntry.pack()
    
    labelHumidity=Label(ui, text="Humidity", font=("Arial", 10), fg="black")
    labelHumidity.pack()
 
    strHumidity=StringVar()
    HumidityEntry=Entry(ui, textvariable=strHumidity)
    HumidityEntry.pack()
    
    switchButton=Button(ui, text="SWITCH LED", font=("Arial",10, "bold"), bg="seagreen3", fg="black", bd=3, relief=RAISED, command=onPushSwitch)
    switchButton.pack()
    
    strLedState=StringVar()
    strLedEntry=Entry(ui, textvariable=strLedState)
    strLedEntry.pack()
    
    
    ui.after(1,askFordatas)
    
    ui.mainloop()  
	
    #-------------------------------------------------------------------       

#    thingy.disconnect()
#    del thingy


#=======================================================================
# $ sudo python3 thingy52_2.py  02:80:e1:00:00:ab --temperature -n 10000
