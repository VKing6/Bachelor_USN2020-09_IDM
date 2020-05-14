#!/usr/bin/env python3
import matplotlib
matplotlib.use('Agg')
import tkinter as tk
from tkinter import filedialog
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from tkinter import ttk
import sqlite3
import os, sys
import csv
import datetime
import threading
import time
sys.path.append("/home/pi/Projects/IDM/GUI/")
import dataobject
import idmserial
from PIL import Image,ImageTk



######################################## initialization  ##################################



########################### PAGE FUNCTION #######################################+

class IDMGUI(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1) #gjør at alt expander av seg selv med pack
        container.grid_columnconfigure(0, weight=1)


        #  Make a new database file for each month
        self.db_month = datetime.date.today().isoformat()[:-3]
        #  Don't store more than 6 months of data. Delete the oldest database file when it turns over.
        dbs = [f for f in os.listdir(".") if os.path.isfile(f) and f[-3:] == ".db"]
        if len(dbs) > 5:
            f = dbs.pop(0)
            if f != f"data_{self.db_month}.db":
                os.remove(dbs[0])
        #  Connect to database
        self.database = sqlite3.connect(f"data_{self.db_month}.db")
        self.cursor = self.database.cursor()
        #  Check if data table exists in database and create it if not
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS data
                    (time date, windspeed int, temperature int, humidity int, pitch int,
                        airpressure int, dragforce int, liftforce int)""")
        self.database.commit()

        #  Initialize communication thread
        self.stop_receiver_event = threading.Event()
        self.sensor_data = dataobject.DataObject()
        self.comm = idmserial.SerialCommunicator(self.sensor_data, self.stop_receiver_event)

        #  Start database write loop
        self._afterjob = self.after(2000, self.amend_database)


        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree,PageFour): #antall sider som skal lages i programmet

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid_rowconfigure(0, weight=0) #gjør at alt expander av seg selv grid
            frame.grid_columnconfigure(0, weight=1)

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage) # viser første side
        self.title("IDM")


    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


    def amend_database(self):
        """
        Copy the sensor data from the data object to the sqlite3 database
        """
        c = self.cursor
        d = self.sensor_data.get_data()
        if d["time"].year > 2000 and d["time"].year < 2100:  # Don't store bad/debug values
            c.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (d["timestring"], d["windspeed"], d["temperature"], d["humidity"],
                    d["pitch"], d["airpressure"], d["dragforce"], d["liftforce"]))
            self.database.commit()
        self._afterjob = self.after(1000, self.amend_database)


    def power_shutdown(self):
        """
        Stop the IDM program and Shut down the IDM
        """
        self.comm.close_serial()
        self.after_cancel(self._afterjob)
        #os.system("sudo shutdown now")
        #os.system("sudo shutdown -r now")
        sys.exit(0)


 ##############################  Start page #####################################################

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 3, width = 18,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        SpeedAndPitch.grid(row = 0 , column = 0)

        Measurments = tk.Button(self, text="Measurements",height = 3, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        Measurments.grid(row = 0 , column = 1)

        probe = tk.Button(self, text="Adjust probe",height = 3, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        probe.grid(row = 0, column = 2)

        export = tk.Button(self, text="Export data",height = 3, width = 11,command=lambda: controller.show_frame(PageFour), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        export.grid(row = 0, column = 3)

        labelsp33 = tk.Label(self, text="",  font=('helvetica', 30, 'bold'))
        labelsp33.grid(row = 1 , column = 1)

        labelsp3 = tk.Label(self, text="                  ",  font=('helvetica', 30, 'bold'))
        labelsp3.grid(row = 1 , column = 0)

        labelsp4 = tk.Label(self, text="Welcome to the Windtunnel software ", bg='red', fg='white', font=('helvetica', 30, 'bold'))
        labelsp4.grid(row = 2 , column = 0, columnspan = 4)

        Kristian = tk.Label(self, text="Kristian Auestad", font=('helvetica', 30, 'bold'))
        Kristian.grid(row = 3 , column = 0, columnspan = 4)

        steffen = tk.Label(self, text="Steffen Barskrind",  font=('helvetica', 30, 'bold'))
        steffen.grid(row = 4 , column = 0, columnspan = 4)

        kristoffer = tk.Label(self, text="Kristoffer Andersen ",  font=('helvetica', 30, 'bold'))
        kristoffer.grid(row = 5 , column = 0, columnspan = 4)

        marisu = tk.Label(self, text="Marius Balsvik ",  font=('helvetica', 30, 'bold'))
        marisu.grid(row = 6 , column = 0, columnspan = 4)


        Håvard = tk.Label(self, text="Håvard Gaska ",  font=('helvetica', 30, 'bold'))
        Håvard.grid(row = 7, column = 0, columnspan = 4)



 ###################################  PAGE 1 Adjust speed and pitch #####################################################


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.transmitter = controller.comm

        counterFan = tk.IntVar()
        windspeed_display = tk.StringVar()
        windspeed_display.set(str(counterFan.get()) + " m/s")
        maxFan, minFan = 100, 0
        def increase_fan():
            current = counterFan.get()
            if current < maxFan:
                new = current + 1
                self.transmitter.transmit(f"W{new}X")
                counterFan.set(new)
                windspeed_display.set(str(counterFan.get()) + " m/s")

        def decrease_fan():
            current = counterFan.get()
            if current > minFan:
                new = current - 1
                self.transmitter.transmit(f"W{new}X")
                counterFan.set(new)
                windspeed_display.set(str(counterFan.get()) + " m/s")

        def stop_fan():
            counterFan.set(0)
            self.transmitter.transmit(f"W0X")
            windspeed_display.set(str(counterFan.get()) + " m/s")


        counterPitch = tk.IntVar()
        pitch_display = tk.StringVar()
        pitch_display.set(str(counterPitch.get()) + u"\N{DEGREE SIGN}")
        maxPitch, minPitch = 10, -10
        def increase_pitch():
            current = counterPitch.get()
            if current < maxPitch:
                new = current + 1
                self.transmitter.transmit(f"P{new}X")
                counterPitch.set(new)
                pitch_display.set(str(counterPitch.get()) + u"\N{DEGREE SIGN}")

        def decrease_pitch():
            current = counterPitch.get()
            if current > minPitch:
                new = current - 1
                self.transmitter.transmit(f"P{new}X")
                counterPitch.set(new)
                pitch_display.set(str(counterPitch.get()) + u"\N{DEGREE SIGN}")

        def reset_pitch():
            counterPitch.set(0)
            self.transmitter.transmit(f"P0X")
            pitch_display.set(str(counterPitch.get()) + u"\N{DEGREE SIGN}")



        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 3, width = 18,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        SpeedAndPitch.grid(row = 0 , column = 0)

        Measurments = tk.Button(self, text="Measurements",height = 3, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        Measurments.grid(row = 0 , column = 1)

        probe = tk.Button(self, text="Adjust probe",height = 3, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        probe.grid(row = 0, column = 2)

        export = tk.Button(self, text="Export data",height = 3, width = 11,command=lambda: controller.show_frame(PageFour), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        export.grid(row = 0, column = 3)


        labelsp33 = tk.Label(self, text="",  font=('helvetica', 30, 'bold'))
        labelsp33.grid(row = 1 , column = 1)


        labeltitle2 = tk.Label(self, text="Adjust wind speed and test model pitch",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)


        labelSpeed = tk.Label(self, text=" Speed ",height = 1,     font=('helvetica', 25, 'bold'))
        labelSpeed.grid(row = 4 , column =1)


        labelpitch = tk.Label(self, text="  Pitch  ",height = 1,   font=('helvetica', 25, 'bold'))
        labelpitch.grid(row = 4 , column =2)


        labelspeedinc = tk.Label(self, textvariable = windspeed_display, bg = "lightgrey", width = 5, font=('helvetica', 25, 'bold'))
        labelspeedinc.grid(row = 5 , column =1)

        pitchinc = tk.Label(self, textvariable = pitch_display, bg = "lightgrey" ,  width = 5, font=('helvetica', 25, 'bold'))
        pitchinc.grid(row = 5 , column =2)


        Speedinc = tk.Button(self, text="Increase",command=increase_fan, bg='cyan', fg='black',height = 2 , width =10, font=('helvetica', 20, 'bold')) #
        Speedinc.grid(row = 6 , column = 1)
        
        

        Speeddec = tk.Button(self, text="Decrease",command=decrease_fan, bg='yellow', fg='black',height = 2 , width =10, font=('helvetica', 20, 'bold')) #
        Speeddec.grid(row = 7 , column = 1)


        pitchinc = tk.Button(self, text="Increase",command=increase_pitch, bg='cyan', fg='black', height = 2 , width =10,font=('helvetica', 20, 'bold')) #
        pitchinc.grid(row = 6 , column = 2)

        pitchdec = tk.Button(self, text="Decrease",command=decrease_pitch, bg='yellow', fg='black',height = 2 , width =10, font=('helvetica', 20, 'bold')) #
        pitchdec.grid(row = 7, column = 2)


        Stopbtn = tk.Button(self, text="STOP FAN",command=stop_fan,height = 2 , width =15, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        Stopbtn.grid(row = 5, column = 0)

        spacer5 = tk.Label(self, text="")
        spacer5.grid(row = 6 , column = 0)

        resetpitch = tk.Button(self, text="Reset pitch",command=reset_pitch,height = 2 , width =15, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        resetpitch.grid(row = 7 , column = 0)

        spacer6 = tk.Label(self, text="")
        spacer6.grid(row = 8 , column = 0)


 ###################################  PAGE 2 Measurements  #####################################################

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        self.windspeed   = tk.StringVar()
        self.temperature = tk.StringVar()
        self.humidity    = tk.StringVar()
        self.pitch       = tk.StringVar()
        self.airpressure = tk.StringVar()
        self.dragforce   = tk.StringVar()
        self.liftforce   = tk.StringVar()

        def update_display():
            self.sensor_data = controller.sensor_data.get_data()
            self.windspeed.set(str(self.sensor_data["windspeed"] / 10) + " m/s")  # Divide by 10 since windspeed is sent as tenths int
            self.temperature.set(str(self.sensor_data["temperature"]) + " C")
            self.humidity.set(str(self.sensor_data["humidity"]) + " %")
            self.pitch.set(str(self.sensor_data["pitch"]) + u"\N{DEGREE SIGN}")
            self.airpressure.set(str(self.sensor_data["airpressure"]) + " Pa")
            self.dragforce.set(str(self.sensor_data["dragforce"]) + " N")
            self.liftforce.set(str(self.sensor_data["liftforce"]) + " N")

            self.after(500, update_display)

        self.after(0, update_display)


        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 3, width = 18,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        SpeedAndPitch.grid(row = 0, column = 0)

        Measurments = tk.Button(self, text="Measurements",height = 3, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        Measurments.grid(row = 0, column = 1)

        probe = tk.Button(self, text="Adjust probe",height = 3, width = 13, command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        probe.grid(row = 0, column = 2)

        export = tk.Button(self, text="Export data",height = 3, width = 11, command=lambda: controller.show_frame(PageFour), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        export.grid(row = 0, column = 3)


        labelsp33 = tk.Label(self, text="",  font=('helvetica', 30, 'bold'))
        labelsp33.grid(row = 1 , column = 1)


        labeltitle2 = tk.Label(self, text="Measurements from sensors",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)



        AirVelocity = tk.Button(self, text="Air Velocity", command=lambda: graph_window("SELECT time, windspeed FROM data WHERE time BETWEEN ? AND ?", "Windspeed", "m/s"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        AirVelocity.grid(row = 4, column = 0)
        labelAirV = tk.Label(self, textvariable = self.windspeed, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labelAirV.grid(row = 4, column = 1)



        spacer4 = tk.Label(self, text="")
        spacer4.grid(row = 5 , column = 0)

        Airtemp = tk.Button(self, text="Air Temperature",command=lambda: graph_window("SELECT time, temperature FROM data WHERE time BETWEEN ? AND ?","Temperature","Celsius"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        Airtemp.grid(row = 6, column = 0)
        labeltemp = tk.Label(self, textvariable = self.temperature ,height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labeltemp.grid(row = 6, column = 1)


        spacer5 = tk.Label(self, text="")
        spacer5.grid(row = 7 , column = 0)

        Airhum = tk.Button(self, text="Air Humidity",command=lambda: graph_window("SELECT time, humidity FROM data WHERE time BETWEEN ? AND ?","Humidity","percent"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        Airhum.grid(row = 8, column = 0)
        labelAirhum = tk.Label(self, text="1500", textvariable=self.humidity, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labelAirhum.grid(row = 8, column = 1)




        Airpress = tk.Button(self, text="Air pressure",command=lambda: graph_window("SELECT time, airpressure FROM data WHERE time BETWEEN ? AND ?","Airpressure","Pascal"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        Airpress.grid(row = 4, column = 2)
        labelAirpress = tk.Label(self, textvariable=self.airpressure, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labelAirpress.grid(row = 4, column = 3)



        forceH = tk.Button(self, text="Drag force",command=lambda: graph_window("SELECT time, dragforce FROM data WHERE time BETWEEN ? AND ?","Dragforce", "Newton"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        forceH.grid(row = 6, column = 2)
        labelforceH = tk.Label(self, text="2 N", textvariable=self.dragforce, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labelforceH.grid(row = 6, column = 3)


        froceV = tk.Button(self, text="Lift force",command=lambda: graph_window("SELECT time, liftforce FROM data WHERE time BETWEEN ? AND ?","Liftforce", "Newton"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        froceV.grid(row = 8, column = 2)
        labelforceV = tk.Label(self, text="15 N", textvariable=self.liftforce, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labelforceV.grid(row = 8, column = 3)


 ###################################  PAGE 3 Røykprobe  #####################################################

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        #menue = tk.Button(self, text="Menu",height = 2, width = 13,command=lambda: controller.show_frame(StartPage), bg='blue', fg='white', font=('helvetica', 30, 'bold')) #
       # menue.grid(row = 0 , column = 0)


        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 3, width = 18,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        SpeedAndPitch.grid(row = 0 , column = 0)

        Measurments = tk.Button(self, text="Measurements",height = 3, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        Measurments.grid(row = 0 , column = 1)

        probe = tk.Button(self, text="Adjust probe",height = 3, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        probe.grid(row = 0, column = 2)

        export = tk.Button(self, text="Export data",height = 3, width = 11,command=lambda: controller.show_frame(PageFour), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        export.grid(row = 0, column = 3)


        labelsp33 = tk.Label(self, text="",  font=('helvetica', 30, 'bold'))
        labelsp33.grid(row = 1 , column = 1)


        labeltitle2 = tk.Label(self, text="Set the smoke probe position",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)



        bar = tk.Scale(self, from_=-200, to=200,orient=tk.HORIZONTAL, length=2000,tickinterval=50, width = 100 ,font=('helvetica', 10, 'bold'))
        bar.grid(row = 5 , column = 0, columnspan =4)


###################################  PAGE 4 Eksport  #####################################################

class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.session_start_time = datetime.datetime.now().isoformat()[:19]


        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 3, width = 18,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        SpeedAndPitch.grid(row = 0 , column = 0)

        Measurments = tk.Button(self, text="Measurements",height = 3, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        Measurments.grid(row = 0 , column = 1)

        probe = tk.Button(self, text="Adjust probe",height = 3, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        probe.grid(row = 0, column = 2)

        export = tk.Button(self, text="Export data",height = 3, width = 11,command=lambda: controller.show_frame(PageFour), bg='green', fg='white', font=('helvetica', 18, 'bold')) #
        export.grid(row = 0, column = 3)

        labelsp33 = tk.Label(self, text="",  font=('helvetica', 30, 'bold'))
        labelsp33.grid(row = 1 , column = 1)


        tkvar = tk.StringVar(self)
        tkvar.set('Select start time')

        tkvar2 = tk.StringVar(self)
        tkvar2.set('Select ')

        labelmen= tk.Label(self, text = "Select start time", font=('helvetica', 15, 'bold'))
        labelmen.grid(row = 1 , column = 1)

        cb = ttk.Combobox(self)
        cb.set("Start time")
        cb.grid(row = 2, column = 1)

        cb2 = ttk.Combobox(self)
        cb2.set("End time")
        cb2.grid(row = 2, column = 2)

        labelmen= tk.Label(self, text = "Select end time", font=('helvetica', 15, 'bold'))
        labelmen.grid(row = 1 , column = 2)

        def update_times_list():
            c = controller.cursor
            c.execute('SELECT time FROM data')
            cblist = c.fetchall()
            cb['values'] = cblist
            cb2['values'] = cblist
        update_times_list()

        def export_to_csv(startTime=cb.get(), endTime=cb2.get()):
            #startTime, endTime = cb.get(), cb2.get()
            if (startTime>=endTime):
                tk.messagebox.showerror("Error", "Start time can not be less or equal to end time")
            else:
                #export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
                export_file_path = f"/var/www/idm.com/public_html/{endTime}.csv"

                #print ("Exporting data into CSV............")
                cursor = controller.cursor
                q = (startTime, endTime)
                cursor.execute("SELECT * FROM data WHERE time BETWEEN ? AND ?", q)

                with open(export_file_path, "w") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([i[0] for i in cursor.description])
                    csv_writer.writerows(cursor)

        def export_session():
            session_end_time = datetime.datetime.now().isoformat()[:19]
            export_to_csv(self.session_start_time, session_end_time)

        export_selected = tk.Button(self, text="Export selected ",height = 2, width = 10,command=export_to_csv, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        export_selected.grid(row = 2, column = 0)

        export_session_button = tk.Button(self, text="Export session",height = 2, width = 10,command=export_session, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        export_session_button.grid(row = 5, column = 0)


        labelspacer= tk.Label(self, text = "", font=('helvetica', 20, 'bold'))
        labelspacer.grid(row = 3, column = 0)

        updateliste = tk.Button(self, text="Update list ",height = 2, width = 10,command=update_times_list, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        updateliste.grid(row = 4, column = 0)

        poweroff = tk.Button(self, text="Power off ",height = 2, width = 10, command=controller.power_shutdown, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        poweroff.grid(row = 4, column = 3)


def graph_window(database_val,label,yaxislab):
    root = tk.Tk()
    root.wm_title("Embedding in Tk")
    graf_name = tk.Label(root, text= label,   bg='green', fg='white', font=('helvetica', 15, 'bold'))
    graf_name.pack(side=tk.TOP)
    f = Figure(figsize=(5,4), dpi=100)
    a = f.add_subplot(111)
    insert_val =database_val
    f.ylabel = 'test'

    def animate(i):
        c1 = app.cursor
        c1.execute("SELECT time FROM data ORDER BY time DESC LIMIT 1")
        now_time_string = c1.fetchone()[0]
        now_time = datetime.datetime.fromisoformat(now_time_string)

        then_time = now_time - datetime.timedelta(seconds=13)
        then_time_string = then_time.isoformat()

        b = (then_time_string, now_time_string)

        c = app.cursor
        c.execute(insert_val,b)
        fetch = c.fetchall()

        Xaxes = [x[-5:] for (x, y) in fetch]
        Yaxes = [y for (x, y) in fetch]

        pltXaxes = np.array(Xaxes)
        pltYaxes = np.array(Yaxes)

        a.clear()
        a.plot(pltXaxes,pltYaxes)
        a.set_ylabel(yaxislab)
        a.set_xlabel("Time")


    canvas = FigureCanvasTkAgg(f, master=root)  # A tk.DrawingArea.

    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def _quit():
        root.quit()
        root.destroy()


    button = tk.Button(master=root, text="Quit", command=_quit, bg='red', fg='white', font=('helvetica', 30, 'bold'))
    button.pack(side=tk.BOTTOM)

    root.ani = animation.FuncAnimation(f,animate, interval=1000)

    root.geometry("800x480+0+0")
    root.attributes("-fullscreen", True)
    root.mainloop()


# Instantiate main GUI class
app = IDMGUI()

# Remove header and force window to touchscreen
app.geometry("800x480+0+0")
app.update_idletasks()
app.attributes("-fullscreen", True)
app.update_idletasks()

# Run the program
app.mainloop()

# Shut down the communicator thread when the GUI closes
app.comm.close_serial()
