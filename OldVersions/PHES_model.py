"""
Pumped Hydro Simulation
11/6/2017
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

PHES_Cap                                                                          , the capacity of the PHES plant
Demand is demand[k]                                                               , the total grid demand for the current hour
Running_Average                                                                   , the the previous hour's running average
Renew_Gen = Nuc_Demand[k] + Sol_Demand[k] + W_Demand[k] + W_Off_Demand[k]         , the amount of power that can be generated this hour by nuclear and renewables
Renew_Dispatched = Nuc_Cap*Nuc_Out[k] + Sol_Tot[k] + W_Tot[k] + W_Off_MWh[k]      , the amount of power dispatched this hour by nuclear and renewables
Grid_Demand_Left is New_D                                                         , the demand that still needs to be met for this hour after dispatching nuclear and renewables 
NG_Gen is NG_Limit                                                                , the amount of NG power that can be generted this hour
PHES_state                                                                        , the state the hydro plant was in the previous hour: 0 is standby, 1 is pumping, 2 is generating
Stored_MW                                                                         , the power stored in the reservoir

Will pass out updated hydro variables in the following order
New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Stored_MW, New_Average

############################################################################
"""

#Water_Lvl keeps track of the water level in the upper reservoir in m
def PumpedHydroPlant(PHES_Cap, Demand, Running_Average, Renew_Gen, Renew_Dispatched, Grid_Demand_Left, NG_Gen, PHES_State, Stored_MW):
    
    if(PHES_Cap == 0.0):
        return 0.0,0.0,0.0,0.0,0.0 
    
    #Operation Thresholds for Running Average
    Pumping_Threshold = 5 #%
    Generating_Threshold = 5 #%  
    
    #Constants for Equations
    Efficiency = 0.75
    
    Max_Storage_MW = PHES_Cap * 8

    #Generating Capacity
    #Max_Gen = PHES_Cap #(MW)
    
    #Pumping Capacity
    #Max_Pump = PHES_Cap #(MW)
    
    #Check if there is a surplus in renewables
    Surplus_Check = 0
    Surplus_Amount = Renew_Gen - Renew_Dispatched
    if( Surplus_Amount > 0):
        Surplus_Check = 1    #There is a surplus of renewable generation
        
    #Running Average
    alpha = 0.13
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
    New_State = PHES_State
    MW_To_Be_Gen = 0
    MW_To_Be_Pump = 0
    New_Stored_MW = Stored_MW
    
        
    #ADD water to res storage from any rainfalland and calculate new water level 
    #TBD
    
    #Check if we should generate
    if((Surplus_Check == 0) and ((Gen_Check == 1) or (NG_Check == 1))):  #There is still demand left and either demand is peaking or NG doesn't satisfy remaining demand
        if(Stored_MW > 0): 
                        
            if(NG_Check == 1):   #If NG doesn't meet grid demand
                MW_To_Be_Gen = np.minimum(PHES_Cap, Grid_Demand_Left - NG_Gen)
            else :
                MW_To_Be_Gen = np.minimum(PHES_Cap, Grid_Demand_Left) #Not 100% sure here
                
            #Only generate the amount stored in reservoir
            MW_To_Be_Gen = np.minimum(Stored_MW, MW_To_Be_Gen)  

            New_State = 2 #Generating
            New_Stored_MW -= MW_To_Be_Gen
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Stored_MW, New_Average
            
            
    #Check if we should pump
    if((Surplus_Check == 1) or (Pump_Check == 1)): #Either a surplus of renewables or demand is very low
        if(Stored_MW < Max_Storage_MW):
                        
            if(Surplus_Check == 1):    #IF there is a renewable surplus, pump up the surplus
                MW_To_Be_Pump = np.minimum(PHES_Cap, Surplus_Amount)
                
            elif(NG_Gen - Grid_Demand_Left > 0): #No renewable surplus, but NG gen is not fully used
                MW_To_Be_Pump = np.minimum(PHES_Cap, NG_Gen - Grid_Demand_Left)
                
            else:  #Just in case demand is very low but expensive generation is dispatched due to portfolio makeup
                New_State = 0 #Standby
                return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Stored_MW, New_Average  
            
            #Only pump what there is room for
            MW_To_Be_Pump = np.minimum(Max_Storage_MW - Stored_MW, MW_To_Be_Pump)
            
            New_State = 1 #Pumping
            New_Stored_MW += MW_To_Be_Pump*Efficiency
            return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Stored_MW, New_Average

    #All pumping and generating conditions failed
    New_State = 0 #Standby
    return New_State, MW_To_Be_Gen, MW_To_Be_Pump, New_Stored_MW, New_Average

