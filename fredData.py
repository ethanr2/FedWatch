# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 18:33:00 2020

@author: ethan
"""

from datetime import date
from datetime import datetime as dt
from time import time
import requests
import json

import numpy as np
import pandas as pd
from scipy import stats

SERIES_IDS = {
        'FFR_upper': 'DFEDTARU', # Federal Funds Target Range - Upper Limit 
        'FFR_lower': 'DFEDTARL'  # Federal Funds Target Range - Lower Limit 
        }
URL = 'https://api.stlouisfed.org/fred/series/observations?series_id={}&api_key={}&limit={}&sort_order=desc&file_type=json'


with open('fredAPIKey.txt') as file:
    key = file.read()

def get_FFR():  
    out = {}
    for k in ['FFR_upper', 'FFR_lower']:    
        data = requests.get(URL.format(SERIES_IDS[k], key, 1)).json()
        out[k] = float(data['observations'][0]['value'])/100
    out = pd.Series(out)
    return out





#%%