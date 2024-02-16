
# Control of next3 with MODBUS 

The next3 is an solar+battery hybrid inverter of Studer-Innotec. It provides solar electricity ON and OFF-grid and allows for energy autonomy/autarky.
There are monitoring tools supplied freely by the Studer-Innotec company (web portal, APP). There are also open possibilities with MODBUS communication and API to the monitoring, that's where it starts to be interesting...

In this repository:
- A script to read the values of the next3
- A simple script to charge and discharge the battery in function of the energy prices varying with the time of day





## Studer lib for Modbus

For the use of modbus TCP (or RTU), a library is ready: nxmodbus with source code available on https://github.com/studer-innotec/next-modbus

A package was done, then to use it, simply type in a terminal:

`pip install nxmodbus`   ( with `sudo` on rasp to avoid trouble with an independant run at startup )

To communicate with the next3 with the Modbus TCP, it must be on the same network (typically on the same router in the house) and you have to give its IP adress, this can be found easily on the nx-interface screen, monitoring screen.

The modbus must be activated in TCP mode on the next3. The modbus menu is in the monitoring page:

![modbus screen](https://albedo.ch/wp-content/uploads/2024/02/image.png)
 

## Status of nx3 over the local network with python

The python script MODBUS_TCP_read_of_next3_status.py  displays in the terminal the live value, the production/consumption of yesterday and of the full life of the next3: 

Change the next 3 IP adress at the beggining of the script: 

`SERVER_HOST = "192.168.1.115"` 

And prices can be adapted at the beginning of the script for your real costs.

Example of result:
``` py
###############################
#### LIVE VALUES
Battery Voltage: 51.99989700317383 Volts
Battery SOC: 40.0 %
Battery SOC for grid feeding: 100.0 % target
Battery BMS Temperature: 22.0 °C
Sensor Temperature: 14.714472770690918 °C
Battery Power: -799.5850219726562 [W]
Solar Power: 3.5032461608120427e-44 [W]
Grid Power: 14.278555870056152 [W]
Consummer Power: 719.4459228515625 [W]
AC-Load Power: 695.4700317382812 [W]
AC-FLEX Load Power: 23.560806274414062 [W]
The date and time is: 08-02-2024, 20:40:09
###############################
#### YESTERDAY
AC-Loads last day energy : 5.41 [kWh]
AC-FLEX last day energy : 17.61 [kWh]
AC-source last day produced energy : 8.86 [kWh]
AC-source last day consummed energy : 9.41 [kWh]
Solar last day energy : 25.8 [kWh]
Battery last day charged energy : 7.79 [kWh]
Battery last day discharged energy : 6.86 [kWh]
Energy sold to the grid yesterday: 1.42 CHF
Energy bought from the grid yesterday: 2.54 CHF
Savings with Autarky 3.67 CHF
TOTAL: 5.09 CHF

###############################
#### ALL LIFE OF NX3

Battery total charged energy : 2291.86 [kWh]
Battery total discharged energy : 2174.5 [kWh]
AC-source total consummed energy : 3932.15 [kWh]
AC-source total produced energy : 9753.5 [kWh]
Solar total energy : 15278.93 [kWh]
AC-Loads total energy : 2739.27 [kWh]
AC-FLEX total energy : 5304.34 [kWh]Total energy sold to the grid: 1560.56 CHF
Total energy bought from the grid: 1061.68 CHF
Total savings with Autarky: 1110.09 CHF
TOTAL: 2670.65 CHF

CO2 saved with autarky and grid-feeding 651.65 kg of CO2 
``` 

  

This script is available here: https://github.com/moixpo/nxcontrol 



## A day programm to charge and discharge the battery at certain times


With the energy transition, the electrical grid of tomorrow will be managed very differently. There will be hours with a lot of solar in excess (even too much) and some other moments where energy is scarce.

For the end consummers it will mean some hours the energy is very cheap and at other times it will be expensive. That is already a reallity in some countries of Europe that have a dynamic tarrification. The example below are the puplished priced in Spain with the Esios PVPC price:

![Esios](https://albedo.ch/wp-content/uploads/2024/02/prices_may2023.jpg)

Some hours the solar is not paid at all (the afternoon of the 30th of may). Here the storage becomes very interesting. It is of course smarter to recharge the battery at that time when it would not be paid on the grid. And inject the solar excess during the morning when electricity has a value. Same for the discharge: it is better to keep the battery energy for the high price hours of electricity.

To cope with that situation in a very simple way, a charging schedule can be done. That is not perfect but that makes probably 80% of the job with 20% of the effort. The perfect solution would be to have the prices, the weather forecast and run an optimization that dispatch optimally the charge and the discharge of the battery. But let’s start simply.

That is also available here in the same folder: https://github.com/moixpo/nxcontrol

The control script is in control_nx3_with_day_program.py and the schedule is in a csv file: day_control_setpoints.csv

Principles of the script are:

- A day program/profile is given in a simple csv file, that could be edited by anybody. Only 24 lines for the 24hours of the day in a given format.
- It has 3 columns: the max charging current, the max discharging current. For more advanced control it is possible to give the power wanted on AC-source (an deltaP compared to the normal behaviour of trying to take as little as possible from the grid to have maximal autarky).
- For each hours, the setpoints from the csv files will be send to the next3 and influences if the battery is charged or not. They are not absolute value taken by the next3 but only setpoint, per example when the battery is full, the charging is stopped even if you say 100A. All the systems continues to be managed properly by the next3. There are no risks except to have an empty battery…
- The control program is running all day (on a computer, or a raspberry) read that csv file and control the nx3 with modbus TCP.
- The csv file is read once at midnight, so if a user want to change its program for the next day in function of the new prices or weather forecasts, he edits the file and save it at anytime during the day. It will be taken into account at midnight. For an immediate application of the setpoints, stop the script and restart it.

Here is an example of a day with that control applied: from 7 to 12h the charge current is set down to a 5A DC (~250W, small for the battery size). Just a small value in order not to give 0A:

![result day](https://albedo.ch/wp-content/uploads/2024/02/image-4.png)
The sent settpoints can be seen on the Studer portal monitoring, on the battery page (but the charging limit displayed is mixed with the setpoint comming from the BMS of the lithium battery, the smallest is taken into account. That is why the charging limit goes down to 0A during the afternoon when the battery has reached 100%):

![result batt](https://albedo.ch/wp-content/uploads/2024/02/image-5.png)

Below is another example for the following case: there is a dynamic tarif with a very low price during some hours of the night. At this time the battery was filled, in order to cover the consumption hours of the morning. Then in the morning the recharge is forbiden: the solar power is injected to the grid when it has more values. From 11h the recharged with solar is allowed in order to store energy for the evening.

![night recharge](https://albedo.ch/wp-content/uploads/2024/02/image-15-1536x605.png)



## Automatic use of the script at startup of a Raspberry


The goal here is to have a small raspberry zero that cost very little, consumes almost nothing and let it make the control instead of my main computer.

### Start from begining

Here are the steps to do to start from beggining. If everything goes smoothly, it should take less thant 1h, including half an hour to wait for the SD card to be written:

- Have an raspberry zero 2 (a zero 1 W is probably enough but so slow as a desktop…). With a casing, to protect it when you leave it runing somewhere. Have the possiblity to write the SD card on your normal PC
    ![the rasp](https://albedo.ch/wp-content/uploads/2024/02/image-1.png)

- Install the lattest OS: https://www.raspberrypi.com/software/operating-systems/ –> download the Raspberry PI Imager
- Create the SD card with Imager. The simplest is to give all options when you create the SD card: user and password, wifi and password, activate ssh in services. Then it’s really straight forward. The wifi access to your local network is necessary to communicate in Modbus TCP with the next3 in the LAN.

    ![Imager](https://albedo.ch/wp-content/uploads/2024/02/image-2.png)


- Take the python script mentionned above and adapt them for your case:
    - Change the next 3 IP adress in the python script with yours: `SERVER_HOST = "192.168.1.115`
- Make your own day programm with the max charge and discharge current in the csv file (the manual current limits must be activated on your next3!)
- Copy the files to your raspberry, the best is to learn to do it from ssh from your PC (usefull to update it later, as long as the PI is connected to the WIFI somewhere in the house, you don’t need to touch it anymore). Open a terminal window and use the following command: pscp
        `scp <file_path in Windows> pi@<IP Address of Raspberry Pi>:<Path to File>`
    - In my case: `pscp C:\Users\moix_\Dropbox\TCC_epfl\nxcontrol\day_control_setpoints.csv pi@raspberrypi.local:Documents/nxcontrol/`
    - note that pi@ is the name I gave as user to the pi when making the SD card with Imager. If the adress name raspberry.local is not ok, maybe the direct IP must be used
    - The password associated with the user pi@ will be asked. Here is how it should look like:

    ![pscp](https://albedo.ch/wp-content/uploads/2024/02/image-3.png)


- To run our control script, the nxmodus library is still missing. Remember we have a brand new OS. The easiest is to have the pi with a screen, mouse, keyboard and make it directly with the PI. Check you have the wifi connection, open a terminal and type sudo pip install nxmodbus with superuser sudo to be sure to have it for all users.
- Now the Raspberry is ready, all the files are copied to it. It would be good to test the programm once before saying that it must run automatically at startup. To check it’s fine and all paths and dependencies are OK. Go to a terminal an runpython `python Documents/nxcontrol/control_nx3_with_day_program.py` (or with the path you use)
- In order to have the control script automatically starting at boot of the rapsberry, here are the possible ways:
    https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup
- goal is to have an rasp zero that is simply powered and the thing is running. I choosed the easiest one that I already used before: add a line in the startup file in the rc.local file:
    - `sudo nano /etc/rc.local` sudo is for superuser access, nano is the small editor
    - In the editor, write the line:
        - `sudo bash -c '/usr/bin/python3 /home/pi/Documents/nxcontrol/control_nx3_with_day_program.py > /home/pi/blink.log 2>&1' & `
        - don’t forget the &, it took me 30 min to see that little error…
        
    ![automatic start](https://albedo.ch/wp-content/uploads/2024/02/image-12.png)
    - there will be the log of the cmd line in the log file in the same folder as the script

- Restart the raspberry pi and that’s it! put it on a plug behing the sofa and forget it:
   ![sofa](https://albedo.ch/wp-content/uploads/2024/02/image-13-e1707722130440.png)


## Changing the charging profile for the next day, a few ideas

The raspberry zero is running hidden somewhere in the house… From my desktop computer I change the setpoints profiles (which are in the csv file), then I can simply update it remotely to the pi with the pscp command. The new schedule will be applied from midnight and for all day until I change it again.

After a few days of test, I see that the first setpoints profiles were nice for good weather, but for cloudy days another programm should be used. In the example below some power was injected in the grid in the morning but it should better have been charge to the battery because during the afternoon the solar is not sufficient and the battery was not filled:

![bad weather](https://albedo.ch/wp-content/uploads/2024/02/image-6.png)



I simply made two typical days profiles, one for nice weather and one for bad weather and I send with pscp the good one the day before. 

Again, that is not perfect but that makes 80% of the job…

### Notes:

- To set up everything in the PI without dedicated screen/keyboard/mouse: use ssh connection in power shell

- Type powershell in the windows search bar, open it and type `ssh pi@raspberry.local` give your password and you are like if you were in the pi terminal… (or with direct IP adress if there are troubles with dns-hostname.

- To check it is running:
    - check remotely what processes are running with the command `ps -ef | grep python`
    - the result can also be seen the next day on the studer portal on the battery current chart.


