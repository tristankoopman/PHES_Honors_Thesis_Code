# -*- coding: utf-8 -*-
"""
Created on Wed May  3 17:23:04 2017

@author: Des
"""

# import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Portfolio_Defs import All_Yrs, PHD, Nuc_Outages 
from PHES_model import PumpedHydroPlant
from operator import sub

#Set the Capacities for Each Technology
Wind_On_Cap = 5000.0 #Original values for ref 97 MW
Wind_Off_Cap = 5000.0 #Original : 0 MW, have to do 1 MW so model will run
Sol_Cap = 5000.0   # 50MW
NG_Cap = 25190.0   # 15190 MW
#Hydro_Cap = 3355.0 # 3355 MW
Oil_Cap = 8000.0   # 7015 MW
Nuc_Cap = 4000.0   # 4300 MW
PHES_Cap = 1000.0  # 1150 MW

Pipe_Cap_Orig = 1358070 ##The 2015 estimated MWh/day pipe cap is 1358070 when converted MMcf/month to MWh/day
Pipe_Cap = Pipe_Cap_Orig ##This is used in the model to keep track of the remainag pipeline cap

   
CT = 0.5 #This is a constant
DA = 1.225 #Density of Air (kg/m^3)
ORDA = 17671.0 # the rotor disk area (m^2) of a 6 MW turbine for offshore
CR = 0.44704 #The conversion from mph to m/s
Cp = 0.4 # The power coeficient picked this arbitrarilty
CpMax = 16.0/27.0 # This is the Betz Limit  CpMax = 0.5926 
NOWT = Wind_Off_Cap/6.0 #Define the capacity by 6 MW to get the number of 6 MW wind turbines
NWT = Wind_On_Cap/5.0 #Number of 5 MW onshore wind turbines
NSP = Sol_Cap/1.0 #Number of 1MW Solar farms 
ARD = 12469.0 #(m^2) this is Rotor Disk Area of 5 MW wind turbine
PRC = 0.75 #Perfomrance Ratio
ART = 9290.34 #Area for 1 MW Farm (m^2)
PCY = 0.15 #Percent Yield 
Wind_On_Hub = 70 # units for hub and meaured heights are in meters
Wind_On_m = 14
Wind_Off_Hub = 150
Wind_Off_m = 24.8
Shear_Co_On = 0.15 ##assume this shear coefficient for airport because smooth level, grass covered. 
Shear_Co_Off = 0.1 ### for open water 

PHES_Energy_Pumped = []
PHES_Energy = []
W_On_Energy = []
W_Off_Energy = []
Sol_Energy = []
NG_Energy = []
#Hydro_Energy = []
Oil_Energy = []
Nuc_Energy = []
PHES_Pow = []
W_On_Pow = []
W_Off_Pow =[]
Sol_Pow = []
NG_Pow = []
#Hydro_Pow = []
Oil_Pow = []
Nuc_Pow = []
PHES_CF = []
W_CF = []
W_Off_CF = []
Sol_CF = []
NG_CF = []
#Hydro_CF = []
Oil_CF = []
Nuc_CF = []
ENS_Tot = []
Risk = []
ENS_Warning = 0 #So if >1 the know we had ENS>0
PH_Start = [12,24,36,48,60] #The Starting section of the heating demand arrays for the different years
Nuc_Out_Start = [73,61,49,37,25]

'''starting the model for historical data'''
yr_num = 0

while yr_num < 1: #5 because conting starts at 0 and only have the following years: 2011, 2012, 2013, 2014, 2015  
    Demand = []
    W_sp1 = []
    W_sp2 = []
    W_sp3 = []
    W_sp4 = []
    Sol_r1 = []
    Sol_r2 = []
    Sol_r3 = []
    Month = []
    
        
    Yr_Data = All_Yrs[yr_num].dropna()
    Demand = Yr_Data['Demand_Project'] #Projected Demand for 2030
    
    ###Onshore wind speeds and conversions
    W_sp_m1 = Yr_Data['W_Mass_Win'] #Wind speed at measured height, will exptrapolate to hub height
    W_sp_m2 = Yr_Data['Boston_Area_Win']
    W_sp_m3 = Yr_Data['Lower_E_Mass_Win']
    
    W_sp1 =  [W_sp_m1[i]*((Wind_On_Hub/Wind_On_m)**Shear_Co_On) for i in range (0, len(W_sp_m1))]#Wind speed data exprapolated to hub height
    W_sp2 = [W_sp_m2[i]*((Wind_On_Hub/Wind_On_m)**Shear_Co_On) for i in range (0, len(W_sp_m2))]
    W_sp3 = [W_sp_m3[i]*((Wind_On_Hub/Wind_On_m)**Shear_Co_On) for i in range (0, len(W_sp_m3))]
    
    ### Off shore wind speeds and conversions
    W_sp_m4 = Yr_Data['Buzzards_Bay_OWin'] #This is offshore wind (wind sp 4)
    W_sp4 = [W_sp_m4[i]*((Wind_Off_Hub/Wind_Off_m)**Shear_Co_Off) for i in range (0, len(W_sp_m4))]#This is offshore wind (wind sp 4)
    
    
    
    Sol_r1 = Yr_Data['W_Mass_Sol'] #Solar Radiation data
    Sol_r2 = Yr_Data['Boston_Area_Sol']
    Sol_r3 = Yr_Data['Lower_E_Mass_Sol']
    Month = Yr_Data['Month']
    
    '''Setting the pipeline capacities'''
    Pipe_Heat = np.zeros(len(Demand)) #Create a zero array then will rewrite below
    Nuc_Out = np.zeros(len(Demand))
    
    
    for m in range(0,len(Month)-1): #Setting pipeline capacities for the year
        if Month[m] == 1:
            Pipe_Heat[m] =PHD[PH_Start[yr_num]] #January 2015 pipeline import capacity in Excel. (Excel sheet is three rows off)
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]] #January 2015 in Nuc Outages is rom 32 which corresponds to array # 25
        if Month[m] == 2:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+1]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-1]
        if Month[m] == 3:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+2]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-2]
        if Month[m] == 4:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+3]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-3]
        if Month[m] == 5:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+4]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-4]
        if Month[m] == 6:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+5]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-5]
        if Month[m] == 7:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+6]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-6]
        if Month[m] == 8:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+7]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-7]
        if Month[m] == 9:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+8]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-8]
        if Month[m] == 10:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+9]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-9]
        if Month[m] == 11:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+10]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-10]
        if Month[m] == 12:
            Pipe_Heat[m] = PHD[PH_Start[yr_num]+11]
            Nuc_Out[m] = Nuc_Outages[Nuc_Out_Start[yr_num]-11]
    
                 
    '''Wind Max power output calc'''
    W_1_MWh = [CT*DA*ARD*((W_sp1[i]*CR)**3)*Cp*NWT*(1/8) for i in range (0, len(W_sp1)-1)] #Max Energy output for wind farm location 1
    W_2_MWh = [CT*DA*ARD*((W_sp2[i]*CR)**3)*Cp*NWT*(6/8) for i in range (0, len(W_sp2)-1)]
    W_3_MWh = [CT*DA*ARD*((W_sp3[i]*CR)**3)*Cp*NWT*(1/8) for i in range (0, len(W_sp3)-1)]
    W_Tot = [(W_1_MWh[i] + W_2_MWh[i] + W_3_MWh[i])/1000000 for i in range (0, len(W_sp1)-1)]
    
    W_Off_MWh = [CT*DA*ORDA*((W_sp4[i]*CR)**3)*Cp*NOWT/1000000 for i in range (0, len(W_sp4)-1)] # Thisis Offshore wind "**" is the exponent
    #W_Off_Tot_15 = sum(W_Off_MWh_15) #Total Energy for the Year
    #W_Off_Power_15 = (W_Off_Tot_15)/(24*365) #Power for the year 
    #W_Off_CF_15 = W_Off_Power_15/Wind_Off_Cap #Capacity factor for offshore wind
    
    '''Solar Power Output Calc'''
    Sol_1_MWh = [(((Sol_r1[i]))*PRC*ART*PCY*NSP/3) for i in range (0, len(Sol_r1)-1)] #Expectd energy for the first solar farm 
    Sol_2_MWh = [(((Sol_r2[i]))*PRC*ART*PCY*NSP/3) for i in range (0, len(Sol_r2)-1)]
    Sol_3_MWh = [(((Sol_r3[i]))*PRC*ART*PCY*NSP/3) for i in range (0, len(Sol_r3)-1)]
    
    Sol_Tot = [(Sol_1_MWh[i] + Sol_2_MWh[i] + Sol_3_MWh[i])/1000000 for i in range (0, len(Sol_r1)-1)] #Total Expected solar energy for each hour in the year
    
    '''Starting the Demand Allocation'''
    #PHES_States = np.zeros(len(Demand)-1)
    PHES_Demand = np.zeros(len(Demand)-1)
    PHES_Pump_Demand = np.zeros(len(Demand)-1)
    Nuc_Demand = np.zeros(len(Demand)-1) #Setting up an empty matrix of all zeros to start initial energy allocation
    W_Demand = np.zeros(len(Demand)-1)
    W_Off_Demand = np.zeros(len(Demand)-1)
    Sol_Demand = np.zeros(len(Demand)-1)
    #Hydro_Demand = np.zeros(len(Demand)-1)
    NG_Demand = np.zeros(len(Demand)-1)
    Oil_Demand = np.zeros(len(Demand)-1)
    ENS = np.zeros(len(Demand)-1) #Electricity not supplied 
    Risk_Check = np.zeros(len(Demand)-1) #Risk Check
    
    #Running Average of Demand used in PHES model
    Running_Average_Demand = 0; #Can be set to start at any value. Starting at 0 means it will take a while to rise
    
    #PHES operating mode
    PHES_State = 0; #Starts in standby
    
    #PHES reservoir water level
    PHES_Stored_Energy = 0 #Can be started at any value 285.9 is the minimum water level
    
    hour_counter = 0 ## Counts the hours in a day for the NG pipline 
    for k in range (0,len(Demand)-1): #Have to do minus 1 because starting at zero 
        Nuc_Demand[k] = np.minimum(Demand[k],Nuc_Cap*Nuc_Out[k]) #Nuclear allocated first 
        New_D = Demand[k] - Nuc_Demand[k] #New_D captures how much demand is left
        
        Sol_Demand[k] = np.minimum(New_D,Sol_Tot[k]) #Solar allocated 2nd
        New_D = New_D - Sol_Demand[k]
        
        W_Demand[k] = np.minimum(New_D, W_Tot[k]) #On shore wind allocation
        New_D = New_D - W_Demand[k]
        
        W_Off_Demand[k] = np.minimum(New_D, W_Off_MWh[k]) #On shore wind allocation
        New_D = New_D -  W_Off_Demand[k]
        
        NG_Limit = np.minimum(NG_Cap, Pipe_Cap-Pipe_Heat[k]) #the np.min can only have two values in it. So would need to use 2 arrays
        
        #########
        ##Insert Pumped Hydro Here
        Renewable_Generation = Nuc_Demand[k] + Sol_Demand[k] + W_Demand[k] + W_Off_Demand[k]        
        Renewables_Dispatched = Nuc_Cap*Nuc_Out[k] + Sol_Tot[k] + W_Tot[k] + W_Off_MWh[k] 
       
        PHES_State, PHES_Demand[k],  PHES_Pump_Demand[k], PHES_Stored_Energy, Running_Average_Demand = PumpedHydroPlant(PHES_Cap, Demand[k], Running_Average_Demand, Renewable_Generation, Renewables_Dispatched, New_D, NG_Limit, PHES_State, PHES_Stored_Energy)
        
        New_D = New_D - PHES_Demand[k] + PHES_Pump_Demand[k]
        
        #Check if renewables need to dispatch any surplus generation
        Extra_Sol_Demand = np.minimum(New_D, (Sol_Tot[k] - Sol_Demand[k]))
        Sol_Demand[k] += Extra_Sol_Demand
        New_D -= Extra_Sol_Demand
        
        Extra_W_Demand = np.minimum(New_D, (W_Tot[k] - W_Demand[k]))
        W_Demand[k] += Extra_W_Demand
        New_D -= Extra_W_Demand
        
        Extra_W_Off_Demand = np.minimum(New_D, (W_Off_MWh[k] - W_Off_Demand[k]))
        W_Off_Demand[k] += Extra_W_Off_Demand
        New_D -= Extra_W_Off_Demand
        #########
            
        NG_D1 = np.minimum(New_D*0.875,NG_Limit) # First round of NG allocation
        '''Need to add pipeline cap above'''
    
        #Hydro_D1 = np.minimum(New_D*0.125,Hydro_Cap) # First round of NG allocation
        #New_D = New_D - NG_D1 - Hydro_D1 #After first round of NG and Hydro allocation
        New_D = New_D - NG_D1
        
        Oil_D1 = np.minimum(New_D,Oil_Cap) if (NG_D1 - Pipe_Cap-Pipe_Heat[k] ==0) else 0 #Pipeline Cap Check
        New_D = New_D - Oil_D1
        
        #Hydro_D2 = np.minimum(New_D,Hydro_Cap-Hydro_D1) #Second round of hydro
        #New_D = New_D - Hydro_D2
        NG_D2 = np.minimum(New_D,NG_Limit-NG_D1)  #Second round of NG
        '''need to add pipeline'''
        New_D = New_D - NG_D2
        
        Oil_D2 = np.minimum(New_D,Oil_Cap-Oil_D1) #Second round of oil
        New_D = New_D - Oil_D2
    
        
        NG_Demand[k] = NG_D1 + NG_D2
        #Hydro_Demand[k] = Hydro_D1 + Hydro_D2
        Oil_Demand[k] = Oil_D1 + Oil_D2
        ENS [k] = New_D
        
        if hour_counter < 24:  ### hour counter to count the days for the pipeline cap
            Pipe_Cap -= NG_Demand[k]
            hour_counter += 1
        elif hour_counter == 24:
            Pipe_Cap = Pipe_Cap_Orig
            hour_counter = 0
            
        '''The below risk check only looks at dispatchable technologies'''
        #Risk_Num = (NG_Cap-NG_Demand[k]) + (Hydro_Cap-Hydro_Demand[k]) + \
        #            (Oil_Cap-Oil_Demand[k]) 
                    #The \ just makes the above more readable. It is like a continue
        #Risk_Den = NG_Cap + Hydro_Cap + Oil_Cap
                    #The "\" is a continue
    #   #This risk check looks at all technologies
    #    Risk_Num = (Nuc_Cap-Nuc_Demand_15[k]) + (Sol_Cap-Sol_Demand_15[k]) + \
    #                (Wind_On_Cap-W_Demand_15[k]) + (Wind_Off_Cap-W_Off_Demand_15[k]) + \
    #                (NG_Cap-NG_Demand_15[k]) + (Hydro_Cap-Hydro_Demand_15[k]) + \
    #                (Oil_Cap-Oil_Demand_15[k]) 
    #                #The \ just makes the above more readable. It is like a continue
    #    Risk_Den = Nuc_Cap + Sol_Cap + Wind_On_Cap + Wind_Off_Cap + NG_Cap + Hydro_Cap + \
    #                Oil_Cap
    #                #The "\" is a continue
    #    Risk_Check[k] =Risk_Num/Risk_Den
        #Thinking maybe I should use total wind and solar produced, instead of Solar Cap??    
    
    '''Reliability'''
    ENS_Tot.append(sum(ENS))
    Risk.append(min(Risk_Check)) #Zero meansno risk here. 
    if ENS_Tot[yr_num] > 0:
        print('Energy not supplied')
        print('year: ', yr_num, 'ENS: ',ENS_Tot[yr_num])
        ENS_Warning +=1
        yr_num = 100
    else:
        
        '''PHES_Demand'''
        PHES_Energy_Pumped.append(sum(PHES_Pump_Demand))
        
        
        '''Energy Produced for the year''' 
        PHES_Energy.append(sum(PHES_Demand))   
        W_On_Energy.append(sum(W_Demand))
        W_Off_Energy.append(sum(W_Off_Demand))
        Sol_Energy.append(sum(Sol_Demand))
        NG_Energy.append(sum(NG_Demand))
        #Hydro_Energy.append(sum(Hydro_Demand))
        Oil_Energy.append(sum(Oil_Demand))
        Nuc_Energy.append(sum(Nuc_Demand))
        
        '''Power for the year'''    #hours in year = len(Demand) . Use this because some data missing
        PHES_Pow.append(PHES_Energy[yr_num]/(len(Demand)))
        W_On_Pow.append(W_On_Energy[yr_num] /(len(Demand)))  
        W_Off_Pow.append(W_Off_Energy[yr_num] /(len(Demand)))
        Sol_Pow.append(Sol_Energy[yr_num] /(len(Demand)))
        NG_Pow.append(NG_Energy[yr_num] /(len(Demand)))
        #Hydro_Pow.append(Hydro_Energy[yr_num] /(len(Demand)))
        Oil_Pow.append(Oil_Energy[yr_num] /(len(Demand)))
        Nuc_Pow.append(Nuc_Energy[yr_num] /(len(Demand)))
        
        '''Capacity Factors'''
        PHES_CF.append(PHES_Pow[yr_num]/PHES_Cap)
        W_CF.append(W_On_Pow[yr_num]  / Wind_On_Cap)
        W_Off_CF.append(W_Off_Pow[yr_num]  /Wind_Off_Cap)
        Sol_CF.append(Sol_Pow[yr_num]  / Sol_Cap )
        NG_CF.append(NG_Pow[yr_num] /NG_Cap)
        #Hydro_CF.append( Hydro_Pow[yr_num]  / Hydro_Cap)
        Oil_CF.append(Oil_Pow[yr_num]  / Oil_Cap)
        Nuc_CF.append(Nuc_Pow[yr_num] /Nuc_Cap)
    yr_num +=1
    print('year number is %d' %yr_num)   
    
    
if ENS_Warning == 0:
    '''Create  Dataframe to display all of the results in a table format'''
    result_data = {'Plant_Type': ['Onshore Wind','Off Shore Wind','Solar','NG','Pumped Hydro', 'Oil','Nuclear'],
                   'Capacity_MW':[Wind_On_Cap,Wind_Off_Cap,Sol_Cap,NG_Cap,PHES_Cap,Oil_Cap,Nuc_Cap],
                   'Total_Energy_MWh':[np.average(W_On_Energy), np.average(W_Off_Energy), np.average(Sol_Energy),np.average(NG_Energy), np.average(PHES_Energy), np.average(Oil_Energy),np.average(Nuc_Energy)],
                   'Total_Power_MW':[np.average(W_On_Pow), np.average(W_Off_Pow), np.average(Sol_Pow),np.average(NG_Pow), np.average(PHES_Pow), np.average(Oil_Pow),np.average(Nuc_Pow)],
                   'Capacity_Factor':[np.average(W_CF), np.average(W_Off_CF), np.average(Sol_CF), np.average(NG_CF), np.average(PHES_CF), np.average(Oil_CF),np.average(Nuc_CF)] }
    
    Result = pd.DataFrame(result_data, columns = ['Plant_Type', 'Capacity_MW', 'Total_Energy_MWh', 'Total_Power_MW','Capacity_Factor'])               
        #Created data frame using pandas
    print('The Results for the Years in study are as follows:')
    print(Result)
    print(' ' )
'''
    PHES_Net_Gen = map(sub, PHES_Energy, PHES_Energy_Pumped)
    print('PHES Total Energy MWH: ')
    print(np.average(PHES_Energy))
    print('PHES Total Power MW: ')
    print(np.average(PHES_Pow))
    print('PHES Capacity Factor: ')
    print(np.average(PHES_CF))
    print('The PHES Generation for Pumped Storage by Year in MWh: ') 
    print( '[%s]' % ', '.join(map(str, PHES_Energy)))
    print('The Energy Pumped for Pumped Storage by Year in MWh: ') 
    print( '[%s]' % ', '.join(map(str, PHES_Energy_Pumped)))
    print('The Net Generation for Pumped Storage by Year in MWh: ') 
    print( '[%s]' % ', '.join(map(str, PHES_Net_Gen)))
    print(' ' )
    '''
    #writer = pd.ExcelWriter('C:/Users/Tish/OneDrive/Documents/Papers/Portfolio Paper/Port_Results_10_2_17.xlsx')
    #Result.to_excel(writer, 'Sheet1')
    #writer.save()

#'''Making a pie chart'''
## Create a list of colors (from iWantHue) can get color names from http://tools.medialab.sciences-po.fr/iwanthue/
#colors = ["#45AE84", "#696FDA", "#ECB427", "#D63B59", "#596BE2", "#EB8076", "#572615", "#E13F29"]
#
#print('The Capacity:')
#plt.pie(
#    # using data from Results_15 dataframe 
#    Result_15['Capacity_MW'],
#    # with the labels being plant types
#    labels=Result_15['Plant_Type'],
#    # with no shadows
#    shadow=False,
#    # with colors that defined above. If erase this line it will come up with its own color allocations
#    colors=colors,
#    #Explode would seperate the triangles from each other 
#    explode=(0, 0, 0, 0, 0, 0, 0), # with one slide exploded out use this code: explode=(0, 0, 0, 0, 0.15, 0, 0),
#    # with the start angle at 90%
#    startangle=90,
#    # with the percent listed with zero decimal places 
#    autopct='%.0f%%',
#    )
#
## View the plot drop above
#plt.axis('equal')
#
## View the plot
#plt.tight_layout()
#plt.show()
#
## Create a list of colors (from iWantHue) can get color names from http://tools.medialab.sciences-po.fr/iwanthue/
colors = ["#45AE84", "#696FDA", "#ECB427", "#D63B59", "#596BE2", "#EB8076", "#572615", "#E13F29"]
#
print('The Energy Usage:')
plt.pie(
    # using data from Results_15 dataframe
    Result['Total_Energy_MWh'],
    # with the labels being plant types
    labels=Result['Plant_Type'],
    # with no shadows
    shadow=False,
    # with colors that defined above. If erase this line it will come up with its own color allocations
    colors=colors,
    #Explode would seperate the triangles from each other 
    explode=(0, 0, 0, 0, 0, 0, 0), # with one slide exploded out use this code: explode=(0, 0, 0, 0, 0.15, 0, 0),
    # with the start angle at 90%
    startangle=90,
    # with the percent listed with zero decimal places 
    autopct='%.0f%%',
    )

# View the plot drop above
plt.axis('equal')

# View the plot
plt.tight_layout()
plt.show()