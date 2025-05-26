# cgm_wecker
This project aims to help people who don't wake up from their bloodsugar alarms at nigth. It does this via some python scripts which can either use Data from the Dexcom Share Server (you have to turn on to share your data in the dexcom app) or data from your per caible connected dexcom g6 receiver. When the programm will detect low bloodsugar under 80 mg/dL it will trigger an alarm that will not stop until you answer a simple math question. This of course means that you have to connect some sort of audio device to receive the alarms. In conclusion this project helps to warn you when your bloodsugar is low and can do this both online and offline.
# Setup
* Download cgm_wecker to your rasberry pi 
For that you will require a rasberry pi that is already setup and configured.
Here are links to tutorials on how to setup your rasberry pi: 
* [Rasberry Pi 5 Tutorial](https://youtu.be/ykTlNf1TXO0?si=05Z-oay19oRd1Q2M) 
* [Rasberry Pi 4 or lower Tutorial](https://youtu.be/y45hsd2AOpw?si=gC5QivFmHwykAVZ9)  
* Note: I can at this time only confirm that this is tested and works on a rasberry pi 5 although other rasberry pis like the rasberry pi 4 should be fine aswell.

* The first step is to open the terminal on the rasberry pi.
* Next enter these commands
```
sudo apt install -y git
git clone https://github.com/lime-nex/cgm_wecker.git
cd cgm_wecker
```
* Run the install script that registers the usb device driver, downloads dependencies and starts the CGM Interface.
```
chmod +x start.sh
sudo ./start.sh
```
* An Interface should popup where you can configure some settings and login to dexcomshare if you want to use the online service of CGM Wecker.

### The next time you want to start the on your desktop there should be a new application called CGM Wecker starten:
* When you execute it it might ask you if you want to execute it in the terminal or not.
* This does not matter and you can just do it either way.
if you have any problems try to google your way through the problem although if you can't fix it yourself you can contact me on my [discord server](https://discord.gg/MetPYyWMHx) for this project. (I am still a student at the moment so I wont always have time to help out everyone if there is demand.)

# Acknowledgements

Big thanks to [winemug](https://github.com/winemug) for his dexpy project which helped me greatly and is a big part of this project. He was so kind as to allow me to fork his project. For the interaction of the online script with the dexcom api credits go to the [pydexcom](https://github.com/gagebenne/pydexcom) project by gagebenne.

Dexcom Share protocol is implemented according to the [reverse engineering](https://gist.github.com/StephenBlackWasAlreadyTaken/adb0525344bedade1e25) performed by github user [StephenBlackWasAlreadyTaken](https://gist.github.com/StephenBlackWasAlreadyTaken)

Dexcom Receiver code for communicating with the receiver via USB is borrowed from the [dexctrack](https://github.com/DexcTrack/dexctrack) project, which in turn is based on the [dexcom_reader](https://github.com/openaps/dexcom_reader) project. Further enhanced to support Dexcom G6 receiver backfill.
