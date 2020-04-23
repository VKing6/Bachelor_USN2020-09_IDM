#!/usr/bin/env python3
import threading
import datetime

class DataObject(object):
    def __init__(self, lock=None):
        self.__lock = lock or threading.RLock()

        self.__datestring = "fnord"
        self.__datetime = datetime.datetime(1900,1,1)
        self.__windspeed = -1
        self.__temperature = -1
        self.__humidity = -1
        self.__pitch = -1
        self.__airpressure = -1
        self.__dragforce = -1
        self.__liftforce = -1
        self.__bools = -1

    def parse_datastring(self, data):
        with self.__lock:
            try:
                datestring, windspeed, temperature, humidity, pitch, bools = data.split(b"|")
            except ValueError:
                try:
                    datestring, windspeed, temperature, humidity, pitch = data.split(b"|")
                    bools = -1
                except ValueError:
                    datestring, windspeed, temperature = "1900-01-01T12:00:00", -1, -1
                    humidity, pitch, bools = -1, -1, -1
            
            self.__datestring = datestring.decode("utf-8")
            self.__datetime = datetime.datetime.fromisoformat(self.__datestring)
            self.__windspeed = int(windspeed)
            self.__temperature = int(temperature)
            self.__humidity = int(humidity)
            self.__pitch = int(pitch)
            # TBA
            #self.__airpressure = int(airpressure)
            #self.__dragforce = int(dragforce)
            #self.__liftforce = int(liftforce)
            self.__bools = int(bools)
                    
    def get_data(self):
        with self.__lock:
            return dict(time=self.__datestring, windspeed=self.__windspeed,
                        temperature=self.__temperature, humidity=self.__humidity,
                        pitch=self.__pitch, airpressure=self.__airpressure,
                        dragforce=self.__dragforce, liftforce=self.__liftforce)  # bools
