#!/usr/bin/env python3
import serial
import threading
import dataobject
import time

class SerialReceiver(threading.Thread):
    def __init__(self, data, stop_event,
                 port="/dev/ttyACM0", rate=57600, timeout=1):
        self.port = port
        self.rate = rate
        self.timeout = timeout
        self.data = data
        self.stop_event = stop_event

    def run(self):
        with serial.Serial(self.port, self.rate, self.timeout) as ser:
            while not self.stop_event.is_set():
                in_data = ser.readline()
                if len(in_data) > 0:
                    self.data.parse_datastring(in_data)

if __name__ == "__main__":
    data = dataobject.DataObject()
    event = threading.Event()
    rcv = SerialReceiver(data, event)
    rcv.run()
    for i in range(20):
        print(data.get_time)
        time.sleep(1.5)
    event.set()
    rcv.join()