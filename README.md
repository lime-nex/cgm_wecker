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
* Leave the terminal open in the background and open the Filemanager and locate the folder cgm_wecker.
* Locate the file scrOpt.py, open it and you will see this.
```
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pydexcom import Dexcom
from datetime import datetime
import pygame
import threading
import random
import time
import os

early_pass = True

while early_pass:
    try:
        pygame.init()
        stop_alarm = threading.Event()
        sername = "enter-username-here(or whatever you use to login to dexcom)" #example: username = "exampleusername"
        password = "enter-password-here" # example: password = "safepassword1234"
        region = "either enter (us) for Amerika, (ous) for out of us and (jp) for japan" #example: region = "ous" 
        dexcom = Dexcom(username=username, password=password, region=region)
        reading = dexcom.get_current_glucose_reading()
        LOW_THRESHOLD = 200
        werte = []
        zeiten = []
        Sound = ['Sound/Alarm1.mp3','Sound/Alarm2.mp3','Sound/Alarm3.mp3','Sound/Alarm4.mp3','Sound/Alarm5.mp3']
        COOLDOWN_SECONDS = 1500  # z.B. 5 Minuten Cooldown
        last_alarm_time = 0
        first_b = True
        last_wert_i = None
        differenz_i = None
        early_pass = False
    except:
        print("Cannot initiate script. This may be a problem with your login information or your internet connection. To be sure please check both.")
        time.sleep(5)
```
* You will no edit the three variables called username, password and region acording to the examples provided in the code behind each variable.
* Then you will save the file and close it.
* Return to the still in the background open terminal.
* Run the install script that registers the usb device driver, downloads dependencies and starts dexpy as a systemd service.
```
chmod +x start.sh
sudo ./start.sh
```
*The script should install everything needed and start the script which will prompt you to type in o and enter for online mode or to just wait 20 seconds and start the offline script.#

### The next time you want to start the script only run these two commands:
```
cd cgm_wecker
sudo ./start.sh
```
if you have any problems try to google your way through the problem although if you can't fix it yourself you can contact me on my [discord server](https://discord.gg/MetPYyWMHx) for this project. (I am still a student at the moment so I wont always have time to help out everyone.)

# Acknowledgements

Big thanks to [winemug](https://github.com/winemug) for his dexpy project which helped me greatly and is a big part of this project. He was so kind as to allow me to fork his project. For the interaction of the online script with the dexcom api credits go to the [pydexcom](https://github.com/gagebenne/pydexcom) project by gagebenne.

Dexcom Share protocol is implemented according to the [reverse engineering](https://gist.github.com/StephenBlackWasAlreadyTaken/adb0525344bedade1e25) performed by github user [StephenBlackWasAlreadyTaken](https://gist.github.com/StephenBlackWasAlreadyTaken)

Dexcom Receiver code for communicating with the receiver via USB is borrowed from the [dexctrack](https://github.com/DexcTrack/dexctrack) project, which in turn is based on the [dexcom_reader](https://github.com/openaps/dexcom_reader) project. Further enhanced to support Dexcom G6 receiver backfill.
