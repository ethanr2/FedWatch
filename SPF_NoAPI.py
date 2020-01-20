# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 15:15:27 2020

@author: ethan
"""
import os
from datetime import datetime as dt

import pandas as pd

import urllib.request

URL = 'https://www.philadelphiafed.org:443/-/media/research-and-data/real-time-center/survey-of-professional-forecasters/data-files/files/individual_corepce.xlsx?la=en'

dataPath = 'data/' + str(dt.now())[:10]

def check_dir():
    if not os.path.isdir(dataPath):
        os.mkdir(dataPath)
        urllib.request.urlretrieve(URL, '{}/spf.xlsx'.format(dataPath))

def get_SPF():
    check_dir()
    PCE = pd.read_excel('{}/spf.xlsx'.format(dataPath), sheet_name = 'COREPCE')
    PCE = PCE.loc[(PCE['YEAR'] == 2019) & (PCE['QUARTER'] == 3), ['COREPCE2', 'COREPCE3', 'COREPCE4', 'COREPCE5', 'COREPCE6']].dropna()/100
    PCE = PCE.stack().reset_index()
    PCE.columns = ['date', 'type', 'data']
    PCE['date'] = pd.NaT
    
    print('Survey of Professional Forecasters:')
    print(PCE)
    
    return PCE

#%%
