from bluepy.btle import UUID, Peripheral, ADDR_TYPE_PUBLIC, DefaultDelegate
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
def Nordic_UUID(val):
    """ Adds base UUID and inserts value to return Nordic UUID """
    return UUID("0000%04X-0000-1000-8000-00805F9B34FB" % val)
# 0000181a-0000-1000-8000-00805f9b34fb


# Definition of all UUID used by Thingy
CCCD_UUID = 0x2902

BATTERY_SERVICE_UUID = 0x180F
BATTERY_LEVEL_UUID = 0x2A19

ENVIRONMENT_SERVICE_UUID = 0x181A
E_TEMPERATURE_CHAR_UUID = 0x2A6F
E_PRESSURE_CHAR_UUID    = 0x0202
E_HUMIDITY_CHAR_UUID    = 0x2A6E
E_GAS_CHAR_UUID         = 0x0204
E_COLOR_CHAR_UUID       = 0x0205
E_CONFIG_CHAR_UUID      = 0x0206

USER_INTERFACE_SERVICE_UUID = 0x0300
UI_LED_CHAR_UUID            = 0x0301
UI_BUTTON_CHAR_UUID         = 0x0302
UI_EXT_PIN_CHAR_UUID        = 0x0303

MOTION_SERVICE_UUID         = 0x0400
M_CONFIG_CHAR_UUID          = 0x0401
M_TAP_CHAR_UUID             = 0x0402
M_ORIENTATION_CHAR_UUID     = 0x0403
M_QUATERNION_CHAR_UUID      = 0x0404
M_STEP_COUNTER_UUID         = 0x0405
M_RAW_DATA_CHAR_UUID        = 0x0406
M_EULER_CHAR_UUID           = 0x0407
M_ROTATION_MATRIX_CHAR_UUID = 0x0408
M_HEAIDNG_CHAR_UUID         = 0x0409
M_GRAVITY_VECTOR_CHAR_UUID  = 0x040A

SOUND_SERVICE_UUID          = 0x0500
S_CONFIG_CHAR_UUID          = 0x0501
S_SPEAKER_DATA_CHAR_UUID    = 0x0502
S_SPEAKER_STATUS_CHAR_UUID  = 0x0503
S_MICROPHONE_CHAR_UUID      = 0x0504

# Notification handles used in notification delegate
e_temperature_handle = None
e_pressure_handle = None
e_humidity_handle = None
e_gas_handle = None
e_color_handle = None
ui_button_handle = None
m_tap_handle = None
m_orient_handle = None
m_quaternion_handle = None
m_stepcnt_handle = None
m_rawdata_handle = None
m_euler_handle = None
m_rotation_handle = None
m_heading_handle = None
m_gravity_handle = None
s_speaker_status_handle = None
s_microphone_handle = None

#=======================================================================

class EnvironmentService():
    """
    Environment service module. Instance the class and enable to get access to the Environment interface.
    """
    serviceUUID =           Nordic_UUID(ENVIRONMENT_SERVICE_UUID)
    temperature_char_uuid = Nordic_UUID(E_TEMPERATURE_CHAR_UUID)
    humidity_char_uuid =    Nordic_UUID(E_HUMIDITY_CHAR_UUID)
    config_char_uuid =      Nordic_UUID(E_CONFIG_CHAR_UUID)

    def __init__(self, periph):
        self.periph = periph
        self.environment_service = None
        self.temperature_char = None
        self.temperature_cccd = None
        self.humidity_char = None
        self.humidity_cccd = None
        self.config_char = None

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
       # if self.config_char is None:
       #     self.config_char = self.environment_service.getCharacteristics(self.config_char_uuid)[0]

    def set_temperature_notification(self, state):
        if self.temperature_cccd is not None:
            if state == True:
                self.temperature_cccd.write(b"\x01\x00", True)
            else:
                self.temperature_cccd.write(b"\x00\x00", True)

    def set_humidity_notification(self, state):
        if self.humidity_cccd is not None:
            if state == True:
                self.humidity_cccd.write(b"\x01\x00", True)
            else:
                self.humidity_cccd.write(b"\x00\x00", True)

   # def configure(self, temp_int=None, press_int=None, humid_int=None, gas_mode_int=None,
   #                     color_int=None, color_sens_calib=None):
   #     if temp_int is not None and self.config_char is not None:
   #         current_config = binascii.b2a_hex(self.config_char.read())
   #         new_config = write_uint16(current_config, temp_int, 0)
   #         self.config_char.write(binascii.a2b_hex(new_config), True)
   #     if humid_int is not None and self.config_char is not None:
   #         current_config = binascii.b2a_hex(self.config_char.read())
   #         new_config = write_uint16(current_config, humid_int, 2)
   #         self.config_char.write(binascii.a2b_hex(new_config), True)

    def disable(self):
        set_temperature_notification(False)
        set_humidity_notification(False)


#=======================================================================

class MyDelegate(DefaultDelegate):
    
    def handleNotification(self, hnd, data):
        #Debug print repr(data)
        if (hnd == e_temperature_handle):
            teptep = binascii.b2a_hex(data)
            #print('Notification: Temp received:  {}.{} degCelcius'.format(
            #            self._str_to_int(teptep[:-2]), int(teptep[-2:], 16)))
            print("Notification: Temp received:" + str(data))            
        elif (hnd == e_humidity_handle):
            teptep = binascii.b2a_hex(data)
            print('Notification: Humidity received: {} %'.format(self._str_to_int(teptep)))      

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

        # Thingy configuration service not implemented
        #self.battery = BatterySensor(self)
        self.environment = EnvironmentService(self)
        #self.ui = UserInterfaceService(self)
        #self.motion = MotionService(self)
        #self.sound = SoundService(self)
        # DFU Service not implemented

#=======================================================================

def main():
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

    try:
        # Set LED so that we know we are connected
        #thingy.ui.enable()
        #thingy.ui.set_led_mode_breathe(0x01, 50, 100) # 0x01 = RED
        #print('LED set to breathe mode...')

        # Enabling selected sensors
        print('Enabling selected sensors...')
        # Environment Service
        if args.temperature:
            thingy.environment.enable()
           # thingy.environment.configure(temp_int=1000)
            thingy.environment.set_temperature_notification(True)
        if args.humidity:
            thingy.environment.enable()
           # thingy.environment.configure(humid_int=1000)
            thingy.environment.set_humidity_notification(True)

        # Allow sensors time to start up (might need more time for some sensors to be ready)
        print('All requested sensors and notifications are enabled...')
        time.sleep(1.0)
        
        counter=1
        while True:
            if counter >= args.count:
                break
            
            counter += 1
            thingy.waitForNotifications(args.t)

    finally:
        thingy.disconnect()
        del thingy


if __name__ == "__main__":
    main()

#=======================================================================
# $ sudo python3 thingy52_2.py  02:80:e1:00:00:ab --temperature -n 10000
