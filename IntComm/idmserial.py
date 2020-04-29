#!/usr/bin/env python3
import threading
import dataobject

import time
import serial

class SerialCommunicator:
    class SerialReceiver(threading.Thread):
        def __init__(self, serialport, data, stop_event):
            self.ser = serialport
            self.data = data
            self.stop_event = stop_event
            threading.Thread.__init__(self)

        def run(self):
            print(__name__, "Running")
            while not self.stop_event.is_set():
                in_data = self.ser.readline()
                if len(in_data) > 0:
                    self.data.parse_datastring(in_data)
                    #print(self.data.get_data())  # Debug
            print(__name__, "Stopping")


    class SerialTransmitter:
        def __init__(self, serialport):
            self.ser = serialport

        def transmit(self, message):
            self.ser.write(message.encode())
            print(__name__, "Transmitted", message.encode())


    def __init__(self, data, stop_event,
                 port='/dev/ttyACM0', rate=57600, timeout=1):
        print(__name__, "Init")
        self.data = data
        self.stop_event = stop_event
        
        self.ser = serial.Serial(port=port, baudrate=rate, timeout=timeout)
        self.transmitter = self.SerialTransmitter(self.ser)
        self.receiver = self.SerialReceiver(self.ser, self.data, self.stop_event)
        self.receiver.start()

    #def __del__(self):  # Destructor, but doesn't work
        #print(__name__, "Destructor")
        #self.close()
        
    def close(self):
        print(__name__, "Close")
        self.stop_event.set()
        self.receiver.join()
        self.ser.close()

    def transmit(self, message):
        self.transmitter.transmit(message)


if __name__ == "__main__":
    print("Start")
    data = dataobject.DataObject()
    event = threading.Event()
    comm = SerialCommunicator(data, event)
    for i in range(4):
        print(i, data.get_data())
        time.sleep(1.5)
    comm.transmit("Fnord")
    comm.close()
    print("End")
