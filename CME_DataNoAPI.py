# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 23:19:17 2020

@author: ethan
"""
import requests
from datetime import datetime as dt
from datetime import timedelta as td

import numpy as np
import pandas as pd

URL = "https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/305/G?quoteCodes=null&_=1null"

def get_futures(path = ''):
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
    #df = df.loc[df['Month'] < dt.now() + td(days = 365)]
    
    print('CME FFR Futures:')
    print(df)
    
    update_db(df, path)
    
    return df

def update_db(df, path = ''):
    db = pd.read_csv(path + 'data/cme_database.csv')
    
    row = [dt.now(), df.loc[0, 'Month'].month]
    row.extend(df['Last'].tolist())
    
    if len(row) < len(db.columns):
        for i in range(len(db.columns) - len(row)):
            row.append('')
    elif len(row) > len(db.columns):
        row = row[:len(db.columns)]
    
    with open(path + 'data/cme_database.csv', 'a') as f:
        row = [str(x) for x in row]
        f.write(','.join(row) + '\n')

#def 



if __name__ == '__main__':
    data_path = __file__[:__file__.find('CME')]
    get_futures(data_path)


#%%




