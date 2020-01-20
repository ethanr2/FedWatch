# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 23:19:17 2020

@author: ethan
"""
import requests
from datetime import datetime as dt
from datetime import timedelta as td

import pandas as pd

URL = "https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/305/G?quoteCodes=null&_=1null"

def get_futures():
    df = {
          'Month': [],
          'Last': []
          }
    
    quotes = requests.get(URL).json()['quotes']
    for quote in quotes:
        if not quote['last'] == '-':
            stamp = str(quote['expirationDate'])
            stamp = dt.strptime(stamp, '%Y%m%d')
            df['Month'].append(stamp)
            df['Last'].append(float(quote['last']))

    df = pd.DataFrame(df)
    df['Last'] = 1 - df['Last']/100 
    df = df.loc[df['Month'] < dt.now() + td(days = 365)]
    
    print('CME FFR Futures:')
    print(df)
    
    return df
get_futures()
#%%