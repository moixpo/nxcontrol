#############
#MODBUS_TCP_read_of_next3_status.py
#
#Example of use of MODBUS TCP to read and display the state of the next3
#Basically I want to know from my next3 what happens now and a summary of yesterday and the whole life of it with a sankey chart.
#Note that the complex sankey chart can be tricky to adjust to have a nice picture.

#february 2023
#Moix P-O
#Albedo Engineering

#forked from the example ex_tcp_read_param.py provided by Studer on github https://github.com/studer-innotec/next-modbus
###################


# First check the version compatibility, then read the serial number, the modbus tcp port and earthing
# scheme relay status.
# Run this example within the 'examples/' folder using 'python ex_tcp_read_param.py' from a CLI after installing
# nxmodbus package with 'pip install nxmodbus'

import sys
import os
import time
from datetime import datetime 
#import pyModbusTCP
import nxmodbus
sys.path.append(os.path.abspath('..'))
from nxmodbus.client_tcp import NextModbusTcp
from nxmodbus.proptypes import PropType

#from PIL import Image
#from sankey_for_nx3 import build_sankey_figure_for_hybridsolar,build_pie_autarky,build_simplified_sankey_autarky_figure


#####################
#initialisation
ADDRESS_OFFSET = 0                                      # the modbus address offset as set inside the Next system
INSTANCE = 0                                            # The instance of the requested device
#SERVER_HOST = "192.168.51.166"        #with UZ batteries           # ipv4 address of nx-interface
SERVER_HOST = "192.168.51.172"        #meeting room     # ipv4 address of nx-interface
SERVER_HOST = "192.168.51.99"        #with cegasa battery  # ipv4 address of nx-interface
SERVER_HOST = "192.168.1.109"        #at home          # ipv4 address of nx-interface
SERVER_HOST = "192.168.1.115"        #at home          # ipv4 address of nx-interface

SERVER_PORT = 502                                       # listening port of nx-interface


#################
#To adjust
PRICE_OF_GRID_ELECTRICITY=0.27      #CHF, price of 2023
PRICE_OF_SOLAR_SOLD_TO_GRID=0.16    #CHF, price of 2023
ELECTRICITY_CO2_INTENSITY= 47 #gCO2/kWh for Switzerland, EU mix: 295gCO2/kWh https://ourworldindata.org/grapher/carbon-intensity-electricity 
#################



if __name__ == "__main__":

    nextModbus = NextModbusTcp(SERVER_HOST, SERVER_PORT, ADDRESS_OFFSET, False)
    
    # check the version
    if not nextModbus.check_version():
        print("WARNING : The Object model version is not correct")

    # Read the serial number
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_nextgateway + INSTANCE,
                                            nextModbus.addresses.nextgateway_idcard_serialnumber,
                                            PropType.STRING,
                                            8)
    print('Serial number:', read_value)

    # # Read the modbus TCP port used by the TCP modbus server
    # read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_nextgateway + INSTANCE,
    #                                         nextModbus.addresses.nextgateway_modbus_modbustcpport,
    #                                         PropType.UINT)
    # print('Modbus TCP port:', read_value)

    # # Read the Earthing relay status
    # read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
    #                                         nextModbus.addresses.system_earthingscheme_relayisclosed,
    #                                         PropType.BOOL)
    # print('Earthing scheme relay status:', read_value)
    
    
    
    
    print('\n \n ############################### \n #### LIVE VALUES \n')   
    # Read the battery voltage
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_battery_voltage,
                                            PropType.FLOAT)
    
    print('Battery Voltage:', read_value, ' Volts')
    
    # Read the battery SOC
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_batterycommon_socinpercent,
                                            PropType.FLOAT)
    print('Battery SOC:', read_value, ' %')
    
    
    
    
    # Read the battery SOC for grid feeding
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_battery_socforgridfeedinginpercent,
                                            PropType.FLOAT)
    print('Battery SOC for grid feeding:', read_value, ' % target')
    
    
    
    # Read the battery Temperature (BMS of battery with lithium battery)
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_battery_temperature,
                                            PropType.FLOAT)
    print('Battery BMS Temperature:', read_value, ' °C')
    
    
    # Read the  Temperature semsor
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_next3,
                                            nextModbus.addresses.next3_batterycontributor_temperature,
                                            PropType.FLOAT)
    print('Sensor Temperature:', read_value, ' °C')
    
    
    
    
    
    
    
    
    
    ##########
    # Instantaneous power fluxes
    
    # Read the battery power
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_batterycommonall_chargingpower,
                                            PropType.FLOAT)
       
    
    print('Battery Power:', read_value, '  [W]')
    if read_value >=0.0:
        power_chargebatt=read_value
        power_dischargebatt=0.0
    else:
        power_chargebatt=0.0
        power_dischargebatt=read_value
    
    # Read the total solar production
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_solarcommonall_power,
                                            PropType.FLOAT)
    print('Solar Power:', read_value, ' [W]')
    produced_power_solar=read_value

    # Read the total grid power
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_systemtotal_acsourcepower,
                                            PropType.FLOAT)
    print('Grid Power:', read_value, ' [W]')    
    power_grid=read_value

    # Read the total consummer power
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_systemtotal_consummerspower,
                                            PropType.FLOAT)
    print('Consummer Power:', read_value, ' [W]')   
    consummed_power_loads=read_value



    # Read the total AC-Load power
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_acloadtriphasemeasure_totalactivepower,
                                            PropType.FLOAT)
    print('AC-Load Power:', read_value, ' [W]')   
    consummed_power_ACLOADS=read_value


    # Read the total AC-FLEX power
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_allflexloadstriphaseacmeasure_totalactivepower,
                                            PropType.FLOAT)
    print('AC-FLEX Load Power:', read_value, ' [W]')   
    consummed_power_ACFLEX=read_value


    timestamp_powers = time.time()
    print("\nTimestamp:", timestamp_powers) 
    date_time = datetime.fromtimestamp(timestamp_powers)
    print("The date and time is:", date_time)
    str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
    print("The date and time is:", str_date_time)
    

    # efficiency=battery_power/(grid_power-consummer_power)
    # print('Charging efficiency:', efficiency*100, ' [%]')   
    
    if power_grid < 0.0:
        #case with power injected back to the grid
        grid_consumption_power=0.0   
        grid_injection_power=-power_grid
    else:
        grid_consumption_power=power_grid   
        grid_injection_power=0.0
        

    #build_simplified_sankey_autarky_figure(consummed_power_loads,grid_consumption_power, abs(power_dischargebatt),' W', "NOW")



    print('\n \n ############################### \n #### YESTERDAY\n')   
    time.sleep(1.0)     #for the limit of 20 reads/sec



    ###############################
    #Yesterday


    # Read the AC-LOAD consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_acloadtriphasemeasure_previousdayconsumedenergy,
                                            PropType.FLOAT)
    print('AC-Loads last day energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_consummed_energy_ACLOADS=read_value/1000
   
    
  
    # Read the AC-FLEX last day consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_allflexloadstriphaseacmeasure_previousdayconsumedenergy,
                                            PropType.FLOAT)
    print('AC-FLEX last day energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_consummed_energy_ACFLEX=read_value/1000
   
    
   
       # Read the AC-source last day produced energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_acsource,
                                            nextModbus.addresses.acsource_triphasemeasure_previousdayproducedenergy,
                                            PropType.FLOAT)
    print('AC-source last day produced energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_produced_energy_ACSOURCE=read_value/1000
   
    
    
    # Read the AC-source last day consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_acsource,
                                            nextModbus.addresses.acsource_triphasemeasure_previousdayconsumedenergy,
                                            PropType.FLOAT)
    print('AC-source last day consummed energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_consummed_energy_ACSOURCE=read_value/1000
   
    
         
    # Read the last day solar total consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_solarcommonall_previousdayenergy,
                                            PropType.FLOAT)
    print('Solar last day energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_produced_energy_Solar=read_value/1000
   
    
    
    # Read the last day battery charged energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_batterycommonall_previousdaychargingenergy,
                                            PropType.FLOAT)
    print('Battery last day charged energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_battery_charged_energy=read_value/1000
   
  
    
    # Read the last day battery discharged energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_batterycommonall_previousdaydischargingenergy,
                                            PropType.FLOAT)
    print('Battery last day discharged energy :', round(read_value/1000, 2), ' [kWh]')   
    previousday_battery_discharged_energy=read_value/1000
   
 
    print(' \n Energy sold to the grid yesterday: ',  str(round(PRICE_OF_SOLAR_SOLD_TO_GRID*previousday_produced_energy_ACSOURCE, 2)),  ' CHF')   
    print(' Energy bought from the grid yesterday: ',  str(round(PRICE_OF_GRID_ELECTRICITY*previousday_consummed_energy_ACSOURCE, 2)),  ' CHF')   
    print(' Savings with Autarky',  str(round(PRICE_OF_GRID_ELECTRICITY*(previousday_consummed_energy_ACLOADS+previousday_consummed_energy_ACFLEX-previousday_consummed_energy_ACSOURCE), 2)),  ' CHF')   
    print(' TOTAL: ',  str(round(PRICE_OF_GRID_ELECTRICITY*(previousday_consummed_energy_ACLOADS+previousday_consummed_energy_ACFLEX-previousday_consummed_energy_ACSOURCE)+PRICE_OF_SOLAR_SOLD_TO_GRID*previousday_produced_energy_ACSOURCE, 2)),  ' CHF')   
    



    
    # build_sankey_figure_for_hybridsolar(previousday_produced_energy_Solar,
    #                                 previousday_produced_energy_ACSOURCE,
    #                                 previousday_consummed_energy_ACSOURCE, 
    #                                 previousday_battery_charged_energy, 
    #                                 -previousday_battery_discharged_energy,  
    #                                 previousday_consummed_energy_ACLOADS, 
    #                                 previousday_consummed_energy_ACFLEX, 
    #                                 ' kWh')
    
    # build_pie_autarky(previousday_consummed_energy_ACLOADS+previousday_consummed_energy_ACFLEX,
    #                   previousday_consummed_energy_ACSOURCE,
    #                   ' kWh',
    #                   "Summary of previous day")
    
    



    print('\n \n ############################### \n #### ALL LIFE OF NX3 \n')   
    time.sleep(1.0) #for the limit of 20 reads/sec

    #####################
    #Total energy
    

    
    # Read the total battery charged energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_battery,
                                            nextModbus.addresses.battery_batterycommon_totalchargingenergy,
                                            PropType.FLOAT64)
    print('Battery total charged energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_battery_charged_energy=read_value/1000
   
  
    
    # Read the total battery discharged energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_batterycommonall_totaldischargingenergy, 
                                            PropType.FLOAT64)
    print('Battery total discharged energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_battery_discharged_energy=read_value/1000
    
    
    # Read the AC-source total consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_acsource,
                                            nextModbus.addresses.acsource_triphasemeasure_totalconsumedenergy,
                                            PropType.FLOAT64)
    print('AC-source total consummed energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_consummed_energy_ACSOURCE=read_value/1000
    
   
    
    # Read the AC-source total produced energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_acsource,
                                            nextModbus.addresses.acsource_triphasemeasure_totalproducedenergy,
                                            PropType.FLOAT64)
    print('AC-source total produced energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_produced_energy_ACSOURCE=read_value/1000
   
    
    
    # Read the total solar total consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_solarcommonall_totalenergy,
                                            PropType.FLOAT64)
    print('Solar total energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_produced_energy_Solar=read_value/1000
   
    
    
    # Read the AC-LOAD total consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_acloadtriphasemeasure_totalconsumedenergy,
                                            PropType.FLOAT64)
    print('AC-Loads total energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_consummed_energy_ACLOADS=read_value/1000
   
    
  
    # Read the AC-FLEX total consummed energy
    read_value = nextModbus.read_parameter( nextModbus.addresses.device_address_system,
                                            nextModbus.addresses.system_allflexloadstriphaseacmeasure_totalconsumedenergy,
                                            PropType.FLOAT64)
    print('AC-FLEX total energy :', round(read_value/1000, 2), ' [kWh]')   
    lifetime_consummed_energy_ACFLEX=read_value/1000
   
    
   

    print('\n Total energy sold to the grid: ',   str(round(PRICE_OF_SOLAR_SOLD_TO_GRID*lifetime_produced_energy_ACSOURCE, 2)),  ' CHF')   
    print(' Total energy bought from the grid: ',   str(round(PRICE_OF_GRID_ELECTRICITY*lifetime_consummed_energy_ACSOURCE, 2)),  ' CHF')   
    print(' Total savings with Autarky: ',   str(round(PRICE_OF_GRID_ELECTRICITY*(lifetime_consummed_energy_ACLOADS+lifetime_consummed_energy_ACFLEX-lifetime_consummed_energy_ACSOURCE), 2)),  ' CHF')   
    print(' TOTAL: ',   str(round(PRICE_OF_GRID_ELECTRICITY*(lifetime_consummed_energy_ACLOADS+lifetime_consummed_energy_ACFLEX-lifetime_consummed_energy_ACSOURCE)
                                  +PRICE_OF_SOLAR_SOLD_TO_GRID*lifetime_produced_energy_ACSOURCE,
                                  2)),  ' CHF')   

    print('\n CO2 saved with autarky and grid-feeding',  str(round(ELECTRICITY_CO2_INTENSITY*(lifetime_consummed_energy_ACLOADS+lifetime_consummed_energy_ACFLEX-lifetime_consummed_energy_ACSOURCE+lifetime_produced_energy_ACSOURCE)/1000.0, 2)),  '  kg of CO2')   
    
         


    
    # build_sankey_figure_for_hybridsolar(lifetime_produced_energy_Solar,
    #                                 lifetime_produced_energy_ACSOURCE,
    #                                 lifetime_consummed_energy_ACSOURCE, 
    #                                 lifetime_battery_charged_energy, 
    #                                 -lifetime_battery_discharged_energy,  
    #                                 lifetime_consummed_energy_ACLOADS, 
    #                                 lifetime_consummed_energy_ACFLEX, 
    #                                 ' kWh')


   
    # build_pie_autarky(lifetime_consummed_energy_ACLOADS+lifetime_consummed_energy_ACFLEX,
    #                   lifetime_consummed_energy_ACSOURCE,
    #                   ' kWh',
    #                   "Over the life of the installation")



        
        