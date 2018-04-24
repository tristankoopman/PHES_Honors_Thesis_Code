# -*- coding: utf-8 -*-
"""
Created on Wed Sep  6 13:32:39 2017

@author: Des
"""


# import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


User_Input_File = pd.ExcelFile('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Portfolio_Capacity_Inputs_TK.xlsx')

#Not use at the moment
User_Inputs = User_Input_File.parse('UserInput',skiprows=1)


Raw_Data_file = pd.ExcelFile('C:/Users/trist_000/Documents/College/Honors Thesis/Python Model/Raw_NE_Port_Data_Mod.xlsx')
###Make sure that when you import the file you have the forward slashes "/" not the back slashes "\"

## View the excel file's sheet names
###print(Raw_Data_file.sheet_names)

### Load the xls file's Sheets as dataframes:
###Yr_2010 = Raw_Data_file.parse('2010',skiprows=122) #I eliminated year 2010 because first 5 dyas of january have no demand data
#           #Alternatively for 2010 can just skip the first 122 rows that don't have demand data
'''importing the projections for energy'''
Yr_2011 = Raw_Data_file.parse('2011',skiprows=1) #Skipped row 1 because this messed up the data frame
Yr_2012 = Raw_Data_file.parse('2012',skiprows=1)
Yr_2013 = Raw_Data_file.parse('2013',skiprows=1)
Yr_2014 = Raw_Data_file.parse('2014',skiprows=1)
Yr_2015 = Raw_Data_file.parse('2015',skiprows=1)


All_Yrs = [Yr_2011, Yr_2012, Yr_2013, Yr_2014, Yr_2015]


Pipe_Data = Raw_Data_file.parse('Pipeline', skiprows=1)
PHD = Pipe_Data['Heat_Est_Project'] # heating demand for NG 
Nuc_Outage_Data = Raw_Data_file.parse('Nuc_Outage',skiprows=5)
Nuc_Outages = Nuc_Outage_Data['Percent_of_Cap']


