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
        threading.Thread.__init__(self)

    def run(self):
        with serial.Serial(port=self.port, baudrate=self.rate, timeout=self.timeout) as ser:
            while not self.stop_event.is_set():
                in_data = ser.readline()
                if len(in_data) > 0:
                    self.data.parse_datastring(in_data)

if __name__ == "__main__":
    data = dataobject.DataObject()
    event = threading.Event()
    rcv = SerialReceiver(data, event)
    rcv.start()
    print("Starting")
    for i in range(4):
        print(i, data.get_time())
        time.sleep(1.5)
    print("End")
    event.set()
    rcv.join()
