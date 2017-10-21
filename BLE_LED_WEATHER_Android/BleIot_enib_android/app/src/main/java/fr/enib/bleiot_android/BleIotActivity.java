package fr.enib.bleiot_android;

import android.app.Activity;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

//http://www.truiton.com/2015/04/android-bluetooth-low-energy-ble-example/

//==================================================================================================
public class BleIotActivity extends Activity {

    private static final String TAG = "BleIotActivity";
    private static TextView ledState;
    AlertDialog mSelectionDialog;
    DevicesAdapter mDevicesAdapter;
    BluetoothAdapter mBluetoothAdapter;
    BluetoothLeScanner mBluetoothLeScanner;
    private BluetoothLeScanner mLEScanner;
    private ScanSettings settings;
    Handler mHandler;
    boolean mScanning;
    BluetoothGatt mGatt;
    BluetoothGatt mWriteCharac;
    private Queue<BluetoothGattDescriptor> descriptorWriteQueue = new LinkedList<>();
    private static final int SCAN_PERIOD = 10000;
    private static final int REQUEST_ENABLE_BT = 1;
    public static BluetoothGattCharacteristic mWriteCharacteristic;

    //==================================================================================================
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        mHandler = new Handler();
        mDevicesAdapter = new DevicesAdapter(getLayoutInflater());

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(R.string.select_device);
        builder.setAdapter(mDevicesAdapter, new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialogInterface, int i) {
                finishScanning();
                BluetoothDevice device = (BluetoothDevice) mDevicesAdapter.getItem(i);
                if (device != null) {
                    Log.i(TAG, "Connecting to GATT server at: " + device.getAddress());
                    mGatt = device.connectGatt(BleIotActivity.this, false, mGattCallback);
                }
            }
        });
        builder.setNegativeButton(R.string.cancel, null);
        builder.setOnDismissListener(new DialogInterface.OnDismissListener() {
            @Override
            public void onDismiss(DialogInterface dialogInterface) {
                finishScanning();
            }
        });
        mSelectionDialog = builder.create();

        BluetoothManager bluetoothManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        mBluetoothAdapter = bluetoothManager.getAdapter();

        mLEScanner = mBluetoothAdapter.getBluetoothLeScanner(); //++++++++++++++++++++++++++
        settings = new ScanSettings.Builder()
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                .build();

        setContentView(R.layout.activity_bleiot);
    }
//==================================================================================================
//                      SWITCH LED BUTTON
//==================================================================================================

    public void onSwitchLedClick(View view) {

        BluetoothGattCharacteristic charac = null;
        List<BluetoothGattService> gattServices = getSupportedGattServices();

        if (gattServices == null) {
            Log.w(TAG, "Not services found.");
            return;
        }

        for (BluetoothGattService gattService : gattServices) {
            List<BluetoothGattCharacteristic> gattCharacteristics = gattService.getCharacteristics();
            for (BluetoothGattCharacteristic gattCharacteristic : gattCharacteristics) {
                if (gattCharacteristic.getUuid().equals(AssignedNumber.getBleUuid("switch led"))) {
                    charac = gattCharacteristic;
                }
            }
        }

        if (charac == null) {
            Log.e(TAG, "char not found!");
            return;
        }

        byte[] value = new byte[1];
        value[0] = (byte) (21 & 0xFF);
        charac.setValue(value);
        boolean status = mGatt.writeCharacteristic(charac);

        return ;
    }

    //==================================================================================================
    public void onConnectClick(View view) {
        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        } else {
            String btnText = ((Button) view).getText().toString();
            if (btnText.equals(getString(R.string.connect))) {
                openSelectionDialog();
            } else if (btnText.equals(getString(R.string.disconnect))) {
                mGatt.disconnect();
                mGatt.close();
                updateConnectButton(BluetoothProfile.STATE_DISCONNECTED);
            }
        }
    }

    //==================================================================================================
    void openSelectionDialog() {
        beginScanning();
        mSelectionDialog.show();
    }

    //==================================================================================================
    private void beginScanning() {
        if (!mScanning) {
            // Stops scanning after a pre-defined scan period.
            mHandler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    finishScanning();
                }
            }, SCAN_PERIOD);

            mDevicesAdapter.clear();
            mDevicesAdapter.add(null);
            mDevicesAdapter.updateScanningState(mScanning = true);
            mDevicesAdapter.notifyDataSetChanged();

            mLEScanner.startScan(mScanCallback);//+++++++//  mBluetoothAdapter.startLeScan(mLeScanCallback);//--------
        }
    }
    //==================================================================================================
    private void finishScanning() {
        if (mScanning) {
            if (mDevicesAdapter.getItem(0) == null) {
                mDevicesAdapter.notifyDataSetChanged();
            }
            mLEScanner.stopScan(mScanCallback);//+++++++//mBluetoothAdapter.stopLeScan(mLeScanCallback); //------
        }
    }
    //==================================================================================================
    private void disconnect() {
        if (mGatt != null) {
            mGatt.disconnect();
            mGatt.close();
            mGatt = null;
        }
    }
    //==================================================================================================
    @Override
    protected void onPause() {
        super.onPause();
        finishScanning();
    }
    //==================================================================================================
    @Override
    protected void onDestroy() {
        super.onDestroy();
        disconnect();
    }
    //==================================================================================================
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQUEST_ENABLE_BT) {
            if (resultCode == Activity.RESULT_OK) {
                openSelectionDialog();
            } else if (resultCode == Activity.RESULT_CANCELED) {
                Toast.makeText(this, "App cannot run with bluetooth off", Toast.LENGTH_LONG).show();
                finish();
            }
        } else
            super.onActivityResult(requestCode, resultCode, data);
    }

    //==================================================================================================
    private void updateConnectButton(int state) {
        Button connectBtn = (Button) BleIotActivity.this.findViewById(R.id.connect_button);
        switch (state) {
            case BluetoothProfile.STATE_DISCONNECTED:
                connectBtn.setText(getString(R.string.connect));
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        TextView humidityTxt = (TextView) BleIotActivity.this.findViewById(R.id.Hvalue);
                        humidityTxt.setText(R.string.Hvalue);
                        TextView temperatureTxt = (TextView)BleIotActivity.this.findViewById(R.id.Tvalue);
                        temperatureTxt.setText(R.string.Tvalue);
                        //TODO
                        TextView pressureTxt = (TextView)BleIotActivity.this.findViewById(R.id.pressureId);
                        pressureTxt.setText(R.string.Pvalue);
                    }
                });
                break;
            case BluetoothProfile.STATE_CONNECTING:
                connectBtn.setText(getString(R.string.connecting));
                break;
            case BluetoothProfile.STATE_CONNECTED:
                connectBtn.setText(getString(R.string.disconnect));
                break;
        }
    }

    //==================================================================================================
    private ScanCallback mScanCallback = new ScanCallback() {
        @Override
        public void onScanResult(int callbackType, ScanResult result) {
            Log.i("callbackType", String.valueOf(callbackType));
            Log.i("result", result.toString());
            BluetoothDevice bluetoothDevice = result.getDevice();
            connectToDevice(bluetoothDevice);
            mDevicesAdapter.add(bluetoothDevice);
            mDevicesAdapter.notifyDataSetChanged();
        }

        @Override
        public void onBatchScanResults(List<ScanResult> results) {
            for (ScanResult sr : results) {
                Log.i("ScanResult - Results", sr.toString());
            }
        }

        @Override
        public void onScanFailed(int errorCode) {
            Log.e("Scan Failed", "Error Code: " + errorCode);
        }
    };
    //==================================================================================================
    public void connectToDevice(BluetoothDevice device) {
        if (mGatt == null) {
            mGatt = device.connectGatt(this, false,  mGattCallback);
            finishScanning();// will stop after first device detection
        }
    }
    //==================================================================================================
    private BluetoothGattCallback mGattCallback = new BluetoothGattCallback() {
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, final int newState) {
            super.onConnectionStateChange(gatt, status, newState);

            if (newState == BluetoothProfile.STATE_CONNECTED) {
                Log.i(TAG, "Connected to GATT server.");
                if (mGatt.discoverServices()) {
                    Log.i(TAG, "Started service discovery.");
                } else {
                    Log.w(TAG, "Service discovery failed.");
                }
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                Log.i(TAG, "Disconnected from GATT server.");
            }
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    updateConnectButton(newState);
                }
            });
        }
//==================================================================================================
//        Callback called when a service is discovered
//        Make a list of supported GATT services and subscribe to the characteristics.
//==================================================================================================
        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            super.onServicesDiscovered(gatt, status);

            List<BluetoothGattService> gattServices = getSupportedGattServices();

            if (gattServices == null) {
                Log.w(TAG, "Not services found.");
                return;
            }

            for (BluetoothGattService gattService : gattServices) {
                List<BluetoothGattCharacteristic> gattCharacteristics = gattService.getCharacteristics();
                for (BluetoothGattCharacteristic gattCharacteristic : gattCharacteristics) {

                    if (gattCharacteristic.getUuid().equals(AssignedNumber.getBleUuid("Humidity"))) {

                        mGatt.setCharacteristicNotification(gattCharacteristic, true);// Enable notifications.

                        BluetoothGattDescriptor descriptor = gattCharacteristic.getDescriptor(AssignedNumber.getBleUuid("Client Characteristic Configuration"));
                        descriptor.setValue( BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE );
                        writeGattDescriptor(descriptor);
                        Log.i(TAG, "Humidity characteristic subscription done");
                    }
//TODO
                    if (gattCharacteristic.getUuid().equals(AssignedNumber.getBleUuid("Pressure"))) {

                        mGatt.setCharacteristicNotification(gattCharacteristic, true);// Enable notifications.

                        BluetoothGattDescriptor descriptor = gattCharacteristic.getDescriptor(AssignedNumber.getBleUuid("Client Characteristic Configuration"));
                        descriptor.setValue( BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE );
                        writeGattDescriptor(descriptor);
                        Log.i(TAG, "Pressure characteristic subscription done");
                    }

                    if (gattCharacteristic.getUuid().equals(AssignedNumber.getBleUuid("switch led"))) {

                        mGatt.setCharacteristicNotification(gattCharacteristic, true);// Enable notifications.
                        Log.i(TAG, "SWITCH LED subscription done");
                    }

                    if (gattCharacteristic.getUuid().equals(AssignedNumber.getBleUuid("led state"))) {

                        mGatt.setCharacteristicNotification(gattCharacteristic, true);// Enable notifications.
                        BluetoothGattDescriptor descriptor = gattCharacteristic.getDescriptor(AssignedNumber.getBleUuid("Client Characteristic Configuration"));
                        descriptor.setValue( BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE );
                        writeGattDescriptor(descriptor);
                        Log.i(TAG, "LED STATE subscription done");
                    }

                    if (gattCharacteristic.getUuid().equals(AssignedNumber.getBleUuid("Temperature"))) {

                        mGatt.setCharacteristicNotification(gattCharacteristic, true);// Enable notifications.
                        BluetoothGattDescriptor descriptor = gattCharacteristic.getDescriptor(AssignedNumber.getBleUuid("Client Characteristic Configuration"));
                        descriptor.setValue( BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE );
                        writeGattDescriptor(descriptor);
                        Log.i(TAG, "Temperature characteristic subscription done");
                    }
                }
            }
        }

//==================================================================================================
//                          Callback called when a characteristic change
//              Check which characteristic has changed and update the TextView accordingly
//==================================================================================================
        @Override
        public void onCharacteristicChanged (BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            super.onCharacteristicChanged(gatt, characteristic);

            //Log.i(TAG, "One characteristic has changed");

            if (characteristic.getUuid().equals(AssignedNumber.getBleUuid("Humidity"))) {
                Log.i(TAG, "Humidity has changed");

                float humidity100 = characteristic.getIntValue(BluetoothGattCharacteristic.FORMAT_UINT16,0).floatValue();
                final float humidity = humidity100 / 10.0f;  // 2 decimals
                runOnUiThread(new Runnable() {
                    public void run() {
                        TextView humidityTxt = (TextView) BleIotActivity.this.findViewById(R.id.Hvalue);
                        humidityTxt.setText(String.format("%.2f%%", humidity));
                    }
                });
                Log.d(TAG, String.format("Update humidity: %.2f%%", humidity));
            }
//TODO
            if (characteristic.getUuid().equals(AssignedNumber.getBleUuid("Pressure"))) {
                Log.i(TAG, "Pressure has changed");

                float pressure100 = characteristic.getIntValue(BluetoothGattCharacteristic.FORMAT_UINT16,0).floatValue();
                final float pressure = pressure100 / 1000.0f;  // 2 decimals
                runOnUiThread(new Runnable() {
                    public void run() {
                        TextView pressureTxt = (TextView) BleIotActivity.this.findViewById(R.id.pressureId);
                       pressureTxt.setText(String.format("%.2f KPA", pressure));
                    }
                });
                Log.d(TAG, String.format("Update presure: %.2f%%", pressure));
            }

            if (characteristic.getUuid().equals(AssignedNumber.getBleUuid("led state"))) {
                Log.i(TAG, "led state has changed");

              final int state = characteristic.getIntValue(BluetoothGattCharacteristic.FORMAT_UINT16,0);
                runOnUiThread(new Runnable() {
                    public void run() {
                        if(state == 0){
                           TextView textLedState = (TextView) BleIotActivity.this.findViewById(R.id.textLedState);
                           textLedState.setText(String.format("LED OFF"));
                        }
                        else{
                            TextView textLedState = (TextView) BleIotActivity.this.findViewById(R.id.textLedState);
                            textLedState.setText(String.format("LED ON"));

                        }
                     }
                });
            }


            if (characteristic.getUuid().equals(AssignedNumber.getBleUuid("Temperature"))) {

                Log.i(TAG, "Temperature has changed");

                float temperature100 = characteristic.getIntValue(BluetoothGattCharacteristic.FORMAT_SINT16,0).floatValue();
                final float temperature = temperature100 / 10.0f; // 2 decimals
                runOnUiThread(new Runnable() {
                    public void run() {
                        TextView temperatureTxt = (TextView) BleIotActivity.this.findViewById(R.id.Tvalue);
                        temperatureTxt.setText(String.format("%.2f°C", temperature));
                    }
                });
                Log.d(TAG, String.format("Update temperature: %.2f°C", temperature));
            }
        }

        /******************* Callback called when descriptor is written ***************************/
        /**** Indicates the result of the operation and deals with the descriptor write queue. ****/

        @Override
        public void onDescriptorWrite(BluetoothGatt gatt, BluetoothGattDescriptor descriptor, int status) {
            Log.d(TAG, "GATT onDescriptorWrite()");

            if (status == BluetoothGatt.GATT_SUCCESS) {
                Log.d(TAG, "GATT: Descriptor wrote successfully."); //Operation ended successfully.
            } else {
                Log.d(TAG, "GATT: Error writing descriptor (" + status + ").");
            }

            descriptorWriteQueue.remove();

            if (descriptorWriteQueue.size() > 0) {
                mGatt.writeDescriptor(descriptorWriteQueue.element());
            }
        }

    };

//==================================================================================================
    /************************** Method to write a descriptor. *************************************/
//==================================================================================================
    public void writeGattDescriptor(BluetoothGattDescriptor descriptor) {
        descriptorWriteQueue.add(descriptor);

        Log.d(TAG, "Subscribed to " + descriptorWriteQueue.size() + " notification/s");

        try {
            if (descriptorWriteQueue.size() == 1)
                mGatt.writeDescriptor(descriptor);
        } catch (Exception e) {
            e.getLocalizedMessage();
        }
    }
//==================================================================================================
    /**
     * Retrieves a list of supported GATT services on the connected device. This should be
     * invoked only after {@code BluetoothGatt#discoverServices()} completes successfully.
     *
     * @return A {@code List} of supported services.
     */
    public List<BluetoothGattService> getSupportedGattServices() {
        if (mGatt == null)
            return null;

        return mGatt.getServices();
    }
}
//==================================================================================================
