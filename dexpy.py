#!/usr/bin/python3
import argparse
import bisect
import datetime as dt
import logging
import signal
import sqlite3
import ssl
import threading
from queue import Queue, Empty
import time

import paho.mqtt.client as mqttc
import requests
import simplejson as json
from influxdb import InfluxDBClient
from paho.mqtt.client import MQTTv311

from dexcom_receiver import DexcomReceiverSession
from dexcom_share import DexcomShareSession
import os
import distro
import datetime
from save_state import save_state, load_state
from config_handler import load_config, load_config_constants
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
filenametxt = BASE_DIR / 'text.txt' 
LOW_THRESHOLD, COOLDOWN_MINUTES = load_config_constants()
COOLDOWN_SECONDS = COOLDOWN_MINUTES * 60

with open(filenametxt, 'w') as file:
    pass  # Nichts reinschreiben → Datei ist leer
last_alarm_time = 0
save_state(True)
last_wert_i = 1
differenz_i = 1

class DexPy:
    def __init__(self, args):
        self.logger = logging.getLogger('DEXPY')

        self.args = args
        self.exit_event = threading.Event()
        self.message_published_event = threading.Event()
        self.start_time = datetime.datetime.now()  # Store the start time
        self.ignore_old_values = True
        self.initialize_db()
        self.mqtt_client = None
        if args.MQTT_SERVER is not None:
            self.mqtt_client = mqttc.Client(client_id=args.MQTT_CLIENTID, clean_session=True, protocol=MQTTv311,
                                            transport="tcp")

            if args.MQTT_SSL != "":
                self.mqtt_client.tls_set(certfile=None,
                                         keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
                                         tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
                self.mqtt_client.tls_insecure_set(True)

            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            self.mqtt_client.on_message = self.on_mqtt_message_receive
            self.mqtt_client.on_publish = self.on_mqtt_message_publish

        self.influx_client = None
        if self.args.INFLUXDB_SERVER is not None:
            self.influx_client = InfluxDBClient(self.args.INFLUXDB_SERVER, self.args.INFLUXDB_PORT, self.args.INFLUXDB_USERNAME,
                                                self.args.INFLUXDB_PASSWORD, self.args.INFLUXDB_DATABASE,
                                                ssl=self.args.INFLUXDB_SSL, verify_ssl=self.args.INFLUXDB_SSL_VERIFY)

        self.callback_queue = Queue()
        self.glucose_values = []
        self.mqtt_pending = {}
        self.influx_pending = []
        self.ns_pending = []

        self.ns_session = None
        if self.args.NIGHTSCOUT_URL is not None:
            self.ns_session = requests.Session()

        self.dexcom_share_session = None
        if self.args.DEXCOM_SHARE_SERVER is not None:
            self.logger.info("starting dexcom share session")
            self.dexcom_share_session = DexcomShareSession(self.args.DEXCOM_SHARE_SERVER,
                                                           self.args.DEXCOM_SHARE_USERNAME,
                                                           self.args.DEXCOM_SHARE_PASSWORD,
                                                           self.glucose_values_received)

        self.dexcom_receiver_session = None
        if self.args.USB_RECEIVER is not None and self.args.USB_RECEIVER:
            self.dexcom_receiver_session = DexcomReceiverSession(self.glucose_values_received, self.args.USB_RESET_COMMAND)
            if not self.dexcom_receiver_session.ensure_connected():
                time.sleep(1)


        for sig in ('HUP', 'INT'):
            signal.signal(getattr(signal, 'SIG' + sig), lambda _0, _1: self.exit_event.set())
    def run(self):
        if self.mqtt_client is not None:
            self.logger.info("starting mqtt service connection")
            self.mqtt_client.reconnect_delay_set(min_delay=15, max_delay=120)
            self.mqtt_client.connect_async(self.args.MQTT_SERVER, port=self.args.MQTT_PORT, keepalive=60)
            self.mqtt_client.retry_first_connection = True
            self.mqtt_client.loop_start()

        if self.dexcom_share_session is not None:
            self.logger.info("starting monitoring dexcom share server")
            self.dexcom_share_session.start_monitoring()

        if self.dexcom_receiver_session is not None:
            self.logger.info("starting usb receiver service")
            self.dexcom_receiver_session.start_monitoring()

        queue_thread = threading.Thread(target=self.queue_handler)
        queue_thread.start()

        try:
            while not self.exit_event.wait(timeout=1000):
                pass
        except KeyboardInterrupt:
            pass

        self.exit_event.clear()
        if self.dexcom_receiver_session is not None:
            self.logger.info("stopping dexcom receiver service")
            self.dexcom_receiver_session.stop_monitoring()

        if self.dexcom_share_session is not None:
            self.logger.info("stopping listening on dexcom share server")
            self.dexcom_share_session.stop_monitoring()

        if self.mqtt_client is not None:
            self.logger.info("stopping mqtt client")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

        if self.influx_client is not None:
            self.logger.info("closing influxdb client")
            self.influx_client.close()

        if self.ns_session is not None:
            self.logger.info("closing nightscout session")
            self.ns_session.close()

    def on_mqtt_connect(self, client, userdata, flags, rc):
        self.logger.info("Connected to mqtt server with result code " + str(rc))
        self.logger.debug("Pending %d messages in local queue" % len(self.mqtt_pending))

    def on_mqtt_disconnect(self, client, userdata, rc):
        self.logger.info("Disconnected from mqtt with result code " + str(rc))
        self.logger.debug("Pending %d messages in local queue" % len(self.mqtt_pending))

    def on_mqtt_message_receive(self, client, userdata, msg):
        self.logger.info("mqtt message received: " + msg)

    def on_mqtt_message_publish(self, client, userdata, msg_id):
        self.logger.info("mqtt message published: " + str(msg_id))
        if msg_id in self.mqtt_pending:
            self.mqtt_pending.pop(msg_id)
        else:
            self.logger.debug("unknown message id: " + str(msg_id))
        self.logger.debug("Pending %d messages in local queue" % len(self.mqtt_pending))

    def glucose_values_received(self, gvs):
        for gv in gvs:
            self.callback_queue.put(gv)

    def queue_handler(self):
        while not self.exit_event.wait(timeout=0.200):
            gvs = []
            while True:
                try:
                    gv = self.callback_queue.get(block=True, timeout=5)
                    gvs.append(gv)
                except Empty:
                    if len(gvs) > 0:
                        self.process_glucose_values(gvs)
                        gvs = []

    def process_glucose_values(self, gvs):
        new_values = []
        for gv in gvs:
            new_val = True
            for gv_check in self.glucose_values:
                if gv_check == gv:
                    new_val = False
                    break
            if new_val:
                new_values.append(gv)
                self.logger.info(f"New gv: {gv}")
                print(gv.value) 
                import threading
                import time
                import random
                import os
                import pygame   
                
                pygame.init()
                stop_alarm = threading.Event()
                Sound = [BASE_DIR / 'Sound' / 'Alarm1.mp3', BASE_DIR / 'Sound' / 'Alarm2.mp3', BASE_DIR / 'Sound' / 'Alarm3.mp3', BASE_DIR / 'Sound' / 'Alarm4.mp3', BASE_DIR / 'Sound' / 'Alarm5.mp3']
                Sound_first = [BASE_DIR / 'Sound' / 'Activation.mp3']
                
                def prediction(wert):
                    global last_alarm_time
                    global first_b
                    global last_wert_i
                    global differenz_i
                    zeit = datetime.now().strftime("%H:%M:%S")
                    first_b = load_state()
                    if first_b:
                        save_state(False)
                        last_wert_i = wert
                    else:
                        differenz_i = last_wert_i - wert
                        if differenz_i > 0:
                            for i in range(1,3):
                                prediction_wert_i = wert - differenz_i
                                if prediction_wert_i < LOW_THRESHOLD and i == 1 and (current_time - last_alarm_time > COOLDOWN_SECONDS):
                                    last_alarm_time = current_time
                                    set_alarm()
                                elif prediction_wert_i < LOW_THRESHOLD and i > 1:
                                    print(f"[{zeit}] Warnung: Blutzucker könnte innerhalb der nächsten {i} Werte unter {LOW_THRESHOLD} sinken")
                        last_wert_i = wert
                
                def play_alarm():
                        try:
                            my_sound = pygame.mixer.Sound(random.choice(Sound))
                            while not stop_alarm.is_set():
                                my_sound.play()
                        except ImportError:
                            while not stop_alarm.is_set():
                                os.system("echo -e '\a'")
                                time.sleep(1)

                def math_problem():
                        a = random.randint(5, 20)
                        b = random.randint(2, 10)
                        correct_answer = a * b
                        while True:
                                try:
                                    user_answer = int(input(f"Was ist {a} × {b}? "))
                                    if user_answer == correct_answer:
                                        print("Richtig! Wecker wird gestoppt.")
                                        stop_alarm.set()
                                        break
                                    else:
                                        print("Falsch! Versuche es noch einmal.")
                                except ValueError:
                                    print("Bitte eine gültige Zahl eingeben!")
                            
                                
                            
                def set_alarm():

                        from threading import Thread
                        stop_alarm.clear()
                        alarm_thread = Thread(target=play_alarm, daemon=True)
                        alarm_thread.start()
                        math_problem()
                        print("Sleeping for 20min")
                        time.sleep(1200)
                        print("Waking up again")


                def main():
                        try:
                            set_alarm()
                        except:
                            print("Error") 
                testnumber = 80
                global last_alarm_time
                global COOLDOWN_SECONDS
                from datetime import datetime
                global first_time
                first_time = load_state()
                current_time = time.time()
                if first_time:
                       my_sound_first = pygame.mixer.Sound(random.choice(Sound_first))
                       my_sound_first.play()
                       save_state(False)
                wert = gv.value
                prediction(wert)
                last_alarm_time = current_time
                print(gv.value)
                print("Neuer Wert")
                file_graphing = open(filenametxt, 'a')
                datum_different = datetime.now().strftime("%H:%M:%S")
                file_graphing.write(str(gv.value) +' - '+ datum_different+'\n')
                time.sleep(1)
                file_graphing.close()
                if gv.value < LOW_THRESHOLD:
                    last_alarm_time = current_time
                    main()
                    print("waiting for next Value")
                    time.sleep(3)
                    return
                else:
                    print("waiting for next Value")
                    time.sleep(3)
                    return
            else:
                return
        if self.mqtt_client is not None:
            for gv in new_values:
                msg = "%d|%s|%s" % (gv.st, gv.trend, gv.value)
                x, mid = self.mqtt_client.publish(self.args.MQTT_TOPIC, payload=msg, qos=1)
                self.mqtt_pending[mid] = gv
                self.logger.debug("publish to mqtt requested with message id: " + str(mid))

        if self.influx_client is not None:
            for gv in new_values:
                point = {
                    "measurement": self.args.INFLUXDB_MEASUREMENT,
                    "tags": {"device": "dexcomg6", "source": "dexpy"},
                    "time": dt.datetime.utcfromtimestamp(gv.st).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "fields": {"cbg": float(gv.value), "direction": int(gv.trend)}
                }
                self.influx_pending.append(point)
            try:
                if self.influx_client.write_points(self.influx_pending):
                    self.influx_pending = []
            except Exception as ex:
                self.logger.error("Error writing to influxdb", exc_info=ex)

        if self.ns_session is not None:
            apiUrl = self.args.NIGHTSCOUT_URL
            if apiUrl[-1] != "/":
                apiUrl += "/"
            apiUrl += "api/v1/entries/"
            headers = {"Content-Type": "application/json"}
            if self.args.NIGHTSCOUT_SECRET:
                headers["api-secret"] = self.args.NIGHTSCOUT_SECRET
            if self.args.NIGHTSCOUT_TOKEN:
                apiUrl += "?token=" + self.args.NIGHTSCOUT_TOKEN

            for gv in new_values:
                payload = {"sgv": gv.value, "type": "sgv", "direction": gv.trend_string(), "date": gv.st * 1000}
                self.ns_pending.append(json.dumps(payload))
                posted_entries = []
                for pendingEntry in self.ns_pending:
                    try:
                        response = self.ns_session.post(apiUrl, headers=headers, data=pendingEntry)
                        if response is not None and response.status_code == 200:
                            posted_entries.append(pendingEntry)
                        else:
                            self.logger.error(f"NS server returned invalid response {response}")
                    except Exception as ex:
                        self.logger.error("Error posting value to nightscout", ex)
                for posted_entry in posted_entries:
                    self.ns_pending.remove(posted_entry)

        for gv in new_values:
            i = bisect.bisect_right(self.glucose_values, gv)
            self.glucose_values.insert(i + 1, gv)

        if len(self.glucose_values) > 4096:
            self.glucose_values = self.glucose_values[4096 - len(self.glucose_values):]

    def initialize_db(self):
        try:
            with sqlite3.connect(self.args.DB_PATH) as conn:
                sql = """ CREATE TABLE IF NOT EXISTS gv (
                          ts REAL,
                          gv REAL,
                          trend TEXT
                          ) """
                conn.execute(sql)

                sql = """ CREATE INDEX "idx_ts" ON "gv" ("ts");"""
                try:
                    conn.execute(sql)
                except:
                    self.logger.debug("Index creation skipped")

        except Exception as ex:
            self.logger.warning("Error initializing local db", exc_info=ex)


if __name__ == '__main__':
    logger = logging.getLogger('DEXPY')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser()
    parser.add_argument("--CONFIGURATION", required=False, default=None, nargs="?")
    parser.add_argument("--DEXCOM-SHARE-SERVER", required=False, default=None, nargs="?")
    parser.add_argument("--DEXCOM-SHARE-USERNAME", required=False, default="", nargs="?")
    parser.add_argument("--DEXCOM-SHARE-PASSWORD", required=False, default="", nargs="?")
    parser.add_argument("--MQTT-SERVER", required=False, default=None, nargs="?")
    parser.add_argument("--MQTT-PORT", required=False, default="1881", nargs="?")
    parser.add_argument("--MQTT-SSL", required=False, default="", nargs="?")
    parser.add_argument("--MQTT-CLIENTID", required=False, default="dexpy", nargs="?")
    parser.add_argument("--MQTT-TOPIC", required=False, default="cgm", nargs="?")
    parser.add_argument("--INFLUXDB-SERVER", required=False, default=None, nargs="?")
    parser.add_argument("--INFLUXDB-PORT", required=False, default="8086", nargs="?")
    parser.add_argument("--INFLUXDB-SSL", required=False, default=False, nargs="?")
    parser.add_argument("--INFLUXDB-SSL-VERIFY", required=False, default=False, nargs="?")
    parser.add_argument("--INFLUXDB-USERNAME", required=False, default="", nargs="?")
    parser.add_argument("--INFLUXDB-PASSWORD", required=False, default="", nargs="?")
    parser.add_argument("--INFLUXDB-DATABASE", required=False, default="", nargs="?")
    parser.add_argument("--INFLUXDB-MEASUREMENT", required=False, default="", nargs="?")
    parser.add_argument("--NIGHTSCOUT-URL", required=False, default=None, nargs="?")
    parser.add_argument("--NIGHTSCOUT-SECRET", required=False, default=None, nargs="?")
    parser.add_argument("--NIGHTSCOUT-TOKEN", required=False, default=None, nargs="?")
    parser.add_argument("--DB-PATH", required=False, default="dexpy.db", nargs="?")
    parser.add_argument("--USB-RECEIVER", required=False, default=True, nargs="?")
    parser.add_argument("--USB-RESET-COMMAND", required=False, default=None, nargs="?")

    args = parser.parse_args()

    if args.CONFIGURATION is not None:
        with open(args.CONFIGURATION, 'r') as stream:
            js = json.load(stream)

        for js_arg in js:
            args.__dict__[js_arg] = js[js_arg]

    dexpy = DexPy(args)
    dexpy.run()
