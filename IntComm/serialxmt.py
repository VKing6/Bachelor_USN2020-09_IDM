#!/usr/bin/env python3
import serial

class SerialTransmitter:
    def __init__(self, serialport):
        self.ser = serialport

    def transmit(self, message):
        self.ser.write(message.encode())


if __name__ == "__main__":
    with serial.Serial('/dev/ttyACM0', 57600, timeout=1) as ser:
        xmt = SerialTransmitter(ser)
        xmt.transmit("Fnord")
