# -*- coding: utf-8 -*-

# import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle, islice


ScenarioNumberToPlot = 0  #The scenario to be plotted, 0 is the first scenario


Capacity_file = pd.ExcelFile('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Portfolio_Capacity_Inputs_TK.xlsx') #Load data from capcity file
capacities = Capacity_file.parse('UserInput', skiprows = 0) #Getting the Cap values for the scenarios
Scenario_Names = capacities['Scenario'] #Get the scenario names


if(len(Scenario_Names) <= ScenarioNumberToPlot): 
    print("ScenarioNumber chosen does not exist") #The ScenarioNumberToPlot is too high if this message appears
else:
    print('Plotting scenario: ' + Scenario_Names[ScenarioNumberToPlot]) #Prints the name of he scenario chosen to plot
    Results_File = pd.ExcelFile('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Scenario_Results_Port_TK.xlsx') #Open results excel file

    Results_Summer = Results_File.parse(Scenario_Names[ScenarioNumberToPlot] + ' Summer',skiprows=0) #Load summer week for chosen scenario
    Results_Winter = Results_File.parse(Scenario_Names[ScenarioNumberToPlot] + ' Winter',skiprows=0) #Load winter week for chosen scenario
    
    """Load the Summer Week Data for Each Gen Source"""
    Nuclear_S = Results_Summer['Nuclear']
    NG_S = Results_Summer['NG']
    Oil_S = Results_Summer['Oil']
    Hydro_S = Results_Summer['Hydro']
    Wind_On_S = Results_Summer['Wind Onshore']
    Wind_Off_S = Results_Summer['Wind Offshore']
    Solar_S = Results_Summer['Solar']
    PHES_S = Results_Summer['PHES']
    
    Summer_Energy = {'Nuclear':Nuclear_S,'NG':NG_S,'Oil':Oil_S,'Hydro':Hydro_S,'Wind Onshore':Wind_On_S,'Wind Offshore':Wind_Off_S,'Solar':Solar_S,'PHES':PHES_S}
    
    WeekSummer = pd.DataFrame(Summer_Energy, columns = [ 'Nuclear','NG','Oil','Hydro', 'Wind Onshore', 'Wind Offshore', 'Solar','PHES']) #Build dataframe of summer week data
    
    
    my_colors = my_colors = list(islice(cycle(['red', "#be5e3d", 'grey', 'blue', 'purple','green','yellow','orange']), None, len(WeekSummer))) #Choose colors
    
    """Plot the summer week area plot"""
    ax = WeekSummer.plot(kind='area', stacked=True, title='Generation Mix for a Summer Week (' + Scenario_Names[ScenarioNumberToPlot] + ')', fontsize = 15,color = my_colors)
    handles, labels = ax.get_legend_handles_labels()
    ax.title.set_size(25)
    ax.legend(reversed(handles), reversed(labels), loc='lower right') #Place the legend in the lower right
    plt.xlabel('Time (Hour)', fontsize = 20)
    plt.ylabel('Energy (MWh)', fontsize = 20)
    plt.show()
    
    """Load the Winter Week Data for Each Gen Source"""
    Nuclear_W = Results_Winter['Nuclear']
    NG_W = Results_Winter['NG']
    Oil_W = Results_Winter['Oil']
    Hydro_W = Results_Winter['Hydro']
    Wind_On_W = Results_Winter['Wind Onshore']
    Wind_Off_W = Results_Winter['Wind Offshore']
    Solar_W = Results_Winter['Solar']
    PHES_W = Results_Winter['PHES']
    
    Winter_Energy = {'Nuclear':Nuclear_W,'NG':NG_W,'Oil':Oil_W,'Hydro':Hydro_W,'Wind Onshore':Wind_On_W,'Wind Offshore':Wind_Off_W,'Solar':Solar_W,'PHES':PHES_W}
    
    WeekWinter = pd.DataFrame(Winter_Energy, columns = [ 'Nuclear','NG','Oil','Hydro', 'Wind Onshore', 'Wind Offshore', 'Solar','PHES']) #Build dataframe for data in winter week
    
    """Plot the winter week area plot"""    
    ax = WeekWinter.plot(kind='area', stacked=True, title='Generation Mix for a Winter Week (' + Scenario_Names[ScenarioNumberToPlot] + ')', fontsize = 15,color = my_colors)
    handles, labels = ax.get_legend_handles_labels()
    ax.title.set_size(25)
    ax.legend(reversed(handles), reversed(labels), loc='lower right') #Place the legend in the lower right
    plt.xlabel('Time (Hour)', fontsize = 20)
    plt.ylabel('Energy (MWh)', fontsize = 20)
    plt.show()