# -*- coding: utf-8 -*-
"""
Created on Wed May  3 17:23:04 2017

@author: Des
this model runs for mutiple scenarios
"""

# import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Portfolio_Defs import All_Yrs, PHD, Nuc_Outages 
from PHES_model_MultiPlant import PumpedHydroPlant

#Set the Capacities for Each Technology
Capacity_file = pd.ExcelFile('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Portfolio_Capacity_Inputs.xlsx')
capacities = Capacity_file.parse('UserInput', skiprows = 0) #Getting the Cap values for the scenarios
Wind_On_Cap = capacities['Wind_On']# get Capacities from Excel file
Wind_Off_Cap = capacities['Wind_Off'] # creates an array for each cap
Sol_Cap = capacities['Solar']  
NG_Cap = capacities['NG'] 
Hydro_Cap =   capacities['Hydro']
Oil_Cap =  capacities['Oil']
Nuc_Cap =  capacities['Nuc']
PHES_Cap =  capacities['PHES']


Pipe_Cap_Orig = 1358070 ##The 2015 estimated MWh/day pipe cap is 1358070 when converted MMcf/month to MWh/day
Pipe_Cap = Pipe_Cap_Orig ##This is used in the model to keep track of the remainag pipeline cap

   
CT = 0.5 #This is a constant
DA = 1.225 #Density of Air (kg/m^3)
ORDA = 17671.0 # the rotor disk area (m^2) of a 6 MW turbine for offshore
CR = 0.44704 #The conversion from mph to m/s
Cp = 0.4 # The power coeficient picked this arbitrarilty
CpMax = 16.0/27.0 # This is the Betz Limit  CpMax = 0.5926 
ARD = 12469.0 #(m^2) this is Rotor Disk Area of 5 MW wind turbine
PRC = 0.75 #Perfomrance Ratio
ART = 9290.34 #Area for 1 MW Farm (m^2)
PCY = 0.15 #Percent Yield 
Wind_On_Hub = 90 # units for hub and meaured heights are in meters
Wind_On_m = 14
Wind_Off_Hub = 150
Wind_Off_m = 24.8
Shear_Co_On = 0.15 ##assume this shear coefficient for airport because smooth level, grass covered. 
Shear_Co_Off = 0.1 ### for open water 

PHES_Energy_Consumed = [] 
PHES_Energy = []
W_On_Energy = []
W_Off_Energy = []
Sol_Energy = []
NG_Energy = []
Hydro_Energy = []
Oil_Energy = []
Nuc_Energy = []
PHES_Pow_Consumed = []
PHES_Pow = []
W_On_Pow = []
W_Off_Pow =[]
Sol_Pow = []
NG_Pow = []
Hydro_Pow = []
Oil_Pow = []
Nuc_Pow = []
PHES_CF = []
W_CF = []
W_Off_CF = []
Sol_CF = []
NG_CF = []
Hydro_CF = []
Oil_CF = []
Nuc_CF = []
ENS_Tot = []
Risk = []
ENS_Warning = 0 #So if >1 the know we had ENS>0
PH_Start = [12,24,36,48,60] #The Starting section of the heating demand arrays for the different years
Nuc_Out_Start = [73,61,49,37,25]
sPHES_Energy = []
sW_On_Energy = []
sW_Off_Energy = []
sSol_Energy = []
sNG_Energy = []
sHydro_Energy = []
sOil_Energy = []
sNuc_Energy = []
sENS = []
sPHES_CF = []
sW_On_CF = []
sW_Off_CF = []
sSol_CF = []
sNG_CF = []
sHydro_CF = []
sOil_CF = []
sNuc_CF = []

Num_PHES_Plants = []

scenario = 0 #Will use this to increment through the capacity scenarios
while scenario < len(Wind_On_Cap):
    '''starting the model for historical data'''
    print('scenario is : ', scenario)
    yr_num = 0 
    
    if(np.mod(PHES_Cap[scenario], 1150)== 0): #Calculate the number of PHES plants to use. np.mod is the modulus operator. Ex: 5%2 = 1; or 4%2 = 0. (Calculates remainder)
        Num_PHES_Plants.append(PHES_Cap[scenario]/1150) #Divide the PHES capacity by 1150 to get number of plants, 1 plant = 1150 MW generation capacity
    else:
        Num_PHES_Plants.append(np.floor(PHES_Cap[scenario]/1150)+1) #If the user defined capacity isnt perfectly divisiable by 1150, round up. (np.floor rounds a decimal down to the nearest integer. Ex: floor(3.5) = 3
        PHES_Capacity = 1150*Num_PHES_Plants[scenario] #Change the PHES_Cap to the rounded up capacity
    
    
    NOWT = Wind_Off_Cap[scenario]/6.0 #Define the capacity by 6 MW to get the number of 6 MW wind turbines
    NWT = Wind_On_Cap[scenario]/5.0 #Number of 5 MW onshore wind turbines
    NSP = Sol_Cap[scenario]/1.0 #Number of 1MW Solar farms 
    W_On_Energy = []
    W_Off_Energy = []
    Sol_Energy = []
    NG_Energy = []
    Hydro_Energy = []
    Oil_Energy = []
    Nuc_Energy = []
    W_On_Pow = []
    W_Off_Pow =[]
    Sol_Pow = []
    NG_Pow = []
    Hydro_Pow = []
    Oil_Pow = []
    Nuc_Pow = []
    W_CF = []
    W_Off_CF = []
    Sol_CF = []
    NG_CF = []
    Hydro_CF = []
    Oil_CF = []
    Nuc_CF = []
    ENS_Tot = []
    Risk = []
    ENS_Warning = 0 #So if >1 the know we had ENS>0
    PH_Start = [12,24,36,48,60] #The Starting section of the heating demand arrays for the different years
    Nuc_Out_Start = [73,61,49,37,25]
    
    
    
    while yr_num < 2: #5 because counting starts at 0 and only have the following years: 2011, 2012, 2013, 2014, 2015  
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
        Available_Cap = np.zeros(len(Demand)-1)
        Available_Cap_Avg = np.zeros(len(Demand)-1)
        PHES_Demand = np.zeros(len(Demand)-1)
        PHES_Demand_Consumed = np.zeros(len(Demand)-1)
        Nuc_Demand = np.zeros(len(Demand)-1) #Setting up an empty matrix of all zeros to start initial energy allocation
        W_Demand = np.zeros(len(Demand)-1)
        W_Off_Demand = np.zeros(len(Demand)-1)
        Sol_Demand = np.zeros(len(Demand)-1)
        Hydro_Demand = np.zeros(len(Demand)-1)
        NG_Demand = np.zeros(len(Demand)-1)
        Oil_Demand = np.zeros(len(Demand)-1)
        ENS = np.zeros(len(Demand)-1) #Electricity not supplied 
        Risk_Check = np.zeros(len(Demand)-1) #Risk Check
        #Running Average of Demand used in PHES model
        Running_Average_AC = 0; #Can be set to start at any value. Starting at 0 means it will take a while to rise
    
        #PHES operating mode
        PHES_State = 0; #Starts in standby
    
        #PHES reservoir water level
        PHES_Water_Lvl = 285.9 #Can be started at any value 285.9 is the minimum water level
    
        hour_counter = 0 ## Counts the hours in a day for the NG pipline 
        for k in range (0,len(Demand)-1): #Have to do minus 1 because starting at zero 
            #Calculations for Available Capacity
            NG_Limit = np.minimum(NG_Cap[scenario], Pipe_Cap-Pipe_Heat[k]) #the np.min can only have two values in it. So would need to use 2 arrays
            Available_Cap[k] = W_Tot[k] + W_Off_MWh[k] + Sol_Tot[k] + NG_Limit + Hydro_Cap[scenario] + Oil_Cap[scenario] + (Nuc_Cap[scenario]*Nuc_Out[k]) - Demand[k]

            Nuc_Demand[k] = np.minimum(Demand[k],Nuc_Cap[scenario]*Nuc_Out[k]) #Nuclear allocated first 
            New_D = Demand[k] - Nuc_Demand[k] #New_D captures how much demand is left
        
            Sol_Demand[k] = np.minimum(New_D,Sol_Tot[k]) #Solar allocated 2nd
            New_D = New_D - Sol_Demand[k]
            
            W_Demand[k] = np.minimum(New_D, W_Tot[k]) #On shore wind allocation
            New_D = New_D - W_Demand[k]
        
            W_Off_Demand[k] = np.minimum(New_D, W_Off_MWh[k]) #On shore wind allocation
            New_D = New_D -  W_Off_Demand[k]

            #########
            ##Insert Pumped Hydro Here
            Renewable_Generation = Nuc_Demand[k] + Sol_Demand[k] + W_Demand[k] + W_Off_Demand[k] #Available renewable generation for current hour   
            Renewables_Dispatched = Nuc_Cap[scenario]*Nuc_Out[k] + Sol_Tot[k] + W_Tot[k] + W_Off_MWh[k] #Rennewable energy dispatched to meet grid demand for current hour
            Surplus_RE = Renewable_Generation - Renewables_Dispatched #The surplus of renewable generation for current hour, always 0 or greater
        
            #Call the PHES model, use the inputs and outputs defined at top of model file
            PHES_State, PHES_Demand[k],  PHES_Demand_Consumed[k], PHES_Water_Lvl, Running_Average_AC = PumpedHydroPlant(Num_PHES_Plants[scenario], Available_Cap[k], Running_Average_AC,Surplus_RE, New_D, PHES_Water_Lvl, scenario)
            Available_Cap_Avg[k] = Running_Average_AC #Save new Avaible capacity running average
            New_D = New_D - PHES_Demand[k] + PHES_Demand_Consumed[k] #Calculte the new Demand remaining
        
            #Check if renewables need to dispatch any surplus generation
            Extra_Sol_Demand = np.minimum(New_D, (Sol_Tot[k] - Sol_Demand[k])) #Check if there was surplus solar generation and new demand to be filled
            Sol_Demand[k] += Extra_Sol_Demand #Add surplus solar demand to demand array if used
            New_D -= Extra_Sol_Demand #Dispatch surplus solar if there is demand to be filled
        
            Extra_W_Demand = np.minimum(New_D, (W_Tot[k] - W_Demand[k])) #Check if there was surplus wind generation and new demand to be filled
            W_Demand[k] += Extra_W_Demand #Add surplus wind demand to demand array if used
            New_D -= Extra_W_Demand #Dispatch surplus wind generation if there is demand to be filled
        
            Extra_W_Off_Demand = np.minimum(New_D, (W_Off_MWh[k] - W_Off_Demand[k])) #Check if there was surplus offshore wind generation and new demand to be filled
            W_Off_Demand[k] += Extra_W_Off_Demand #Add surplus offshore wind demand to demand array if used
            New_D -= Extra_W_Off_Demand #Dispatch surplus offshore wind generation if there is demand to be filled
            #############
        
            NG_D1 = np.minimum(New_D*0.875,NG_Limit) # First round of NG allocation
            '''Need to add pipeline cap above'''
    
            Hydro_D1 = np.minimum(New_D*0.125,Hydro_Cap[scenario]) # First round of NG allocation
            New_D = New_D - NG_D1 - Hydro_D1 #After first round of NG and Hydro allocation
        
            Oil_D1 = np.minimum(New_D,Oil_Cap[scenario]) if (NG_D1 - Pipe_Cap-Pipe_Heat[k] ==0) else 0 #Pipeline Cap Check
            New_D = New_D - Oil_D1
        
            Hydro_D2 = np.minimum(New_D,Hydro_Cap[scenario]-Hydro_D1) #Second round of hydro
            New_D = New_D - Hydro_D2
            NG_D2 = np.minimum(New_D,NG_Limit-NG_D1)  #Second round of NG
            '''need to add pipeline'''
            New_D = New_D - NG_D2
        
            Oil_D2 = np.minimum(New_D,Oil_Cap[scenario]-Oil_D1) #Second round of oil
            New_D = New_D - Oil_D2
    
        
            NG_Demand[k] = NG_D1 + NG_D2
            Hydro_Demand[k] = Hydro_D1 + Hydro_D2
            Oil_Demand[k] = Oil_D1 + Oil_D2
            ENS [k] = New_D
        
            if hour_counter < 24:  ### hour counter to count the days for the pipeline cap
                Pipe_Cap -= NG_Demand[k]
                hour_counter += 1
            elif hour_counter == 24:
                Pipe_Cap = Pipe_Cap_Orig
                hour_counter = 0
            
            '''The below risk check only looks at dispatchable technologies'''
            Risk_Num = (NG_Cap[scenario]-NG_Demand[k]) + (Hydro_Cap[scenario]-Hydro_Demand[k]) + \
                        (Oil_Cap[scenario]-Oil_Demand[k]) 
                        #The \ just makes the above more readable. It is like a continue
            Risk_Den = NG_Cap[scenario] + Hydro_Cap[scenario] + Oil_Cap[scenario]
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
            Risk_Check[k] =Risk_Num/Risk_Den
            #Thinking maybe I should use total wind and solar produced, instead of Solar Cap??    
        
        '''Reliability'''
        ENS_Tot.append(sum(ENS))
        Risk.append(min(Risk_Check)) #Zero meansno risk here. 
           
        '''Energy Produced for the year''' 
        PHES_Energy_Consumed.append(sum(PHES_Demand_Consumed))
        PHES_Energy.append(sum(PHES_Demand))      
        W_On_Energy.append(sum(W_Demand))
        W_Off_Energy.append(sum(W_Off_Demand))
        Sol_Energy.append(sum(Sol_Demand))
        NG_Energy.append(sum(NG_Demand))
        Hydro_Energy.append(sum(Hydro_Demand))
        Oil_Energy.append(sum(Oil_Demand))
        Nuc_Energy.append(sum(Nuc_Demand))
        
        '''Power for the year'''    #hours in year = len(Demand) . Use this because some data missing
        PHES_Pow_Consumed.append(PHES_Energy_Consumed[yr_num]/(len(Demand)))
        PHES_Pow.append(PHES_Energy[yr_num]/(len(Demand)))
        W_On_Pow.append(W_On_Energy[yr_num] /(len(Demand)))  
        W_Off_Pow.append(W_Off_Energy[yr_num] /(len(Demand)))
        Sol_Pow.append(Sol_Energy[yr_num] /(len(Demand)))
        NG_Pow.append(NG_Energy[yr_num] /(len(Demand)))
        Hydro_Pow.append(Hydro_Energy[yr_num] /(len(Demand)))
        Oil_Pow.append(Oil_Energy[yr_num] /(len(Demand)))
        Nuc_Pow.append(Nuc_Energy[yr_num] /(len(Demand)))
        
        '''Capacity Factors'''
        PHES_CF.append(PHES_Pow[yr_num]/PHES_Capacity)
        W_CF.append(W_On_Pow[yr_num]  / Wind_On_Cap[scenario])
        W_Off_CF.append(W_Off_Pow[yr_num]  /Wind_Off_Cap[scenario])
        Sol_CF.append(Sol_Pow[yr_num]  / Sol_Cap[scenario] )
        NG_CF.append(NG_Pow[yr_num] /NG_Cap[scenario])
        Hydro_CF.append( Hydro_Pow[yr_num]  / Hydro_Cap[scenario])
        Oil_CF.append(Oil_Pow[yr_num]  / Oil_Cap[scenario])
        Nuc_CF.append(Nuc_Pow[yr_num] /Nuc_Cap[scenario])
        yr_num +=1
        print('year number is %d' %yr_num)
    
    print('max ENS for scenario ', scenario, 'is: ', max(ENS_Tot))   

    ##Scenario Results##
    sPHES_Energy.append(np.average(PHES_Energy))
    sW_On_Energy.append(np.average(W_On_Energy)) #The small s means scenario
    sW_Off_Energy.append(np.average (W_Off_Energy))
    sSol_Energy.append(np.average (Sol_Energy))
    sNG_Energy.append(np.average (NG_Energy))
    sHydro_Energy.append(np.average (Hydro_Energy))
    sOil_Energy.append(np.average (Oil_Energy))
    sNuc_Energy.append(np.average (Nuc_Energy))

    sPHES_CF.append(np.average(PHES_CF))
    sW_On_CF.append(np.average(W_CF)) #The small s means scenario
    sW_Off_CF.append(np.average (W_Off_CF))
    sSol_CF.append(np.average (Sol_CF))
    sNG_CF.append(np.average (NG_CF))
    sHydro_CF.append(np.average (Hydro_CF))
    sOil_CF.append(np.average (Oil_CF))
    sNuc_CF.append(np.average (Nuc_CF))
    sENS.append(max(ENS_Tot))

    scenario += 1    
'''Create  Dataframe to display all of the results in a table format'''
result_data_energy = {'Scenario': ['Base','High_Off','Med_Off','No_Nuc','Favor_Nuc'],
        'PHES_MWh':[sPHES_Energy[s] for s in range(0,scenario)],
        'On_Wi_MWh':[sW_On_Energy[s] for s in range(0,scenario)],
        'Off_Wi_MWh' :[sW_Off_Energy[s] for s in range(0,scenario)],
        'Sol_MWh' : [sSol_Energy[s] for s in range(0,scenario)],
        'NG_MWh': [sNG_Energy[s] for s in range(0,scenario)],
        'Hydro_MWh': [sHydro_Energy[s] for s in range(0,scenario)],                      
        'Oil_MWh': [sOil_Energy[s] for s in range(0,scenario)],
        'Nuc_MWh':[sNuc_Energy[s] for s in range(0,scenario)],
        'On_Wi_CF':[sW_On_CF[s] for s in range(0,scenario)],
        'Off_Wi_CF' :[sW_Off_CF[s] for s in range(0,scenario)],
        'Sol_CF' : [sSol_CF[s] for s in range(0,scenario)],
        'NG_CF': [sNG_CF[s] for s in range(0,scenario)],
        'Hydro_CF': [sHydro_CF[s] for s in range(0,scenario)],
        'Oil_CF': [sOil_CF[s] for s in range(0,scenario)],
        'Nuc_CF':[sNuc_CF[s] for s in range(0,scenario)],
        'PHES_CF':[sPHES_CF[s] for s in range(0,scenario)],
        'ENS':[sENS[s] for s in range(scenario)] }
    
Result = pd.DataFrame(result_data_energy, columns = ['Scenario', 'PHES_MWh', 'PHES_CF','On_Wi_MWh','Off_Wi_MWh','Sol_MWh','NG_MWh','Hydro_MWh','Oil_MWh','Nuc_MWh','On_Wi_CF','Off_Wi_CF','Sol_CF','NG_CF','Hydro_CF','Oil_CF','Nuc_CF','ENS'])#Created data frame using pandas
print('The Results for the Years in study are as follows:')
print(Result)
writer = pd.ExcelWriter('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Results_Port_12_17.xlsx')
Result.to_excel(writer, 'Sheet1')
writer.save()

print('done done doooonnnneee')
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
#colors = ["#45AE84", "#696FDA", "#ECB427", "#D63B59", "#596BE2", "#EB8076", "#572615", "#E13F29"]
#
#print('The Energy Usage:')
#plt.pie(
#    # using data from Results_15 dataframe
#    Result_15['Total_Energy_MWh'],
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





