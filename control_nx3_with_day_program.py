# -*- coding: utf-8 -*-
""" 
control_nx3_with_day_program.py

An simple way to control the charge and discharge of the batteries of the next 3 in function of the time of the day using modbus
A programm for each hours of the day is given in columns of a csv and is applied by this script.

An typical application is the dynamic tarif: in order to inject solar power in the grid in the morning when energy is expensive, 
the charge current to the battery (DC) is reduced close to zero and automatically the solar power available goes to the grid.
The charge current is then increased to allow the recharge during the afternoon when the solar energy is paid less.

If you play only with charge an discharge current, the battery will never be charged or discharged from the grid. The stategy is always to use it for autarky.

If you want to charge the battery from the grid or discharge it in the grid, use the delta power on AC source. 
Its default value is 0W and with that value, the next always try to minimize the grid power: solar goes first to load or battery, load is covered first by solar or battery
The delta P is a direct power setpoint on the AC-source connection, but all other constraints are respected: max charge/discharging current, SOC for backup, max amps on AC-source ,...

 

notes: 
-The manual charge limits must be activated! 
-and of course the modbus TCP, the IP adress can be seen on the nx-interface screen
-charge and discharge limits: let a little current in case of the control is lost, just in case of
-delta power: is for each phase! so if you set 2000W there will be 6kW taken from the grid 
-...the csv can be changed manually or could be overwriten every day by another script that get the prices and choose the best time to charge or discharge.


Created on Fri Feb  2 21:58:29 2024
@author: moix_po
"""

#import pandas as pd

from datetime import date, datetime, timedelta
import sys
import os
import time
#from datetime import datetime 

import nxmodbus
sys.path.append(os.path.abspath('..'))
from nxmodbus.client_tcp import NextModbusTcp
from nxmodbus.proptypes import PropType


#####   TO ADAPT TO YOUR INSTALLATION   ######
SERVER_HOST = "192.168.1.115"           #at home     # set address of nx-interface, can be seen on nx-interface
###############################################


#######
#The file source for the profile
FILENAME="day_control_setpoints.csv"  #keep the format of the original file with 4 colums, comma at the end!



############################
#initialisation of modbus tcp
ADDRESS_OFFSET = 0                                      # the modbus address offset as set inside the Next system
INSTANCE = 0                                            # The instance of the requested device
SERVER_PORT = 502                                       # listening port of nx-interface
nextModbus = NextModbusTcp(SERVER_HOST, SERVER_PORT, ADDRESS_OFFSET, False)
last_set_point_sent = -1 #time it was sent in hour of the day, init at -1, then it is between 0 and 23h



#######
#Functions

def read_control_file(FILENAME):
    #a reader that don't use pandas csv reader but the simple file open function:
    file = open(FILENAME)
    content = file.readlines() #with readlines I have an array of all lines available
    file.close() 

    #let's take out all the lines to create the setpoints arrays, start empty
    max_charge_power_profile = []
    max_discharge_power_profile = []
    ac_source_delta_profile = []


    number_of_occurence = 0
    for line in content:
        line_separated = line.split(",")
        
        if number_of_occurence > 0:
            #first line is the header, then we have the data in each columns: 
            #    time, max_charge_power, max_discharge_power, ac_source_delta_per_phase
            max_charge_power_profile.append(float(line_separated[1]))
            max_discharge_power_profile.append(float(line_separated[2]))
            ac_source_delta_profile.append(float(line_separated[3]))
            
        number_of_occurence += 1

    print(" CSV file readed. Number of lines in file: " +str(number_of_occurence))
    
    return max_charge_power_profile, max_discharge_power_profile, ac_source_delta_profile





#**************************************
# main loop of the control
#**************************************

while True:   
            
    if last_set_point_sent == -1 :
        #read the csv at beginning and every midnight
        try:    
            # #***************************************
            # #Read the file once a day with the setpoints: very simply with panda, but it's too heavy for a rasp zero
            # setpoints_rough = pd.read_csv(FILENAME)

            # #let's take out the values in simple list format:
            # max_charge_power_profile = setpoints_rough["max_charge_power"].values
            # max_discharge_power_profile = setpoints_rough["max_discharge_power"].values
            # ac_source_delta_profile = setpoints_rough["ac_source_delta_per_phase"].values

            #***************************************
            #Read the file with own function: 
            [max_charge_power_profile, max_discharge_power_profile, ac_source_delta_profile]=read_control_file(FILENAME)
                

            #TODO: check it is the good day, limits of values, ...
        except:
            print("! ERROR when reading the csv file \n")




    
    #***************************
    # Sent the data every hour: 
    #this works only for round hours, no other sampling time possible with this script (for the moment, TODO)
            
    # Current local datetime
    now = datetime.now()

    if now.hour > last_set_point_sent :
        #here the hour has passed, update the sepoint value
        print("\nUpdate setpoints at " + str(now.hour) +  "h")
        
        #we simply use the hour of the day as index of the array: 0 to 23
        setpoint_bmaxchargingcurrentlimit = max_charge_power_profile[now.hour]
        setpoint_bmaxdischargingcurrentlimit = max_discharge_power_profile[now.hour]
        setpoint_ac_source_delta_p = ac_source_delta_profile[now.hour]      


        #***************************************
        #And finally write it to the next3 on the modbus
        one_error_in_sending_param = False #to check it was ok for all param
        try:
            ok = nextModbus.write_parameter(nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_battery_maxchargingcurrentlimit,
                                            setpoint_bmaxchargingcurrentlimit,
                                            PropType.FLOAT)
            if ok:
                print('---> Charge current written to' , round(setpoint_bmaxchargingcurrentlimit, 2) ,' Adc')
            else:
                print('Error when writing charge currrent')
                one_error_in_sending_param = True
    
            #send max discharge current    
            ok = nextModbus.write_parameter(nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_battery_maxdischargingcurrentlimit,
                                            setpoint_bmaxdischargingcurrentlimit,
                                            PropType.FLOAT)
            if ok:
                print('---> Discharge current written to' , round(setpoint_bmaxdischargingcurrentlimit, 2) ,' Adc')
            else:
                print('Error with discharge currrent') 
                one_error_in_sending_param = True

            #send direct delta power for each phase on AC input (direct take from the grid or give)  
            #positive will force battery recharge and negative will force battery discharge
                
            #send delta P per phase:   
            ok = nextModbus.write_parameter(nextModbus.addresses.device_address_acsource,
                                            nextModbus.addresses.acsource_source_targetactivepowerperphase,
                                            setpoint_ac_source_delta_p,
                                            PropType.FLOAT)
            if ok:
                print('---> Delta P AC source written to' , round(setpoint_ac_source_delta_p, 2) ,' W per phase, that is total', round(3*setpoint_ac_source_delta_p, 2), "W" )
            else:
                print('Error with delta P sent') 
                one_error_in_sending_param = True

            #If everything was sent, that is ok, else it will be resent in the next loop until ok
            if  not one_error_in_sending_param:
                #all points were sent, we can say the setpoint is ok for this hour and we can wait for the next one
                last_set_point_sent = now.hour
        except:
            print("! ERROR when sending the Modbus values !")     

            
    #but reset at midnight to restart another day:
    if now.hour == 0 and last_set_point_sent == 23:
        last_set_point_sent = -1

    print("time: " + str(now))   
    time.sleep(5*60.0)      #try every 1 or 5 minutes, not every hours, so if it did'nt went well once, that is tried again after a short delay.
                            #TODO: Active waiting is not very good, to to with threads...


