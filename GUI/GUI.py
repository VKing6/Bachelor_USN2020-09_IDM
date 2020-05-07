#!/usr/bin/env python3

import tkinter as tk
from tkinter import filedialog
from pandas import DataFrame
import serial
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import style
from tkinter import ttk
import sqlite3
import os
import csv
from dateutil import parser
import datetime
import threading
import dataobject
import idmserial
import time


LARGE_FONT= ("Verdana", 12)

######################################## initialization  ##################################

db_cursor = ""


    


########################### PAGE FUNCTION #######################################+

class IDM_app(tk.Tk):

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
        self.after(2000, self.amend_database)



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
        self.after(1000, self.amend_database)




 ##############################  Start page #####################################################



class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

       # labelmenu = tk.Label(self, text="Menu",height = 2, width = 16,  bg='blue', fg='white', font=('helvetica', 30, 'bold'))
        #labelmenu.grid(row = 0 , column = 0)

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

        counterFan = tk.IntVar()

        def increaseFan():
            counterFan.set(counterFan.get() + 1)

        def decreasefan():
            counterFan.set(counterFan.get() - 1)

        counterPitch = tk.IntVar()

        def increasePitch():
            counterPitch.set(counterPitch.get() + 1)

        def decreasePitch():
            counterPitch.set(counterPitch.get() - 1)

        def StopFan():
            counterFan.set(counterFan.get() * 0)

        def ResetPitch():
            counterPitch.set(counterPitch.get() * 0)




       # menue = tk.Button(self, text="Menu",height = 2, width = 13,command=lambda: controller.show_frame(StartPage), bg='blue', fg='white', font=('helvetica', 30, 'bold')) #
        #menue.grid(row = 0 , column = 0)

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


        labeltitle2 = tk.Label(self, text="Adjusting speed and pitch controller",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)


        lableSpeed = tk.Label(self, text=" Speed ",height = 1,     font=('helvetica', 25, 'bold'))
        lableSpeed.grid(row = 4 , column =1)


        lablepitch = tk.Label(self, text="  Pitch  ",height = 1,   font=('helvetica', 25, 'bold'))
        lablepitch.grid(row = 4 , column =2)


        labelspeedinc = tk.Label(self, textvariable = counterFan, bg = "lightgrey", width = 5, font=('helvetica', 25, 'bold'))
        labelspeedinc.grid(row = 5 , column =1)

        pitchinc = tk.Label(self, textvariable = counterPitch, bg = "lightgrey" ,  width = 5, font=('helvetica', 25, 'bold'))
        pitchinc.grid(row = 5 , column =2)


        Speedinc = tk.Button(self, text="Increase",command=increaseFan, bg='cyan', fg='black',height = 2 , width =10, font=('helvetica', 20, 'bold')) #
        Speedinc.grid(row = 6 , column = 1)

        Speeddec = tk.Button(self, text="Decrease",command=decreasefan, bg='yellow', fg='black',height = 2 , width =10, font=('helvetica', 20, 'bold')) #
        Speeddec.grid(row = 7 , column = 1)


        pitchinc = tk.Button(self, text="Increase",command=increasePitch, bg='cyan', fg='black', height = 2 , width =10,font=('helvetica', 20, 'bold')) #
        pitchinc.grid(row = 6 , column = 2)



        pitchdec = tk.Button(self, text="Decrease",command=decreasePitch, bg='yellow', fg='black',height = 2 , width =10, font=('helvetica', 20, 'bold')) #
        pitchdec.grid(row = 7, column = 2)


        Stopbtn = tk.Button(self, text="STOP FAN",command=StopFan,height = 2 , width =15, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        Stopbtn.grid(row = 5, column = 0)

        spacer5 = tk.Label(self, text="")
        spacer5.grid(row = 6 , column = 0)

        resetpitch = tk.Button(self, text="Reset pitch",command=ResetPitch,height = 2 , width =15, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        resetpitch.grid(row = 7 , column = 0)

        spacer6 = tk.Label(self, text="")
        spacer6.grid(row = 8 , column = 0)


 ###################################  PAGE 2 Measurements  #####################################################


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


        self.windspeed   = tk.IntVar()
        self.temperature = tk.IntVar()
        self.humidity    = tk.IntVar()
        self.pitch       = tk.IntVar()
        self.airpressure = tk.IntVar()
        self.dragforce   = tk.IntVar()
        self.liftforce   = tk.IntVar()

        def update_display():
            self.sensor_data = controller.sensor_data.get_data()
            self.windspeed.set(self.sensor_data["windspeed"])
            self.temperature.set(self.sensor_data["temperature"])
            self.humidity.set(self.sensor_data["humidity"])
            self.pitch.set(self.sensor_data["pitch"])
            self.airpressure.set(self.sensor_data["airpressure"])
            self.dragforce.set(self.sensor_data["dragforce"])
            self.liftforce.set(self.sensor_data["liftforce"])
            #ableAirV.config(text=str(self.ws))

            self.after(500, update_display)

        self.after(0, update_display)



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


        labeltitle2 = tk.Label(self, text="Measurements from sensors",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)



        AirVelocity = tk.Button(self, text="Air Velocity",command=lambda: graph_window("SELECT time, windspeed FROM data WHERE time BETWEEN ? AND ?", "windspeed"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        AirVelocity.grid(row = 4, column = 0)
        lableAirV = tk.Label(self, text="5 m/s", textvariable = self.windspeed, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        lableAirV.grid(row = 4, column = 1)


        spacer4 = tk.Label(self, text="")
        spacer4.grid(row = 5 , column = 0)

        Airtemp = tk.Button(self, text="Air Temprature",command=lambda: graph_window("SELECT time, temperature FROM data WHERE time BETWEEN ? AND ?","Temperature"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        Airtemp.grid(row = 6, column = 0)
        labletemp = tk.Label(self, textvariable = self.temperature ,height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        labletemp.grid(row = 6, column = 1)


        spacer5 = tk.Label(self, text="")
        spacer5.grid(row = 7 , column = 0)

        Airhum = tk.Button(self, text="Air Humidity",command=lambda: graph_window("SELECT time, humidity FROM data WHERE time BETWEEN ? AND ?","Humidity"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        Airhum.grid(row = 8, column = 0)
        lableAirhum = tk.Label(self, text="1500", textvariable=self.humidity, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        lableAirhum.grid(row = 8, column = 1)




        Airpress = tk.Button(self, text="Air pressure",command=lambda: graph_window("SELECT time, airpressure FROM data WHERE time BETWEEN ? AND ?","Airpressure"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        Airpress.grid(row = 4, column = 2)
        lableAirpress = tk.Label(self, text="15 kg/m3", textvariable=self.airpressure, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        lableAirpress.grid(row = 4, column = 3)



        forceH = tk.Button(self, text="Drag force",command=lambda: graph_window("SELECT time, dragforce FROM data WHERE time BETWEEN ? AND ?","Dragforce"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        forceH.grid(row = 6, column = 2)
        lableforceH = tk.Label(self, text="2 N", textvariable=self.dragforce, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        lableforceH.grid(row = 6, column = 3)


        froceV = tk.Button(self, text="Lift force",command=lambda: graph_window("SELECT time, liftforce FROM data WHERE time BETWEEN ? AND ?","Liftforce"),height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 15, 'bold')) #
        froceV.grid(row = 8, column = 2)
        lablefroceV = tk.Label(self, text="15 N", textvariable=self.liftforce, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 15, 'bold')) #
        lablefroceV.grid(row = 8, column = 3)




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


class PageFour(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


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

        lablemen= tk.Label(self, text = "Select start time", font=('helvetica', 15, 'bold'))
        lablemen.grid(row = 1 , column = 1)

        #popupMenu = tk.OptionMenu(self, tkvar, *choices)
        #popupMenu.config(font=('helvetica', 15, 'bold'))

        #popupMenu.grid(row = 2 , column = 1)


        cb = ttk.Combobox(self)
        cb.set("Start time")
        cb.grid(row = 2, column = 1)



        cb2 = ttk.Combobox(self)
        cb2.set("End time")
        cb2.grid(row = 2, column = 2)

        lablemen= tk.Label(self, text = "Select end time", font=('helvetica', 15, 'bold'))
        lablemen.grid(row = 1 , column = 2)

        #popupMenu2 = tk.OptionMenu(self, tkvar2, *choices2)
        #popupMenu2.grid(row = 2 , column = 2)

        def update_times_list():
            c = controller.cursor
            c.execute('SELECT time FROM data')
            cblist = c.fetchall()
            cb['values'] = cblist
            cb2['values'] = cblist
        update_times_list()

        def export_to_csv():
            #print(tkvar.get()[2:-3], tkvar2.get()[2:-3])
            q = (cb.get(), cb2.get())
            # for row in c.execute("SELECT * FROM data WHERE time BETWEEN ? AND ?", q):
                #print(row)
            if (cb.get()>=cb2.get()):
                tk.messagebox.showerror("Error", "Start time can not be less or equal to end time")
            else:
                export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')

                print ("Exporting data into CSV............")
                cursor = controller.cursor
                cursor.execute("SELECT * FROM data WHERE time BETWEEN ? AND ?", q)

                with open(export_file_path, "w") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([i[0] for i in cursor.description])
                    csv_writer.writerows(cursor)

        export2 = tk.Button(self, text="Export ",height = 2, width = 10,command=export_to_csv, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        export2.grid(row = 2, column = 0)


        lablespacer= tk.Label(self, text = "", font=('helvetica', 20, 'bold'))
        lablespacer.grid(row = 3, column = 0)

        updateliste = tk.Button(self, text="Update list ",height = 2, width = 10,command=update_times_list, bg='red', fg='white', font=('helvetica', 20, 'bold')) #
        updateliste.grid(row = 4, column = 0)






def graph_window(database_val,lable):
    
    
    root = tk.Tk()
    root.wm_title("Embedding in Tk")
    graf_name = tk.Label(root, text= lable,   bg='green', fg='white', font=('helvetica', 15, 'bold'))
    graf_name.pack(side=tk.TOP)
    f = Figure(figsize=(5,4), dpi=100)
    a = f.add_subplot(111)
    insert_val =database_val

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
        
       # a.locator_params(axis='Xaxes', nbins=10)

        pltXaxes = np.array(Xaxes)
        pltYaxes = np.array(Yaxes)
        
    
        a.clear()
        a.plot(pltXaxes,pltYaxes)
        
        #ax.plot(pltYaxes)
        
    
    canvas = FigureCanvasTkAgg(f, master=root)  # A tk.DrawingArea.

    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
   # toolbar = NavigationToolbar2Tk(canvas, root)
    #toolbar.update()

    
    def _quit():
        root.quit()     
        root.destroy()
    

   # spacer = tk.Label(root, text= "")
    #spacer.pack()
    button = tk.Button(master=root, text="Quit", command=_quit, bg='red', fg='white', font=('helvetica', 30, 'bold'))
    button.pack(side=tk.BOTTOM)
   # time.sleep(10)
    root.ani = animation.FuncAnimation(f,animate, interval=1000)

    root.geometry("800x480+0+0")
    root.attributes("-fullscreen", True)
    root.mainloop()





app = IDM_app()




# Remove header and force window size
app.geometry("800x480+0+0")
app.update_idletasks()
app.attributes("-fullscreen", True)
app.update_idletasks()

# Run the program
app.mainloop()

# Shut down the communicator thread when the GUI closes
app.comm.close()
