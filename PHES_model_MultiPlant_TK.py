"""
Pumped Hydro Simulation
12/11/2017
@author: Tristan
"""

#import modules
import numpy as np
import pandas as pd
#import rain data TBD    

"""   
############################################################################
WHERE THIS FUNCTION FITS INTO THE LARGE PORTFOLIO MODEL

After allocating nuclear and RE,
Then run PumpedHydroPlant function and pass in arguments below:

Num_Plants_Installed                                                              , Number of PHES plants used, determined by the input user capacity
AC                                                                                , the total available capacity for the current hour AC = generation capacity - demand
Running_Average                                                                   , the the previous hour's running average
Surplus_RE                                                                        , the amount of surplus renewable and nuclear generation this hour
Grid_Demand_Left is New_D                                                         , the demand that still needs to be met for this hour after dispatching nuclear and renewables 
Water_Lvl                                                                         , the height of the water in the upper reservoir

Will pass out updated hydro variables in the following order:
New_State                                                                         , 0 is standby, 1 is pumping, 2 is generating (Can be ignored or used, useful for debugging)
MW_To_Be_Gen                                                                      , The Power generated by the PHES plant, if it generated electricty this hour
MW_To_Be_Pump                                                                     , The Power consumed by the PHES plant, if it stored water this hour
New_Water_Level                                                                   , the new water level in the upper reservoir
New_Average                                                                       , the new running average of the available capcity

############################################################################
"""

Capacity_file = pd.ExcelFile('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Portfolio_Capacity_Inputs_TK.xlsx')
capacities = Capacity_file.parse('UserInput', skiprows = 0) #Getting the Cap values for the scenarios

#Water_Lvl keeps track of the water level in the upper reservoir in m
def PumpedHydroPlant(Num_Plants_Installed, AC, Running_Average, Surplus_RE, Grid_Demand_Left, Water_Lvl, scenario): #This is the main function that is called on in the other model
    
    if(Num_Plants_Installed == 0): #When PHES capacity is 0, just return all 0's to save time
        return 0.0,0.0,0.0,0.0,0.0
    
    #PHES Plant variables
    Water_Flow_Rate_Gen =  566.337 #((m^3/s) (141.58 (m^3/s) / turbine) Maximum water flow rate while generating
    Water_Flow_Rate_Pump = 430.4 #((m^3/s) (107.6 (m^3/s) / turbine) Maximum water flow rate while pumping
    PHES_Water_Lvl_Min = 285.9 # m minumim water level for upper reservoir
    PHES_Water_Lvl_Max = 304.95 # m maximum water level for upper reservoir
    Efficiency = 0.82 #Both gen and pump efficiency, overal efficiency for PHES plant is 0.82*0.82=0.67239 (Can be changed here)
    Pumping_Threshold = capacities['PHES Pumping Threshold'][scenario] #% #Operation Thresholds for Running Average (Pumping)
    Generating_Threshold = capacities['PHES Generating Threshold'][scenario] #% #Operation Thresholds for Running Average  (Generating)
    
    #Constants for Equations
    Water_Density = 1000 #kg/m^3 #Density of water
    G = 9.8 #gravity (m/s^2) #Acceleration of gravity
    
    #Hydraulic Head
    Hydraulic_Head = Water_Lvl - 54.84 #Calculate the Hydraulic head, the 54.8 m is an offset specific to Northfield

    #Generating Capacity
    Max_Gen = Water_Density*Water_Flow_Rate_Gen*G*Hydraulic_Head*Efficiency/1000000*Num_Plants_Installed #(MW) Calcaulte the maximum generation power output 
    
    #Pumping Capacity
    Max_Pump = Water_Density*Water_Flow_Rate_Pump*G*Hydraulic_Head*Efficiency/1000000*Num_Plants_Installed #(MW) Calculate the maximum power consumption if storing water

        
    #Running Average
    alpha = capacities['PHES Smoothing Factor'][scenario] #Smoothing Factor
    New_Average = alpha*AC + (1-alpha)*Running_Average #Calculate new running average
    
    #Check if pumping or generating thresholds are exceeded
    Gen_Check = 0 #Pseudo Boolean used to keep track of whether or not the generating threshold is crossed
    Pump_Check = 0 #Pseudo Boolean used to keep track of whether or not the pumping threshold is crossed
    if((AC/New_Average)>(1+Pumping_Threshold/100)): #Check if Available capacity is above pumping threshold
        Pump_Check = 1    #Pumping threshold exceeded
    elif((AC/New_Average)<(1-Generating_Threshold/100)): #Check if Available capacity is below generating threshold
        Gen_Check = 1    #Generating threshold exceeded
    
    #Initialize Outputs
    New_State = 0; #Keeps track of the next state the PHES plant is in
    MW_To_Be_Gen = 0; #Amount of energy to generate 
    MW_To_Be_Pump = 0; #Amount of energy to be consumed by the PHES plant to pump water to upper reservoir
    New_Water_Level = Water_Lvl; #The new water level in m
    
        
    #ADD water to res storage from any rainfalland and calculate new water level 
    #TBD
    
    #Check if we should generate
    if((Surplus_RE == 0) and (Gen_Check == 1) ):  #Check if the generating threshold is exceeded and there is no surplus renewable energy generated
        if(Water_Lvl > PHES_Water_Lvl_Min): #Check that the water level in the reservoir is above the minimum water level
            MW_To_Be_Gen = np.minimum(Max_Gen, Grid_Demand_Left) #Calculate amount of power to generate, either the maximum or the amount of demand left on the grid after nuclear and RE allocated
            
            PHES_Energy_Output = np.zeros(3600) #Initialize output array, 1 cell for each second
            
            for x in range(0,3600): #Generate for 1 hour (3600 seconds)
                temp, PHES_Energy_Output[x] = GenOneSecond(New_Water_Level, MW_To_Be_Gen/Num_Plants_Installed, Efficiency) #Calculate amount of water released, energy generated, new water level for current second
                
                if(temp == 0): #The minimum water level was reached so operation must stop
                    New_Water_Level = PHES_Water_Lvl_Min #Set water level to the minimum
                    break #Minimum Water Level Reached
                    
                New_Water_Level = temp #Use new water level
                
            MW_To_Be_Gen = np.mean(PHES_Energy_Output)*Num_Plants_Installed #Calculate power generated for the current hour
                
            New_State = 2 #Generating now 
            
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average #return the output variables, MW_To_Be_Pump will be 0 and the new_state will be 2 (Generating)
            
            
    #Check if we should pump
    if((Surplus_RE > 0) or (Pump_Check == 1)): #Check if there is a surplus of RE or the pumping threshold is crossed
        if(Water_Lvl < PHES_Water_Lvl_Max): #check if the water level is below the maximum water level
                        
            if(Surplus_RE > 0):    #IF there is a renewable surplus, pump up the surplus
                MW_To_Be_Pump = np.minimum(Max_Pump, Surplus_RE)  #Amount of power to consume is the lowest of the maximum or surplus of RE
            else: #Otherwise pump either the maximum amount or the surplus generation for the current hour (Available capacity)
                MW_To_Be_Pump = np.minimum(Max_Pump, AC-1) #Amount of power to consume is the lowest of the maximum or the available capacity
            
            PHES_Energy_Consumed = np.zeros(3600) #Initialize output array, 1 cell for each second
            
            for x in range(0,3600): #Pump for 1 hour (3600 seconds)
                
                temp, PHES_Energy_Consumed[x] = PumpOneSecond(New_Water_Level, MW_To_Be_Pump/Num_Plants_Installed, Efficiency) #Calculate amount of water added, energy consumed, new water level for current second
                
                if(temp == 0): #The maximum water level was reached so operation must stop
                    New_Water_Level = PHES_Water_Lvl_Max #Set water level to the maximum
                    break #Maximum water level reached
                    
                New_Water_Level = temp #Use new water level

            MW_To_Be_Pump = np.mean(PHES_Energy_Consumed)*Num_Plants_Installed  ##Calculate power consumed for the current hour
            
            New_State = 1 #Pumping now 
            
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average #return the output variables, MW_To_BeGen will be 0 and the new_state will be 1 (Pumping)

    #All pumping and generating conditions failed
    New_State = 0 #Standby
    
    return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average #return the output variables, MW_To_Be_Pump and MW_To_Be_Gen will be 0 and the new_state will be 0 (Standby)

def PumpOneSecond(Water_Level, Energy_To_Pump, Efficiency): #Pump water up to the upper reservoir for one second
    
    if(Water_Level >= 304.95): #If the maximum water level is reached, stop operation
        return 0, 0
        
    Water_Density = 1000 #kg/m^3 #Density of water
    G = 9.8 #gravity (m/s^2) Acceleration of gravity
    Volume_In_Res = getVolumeStored(Water_Level)#m^3 #Calculate current volume stored in upper reservoir
    Max_Flow_Rate = 430.4#(m^3/s) #Maximum water flow rate while pumping
    Head = Water_Level - 54.84#m #Calculate current hydraulic head for reservoir
    
    Flow_Rate = (Energy_To_Pump*1000000)/(Water_Density*G*Head*Efficiency) #(m^3/s) Calculate flow rate required
    Flow_Rate = np.minimum(Flow_Rate, Max_Flow_Rate) #Limit the flow rate to the maximum

    Energy_Consumed = Water_Density*Flow_Rate*G*Head*Efficiency/1000000 #(MW) Calculate energy consumed this second

    New_Volume = Volume_In_Res + Flow_Rate #Add water flowing in to the volume in the reservoir
    New_Water_Level = getWaterLevel(New_Volume) #Calculate the new water level
    
    return New_Water_Level, Energy_Consumed #Return new water level and the energy consumed for current second
    
def GenOneSecond(Water_Level, Energy_To_Gen, Efficiency): #Generate electricty from the stored water for one second
    
    if(Water_Level <= 285.9): #Check if the water level is below the minimum, if so stop operation
        return 0, 0
    
    Water_Density = 1000 #kg/m^3 #Density of water
    G = 9.8 #gravity (m/s^2) Acceleration of gravity
    Volume_In_Res = getVolumeStored(Water_Level) #Calculate current volume stored in upper reservoir
    Max_Flow_Rate = 566.337#(m^3/s) #Maximum water flow rate while generating
    Head = Water_Level - 54.84 #Calculate current hydraulic head for reservoir
    
    Flow_Rate = (Energy_To_Gen*1000000)/(Water_Density*G*Head*Efficiency) #(m^3/s) Calculate the flow rate
    Flow_Rate = np.minimum(Flow_Rate, Max_Flow_Rate) #Limit the flow rate to the maximum
    
    Energy_Generated = Water_Density*Flow_Rate*G*Head*Efficiency/1000000 #(MW) Find energy generated this second

    New_Volume = Volume_In_Res - Flow_Rate #Subtract water flowing out from the volume in the reservoir
    New_Water_Level = getWaterLevel(New_Volume) #Find the new water level in the reservoir
    
    return New_Water_Level, Energy_Generated #Return new water level and the energy generated for current second

#Equations calculated from northfield data and created using https://www.mycurvefit.com/
def getWaterLevel(Storage): #Takes in volume stored (m^3) in reservoir as an arg
    return 10*(((1744599*Storage+5318406157000)**0.5)+ 47560900)/1744599 #Outputs water level in m
    
def getVolumeStored(WaterLevel): #Takes in the water level (m) of reservoir as an arg
    return (17445.99*((WaterLevel)*(WaterLevel)) - 9512180*(WaterLevel) + 1293547000) #Outputs volume of water stored in m^3

