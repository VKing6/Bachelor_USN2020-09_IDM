#!/usr/bin/env python3
import threading

class DataObject(object):
    def __init__(self, lock=None):
        self.__lock = lock or threading.RLock()

        self.__time = "fnord"
        self.__windspeed = -1
        self.__temperature = -1
        self.__humidity = -1
        self.__pitch = -1
        self.__bools = -1

    def parse_datastring(self, data):
        with self.__lock:
            try:
                time, windspeed, temperature, humidity, pitch, bools = data.split("|")
            except ValueError:
                try:
                    time, windspeed, temperature, humidity, pitch = data.split("|")
                    bools = -1
                except ValueError:
                    time, windspeed, temperature, humidity, pitch, bools = "error", -1, -1, -1, -1, -1
            
            self.__time = time
            self.__windspeed = windspeed
            self.__temperature = temperature
            self.__humidity = humidity
            self.__pitch = pitch
            self.__bools = bools
                    
    def get_data(self):
        with self.__lock:
            return dict(time=self.__time, windspeed=self.__windspeed,
                        temperature=self.__temperature, humidity=self.__humidity,
                        pitch=self.__pitch)  # bools
