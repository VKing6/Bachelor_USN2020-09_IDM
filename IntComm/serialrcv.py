#!/usr/bin/env python3
import threading
import dataobject

import time
import serial

class SerialReceiver(threading.Thread):
    def __init__(self, serialport, data, stop_event):
        self.ser = serialport
        self.data = data
        self.stop_event = stop_event
        threading.Thread.__init__(self)

    def run(self):
        while not self.stop_event.is_set():
            in_data = self.ser.readline()
            if len(in_data) > 0:
                self.data.parse_datastring(in_data)

if __name__ == "__main__":
    data = dataobject.DataObject()
    event = threading.Event()
    with serial.Serial('/dev/ttyACM0', 57600, timeout=1) as ser:
        rcv = SerialReceiver(ser, data, event)
        rcv.start()
        print("Starting")
        for i in range(4):
            print(i, data.get_time())
            time.sleep(1.5)
        print("End")
        event.set()
        rcv.join()
