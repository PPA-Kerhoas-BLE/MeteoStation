//
//  ViewController.swift
//  BLE_NUCLEO_iOS
//
//  Created by Paulo Henrique Favero Pereira on 05/10/2017.
//  Copyright © 2017 Paulo Henrique Favero Pereira. All rights reserved.
//

//
//  TemperatureViewController.swift
//  iOSRemoteConfBLEDemo
//
//  Created by Evan Stone on 4/9/16.
//  Copyright © 2016 Cloud City. All rights reserved.
//

import UIKit
import CoreBluetooth

// Conform to CBCentralManagerDelegate, CBPeripheralDelegate protocols

class ViewController: UIViewController, CBCentralManagerDelegate, CBPeripheralDelegate {
    
    @IBOutlet weak var temperatureLabel: UILabel!
    @IBOutlet weak var humidityLabel: UILabel!
    // define our scanning interval times
    let timerPauseInterval:TimeInterval = 10.0
    let timerScanInterval:TimeInterval = 2.0

    var keepScanning = false
    //var isScanning = false
    
    // Core Bluetooth properties
    var centralManager:CBCentralManager!
    var nucleoEnviroment:CBPeripheral?
    var temperatureCharacteristic:CBCharacteristic?
    var humidityCharacteristic:CBCharacteristic?

    
    
    // This could be simplified to "SensorTag" and check if it's a substring.
    // (Probably a good idea to do that if you're using a different model of
    // the SensorTag, or if you don't know what model it is...)
    let boardName = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()
        

        
        // Create our CBCentral Manager
        // delegate: The delegate that will receive central role events. Typically self.
        // queue:    The dispatch queue to use to dispatch the central role events.
        //           If the value is nil, the central manager dispatches central role events using the main queue.
        centralManager = CBCentralManager(delegate: self, queue: nil)
        
    }
    
    override func viewWillAppear(_ animated: Bool) {
        
    }
    
    
    // MARK: - Handling User Interaction
    

    
    func disconnect() {
        if let nucleoEnviroment = self.nucleoEnviroment {
            if let tc = self.temperatureCharacteristic {
                nucleoEnviroment.setNotifyValue(false, for: tc)
            }
            if let hc = self.humidityCharacteristic {
                nucleoEnviroment.setNotifyValue(false, for: hc)
            }
            
            /*
             NOTE: The cancelPeripheralConnection: method is nonblocking, and any CBPeripheral class commands
             that are still pending to the peripheral you’re trying to disconnect may or may not finish executing.
             Because other apps may still have a connection to the peripheral, canceling a local connection
             does not guarantee that the underlying physical link is immediately disconnected.
             
             From your app’s perspective, however, the peripheral is considered disconnected, and the central manager
             object calls the centralManager:didDisconnectPeripheral:error: method of its delegate object.
             */
            centralManager.cancelPeripheralConnection(nucleoEnviroment)
        }
        temperatureCharacteristic = nil
        humidityCharacteristic = nil
    }
    
    
    // MARK: - Bluetooth scanning
    
    @objc func pauseScan() {
        // Scanning uses up battery on phone, so pause the scan process for the designated interval.
        print("*** PAUSING SCAN...")
        _ = Timer(timeInterval: timerPauseInterval, target: self, selector: #selector(resumeScan), userInfo: nil, repeats: false)
        centralManager.stopScan()
        //disconnectButton.isEnabled = true
    }
    
    @objc func  resumeScan() {
        if keepScanning {
            // Start scanning again...
            print("*** RESUMING SCAN!")
            //disconnectButton.isEnabled = false
            temperatureLabel.text = "Searching"
            _ = Timer(timeInterval: timerScanInterval, target: self, selector: #selector(pauseScan), userInfo: nil, repeats: false)
            centralManager.scanForPeripherals(withServices: nil, options: nil)
        } else {
            //disconnectButton.isEnabled = true
        }
    }

    
    func displayTemperature(data:NSData) {
        // We'll get four bytes of data back, so we divide the byte count by two
        // because we're creating an array that holds two 16-bit (two-byte) values
        let dataLength = data.length / MemoryLayout<UInt16>.size
        var dataArray = [UInt16](repeating: 0, count:dataLength)
        data.getBytes(&dataArray, length: dataLength * MemoryLayout<Int16>.size)
        
        //        // output values for debugging/diagnostic purposes
        //        for i in 0 ..< dataLength {
        //            let nextInt:UInt16 = dataArray[i]
        //            print("next int: \(nextInt)")
        //        }
        
        let rawAmbientTemp:UInt16 = dataArray[Device.SensorDataIndexTempAmbient]
        let ambientTempC = Double(rawAmbientTemp) / 128.0
        let ambientTempF = convertCelciusToFahrenheit(celcius: ambientTempC)
        print("*** AMBIENT TEMPERATURE SENSOR (C/F): \(ambientTempC), \(ambientTempF)");
        
        // Device also retrieves an infrared temperature sensor value, which we don't use in this demo.
        // However, for instructional purposes, here's how to get at it to compare to the ambient temperature:
        let rawInfraredTemp:UInt16 = dataArray[Device.SensorDataIndexTempInfrared]
        let infraredTempC = Double(rawInfraredTemp) / 128.0
        let infraredTempF = convertCelciusToFahrenheit(celcius: infraredTempC)
        print("*** INFRARED TEMPERATURE SENSOR (C/F): \(infraredTempC), \(infraredTempF)");
        
        let temp = Int(ambientTempF)
        //lastTemperature = temp
        //print("*** LAST TEMPERATURE CAPTURED: \(lastTemperature)° F")
        
        if UIApplication.shared.applicationState == .active {
            
        }
    }
    
    func displayHumidity(data:NSData) {
        let dataLength = data.length / MemoryLayout<UInt16>.size
        var dataArray = [UInt16](repeating: 0, count:dataLength)
        data.getBytes(&dataArray, length: dataLength * MemoryLayout<Int16>.size)
        
        for i in 0 ..< dataLength {
            let nextInt:UInt16 = dataArray[i]
            print("next int: \(nextInt)")
        }
        
        let rawHumidity:UInt16 = dataArray[Device.SensorDataIndexHumidity]
        let calculatedHumidity = calculateRelativeHumidity(rawH: rawHumidity)
        print("*** HUMIDITY: \(calculatedHumidity)");
        humidityLabel.text = String(format: "Humidity: %.01f%%", calculatedHumidity)
        humidityLabel.isHidden = false
        
        // Humidity sensor also retrieves a temperature, which we don't use.
        // However, for instructional purposes, here's how to get at it to compare to the ambient sensor:
        let rawHumidityTemp:UInt16 = dataArray[Device.SensorDataIndexHumidityTemp]
        let calculatedTemperatureC = calculateHumidityTemperature(rawT: rawHumidityTemp)
        let calculatedTemperatureF = convertCelciusToFahrenheit(celcius: calculatedTemperatureC)
        print("*** HUMIDITY TEMP C: \(calculatedTemperatureC) F: \(calculatedTemperatureF)")
        
    }
    
    // MARK: - CBCentralManagerDelegate methods
    
    // Invoked when the central manager’s state is updated.
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        var showAlert = true
        var message = ""
        
        switch central.state {
        case .poweredOff:
            message = "Bluetooth on this device is currently powered off."
        case .unsupported:
            message = "This device does not support Bluetooth Low Energy."
        case .unauthorized:
            message = "This app is not authorized to use Bluetooth Low Energy."
        case .resetting:
            message = "The BLE Manager is resetting; a state update is pending."
        case .unknown:
            message = "The state of the BLE Manager is unknown."
        case .poweredOn:
            showAlert = false
            message = "Bluetooth LE is turned on and ready for communication."
            
            print(message)
            keepScanning = true
            _ = Timer(timeInterval: timerScanInterval, target: self, selector: #selector(pauseScan), userInfo: nil, repeats: false)
            
            // Initiate Scan for Peripherals
            //Option 1: Scan for all devices
            centralManager.scanForPeripherals(withServices: nil, options: nil)
            
            // Option 2: Scan for devices that have the service you're interested in...
            //let sensorTagAdvertisingUUID = CBUUID(string: Device.SensorTagAdvertisingUUID)
            //print("Scanning for SensorTag adverstising with UUID: \(sensorTagAdvertisingUUID)")
            //centralManager.scanForPeripheralsWithServices([sensorTagAdvertisingUUID], options: nil
        }
        
        if showAlert {
            let alertController = UIAlertController(title: "Central Manager State", message: message, preferredStyle: UIAlertControllerStyle.alert)
            let okAction = UIAlertAction(title: "OK", style: UIAlertActionStyle.cancel, handler: nil)
            alertController.addAction(okAction)
            self.show(alertController, sender: self)
        }
    }
    
    
    /*
     Invoked when the central manager discovers a peripheral while scanning.
     
     The advertisement data can be accessed through the keys listed in Advertisement Data Retrieval Keys.
     You must retain a local copy of the peripheral if any command is to be performed on it.
     In use cases where it makes sense for your app to automatically connect to a peripheral that is
     located within a certain range, you can use RSSI data to determine the proximity of a discovered
     peripheral device.
     
     central - The central manager providing the update.
     peripheral - The discovered peripheral.
     advertisementData - A dictionary containing any advertisement data.
     RSSI - The current received signal strength indicator (RSSI) of the peripheral, in decibels.
     
     */
    func centralManager(central: CBCentralManager, didDiscoverPeripheral peripheral: CBPeripheral, advertisementData: [String : AnyObject], RSSI: NSNumber) {
        print("centralManager didDiscoverPeripheral - CBAdvertisementDataLocalNameKey is \"\(CBAdvertisementDataLocalNameKey)\"")
        
        // Retrieve the peripheral name from the advertisement data using the "kCBAdvDataLocalName" key
        if let peripheralName = advertisementData[CBAdvertisementDataLocalNameKey] as? String {
            print("NEXT PERIPHERAL NAME: \(peripheralName)")
            print("NEXT PERIPHERAL UUID: \(peripheral.identifier.uuidString)")
            
            if peripheralName == boardName {
                print("SENSOR TAG FOUND! ADDING NOW!!!")
                // to save power, stop scanning for other devices
                keepScanning = false
                //disconnectButton.isEnabled = true
                
                // save a reference to the sensor tag
                nucleoEnviroment = peripheral
                nucleoEnviroment!.delegate = self
                
                // Request a connection to the peripheral
                centralManager.connect(nucleoEnviroment!, options: nil)
            }
        }
    }
    
    
    /*
     Invoked when a connection is successfully created with a peripheral.
     
     This method is invoked when a call to connectPeripheral:options: is successful.
     You typically implement this method to set the peripheral’s delegate and to discover its services.
     */
    func centralManager(central: CBCentralManager, didConnectPeripheral peripheral: CBPeripheral) {
        print("**** SUCCESSFULLY CONNECTED TO SENSOR TAG!!!")
        temperatureLabel.text = "Connected"
        
        // Now that we've successfully connected to the SensorTag, let's discover the services.
        // - NOTE:  we pass nil here to request ALL services be discovered.
        //          If there was a subset of services we were interested in, we could pass the UUIDs here.
        //          Doing so saves battery life and saves time.
        peripheral.discoverServices(nil)
    }
    
    
    /*
     Invoked when the central manager fails to create a connection with a peripheral.
     
     This method is invoked when a connection initiated via the connectPeripheral:options: method fails to complete.
     Because connection attempts do not time out, a failed connection usually indicates a transient issue,
     in which case you may attempt to connect to the peripheral again.
     */
    func centralManager(central: CBCentralManager, didFailToConnectPeripheral peripheral: CBPeripheral, error: NSError?) {
        print("**** CONNECTION TO SENSOR TAG FAILED!!!")
    }
    
    
    /*
     Invoked when an existing connection with a peripheral is torn down.
     
     This method is invoked when a peripheral connected via the connectPeripheral:options: method is disconnected.
     If the disconnection was not initiated by cancelPeripheralConnection:, the cause is detailed in error.
     After this method is called, no more methods are invoked on the peripheral device’s CBPeripheralDelegate object.
     
     Note that when a peripheral is disconnected, all of its services, characteristics, and characteristic descriptors are invalidated.
     */
    func centralManager(central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: NSError?) {
        print("**** DISCONNECTED FROM SENSOR TAG!!!")
        temperatureLabel.text = "Tap to search"
        humidityLabel.text = ""
        humidityLabel.isHidden = true
        if error != nil {
            print("****** DISCONNECTION DETAILS: \(error!.localizedDescription)")
        }
        nucleoEnviroment = nil
    }
    
    
    //MARK: - CBPeripheralDelegate methods
    
    /*
     Invoked when you discover the peripheral’s available services.
     
     This method is invoked when your app calls the discoverServices: method.
     If the services of the peripheral are successfully discovered, you can access them
     through the peripheral’s services property.
     
     If successful, the error parameter is nil.
     If unsuccessful, the error parameter returns the cause of the failure.
     */
    // When the specified services are discovered, the peripheral calls the peripheral:didDiscoverServices: method of its delegate object.
    func peripheral(peripheral: CBPeripheral, didDiscoverServices error: NSError?) {
        if error != nil {
            print("ERROR DISCOVERING SERVICES: \(error?.localizedDescription)")
            return
        }
        
        // Core Bluetooth creates an array of CBService objects —- one for each service that is discovered on the peripheral.
        if let services = peripheral.services {
            for service in services {
                print("Discovered service \(service)")
                // If we found either the temperature or the humidity service, discover the characteristics for those services.
                if (service.uuid == CBUUID(string: Device.TemperatureServiceUUID)) ||
                    (service.uuid == CBUUID(string: Device.HumidityServiceUUID)) {
                    peripheral.discoverCharacteristics(nil, for: service)
                }
            }
        }
    }
    
    
    /*
     Invoked when you discover the characteristics of a specified service.
     
     If the characteristics of the specified service are successfully discovered, you can access
     them through the service's characteristics property.
     
     If successful, the error parameter is nil.
     If unsuccessful, the error parameter returns the cause of the failure.
     */
    func peripheral(peripheral: CBPeripheral, didDiscoverCharacteristicsForService service: CBService, error: NSError?) {
        if error != nil {
            print("ERROR DISCOVERING CHARACTERISTICS: \(error?.localizedDescription)")
            return
        }
        
        if let characteristics = service.characteristics {
            var enableValue:UInt8 = 1
            let enableBytes = NSData(bytes: &enableValue, length: MemoryLayout<UInt8>.size)
            
            for characteristic in characteristics {
                // Temperature Data Characteristic
                if characteristic.uuid == CBUUID(string: Device.TemperatureDataUUID) {
                    // Enable the IR Temperature Sensor notifications
                    temperatureCharacteristic = characteristic
                    nucleoEnviroment?.setNotifyValue(true, for: characteristic)
                }
                
                // Temperature Configuration Characteristic
                if characteristic.uuid == CBUUID(string: Device.TemperatureConfig) {
                    // Enable IR Temperature Sensor
                    nucleoEnviroment?.writeValue(enableBytes as Data, for: characteristic, type: .withResponse)
                }
                
                if characteristic.uuid == CBUUID(string: Device.HumidityDataUUID) {
                    // Enable Humidity Sensor notifications
                    humidityCharacteristic = characteristic
                    nucleoEnviroment?.setNotifyValue(true, for: characteristic)
                }
                
                if characteristic.uuid == CBUUID(string: Device.HumidityConfig) {
                    // Enable Humidity Temperature Sensor
                    nucleoEnviroment?.writeValue(enableBytes as Data, for: characteristic, type: .withResponse)
                }
            }
        }
    }
    
    
    /*
     Invoked when you retrieve a specified characteristic’s value,
     or when the peripheral device notifies your app that the characteristic’s value has changed.
     
     This method is invoked when your app calls the readValueForCharacteristic: method,
     or when the peripheral notifies your app that the value of the characteristic for
     which notifications and indications are enabled has changed.
     
     If successful, the error parameter is nil.
     If unsuccessful, the error parameter returns the cause of the failure.
     */
    func peripheral(peripheral: CBPeripheral, didUpdateValueForCharacteristic characteristic: CBCharacteristic, error: NSError?) {
        if error != nil {
            print("ERROR ON UPDATING VALUE FOR CHARACTERISTIC: \(characteristic) - \(error?.localizedDescription)")
            return
        }
        
        // extract the data from the characteristic's value property and display the value based on the characteristic type
        if let dataBytes = characteristic.value {
            if characteristic.uuid == CBUUID(string: Device.TemperatureDataUUID) {
                displayTemperature(data: dataBytes as NSData)
            } else if characteristic.uuid == CBUUID(string: Device.HumidityDataUUID) {
                displayHumidity(data: dataBytes as NSData)
            }
        }
    }
    
    
    // MARK: - TI Sensor Tag Utility Methods
    
    func convertCelciusToFahrenheit(celcius:Double) -> Double {
        let fahrenheit = (celcius * 1.8) + Double(32)
        return fahrenheit
    }
    
    func calculateRelativeHumidity(rawH:UInt16) -> Double {
        // clear status bits [1..0]
        let clearedH = rawH & ~0x003
        
        //-- calculate relative humidity [%RH] --
        // RH= -6 + 125 * SRH/2^16
        let relativeHumidity:Double = -6.0 + 125.0/65536 * Double(clearedH)
        return relativeHumidity
    }
    
    func calculateHumidityTemperature(rawT:UInt16) -> Double {
        //-- calculate temperature [deg C] --
        let temp = -46.85 + 175.72/65536 * Double(rawT);
        return temp;
    }
    
}


