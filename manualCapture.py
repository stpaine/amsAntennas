##########################################################################
#
#   RRSG - ANTENNA MEASUREMNET SCRIPT FOR MEADE PEDESTAL MEASUREMENT TOOL
#           
#   WRITTEN BY: STEPHEN PAINE (PNXSTE002)
#
#   DATE: 20 November 2015
#
#   EDIT: 28/04/2017 - Comments and bug fixes
#
#   This script is to be used with any rotating pedestal and the ThinkRF SA.
#   NOTE: To find the IP on UCTs network, use "ping thinkrf.uct.ac.za"
#
#   This script takes in 3 arguments, namely: IP, Freq, File
#   IP:     Provide the IP for the WSA5000 (eg 137.258.131.247)
#   Freq:   Provide the WSA with a centre frequency in GHz (eg 1.3)
#   File:   Give a file name (eg Test)
#
##########################################################################

#Used to run the ThinkRF
import sys
import time
from pyrf.sweep_device import SweepDevice
from pyrf.devices.thinkrf import WSA
from datetime import datetime
from pyrf.devices.thinkrf import discover_wsa
dut = WSA()

#Used to run GUI
import os
from Tkinter import *
import tkMessageBox,tkFileDialog

#Declare global variables
global counter
counter = 0
global newName
newName = ""
fail = 0
global success
success = "Connected!"
global errorMessage
errorMessage = "Setup Failed"

#############################
# Insert variable data here #
#############################

#ThinkRF IP 
IP = "137.158.131.211"

#Frequency of interest
freq = 1.3      

#File Name
Name = 'test'

#Set the initial state
degrees = 1

#############################
#       Main Function       #
#############################

def GetReading(IP,Frequency,Name,degrees):
    #read command line for IP (WSA5000 hostname: thinkrf.uct.ac.za)
    try:

        global fail
        dut.connect(IP)
        dut.reset()
                 
        freq=float(Frequency)*1000000000
        
        #we need to set the sweep range (this is approximately the default set by pyRF RTSA)
        start=freq-62.5e6
        stop=freq+62.5e6
        bw=976.562e3

        dut.request_read_perm()
        sd = SweepDevice(dut)

        fstart, fstop, bins = sd.capture_power_spectrum(start, stop, bw,
            {'attenuator':0})

        #Checks the date to add to the file name
        i = datetime.now()

        #Sets the text file name as "FileName_Date"
        text = Name+'_[deg_('+degrees+')]'+i.strftime('_%Y_%m_%d')+'.csv'
        f = open(text, 'a')
        
        global success
        print success
        
        peak=-200
        for i in bins:
            if i>peak:
                peak=i

        print "Peak:",peak,"dBm"
        f.write(str(peak)+',\n')

        print "Saved to file:",text
        
        #Check to see whether the file name has changed to that
        #we can reset the counter
        global counter
        global newName
        if newName == Name:
            counter = counter+int(degrees)
            print "Degree:",counter

        else:
            counter = 0
            print "Degree:",counter
            newName=Name

        print
        f.close()
        fail = 0

    #if error, throw exception to user
    except:
        global errorMessage
        print errorMessage
        fail = 1
        print

#############################
#       GUI Function        #
#############################

def GUIFunction(W,X,Y,Z):
    root = Tk()
    root.title('Antenna Measurement System v1.1')
        
#create first entry field
    textFrame_1=Frame(root)
    entry_ip=Label(textFrame_1)
    entry_ip["text"]="Enter ThinkRF IP: "
    entry_ip.pack(side=LEFT)

    ip_widget=Entry(textFrame_1)
    ip_widget["width"]=50
    ip_widget.pack(side=LEFT)

    ## ADD TEXT TO TEXT BOX
    try:
    # Used to discover the IP of the device if connected directly (not through network)
        wsas_on_network = discover_wsa()
        for wsa in wsas_on_network:
    ##        print wsa["MODEL"], wsa["SERIAL"], wsa["FIRMWARE"], wsa["HOST"]
            findIP = wsa["HOST"]
        ip_widget.insert(END, findIP)
    except:
        ip_widget.insert(END, "thinkrf.uct.ac.za")

    textFrame_1.pack()

#Create second entry field
    textFrame_2=Frame(root)
    entry_freq=Label(textFrame_2)
    entry_freq["text"]="Enter Freq (GHz): "
    entry_freq.pack(side=LEFT)

    freq_widget=Entry(textFrame_2)
    freq_widget["width"]=50
    freq_widget.pack(side=LEFT)

    ## ADD TEXT TO TEXT BOX
    freq_widget.insert(END, "1.3")

    textFrame_2.pack()

#Create third entry field
    textFrame_3=Frame(root)
    entry_name=Label(textFrame_3)
    entry_name["text"]="Enter File Name:  "
    entry_name.pack(side=LEFT)

    name_widget=Entry(textFrame_3)
    name_widget["width"]=50
    name_widget.pack(side=LEFT)

    ## ADD TEXT TO TEXT BOX
    name_widget.insert(END, "Example")

    textFrame_3.pack()

#create forth entry field
    textFrame_4=Frame(root)
    entry_degrees=Label(textFrame_4)
    entry_degrees["text"]="Step Size (deg):    "
    entry_degrees.pack(side=LEFT)

    degrees_widget=Entry(textFrame_4)
    degrees_widget["width"]=50
    degrees_widget.pack(side=LEFT)

    ## ADD TEXT TO TEXT BOX
    degrees_widget.insert(END, "1")

    textFrame_4.pack()

    def RunTest(enter):
        IP=ip_widget.get()
        freq=freq_widget.get()
        Name=name_widget.get()
        degrees=degrees_widget.get()

        GetReading(IP,freq,Name,degrees)

        global success
        global errorMessage
        global counter

        # Count the degree that we are on so that the user doesnt get confused
        # or forget and take a double measurement
        if fail == 0:
            completed['text'] = "Degree: {}".format(counter)
        if fail == 1:
            completed['text'] = "Error: {}".format(errorMessage)

    def Close(enter):
        root.destroy()

    # Bind the buttons as needed so that the user can use the pointer device to
    # click from a distance. The pointers generally use page up and down for
    # forward and backwards
    b1=Button(root, text='Next',bg="blue",fg="white", command=RunTest)
    root.bind("<Prior>", RunTest)
    root.bind("<Next>", RunTest)
    root.bind("<Return>", RunTest)
    b1.pack(side=LEFT)
    b2=Button(root, text='Done',bg="red",fg="white", command=Close)
    root.bind("<Escape>", Close)
    b2.pack(side=RIGHT)

    global completed
    completed=Label(root, text="Ready")
    completed.pack()
    
    root.mainloop()

##############################################
##############################################
  
GUIFunction(IP,freq,Name,degrees)
