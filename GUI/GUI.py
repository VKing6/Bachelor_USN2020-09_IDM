#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog
from pandas import DataFrame
#from tkinter import Tk, Canvas, Frame, BOTH
#from math import * 
#import matplotlib.pyplot as plt
import serial
#import numpy as np
#import math
#from colorama import Fore, Back, Style 
from PIL import Image
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
sys.path.insert(0, "/home/pi/Projects/IDM/IntComm")
import dataobject
import idmserial
import threading

#from PIL import Image,ImageTk

LARGE_FONT= ("Verdana", 12)

######################################## initialization  ##################################
    

stop_receiver_event = threading.Event()
sensor_data = dataobject.DataObject()
comm = idmserial.SerialCommunicator(sensor_data,stop_receiver_event)




########################### PAGE FUNCTION #######################################+

class SeaofBTCapp(tk.Tk):

    def __init__(self, *args, **kwargs): 
        
        
        tk.Tk.__init__(self, *args, **kwargs)
        
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1) #gjør at alt expander av seg selv med pack
        container.grid_columnconfigure(0, weight=1)
        

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo, PageThree): #antall sider som skal lages i programmet

            frame = F(container, self)
            

            self.frames[F] = frame
            
            frame.grid_rowconfigure(0, weight=0) #gjør at alt expander av seg selv grid
            frame.grid_columnconfigure(0, weight=1)
            
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage) # viser første side
        #self.geometry("1300x500")
        #self.geometry("800x480")
        self.title("IDM")


    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()



 ###################################  Start page #####################################################   


        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        

       # labelmenu = tk.Label(self, text="Menu",height = 2, width = 16,  bg='blue', fg='white', font=('helvetica', 30, 'bold'))
        #labelmenu.grid(row = 0 , column = 0)
        
        SpeedAndPitch = tk.Button(self, text="Menu",height = 2, width = 15,command=lambda: controller.show_frame(StartPage), bg='blue', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 0)
        
        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 2, width = 15,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 1)
        
        Measurments = tk.Button(self, text="Measurments",height = 2, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        Measurments.grid(row = 0 , column = 2)   
        
        probe = tk.Button(self, text="Adjust probe",height = 2, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        probe.grid(row = 0, column = 3)
        
        
        labelsp3 = tk.Label(self, text="",  font=('helvetica', 30, 'bold'))
        labelsp3.grid(row = 1 , column = 1) 
        
        
        
        
        labelsp3 = tk.Label(self, text="                  ",  font=('helvetica', 30, 'bold'))
        labelsp3.grid(row = 1 , column = 0)       
        
        labelsp4 = tk.Label(self, text="Project members: ", bg='red', fg='white', font=('helvetica', 30, 'bold'))
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
            
            
            
            
            
        SpeedAndPitch = tk.Button(self, text="Menu",height = 2, width = 15,command=lambda: controller.show_frame(StartPage), bg='blue', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 0)
        
        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 2, width = 15,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 1)
        
        Measurments = tk.Button(self, text="Measurments",height = 2, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        Measurments.grid(row = 0 , column = 2)   
        
        probe = tk.Button(self, text="Adjust probe",height = 2, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        probe.grid(row = 0, column = 3)
        
        

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 1 , column = 0)
     
        
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
        
        def empty():
            test = 3
            
        
        self.windspeed   = tk.IntVar()
        self.temperature = tk.IntVar()
        self.humidity    = tk.IntVar()
        self.pitch       = tk.IntVar()
        self.airpressure = tk.IntVar()
        self.dragforce   = tk.IntVar()
        self.liftforce   = tk.IntVar()
            
        def update_display():
            self.sensor_data = sensor_data.get_data()
            self.windspeed.set(self.sensor_data["windspeed"])
            self.temperature.set(self.sensor_data["temperature"])
            self.humidity.set(self.sensor_data["humidity"])
            self.pitch.set(self.sensor_data["pitch"])
            self.airpressure.set(self.sensor_data["airpressure"])
            self.dragforce.set(self.sensor_data["dragforce"])
            self.liftforce.set(self.sensor_data["liftforce"])
            #ableAirV.config(text=str(self.ws))
            
            self.after(500, update_display)
            

        
        def temp2():

            temp2 = float(serialArduino.readline()) 
            tempvar.set(temp2)
              
            
           
        def temp_update():
            temp2()
            self.after(5000, temp_update)
        
     
        #temp_update()            
        
               
        
        SpeedAndPitch = tk.Button(self, text="Menu",height = 2, width = 15,command=lambda: controller.show_frame(StartPage), bg='blue', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 0)
        
        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 2, width = 15,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 1)
        
        Measurments = tk.Button(self, text="Measurments",height = 2, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        Measurments.grid(row = 0 , column = 2)   
        
        probe = tk.Button(self, text="Adjust probe",height = 2, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        probe.grid(row = 0, column = 3)
        
        

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 1 , column = 0)
     
        
        labeltitle2 = tk.Label(self, text="Measurments from sensors",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)
        
        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)    



        AirVelocity = tk.Button(self, text="Air Velocity",command=empty,height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 20, 'bold')) # 
        AirVelocity.grid(row = 4, column = 0)  
        lableAirV = tk.Label(self, text="5 m/s", textvariable = self.windspeed, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 20, 'bold')) # 
        lableAirV.grid(row = 4, column = 1)  


        spacer4 = tk.Label(self, text="")
        spacer4.grid(row = 5 , column = 0)

        Airtemp = tk.Button(self, text="Air Temprature",command=grphtest,height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 20, 'bold')) # 
        Airtemp.grid(row = 6, column = 0)  
        labletemp = tk.Label(self, textvariable = self.temperature ,height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 20, 'bold')) # 
        labletemp.grid(row = 6, column = 1)  


        spacer5 = tk.Label(self, text="")
        spacer5.grid(row = 7 , column = 0)

        Airhum = tk.Button(self, text="Air Humidity",command=empty,height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 20, 'bold')) # 
        Airhum.grid(row = 8, column = 0)  
        lableAirhum = tk.Label(self, text="1500", textvariable=self.humidity, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 20, 'bold')) # 
        lableAirhum.grid(row = 8, column = 1)  




        Airpress = tk.Button(self, text="Air pressure",command=empty,height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 20, 'bold')) # 
        Airpress.grid(row = 4, column = 2)  
        lableAirpress = tk.Label(self, text="15 kg/m3", textvariable=self.airpressure, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 20, 'bold')) # 
        lableAirpress.grid(row = 4, column = 3)  



        forceH = tk.Button(self, text="Force Horizontal",command=empty,height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 20, 'bold')) # 
        forceH.grid(row = 6, column = 2)  
        lableforceH = tk.Label(self, text="2 N", textvariable=self.dragforce, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 20, 'bold')) # 
        lableforceH.grid(row = 6, column = 3) 


        froceV = tk.Button(self, text="Force Vertical",command=empty,height = 2 , width =15, bg='cyan', fg='black', font=('helvetica', 20, 'bold')) # 
        froceV.grid(row = 8, column = 2)  
        lablefroceV = tk.Label(self, text="15 N", textvariable=self.liftforce, height = 2 , width =15, bg='lightgrey', fg='black', font=('helvetica', 20, 'bold')) # 
        lablefroceV.grid(row = 8, column = 3) 
        
        self.after(0, update_display)



 ###################################  PAGE 3 Røykprobe  #####################################################   


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        

        SpeedAndPitch = tk.Button(self, text="Menu",height = 2, width = 15,command=lambda: controller.show_frame(StartPage), bg='blue', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 0)
        
        SpeedAndPitch = tk.Button(self, text="Adjust speed/pitch",height = 2, width = 15,command=lambda: controller.show_frame(PageOne), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        SpeedAndPitch.grid(row = 0 , column = 1)
        
        Measurments = tk.Button(self, text="Measurments",height = 2, width = 13, command=lambda: controller.show_frame(PageTwo), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        Measurments.grid(row = 0 , column = 2)   
        
        probe = tk.Button(self, text="Adjust probe",height = 2, width = 13,command=lambda: controller.show_frame(PageThree), bg='green', fg='white', font=('helvetica', 30, 'bold')) # 
        probe.grid(row = 0, column = 3)
        
        

        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 1 , column = 0)
     
        
        labeltitle2 = tk.Label(self, text="Set the smoke probe posistion",   bg='red', fg='white', font=('helvetica', 20, 'bold'))
        labeltitle2.grid(row = 2 , column =0, columnspan = 5)
        
        spacer3 = tk.Label(self, text="")
        spacer3.grid(row = 3 , column = 0)  

        
        
        bar = tk.Scale(self, from_=-200, to=200,orient=tk.HORIZONTAL, length=2000,tickinterval=50, width = 100 ,font=('helvetica', 10, 'bold'))
        bar.grid(row = 5 , column = 0, columnspan =4)  
  













###### GLOBAL FUNCTIONS ######################################################################
 
def grphtest():
    
        
    
    fig = plt.figure(figsize=(5, 4), dpi=200)
    ax = fig.add_subplot(1, 1, 1)
    xs = []
    ys = []
    
    def animate(i, xs, ys):
        
    
        temp = float(serialArduino.readline())  #hva som skal plottes i y axe
        print(temp)
    
        xs.append(dt.datetime.now().strftime('%H:%M:%S')) # sender inn hva som plottes  i X axe med tid
        ys.append(temp)                                   # sender inn hva som plottes  i Y axe   med temp            
    
        ax.clear()
        ax.plot(xs, ys)
    
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('Time')
        plt.ylabel('Degree C')
    


    ani= animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=5000)
    plt.show(ani)


 ################################################################################################       
    
def create_window_graph(windspeed,drag,windforce,reqpower):
   
    window = tk.Toplevel()
    
    
    #t = np.arange(5, 10, .01) #plotter x axes
    #t1 = np.arange(10, 15, .01) #plotter x axes

    
    
    fig = Figure(figsize=(5, 4), dpi=150)
    
    fig.add_subplot(111).plot(windspeed,drag, 'r--', label = "Drag") #plotter y og x axes NB DE MÅ VÆRE LIKE LANGE OM DU VIL HA EN NY LINJE COPY PAST DENNE
    
    fig.add_subplot(111).plot(windspeed,windforce, 'b--', label = "Windforce") 
    
    fig.add_subplot(111).plot(windspeed,reqpower, 'g--', label = "Requierd power") 
    
    
    
    fig.legend()
    
    
    
    canvas = FigureCanvasTkAgg(fig, master=window)  
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    
    def on_key_press(event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, canvas, toolbar)
    
    
    canvas.mpl_connect("key_press_event", on_key_press)
    
    
    def _quit():
        #window.quit()     
        window.destroy() 
                       
    lable32 = tk.Label(master = window, text = "Windspeed")
    lable32.pack()
    
    sap = tk.Label(master = window, text = "")
    sap.pack()
    
    button = tk.Button(master=window, text="Quit", command=_quit, bg='red', fg='white', font=('helvetica', 10, 'bold'))
    button.pack()
    
    
    
 ################################################################################################       


   
def create_window_picture(pic):
   
    window = tk.Toplevel()
    
    load = Image.open(pic) # set in file directory 
    render = ImageTk.PhotoImage(load)
    
   
    
    
    img = tk.Label(window, image=render)
    
    img.image = render
    img.place(x=0, y=0)
    
    img.pack()
       

    def _quit():
       # window.quit()     
        window.destroy() 
                       
    
    
    button = tk.Button(master=window, text="Quit", command=_quit, bg='red', fg='white', font=('helvetica', 10, 'bold'))
    button.pack()    



################################################################################################
        
def exportCSV ():
  
    values = {'Speed': Windspeed}
    
    df = DataFrame( values,columns= ['Speed', 'Drag','windforce','Requierd power',  'Areal','lift']) 
    
    
    
    export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    df.to_csv (export_file_path, index = False, header=True)    
    
    
    



    
    
################################################################################################




    
################################################################################################


def NewWindow():
   
    window = tk.Toplevel()


    
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
   

    

    def _quit():
        #window.quit()     
        window.destroy() 
                       
    
    
    button = tk.Button(master=window, text="Quit", command=_quit, bg='red', fg='white', font=('helvetica', 10, 'bold'))
    button.grid(row=15, column = 0)   
    
    return window






app = SeaofBTCapp()

#app.resizable(0, 0)
#app.attributes("-type","splash")

app.mainloop()

comm.close()



