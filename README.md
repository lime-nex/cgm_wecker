# cgm_wecker
This project aims to help people who don't wake up from their bloodsugar alarms at nigth. It does this via some python scripts which can either use Data from the Dexcom Share Server (you have to turn on to share your data in the dexcom app) or data from your per caible connected dexcom g6 receiver. When the programm will detect low bloodsugar under 80 mg/dL it will trigger an alarm that will not stop until you answer a simple math question. This of course means that you have to connect some sort of audio device to receive the alarms. In conclusion this project helps to warn you when your bloodsugar is low and can do this both online and offline.
# Setup
* Download cgm_wecker to your rasberry pi 
For that you will require a rasberry pi that is already setup and configured.
Here are links to tutorials on how to setup your rasberry pi:
Rasberry Pi 5: https://youtu.be/ykTlNf1TXO0?si=05Z-oay19oRd1Q2M
Rasberry Pi 4 or lower: https://youtu.be/y45hsd2AOpw?si=gC5QivFmHwykAVZ9
Note: I can at this time only confirm that this is tested and works on a rasberry pi 5 although other rasberry pis like the rasberry pi 4 should be fine aswell.

* The first step is to open the terminal on the rasberry pi.
* Next enter these commands
```
sudo apt install -y git
git clone https://github.com/lime-nex/cgm_wecker.git
cd cgm_wecker
```

* Edit the configuration:
```
nano dexpy.json
```

Configuration example:
* Here you will only need to set the first one that reads USB_RECEIVER to true.
```
{
  "USB_RECEIVER": true,
  "DEXCOM_SHARE_SERVER": "eu",
  "DEXCOM_SHARE_USERNAME": "username",
  "DEXCOM_SHARE_PASSWORD": "password",
  "MQTT_SERVER": "mqtt.myserver.example",
  "MQTT_PORT": 1883,
  "MQTT_SSL": false,
  "MQTT_CLIENTID": "dexpy-mqtt-client",
  "MQTT_TOPIC": "cgm",
  "INFLUXDB_SERVER": "influxdb.myserver.example",
  "INFLUXDB_PORT": 8086,
  "INFLUXDB_SSL": false,
  "INFLUXDB_SSL_VERIFY": false,
  "INFLUXDB_USERNAME": "username",
  "INFLUXDB_PASSWORD": "password",
  "INFLUXDB_DATABASE": "dexpy",
  "INFLUXDB_MEASUREMENT": "bg",
  "NIGHTSCOUT_URL": "https://nightscout.myserver.example",
  "NIGHTSCOUT_SECRET": null,
  "NIGHTSCOUT_TOKEN": "ns-yadayadayada"
}
```

* Run the install script that registers the usb device driver, downloads dependencies and starts dexpy as a systemd service
```
sudo ./install.sh
```

### Reading from Dexcom Receiver via USB
**USB_RECEIVER**: _true_ to enable reading from the receiver, otherwise _false_<br/>

### Then run this command to start the script###:
```
venv/bin/python scrOpt.py
```
# Acknowledgements

Dexcom Share protocol is implemented according to the [reverse engineering](https://gist.github.com/StephenBlackWasAlreadyTaken/adb0525344bedade1e25) performed by github user [StephenBlackWasAlreadyTaken](https://gist.github.com/StephenBlackWasAlreadyTaken)

Dexcom Receiver code for communicating with the receiver via USB is borrowed from the [dexctrack](https://github.com/DexcTrack/dexctrack) project, which in turn is based on the [dexcom_reader](https://github.com/openaps/dexcom_reader) project. Further enhanced to support Dexcom G6 receiver backfill.
