#!/usr/bin/env python3
import threading

class DataObject(object):
    def __init__(self, lock=None):
        self.lock = lock or threading.RLock()

        self.__time = "fnord"
        self.__windSpeed = 0
        self.__hatchLocked = False

    def set_time(self, time):
        with self.lock:
            self.__time = time[2:]

    def get_time(self):
        with self.lock:
            return self.__time

    def set_windspeed(self, speed):
        with self.lock:
            self.__windSpeed = speed

    def get_windspeed(self):
        with self.lock:
            return self.__windSpeed

    def set_hatchlocked(self, locked):
        with self.lock:
            self.__hatchLocked = locked

    def get_hatchlocked(self):
        with self.lock:
            return self.__hatchLocked

    def set_data(self, **kwargs):
        with self.lock:
            for key, value in kwargs.items():
                if key == "time":
                    self.set_time(str(value))
                if key == "windspeed":
                    self.set_windspeed(int(value))
                    
    def get_dataString(self):
        with self.lock:
            return f"Time: {self.get_time()};  Windspeed: {self.get_windspeed()}"

