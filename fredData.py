# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 18:33:00 2020

@author: ethan
"""

import requests
from datetime import timedelta as td
from datetime import datetime as dt

import pandas as pd
from selenium import webdriver

SERIES_IDS = {
        'FFR_upper': 'DFEDTARU', # Federal Funds Target Range - Upper Limit 
        'FFR_lower': 'DFEDTARL',  # Federal Funds Target Range - Lower Limit 
        'qmax': 'JCXFERH', # FOMC SEP for the PCE-Core Inflation Rate, Range, High
        'q3': 'JCXFECTH', # FOMC SEP for the PCE-Core Inflation Rate, Central Tendency, High
        'q2': 'JCXFEMD', # FOMC SEP for the PCE-Core Inflation Rate, Median
        'q1': 'JCXFECTL', # FOMC SEP for the PCE-Core Inflation Rate, Central Tendency, Low
        'qmin': 'JCXFERL', # FOMC SEP for the PCE-Core Inflation Rate, Range, Low
        'TIPS_5': 'T5YIE', # 5-Year Breakeven Inflation Rate
        'TIPS_10': 'T10YIE', # 5-Year Breakeven Inflation Rate
        }
# FRED API URL
URL = 'https://api.stlouisfed.org/fred/series/observations?series_id={}&api_key={}&limit={}&sort_order=desc&file_type=json'
# Fedsearch url
URL2 = 'https://www.fedsearch.org/fomc-docs/search?advanced_search=true&fomc_document_type=allpresconf&text=Projection+materials&search_precision=Exact+Phrase&from_month=3&from_year=2019&to_month=7&to_year=2020&sort=Most+Recent+First&Search=Search+Again'

with open('fredAPIKey.txt') as file:
    key = file.read()

def get_FFR():  
    out = {}
    for k in ['FFR_upper', 'FFR_lower']:    
        data = requests.get(URL.format(SERIES_IDS[k], key, 1)).json()
        out[k] = float(data['observations'][0]['value'])/100
    out = pd.Series(out)
    
    print('Federal Funds Rate:')
    print(out)
    
    return out

def get_SEP():
    sep = {}
    for k in ['qmax', 'q3', 'q2', 'q1', 'qmin']:
        data = requests.get(URL.format(SERIES_IDS[k], key, 4)).json()
        data = pd.DataFrame(data['observations']).set_index('date')
        data = data.loc[data['value'] != '.',:]
        data = data['value'].astype(float)/100
        sep[k] = data
    sep = pd.DataFrame(sep)
    dates = sep.index.to_series()
    for date in dates:
        dates[date] = date[:4]
    sep = sep.set_index(dates).sort_index()
    sep['upper'] = sep['qmax']
    sep['lower'] = sep['qmin']
    
    mtg_date = get_SEP_date()
    sep.year = mtg_date.year
    sep.quarter = (mtg_date.month - 1)//3 + 1
    print('Summary of Economic Projections:')
    print(sep)
    
    return sep

def get_TIPS():
    tips = {}
    for k in ['TIPS_5', 'TIPS_10']:
        data = requests.get(URL.format(SERIES_IDS[k], key, 42)).json()
        data = pd.DataFrame(data['observations'])
        data['date'] = pd.DatetimeIndex(data['date'])
        data = data.set_index('date')
        data = data.loc[data['value'] != '.', :]
        data = data['value'].astype(float)/100
        tips[k] = data
        
    tips = pd.DataFrame(tips)
    tips = tips.stack().reset_index()
    tips.columns = ['date', 'type', 'data']
    tips = tips.loc[tips['data'] != 0,:]
    
    print('TIPS Spread:')
    print(tips)
    
    return tips

# Finds the date that the most recent SEP was released. 
def get_SEP_date():
    with webdriver.Chrome() as driver:
        driver.get(URL2)
        tag = driver.find_element_by_partial_link_text('Projections')
        text = tag.text
        i = text.find(',') + 2 
        date = dt.strptime(text[i:], '%B %d, %Y')
        
    return date

