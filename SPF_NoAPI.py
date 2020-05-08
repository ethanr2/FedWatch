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


def get_SPF():
    urllib.request.urlretrieve(URL, 'data/spf.xlsx')
    PCE = pd.read_excel('data/spf.xlsx', sheet_name = 'COREPCE')
    yr, q = PCE.iloc[-1,[0,1]].astype(int)
    PCE = PCE.loc[(PCE['YEAR'] == yr) & (PCE['QUARTER'] == q), ['COREPCE2', 'COREPCE3', 'COREPCE4', 'COREPCE5', 'COREPCE6']].dropna()/100
    PCE = PCE.stack().reset_index()
    PCE.columns = ['date', 'type', 'data']
    PCE['date'] = pd.NaT
    PCE.year = yr
    PCE.quarter = q
    
    print('Survey of Professional Forecasters:')
    print(PCE)
    
    return PCE


#%%

