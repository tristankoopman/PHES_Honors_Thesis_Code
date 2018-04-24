"""
Pumped Hydro Simulation
10/23/2017
@author: Tristan
"""

#import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import rain data TBD    

"""   
############################################################################
WHERE THIS FUNCTION FITS INTO THE LARGE PORTFOLIO MODEL

After allocating nuclear, solar, onshore, offshore, and  calculating NG_limit
Then run PumpedHydroPlant function and pass in arguments below:

Demand is demand[k]                                                               , the total grid demand for the current hour
Running_Average                                                                   , the the previous hour's running average
Renew_Gen = Nuc_Demand[k] + Sol_Demand[k] + W_Demand[k] + W_Off_Demand[k]         , the amount of power that can be generated this hour by nuclear and renewables
Renew_Dispatched = Nuc_Cap*Nuc_Out[k] + Sol_Tot[k] + W_Tot[k] + W_Off_MWh[k]      , the amount of power dispatched this hour by nuclear and renewables
Grid_Demand_Left is New_D                                                         , the demand that still needs to be met for this hour after dispatching nuclear and renewables 
NG_Gen is NG_Limit                                                                , the amount of NG power that can be generted this hour
PHES_state                                                                        , the state the hydro plant was in the previous hour: 0 is standby, 1 is pumping, 2 is generating
Water_Lvl                                                                         , the height of the water in the upper reservoir

Will pass out updated hydro variables in the following order
New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average

############################################################################
"""

#Water_Lvl keeps track of the water level in the upper reservoir in m
def PumpedHydroPlant(Demand, Running_Average, Renew_Gen, Renew_Dispatched, Grid_Demand_Left, NG_Gen, PHES_State, Water_Lvl):
    #Set the Capacities for PHES Plant  
    #These variables could be read in from an excel file, allowing different PHES plant parameters to be testsed easily. 
    #Would need to find  a way to recalculate the getVolumeStored and getWaterLevel functions
    Water_Flow_Rate_Gen =  566.337 #((m^3/s) (141.58 (m^3/s) / turbine)
    Water_Flow_Rate_Pump = 430.4 #((m^3/s) (107.6 (m^3/s) / turbine)
    #PHES_Storage_Cap = 15194007 #(m^3) #Might not need this
    PHES_Water_Lvl_Min = 285.9 # m
    PHES_Water_Lvl_Max = 304.95 # m
    Hydraulic_Head = Water_Lvl - 54.864 # m #Calculated from Northfield Data
    
   
    #Constants for Equations
    Water_Density = 1000 #kg/m^3
    Gen_Efficiency = 0.87
    G = 9.8 #gravity (m/s^2)

    #Generating Capacity
    Max_Gen = Water_Density*Water_Flow_Rate_Gen*G*Hydraulic_Head*Gen_Efficiency/1000000 #(MW)
    #Max_Gen_Volume = Water_Flow_Rate_Gen*3600 #(m^3)
    
    #Pumping Capacity
    Max_Pump = Water_Density*Water_Flow_Rate_Pump*G*Hydraulic_Head/1000000 #(MW)
    #Max_Pump_Volume = Water_Flow_Rate_Pump*3600 #(m^3)
    
    #Check if there is a surplus in renewables
    Surplus_Check = 0
    Surplus_Amount = Renew_Gen - Renew_Dispatched
    if( Surplus_Amount > 0):
        Surplus_Check = 1    #There is a surplus of renewable generation
        
    #Running Average
    alpha = 0.13
    Pumping_Threshold = 5 #%
    Generating_Threshold = 5 #%
    New_Average = alpha*Demand + (1-alpha)*Running_Average #Calculate new running average
    
    #Check if pumping or generating thresholds are exceeded
    Gen_Check = 0
    Pump_Check = 0
    if((Demand/New_Average)>(1+Generating_Threshold/100)):
        Gen_Check = 1    #Generating threshold exceeded
    elif((Demand/New_Average)<(1-Pumping_Threshold/100)):
        Pump_Check = 1    #Pumping threshold exceeded
        
    #Check if NG will be fully dispatched
    NG_Check = 0
    if((Grid_Demand_Left - NG_Gen) > 0):
        NG_Check = 1
    
    #Initialize Outputs
    New_State = PHES_State;
    MW_To_Be_Gen = 0;
    MW_To_Be_Pump = 0;
    New_Water_Level = Water_Lvl;
    
        
    #ADD water to res storage from any rainfalland and calculate new water level 
    #TBD
    
    #Check if we should generate
    if((Surplus_Check == 0) and ((Gen_Check == 1) or (NG_Check == 1))):  #There is still demand left and either demand is peaking or NG doesn't satisfy remaining demand
        if(Water_Lvl > PHES_Water_Lvl_Min): #+ 1 as a buffer temporarily
            
            Stored_Water = getVolumeStored(Water_Lvl)
            
            if(NG_Check == 1):   #If NG doesn't meet grid demand
                MW_To_Be_Gen = np.minimum(Max_Gen, Grid_Demand_Left - NG_Gen)  
            else :
                MW_To_Be_Gen = np.minimum(Max_Gen, Grid_Demand_Left) #Not 100% sure here
            
            time = 3600
                    
            for x in range(0,3600):
                temp = GenOneSecond(New_Water_Level, MW_To_Be_Gen)
                if(temp == 0):
                    time = x
                    break
                New_Water_Level = temp
                
            MW_To_Be_Gen = time/3600 * MW_To_Be_Gen   
            #Flow_Rate = (MW_To_Be_Gen*1000000)/(Water_Density*G*Hydraulic_Head*Gen_Efficiency)
            #Volume_Needed = Flow_Rate*3600  #Volume of water from upper reservoir needed to produce MW_To_Be_Gen
            
            #if(Stored_Water < Volume_Needed): #If there isnt enough water stored
            #    New_Flow_Rate = Stored_Water/3600  #m^3/s
            #    MW_To_Be_Gen = Water_Density*New_Flow_Rate*G*Hydraulic_Head*Gen_Efficiency/1000000
            #    New_Water_Level = PHES_Water_Lvl_Min # We use whatever volume of water was stored in res to generate power
                
            #else :
            #    New_Water_Level = getWaterLevel(Stored_Water-Volume_Needed) #m
                
            New_State = 2 #Generating
            
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average
            
            
    #Check if we should pump
    if((Surplus_Check == 1) or (Pump_Check == 1)): #Either a surplus of renewables or demand is very low
        if(Water_Lvl < PHES_Water_Lvl_Max): #- 1 as a buffer temporarily
            
            Stored_Water = getVolumeStored(Water_Lvl)
            
            if(Surplus_Check == 1):    #IF there is a renewable surplus, pump up the surplus
                MW_To_Be_Pump = np.minimum(Max_Pump, Surplus_Amount)
                
            elif(NG_Gen - Grid_Demand_Left > 0): #No renewable surplus, but NG gen is not fully used
                MW_To_Be_Pump = np.minimum(Max_Pump, NG_Gen - Grid_Demand_Left)
                
            else:  #Just in case demand is very low but expensive generation is dispatched due to portfolio makeup
                New_State = 0 #Standby
                return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average
            
            time = 3600
            
            for x in range(0,3600):
                temp = PumpOneSecond(New_Water_Level, MW_To_Be_Pump)
                if(temp == 0):
                    time = x
                    break
                New_Water_Level = temp

            MW_To_Be_Pump = time/3600 * MW_To_Be_Pump   

            #Flow_Rate = (MW_To_Be_Pump*1000000)/(Water_Density*G*Hydraulic_Head*Pump_Efficiency) #(m^3/s)
            #Volume_Added = Flow_Rate*3600   #(m^3)
            
            #if((Stored_Water+Volume_Added) > PHES_Storage_Cap):
             #   New_Flow_Rate = (PHES_Storage_Cap-Stored_Water)/3600  #m^3/s
              #  MW_To_Be_Pump = Water_Density*New_Flow_Rate*G*Hydraulic_Head*Pump_Efficiency/1000000
               # New_Water_Level = 304.95 # We fill up the reservoir to the top limit
                
            #else:
             #   New_Water_Level = getWaterLevel(Stored_Water+Volume_Added) #m
            
            New_State = 1 #Pumping
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average

    #All pumping and generating conditions failed
    New_State = 0 #Standby
    return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average


#Equations calculated from northfield data and created using https://www.mycurvefit.com/
#Excel is terrible at best fit equations and messed it up
#But i did graph the new equations in excel to double check the website is correct

def PumpOneSecond(Water_Level, Energy_To_Pump):
    if(Water_Level >= 304.95):
        return 0
    
    Head = Water_Level - 54.864 #m
    Water_Density = 1000 #kg/m^3
    G = 9.8 #gravity (m/s^2)
    Volume_In_Res = getVolumeStored(Water_Level)
    
    Flow_Rate = (Energy_To_Pump*1000000)/(Water_Density*G*Head) #(m^3/s)

    New_Volume = Volume_In_Res + Flow_Rate
    New_Water_Level = getWaterLevel(New_Volume)
    
    return New_Water_Level
    
def GenOneSecond(Water_Level, Energy_To_Gen):
    if(Water_Level <= 285.9):
        return 0
    
    Head = Water_Level - 54.864 #m
    Water_Density = 1000 #kg/m^3
    Gen_Efficiency = 0.87
    G = 9.8 #gravity (m/s^2)
    Volume_In_Res = getVolumeStored(Water_Level)
    
    Flow_Rate = (Energy_To_Gen*1000000)/(Water_Density*G*Head*Gen_Efficiency) #(m^3/s)

    New_Volume = Volume_In_Res - Flow_Rate
    New_Water_Level = getWaterLevel(New_Volume)
    
    return New_Water_Level


#x = (10 (sqrt(1744599 y + 5318406157000) + 47560900))/1744599
def getWaterLevel(Storage): #Takes in volume stored (m^3) in reservoir as an arg
    return 10*(((1744599*Storage+5318406157000)**0.5)+ 47560900)/1744599 #Outputs water level in m
    
#y = 1293547000 - 9512180*x + 17445.99*x^2
def getVolumeStored(WaterLevel): #Takes in the water level (m) of reservoir as an arg
    return (17445.99*((WaterLevel)*(WaterLevel)) - 9512180*(WaterLevel) + 1293547000) #Outputs volume of water stored in m^3

