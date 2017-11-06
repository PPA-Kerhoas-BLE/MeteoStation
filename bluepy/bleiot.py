from bluepy.btle import UUID, Peripheral, DefaultDelegate, AssignedNumbers
import struct
import math

def _STM32_UUID(val):
    return UUID("0000%08X-0000-1000-8000-00805f9B34fb" % (0x0F000000+val))

# Sensortag versions
AUTODETECT = "-"
SENSORTAG_V1 = "v1"
SENSORTAG_2650 = "CC2650"

class SensorBase:
    # Derived classes should set: svcUUID, ctrlUUID, dataUUID
    sensorOn  = struct.pack("B", 0x01)
    sensorOff = struct.pack("B", 0x00)


    def __init__(self, periph):
        self.periph = periph
        self.service = None
        self.ctrl = None
        self.data = None

    def enable(self):
        if self.service is None:
            self.service = self.periph.getServiceByUUID(self.svcUUID)
        if self.ctrl is None:
            self.ctrl = self.service.getCharacteristics(self.ctrlUUID) [0]
        if self.data is None:
            self.data = self.service.getCharacteristics(self.dataUUID) [0]
     #   if self.sensorOn is not None:
     #       self.ctrl.write(self.sensorOn,withResponse=True)

    def read(self):
        return self.data.read()

    def disable(self):
        if self.ctrl is not None:
            self.ctrl.write(self.sensorOff)

    # Derived class should implement _formatData()

def calcPoly(coeffs, x):
    return coeffs[0] + (coeffs[1]*x) + (coeffs[2]*x*x)

       
#=======================================================================

class HumiditySensor(SensorBase):
    svcUUID  = UUID("0000181a-0000-1000-8000-00805f9b34fb") #_STM32_UUID(0x181A)
    dataUUID = UUID("00002a6e-0000-1000-8000-00805f9b34fb") # _STM32_UUID(0x2A6F)
    ctrlUUID = UUID("00002a6f-0000-1000-8000-00805f9b34fb") # _STM32_UUID(0x2A6E)

    def __init__(self, periph):
        print("humidity sensorBase init")
        SensorBase.__init__(self, periph)

    def read(self):
        '''Returns (ambient_temp, rel_humidity)'''
        humidity=self.data.read()
        print("humidity = " + str(humidity))
        
        #(rawT, rawH) = struct.unpack('<HH', self.data.read())
        #temp = -46.85 + 175.72 * (rawT / 65536.0)
        #RH = -6.0 + 125.0 * ((rawH & 0xFFFC)/65536.0)
        return (humidity)

#=======================================================================

class SensorTag(Peripheral):
    def __init__(self,addr,version=AUTODETECT):
        Peripheral.__init__(self,addr)
        version = SENSORTAG_V1
        #if version==AUTODETECT:
        #    svcs = self.discoverServices()
        #    if _STM32_UUID(0xAA70) in svcs:
        #        version = SENSORTAG_2650
        #    else:
        #        version = SENSORTAG_V1

        #fwVers = self.getCharacteristics(uuid=AssignedNumbers.firmwareRevisionString)
        #if len(fwVers) >= 1:
        #    self.firmwareVersion = fwVers[0].read().decode("utf-8")
        #    print("Firmware Version = " + str(Self.fimwareVersion))
        #else:
        #    self.firmwareVersion = u''

        #if version==SENSORTAG_V1:
        self.humidity = HumiditySensor(self)
 
def main():
    import time
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('host', action='store',help='MAC of BT device')
    parser.add_argument('-n', action='store', dest='count', default=0,
            type=int, help="Number of times to loop data")
    parser.add_argument('-t',action='store',type=float, default=5.0, help='time between polling')
    parser.add_argument('-T','--temperature', action="store_true",default=False)
    parser.add_argument('-A','--accelerometer', action='store_true',
            default=False)
    parser.add_argument('-H','--humidity', action='store_true', default=False)
    parser.add_argument('-M','--magnetometer', action='store_true',
            default=False)
    parser.add_argument('-B','--barometer', action='store_true', default=False)
    parser.add_argument('-G','--gyroscope', action='store_true', default=False)
    parser.add_argument('-K','--keypress', action='store_true', default=False)
    parser.add_argument('-L','--light', action='store_true', default=False)
    parser.add_argument('-P','--battery', action='store_true', default=False)
    parser.add_argument('--all', action='store_true', default=False)

    arg = parser.parse_args(sys.argv[1:])

    print('Connecting to ' + arg.host)
    tag = SensorTag(arg.host)

    # Enabling selected sensors
    if arg.temperature or arg.all:
        tag.IRtemperature.enable()
    if arg.humidity or arg.all:
        tag.humidity.enable()
    if arg.barometer or arg.all:
        tag.barometer.enable()
    if arg.accelerometer or arg.all:
        tag.accelerometer.enable()
    if arg.magnetometer or arg.all:
        tag.magnetometer.enable()
    if arg.gyroscope or arg.all:
        tag.gyroscope.enable()
    if arg.battery or arg.all:
        tag.battery.enable()
    if arg.keypress or arg.all:
        tag.keypress.enable()
        tag.setDelegate(KeypressDelegate())
    if arg.light and tag.lightmeter is None:
        print("Warning: no lightmeter on this device")
    if (arg.light or arg.all) and tag.lightmeter is not None:
        tag.lightmeter.enable()

    # Some sensors (e.g., temperature, accelerometer) need some time for initialization.
    # Not waiting here after enabling a sensor, the first read value might be empty or incorrect.
    time.sleep(1.0)

    counter=1
    while True:
       if arg.humidity or arg.all:
           print("Humidity: ", tag.humidity.read())
       counter += 1
       tag.waitForNotifications(arg.t)

    tag.disconnect()
    del tag

if __name__ == "__main__":
    main()
