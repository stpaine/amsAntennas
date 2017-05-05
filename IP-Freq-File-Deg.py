##########################################################################
#
#   RRSG - ANTENNA MEASUREMNET SCRIPT FOR MEADE PEDESTAL MEASUREMENT TOOL
#           
#   WRITTEN BY: STEPHEN PAINE (PNXSTE002)
#
##########################################################################
#                              Version 1.1
##########################################################################
#
#   Version 1.0
#   DATE: 11 APRIL 2015
#
#   Version 1.1
#   EDIT: 28/04/2017 - Bug fixes and comments
#                    - Added ability to save increments (deg) to file name
#                    - Added the ability to automatically connect
#                      if thinkRF is connected directly to PC
#
#   This script is to be used in conjunction with the Meade Pedestal
#   using the Meade Pedestal Measurement Tool included in the .zip folder
#   written by Dr Craig Tong.
#
#   This script takes in 4 arguments, namely: IP, Freq, File, Deg
#   IP:     Provide the IP for the WSA5000 (eg 137.258.131.247)
#   Freq:   Provide the WSA with a centre frequency in GHz (eg 1.3)
#   File:   Give a file name (eg Test)
#   Deg:    Increments in degrees so that you know what the file is doing
#
#   If connected directly to PC, no IP argument is required
#
##########################################################################

import sys
import time
from pyrf.sweep_device import SweepDevice
from pyrf.devices.thinkrf import WSA
from pyrf.devices.thinkrf import discover_wsa
from datetime import datetime

dut = WSA()
IP_found = 0

# Read command line for IP (WSA5000 hostname: thinkrf.uct.ac.za)
# Used to discover the IP of the device if directly connected
try:
    wsas_on_network = discover_wsa()
    for wsa in wsas_on_network:
        findIP = wsa["HOST"]
        IP_found = 1

# Find the device on network given user inputted IP
except:
    if IP_found == 1:
        dut.connect(findIP)
        print "Connected to: ",findIP
    else:
        dut.connect(sys.argv[1]) 
        #dut.connect("137.158.131.211")
        print "Connected to: ",sys.argv[1]
        
    dut.reset()
    
    #read second argument in command line for frequency in GHz (eg 1.3)
    if IP_found == 1:
        freq = float(sys.argv[1])*1000000000
    else:
        freq = float(sys.argv[2])*1000000000
        #freq = float(8.5)*1000000000 # For testing purposes

    #we need to set the sweep range (this is approximately the default set by pyRF RTSA)
    start=freq-62.5e6
    stop=freq+62.5e6
    bw=976.562e3

    dut.request_read_perm()
    sd = SweepDevice(dut)

    fstart, fstop, bins = sd.capture_power_spectrum(start, stop, bw,
        {'attenuator':0})

    i = datetime.now()

    #Sets the text file name as "FileName_Frequency_Date"
    if IP_found == 1:
        text = sys.argv[2]+'_[deg_('+sys.argv[3]+')]_'+sys.argv[1]+'GHz'+i.strftime('_%Y_%m_%d')+'.csv'
    else:
        text = sys.argv[3]+'_[deg_('+sys.argv[4]+')]_'+sys.argv[2]+'GHz'+i.strftime('_%Y_%m_%d')+'.csv'
        #text = 'test' # For testing purposes

    f = open(text, 'a')

    peak=-200
    for i in bins:
        if i>peak:
            peak=i

    print "Peak:",peak,"dBm"
    f.write(str(peak)+',\n')

    print "Saved to file:",text
    f.close()
