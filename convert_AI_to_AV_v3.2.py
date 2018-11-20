#%%
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 09 09:53:06 2018

@author: kweber
@contributors: bcubrich
This script takes a monthly 5-min Antelope Island station data from a CSV, and
converts it to an hourly format which can be used to import into AirVision, 
and ultimately AQS.

#**** How to Use *****#

(1) Grab data from Antelope Island, or "SNX", from the following website monthly:
    http://mesowest.utah.edu/cgi-bin/droman/download_api2.cgi?stn=SNX&year1=2018&day1=6&month1=4&hour1=14&timetype=LOCAL&unit=0
(2) Run this script unsing the downloaded SNX data.
        A) choose fielname
        b) Cchoose start and end date (use auto end date if you want)
(3) In AirVision, import the new data using Utilities/File Import Tool with 
    template "UofU Antelope Island Met"
(4) It should take about 5 minutes to import all the data, then the data can 
    be QA/QC'd and imported to AQS! 

INDEX

1. GUI
    This UI help to ensure that the program is run correctly. It asks for a 
    file name and the data time period
    a) get filename
    b) create button disctionaries and lists
    c) get data from GUI

2. Initialize
    read in file and get values from file

3. Calculation
    get hourly data from minute data

4. Output
    write to output file


"""

# import libraries
import numpy as np
from jdcal import gcal2jd,jd2gcal
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter import *




'''--------------------------------------------------------------------------
                                1. GUI
---------------------------------------------------------------------------'''

'''------------------
a) get filename of input antelope island data file'''
    
    
def get_dat():
    root = Tk()
    root.withdraw()
    root.focus_force()
    root.attributes("-topmost", True)      #makes the dialog appear on top
    filename = askopenfilename()      # Open single file
    root.destroy()
    return filename

# data input path
file_data = get_dat()



#main tkinter window=msater
master = Tk()


master.attributes("-topmost", True)      #makes the dialog appear on top


'''------------------
b) create some lists for the buttons'''
    
dates=[x for x in np.arange(1,32)]      #need days of the month
years=[x for x in np.arange(2016,2030)] #need years
mon_dict={'January':1,'February':2, 'March':3,'April':4, 'May':5,
               'June':6, 'July':7, 'August':8, 'Spetember':9, 'October':10, 
               'November':11, 'December':12}
mon__len_dict={'January':31,'February':28, 'March':31,'April':30, 'May':31,
               'June':30, 'July':31, 'August':31, 'September':30, 'October':31, 
               'November':30, 'December':31}
'''------------------
c) create buttons and dropdowns   
  -each w is a tk object, just got w from the code I copied from the internet
  -each variable is a field in the tk windown. variables1, 2, and 3 are the 
   fields for the start date: Month, day, year respectively
  -I used the grid method to indicate the placement of each button, as it is
   more precise than pack
    ''' 
#start date month
variable1 = StringVar(master)
variable1.set("January") # default value
w = OptionMenu(master, variable1, 'January','February', 'March','April', 'May',
               'June', 'July', 'August', 'September', 'October', 'November', 
               'December')
w.grid(row=1, sticky=W, column=0)

#start date day of month
variable2 = StringVar(master)
variable2.set(1) # default value
w2 = OptionMenu(master, variable2, *dates)
w2.grid(row=1, sticky=W, column=1)

#start date year
variable3 = StringVar(master)
variable3.set(2019) # default value
w3 = OptionMenu(master, variable3, *years)
w3.grid(row=1, sticky=W, column=2)

#end date month
variable4 = StringVar(master)
variable4.set('January') # default value
w4 = OptionMenu(master, variable4, 'January','February', 'March','April', 'May',
               'June', 'July', 'August', 'September', 'October', 'November', 
               'December')
w4.grid(row=3, sticky=W, column=0)

#end date day of month
variable5 = StringVar(master)
variable5.set(31) # default value
w5 = OptionMenu(master, variable5, *dates)
w5.grid(row=3, sticky=W, column=1)

#end date year
variable6 = StringVar(master)
variable6.set(2019) # default value
w6 = OptionMenu(master, variable6, *years)
w6.grid(row=3, sticky=W, column=2)

'''------------------
d) get data from GUI'''

def auto_get():
    variable4.set(variable1.get())
    variable5.set(mon__len_dict.get(variable1.get()))
    variable6.set(variable3.get()) # default value
    
def quit():
    global date1
    global date2
    date1=(variable3.get(), mon_dict.get(variable1.get()), variable2.get())
    date2=(variable6.get(), mon_dict.get(variable4.get()),  variable5.get())
    master.destroy()

Autoset = Button(master, text="Auto \n End Date", command=auto_get)
Autoset.grid(row=5, sticky=W, column=0)

button = Button(master, text="OK", command=quit)
button.grid(row=5, sticky=W, column=2)

labelText=StringVar()
labelText.set("Choose State Date")
label1=Label(master, textvariable=labelText, height=4)
label1.grid(row=0, sticky=W, column=1, columnspan=2)

labelText=StringVar()
labelText.set("Choose End Date")
label1=Label(master, textvariable=labelText, height=4)
label1.grid(row=2, sticky=W, column=1)


mainloop()

'''---------------------------------------------------------------------------
                            2. Initialize
Get some data from the file
----------------------------------------------------------------------------'''
#test=pd.read_csv(file_data, skiprows=6)



st_ID = 'SNX'


# data ouput path
save_file = True
out_file = file_data[:-4]+'_1hr.csv'

#date1=(2018,10,1)
# Constant Variables

# time averaging
time_st = gcal2jd(*date1)[0]+gcal2jd(*date1)[1]        # jan 1 2018 00:00
time_ed = gcal2jd(*date2)[0]+gcal2jd(*date2)[1]+(23.0/24.0) # jan 31 2018 23:00
avg_int = 1.0/24.0 # average hourly


# functions

# extract data from AQS pipe-delim format
def AI_extract(st_ID,file_data):
 
    '''
    ### FUNCTION SUMMARY ###
    This function extracts data from a specific monitor using the inputs 
    provided to this function.
    
    ### INPUT ###
    
         * st_ID: _TYPE = string; abbreviation used for site name 
         * file_data: _TYPE = string; This is the full path location of the 
           AMP_501 used in this analysis

         
     ### OUTPUT ###
     
     This function will output a number of NumPy matrices with details about 
     the ambient measurement value, time, and null
     
         * BR_RH_data: _TYPE = numpy float array; ambient measurement value of 
           relative humidity [%]
         * BR_SWS_data: _TYPE = numpy float array; ambient measurement value of 
           wind speed [mph]
         * BR_SWD_data: _TYPE = numpy float array; ambient measurement value of 
           wind direction [Degrees]           
         * BR_V_data: _TYPE = numpy float array; ambient measurement value of 
           Battery Voltage [Volts]           
         * BR_T_data: _TYPE = numpy float array; ambient measurement value of 
           temperature [Deg C]           
         * BR_RH_date_JD: _TYPE = numpy float array; units = Julian date; date 
           corresponds to decimal time when measurement occurred              
    '''
        
    ##### Read in data
    text_file = open(file_data, "r")
     
    BR_RH_data = []         # Relative Humidity [%]
    BR_SWS_data = []        # Wind Speed [mph]
    BR_SWD_data = []        # Wind Direction [Degrees]
    BR_V_data = []          # Voltage
    BR_T_data = []          # Temperature [Celsius]
    BR_RH_date_JD = []      # Julian Date [Days]

    
#this part could be improved with pandas
    for line in text_file:
        ln_spl = line.split(',')
        if len(ln_spl) > 1 and ln_spl[0] == st_ID: 
            
            # date
            yyyy = ln_spl[1][6:10]
            mon = ln_spl[1][0:2]
            day = ln_spl[1][3:5]
            timehh = ln_spl[1][11:13]
            timemm = ln_spl[1][14:16]
                    
            # convert to JD
            JD_dayc = (float(timemm)/(60.0*24.0)) + (float(timehh)/(24.0))
            JD_time = gcal2jd(yyyy,mon,day)[0] + gcal2jd(yyyy,mon,day)[1] + JD_dayc
            BR_RH_date_JD = np.append(BR_RH_date_JD,[JD_time])
                
            # RH data values
            if ln_spl[6] != '':
                BR_RH_data = np.append(BR_RH_data,[float(ln_spl[6])])
            else:
                BR_RH_data = np.append(BR_RH_data,[np.nan])
            
            # SWS data values    
            if ln_spl[7] != '':
                BR_SWS_data = np.append(BR_SWS_data,[float(ln_spl[7])])
            else:
                BR_SWS_data = np.append(BR_SWS_data,[np.nan])                
            
            # SWD data values
            if ln_spl[10] != '':
                BR_SWD_data = np.append(BR_SWD_data,[float(ln_spl[10])])
            else:
                BR_SWD_data = np.append(BR_SWD_data,[np.nan]) 
            
            # Voltage data values        
            if ln_spl[8] != '':
                BR_V_data = np.append(BR_V_data,[float(ln_spl[8])])
            else:
                BR_V_data = np.append(BR_V_data,[np.nan]) 
             
            # Temperature data values    
            if ln_spl[3] != '':
                BR_T_data = np.append(BR_T_data,[(5.0/9.0)*(float(ln_spl[3])-32.0)])   # convert to Celsius
            else:
                BR_T_data = np.append(BR_T_data,[np.nan])         

                    
                    
    text_file.close()    
    del text_file
       
    return BR_RH_data,BR_SWS_data,BR_SWD_data,BR_V_data,BR_T_data,BR_RH_date_JD



# Use function to extract data from MesoWest file

BR_RH_data,BR_SWS_data,BR_SWD_data,BR_V_data,BR_T_data,BR_RH_date_JD = AI_extract(st_ID,file_data)


'''---------------------------------------------------------------------------
                            3. Calculations
Average Data Parameters Hourly 
----------------------------------------------------------------------------'''


hr_JD_timevec = []
hr_G_timevec = []
hr_RH = []
hr_SWS = []
hr_SWD = []
hr_V = []
hr_T = []

t0 = time_st
while t0 < time_ed:             # perform averaging to end of month
    
    # iterate to end of hourly averaging window
    t2 = t0+avg_int
    
    # initialize time averaging indices
    t_gd1 = np.zeros(len(BR_RH_data),dtype = int)
    t_gd2 = np.zeros(len(BR_RH_data),dtype = int)
    
    # create matix to represent values corresponding to hour of interest
    t_gd1 = np.where(BR_RH_date_JD>=t0,1,0)
    t_gd2 = np.where(BR_RH_date_JD<t2,1,0)
    tgd3 = t_gd1+t_gd2
    
    # average data values hourly
    hr_RH = np.append(hr_RH,[np.nanmean(BR_RH_data[tgd3==2])])
    hr_SWS = np.append(hr_SWS,[np.nanmean(BR_SWS_data[tgd3==2])])
    hr_SWD = np.append(hr_SWD,[np.nanmean(BR_SWD_data[tgd3==2])])
    hr_V = np.append(hr_V,[np.nanmean(BR_V_data[tgd3==2])])
    hr_T = np.append(hr_T,[np.nanmean(BR_T_data[tgd3==2])])
    
    hr_JD_timevec = np.append(hr_JD_timevec,[t0])
    
    # convert from julian to gregorian
    gtime0 = jd2gcal(t0,0.0)
    yr0 = str(gtime0[0])
    
    # 2-digit month
    if int(gtime0[1])<10:
        MM0 = '0'+str(gtime0[1])
    else:
        MM0 = str(gtime0[1])

    # 2-digit day
    if int(gtime0[2])<10:
        dd0 = '0'+str(gtime0[2])
    else:
        dd0 = str(gtime0[2])  

    # 2-digit hour
    if round(gtime0[3]*24.0) <10:
        hh0 = '0'+str(int(round(gtime0[3]*24.0)))
    else:
        hh0 = str(int(round(gtime0[3]*24.0)))       
        
    # output formatted time for AirVision
    hr_G_timevec = np.append(hr_G_timevec,[MM0+'/'+dd0+'/'+yr0+' '+hh0+':00'])
     
    # reset time to iterate to next non-overlapping hourly averaging window
    t0 = t2


'''---------------------------------------------------------------------------
                            4. File Output
# format variable for output to .csv 
----------------------------------------------------------------------------'''


     
allvars0 = np.vstack((hr_G_timevec,hr_RH,hr_SWS,hr_SWD,hr_V,hr_T))
allvars1 = np.transpose(allvars0)

# save output to .csv
if save_file == True:
    np.savetxt(out_file, \
        allvars1,fmt = ('%s','%s','%s','%s','%s','%s'),delimiter = ',', \
        header = 'Date, 1-hr RH [%], 1-hr SWS [mph], 1-hr SWD [Deg], 1-hr Voltage [V], 1-hr Temp [DegC]',comments = '')