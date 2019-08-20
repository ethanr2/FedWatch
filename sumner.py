# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 16:33:42 2019

@author: ethan
"""

from datetime import date
from datetime import datetime as dt
from time import time

import numpy as np
import pandas as pd
from scipy import stats

from bokeh.io import export_png,output_file,show
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter, Label,ColumnDataSource
from bokeh.models.tickers import FixedTicker, SingleIntervalTicker
from bokeh.layouts import row, column

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

import os 

def getTable():
    path = 'chromedriver'
    driver = Chrome(path)
    URL = "http://www.cmegroup.com/trading/interest-rates/stir/30-day-federal-fund.html"
    driver.get(URL)
    
    table = driver.find_elements_by_class_name('cmeTable')[0]
    table = pd.read_html(table.get_attribute('outerHTML'))[0]
    table.columns = table.columns.droplevel(0)
    driver.close()
    bools =  table['Last'].apply(lambda x: x[0]=='9')
    
    table = table.loc[bools, ['Month', 'Last', 'Updated']]
    def getDTS(x):
        
        return dt.strptime(x,'%b %Y')
    table['Month'] = table['Month'].apply(getDTS)
    table['Last'] = table['Last'].astype(float)/100
    
    name = dataPath +  '/cme.pkl'
    table.to_pickle(name)
    
    return table

def set_up(x, y, truncated = True, margins = None):
    if truncated: 
        b = (3 * y.min() - y.max())/2
    else:
        b = y.min()
    if margins == None:    
        xrng = (x.min(),x.max())
        yrng = (b,y.max())
    else:
        xrng = (x.min() - margins,x.max() + margins)
        yrng = (b - margins,y.max() + margins)
        
    x = x.dropna()
    y = y.dropna()
    
    return(x,y,xrng,yrng)
    
def chart_NGDP_ser(data,low, up, name):
    xdata, ydata, xrng, yrng = set_up(data['Month'], data['Last'])
    yrng = (0,.03)
    now = dt.now().strftime('%B, %d, %Y')
    
    p = figure(width = 1000, height = 700,
               title="CME 30-Day Federal Fund Futures: {}".format(now), 
               x_axis_label = 'Date', x_axis_type = 'datetime',
               y_axis_label = 'Implied Federal Funds Rate', 
               y_range = yrng, x_range = xrng)

    p.line(xrng,[0,0], color = 'black')
    p.line(xdata,ydata, color = 'blue')
    p.line(xrng, [low,low], color ='Black', line_dash = 'dashed')
    p.line(xrng, [up,up], color ='Black', line_dash = 'dashed')
    
    xpos = len(xdata) // 2
    ypos = (low + up)/2
    lbl = Label(x=xdata[xpos - 4], y=ypos - .0005,
                 text='Current FFR Target Range')
    p.add_layout(lbl)
    
    tik = SingleIntervalTicker()
    tik.interval = .0025
    p.yaxis[0].ticker = tik
    p.xaxis[0].ticker.desired_num_ticks = 12
    p.ygrid.grid_line_color = None
    p.yaxis.formatter=NumeralTickFormatter(format="0.00%")
    
    export_png(p,name + '.png')
    
    return p
#df = getTable()
path = 'chromedriver'
driver = Chrome(path)
dataPath = 'data/' + str(dt.now())[:10]
os.mkdir(dataPath)

def find_note():
    URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    driver.get(URL)
    
    items = driver.find_elements_by_xpath('//*[@id="article"]/div[2]/div')[1:]
    
    for i in range(len(items)):
        text = items[i].text
        if not 'Implementation Note' in text.split('\n'):
            break
    item = items[i-1].find_element_by_link_text('Implementation Note')
    return item.get_attribute('href')

#URL = find_note()
#driver.get(URL)
#item = driver.find_element_by_xpath('//*[@id="content"]/div[3]/div[1]/ul')
#with open(dataPath + '/FedImpNote.txt', 'w') as file:
#    file.write(item.text)
#words = item.text.split()    
#find = ['maintain', 'the', 'federal', 'funds', 'rate', 'in', 'a', 'target',
#        'range', 'of']
#n = len(find)
#for i in range(len(words) - len(find)):
#    if words[i: i + n] == find:
#        lo = float(words[i + n])
#        print(, words[i + n + 2]) 
getTable()
#df = pd.read_pickle(r'data\2019-08-14\cme.pkl')
#df['Last'] = 1 - df['Last'] 
#name = u'imgs/ffr' + str(dt.now())[:10]
#output_file(name + '.html')
#show(chart_NGDP_ser(df,.02,.0225, name))







driver.close()






