"""
Pumped Hydro Simulation
12/05/2017
@author: Tristan
"""

#import modules
import numpy as np
#import rain data TBD    

"""   
############################################################################
WHERE THIS FUNCTION FITS INTO THE LARGE PORTFOLIO MODEL

After allocating nuclear, solar, onshore, offshore, and  calculating NG_limit
Then run PumpedHydroPlant function and pass in arguments below:

PHES_Cap                                                                          , the capacity of the PHES plant
AC                                                                                , the total available capacity for the current hour AC = generation capacity - demand
Running_Average                                                                   , the the previous hour's running average
Surplus_RE                                                                        , the amount of surplus renewable and nuclear generation this hour
Grid_Demand_Left is New_D                                                         , the demand that still needs to be met for this hour after dispatching nuclear and renewables 
Water_Lvl                                                                         , the height of the water in the upper reservoir

Will pass out updated hydro variables in the following order
New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average

############################################################################
"""

#Water_Lvl keeps track of the water level in the upper reservoir in m
def PumpedHydroPlant(PHES_Cap, AC, Running_Average, Surplus_RE, Grid_Demand_Left, Water_Lvl):
    #PHES PLANT CHARACTERISTCS 
    
    #y = 1.84*x - 2 where y is MW Output and x is flow rate gen, assuming hydraulic head at max
    if(PHES_Cap == 0.0):
        return 0.0,0.0,0.0,0.0,0.0
    
    #PHES Plant variables
    Water_Flow_Rate_Gen =  566.337 #((m^3/s) (141.58 (m^3/s) / turbine)
    Water_Flow_Rate_Pump = 430.4 #((m^3/s) (107.6 (m^3/s) / turbine)
    PHES_Water_Lvl_Min = 285.9 # m
    PHES_Water_Lvl_Max = 304.95 # m
    Efficiency = 0.82 #Both gen and pump, overal efficiency is 0.82*0.82=0.67239
    
    #PHES_Cap not used rn
    #Move reservoir in height to scale output capacity
    #Max_Head_Calc = 0.211974*PHES_Cap - 0.00533333 # m
    #Height_Scale = Max_Head_Calc - (PHES_Water_Lvl_Max - 54.84)
    
    #Operation Thresholds for Running Average
    Pumping_Threshold = 8 #%
    Generating_Threshold = 12 #%  
    
    #Constants for Equations
    Water_Density = 1000 #kg/m^3
    G = 9.8 #gravity (m/s^2)
    
    #Hydraulic Head
    Hydraulic_Head = Water_Lvl - 54.84 #+ Height_Scale

    #Generating Capacity
    Max_Gen = Water_Density*Water_Flow_Rate_Gen*G*Hydraulic_Head*Efficiency/1000000 #(MW) 1150 MW max with no scaling
    
    #Pumping Capacity
    Max_Pump = Water_Density*Water_Flow_Rate_Pump*G*Hydraulic_Head*Efficiency/1000000 #(MW) 865 MW max worth of water
    
    #Check if there is a surplus in renewables
    Surplus_Check = 0
    if( Surplus_RE > 0):
        Surplus_Check = 1    #There is a surplus of renewable generation
        
    #Running Average
    alpha = 0.12
    New_Average = alpha*AC + (1-alpha)*Running_Average #Calculate new running average
    
    #Check if pumping or generating thresholds are exceeded
    Gen_Check = 0
    Pump_Check = 0
    if((AC/New_Average)>(1+Pumping_Threshold/100)):
        Pump_Check = 1    #Generating threshold exceeded
    elif((AC/New_Average)<(1-Generating_Threshold/100)):
        Gen_Check = 1    #Pumping threshold exceeded
    
    #Initialize Outputs
    New_State = 0;
    MW_To_Be_Gen = 0;
    MW_To_Be_Pump = 0;
    New_Water_Level = Water_Lvl;
    
        
    #ADD water to res storage from any rainfalland and calculate new water level 
    #TBD
    
    #Check if we should generate
    if((Surplus_Check == 0) and (Gen_Check == 1) ):  #There is still demand left and either demand is peaking or NG doesn't satisfy remaining demand
        if(Water_Lvl > PHES_Water_Lvl_Min): 
            MW_To_Be_Gen = np.minimum(Max_Gen, Grid_Demand_Left) 
            
            PHES_Power_Output = np.zeros(3600)
            
            for x in range(0,3600): #Generate for 1 hour (3600 seconds)
                temp, PHES_Power_Output[x] = GenOneSecond(New_Water_Level, MW_To_Be_Gen, Efficiency)
                if(temp == 0):
                    New_Water_Level = PHES_Water_Lvl_Min
                    break #Minimum Water Level Reached
                New_Water_Level = temp
                
            MW_To_Be_Gen = np.mean(PHES_Power_Output)
                
            New_State = 2 #Generating
            
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average
            
            
    #Check if we should pump
    if((Surplus_Check == 1) or (Pump_Check == 1)): #Either a surplus of renewables or demand is very low
        if(Water_Lvl < PHES_Water_Lvl_Max): 
                        
            if(Surplus_Check == 1):    #IF there is a renewable surplus, pump up the surplus
                MW_To_Be_Pump = np.minimum(Max_Pump, Surplus_RE)  
            else:
                MW_To_Be_Pump = np.minimum(Max_Pump, AC-1) #-1 temporary
            
            PHES_Power_Consumed = np.zeros(3600)
            
            for x in range(0,3600): #Pump for 1 hour (3600 seconds)
                temp, PHES_Power_Consumed[x] = PumpOneSecond(New_Water_Level, MW_To_Be_Pump, Efficiency)
                if(temp == 0):
                    New_Water_Level = PHES_Water_Lvl_Max
                    break
                New_Water_Level = temp

            MW_To_Be_Pump = np.mean(PHES_Power_Consumed)  
            
            New_State = 1 #Pumping
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average

    #All pumping and generating conditions failed
    New_State = 0 #Standby
    return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Water_Level, New_Average


#Equations calculated from northfield data and created using https://www.mycurvefit.com/
#Excel is terrible at best fit equations and messed it up
#But i did graph the new equations in excel to double check the website is correct

def PumpOneSecond(Water_Level, Energy_To_Pump, Efficiency):
    if(Water_Level >= 304.95):
        return 0, 0
    
    Water_Density = 1000 #kg/m^3
    G = 9.8 #gravity (m/s^2)
    Volume_In_Res = getVolumeStored(Water_Level)#m^3
    Max_Flow_Rate = 430.4#(m^3/s) 
    Head = Water_Level - 54.84#m
    
    Flow_Rate = (Energy_To_Pump*1000000)/(Water_Density*G*Head*Efficiency) #(m^3/s) 
    Flow_Rate = np.minimum(Flow_Rate, Max_Flow_Rate)

    Power_Consumed = Water_Density*Flow_Rate*G*Head*Efficiency/1000000 #(MW)

    New_Volume = Volume_In_Res + Flow_Rate
    New_Water_Level = getWaterLevel(New_Volume)
    
    return New_Water_Level, Power_Consumed
    
def GenOneSecond(Water_Level, Energy_To_Gen, Efficiency):
    if(Water_Level <= 285.9):
        return 0, 0
    
    Water_Density = 1000 #kg/m^3
    G = 9.8 #gravity (m/s^2)
    Volume_In_Res = getVolumeStored(Water_Level)
    Max_Flow_Rate = 566.337#(m^3/s) 
    Head = Water_Level - 54.84
    
    Flow_Rate = (Energy_To_Gen*1000000)/(Water_Density*G*Head*Efficiency) #(m^3/s) 
    Flow_Rate = np.minimum(Flow_Rate, Max_Flow_Rate) 
    
    Power_Generated = Water_Density*Flow_Rate*G*Head*Efficiency/1000000 #(MW)

    New_Volume = Volume_In_Res - Flow_Rate
    New_Water_Level = getWaterLevel(New_Volume)
    
    return New_Water_Level, Power_Generated


#x = (10 (sqrt(1744599 y + 5318406157000) + 47560900))/1744599
def getWaterLevel(Storage): #Takes in volume stored (m^3) in reservoir as an arg
    return 10*(((1744599*Storage+5318406157000)**0.5)+ 47560900)/1744599 #Outputs water level in m
    
#y = 1293547000 - 9512180*x + 17445.99*x^2
def getVolumeStored(WaterLevel): #Takes in the water level (m) of reservoir as an arg
    return (17445.99*((WaterLevel)*(WaterLevel)) - 9512180*(WaterLevel) + 1293547000) #Outputs volume of water stored in m^3

