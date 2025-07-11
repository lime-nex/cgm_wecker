import os
import time
from glucose import GlucoseValue
import threading
import logging
import random

from usbreceiver import constants
from usbreceiver.readdata import Dexcom

from save_state import save_state, load_state
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class DexcomReceiverSession():
    def __init__(self, callback, usb_reset_cmd = None):
        self.logger = logging.getLogger('DEXPY')
        self.callback = callback
        self.device = None
        self.timer = None
        self.lock = threading.RLock()
        self.initial_backfill_executed = False
        self.last_gv = None
        self.system_time_offset = None
        self.usb_reset_cmd = usb_reset_cmd
        self.ts_usb_reset = time.time() + 360

    def start_monitoring(self):
        self.on_timer()

    def on_timer(self):
        with self.lock:
            if not self.ensure_connected():
                self.set_timer(15)
            elif self.read_glucose_values():
                self.ts_usb_reset = time.time() + 360
                self.set_timer(30)
            else:
                if self.usb_reset_cmd is not None:
                    ts_now = time.time()
                    if ts_now > self.ts_usb_reset:
                        self.logger.debug('performing usb reset')
                        os.system(self.usb_reset_cmd)
                        ts_now = time.time()
                        self.ts_usb_reset = ts_now + 360
                self.set_timer(10)

    def ensure_connected(self):
        try:
            if self.device is None:
                port = Dexcom.FindDevice()
                if port is None:
                    self.logger.warning("Dexcom receiver not found")
                    return False
                else:
                    self.device = Dexcom(port)
            self.system_time_offset = self.get_device_time_offset()
            return True
        except Exception as e:
            self.logger.warning("Error reading from usb device\n" + str(e))
            self.device = None
            self.system_time_offset = None
            save_state(True)
            import pygame
            pygame.init()
            Sound_last = [BASE_DIR / 'Sound' / 'Deactivation.mp3']
            counter = 1
            while True:
                counter = counter + 1
                my_sound_last = pygame.mixer.Sound(random.choice(Sound_last))
                my_sound_last.play()
                time.sleep(3)
                if counter == 4:
                    break
            return False

    def set_timer(self, seconds):
        self.timer = threading.Timer(seconds, self.on_timer)
        self.timer.setDaemon(True)
        self.logger.debug("timer set to %d seconds" % seconds)
        self.timer.start()

    def stop_monitoring(self):
        with self.lock:
            self.timer.cancel()

    def read_glucose_values(self, ts_cut_off: float = None):
        try:
            if ts_cut_off is None:
                if self.initial_backfill_executed:
                    ts_cut_off = time.time() - 3 * 60 * 60
                else:
                    ts_cut_off = time.time() - 24 * 60 * 60

            records = self.device.iter_records('EGV_DATA')
            new_value_received = False

            for rec in records:
                if not rec.display_only:
                    gv = self._as_gv(rec)
                    if self.last_gv is None or self.last_gv.st != gv.st:
                        self.last_gv = gv
                        new_value_received = True
                    self.callback([gv])
                    break

            if new_value_received:
                for rec in records:
                    if not rec.display_only:
                        gv = self._as_gv(rec)
                        if gv.st >= ts_cut_off:
                            self.callback([gv])
                        else:
                            break

                for rec in self.device.iter_records('BACKFILLED_EGV'):
                    if not rec.display_only:
                        gv = self._as_gv(rec)
                        if gv.st >= ts_cut_off:
                            self.callback([gv])
                        else:
                            break

            self.initial_backfill_executed = True
            return new_value_received
        except Exception as e:
            self.logger.warning("Error reading from usb device\n" + str(e))
            global first_time
            first_time = True
            import pygame
            pygame.init()
            Sound_last = ['/home/nexus/Desktop/Pi/Desktop/Sound/Deactivation.mp3']
            my_sound_last = pygame.mixer.Sound(random.choice(Sound_last))
            my_sound_last.play()
            return False

    def get_device_time_offset(self):
        now_time = time.time()
        device_time = self.device.ReadSystemTime()
        return now_time - device_time

    def _as_gv(self, record):
        st = record.meter_time + self.system_time_offset
        direction = record.full_trend & constants.EGV_TREND_ARROW_MASK
        return GlucoseValue(None, None, st, record.glucose, direction)
    

                

if __name__ == "__main__":
    print(GlucoseValue)


