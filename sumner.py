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
    
    name = 'data\cme_' + str(dt.now())[:10] + '.pkl'
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
URL = "https://www.federalreserve.gov/monetarypolicy/materials/"
driver.get(URL)
table = driver.find_elements_by_tag_name("div")
print(table)
#df = pd.read_pickle('data\cme_2019-08-05.pkl')
#df['Last'] = 1 - df['Last'] 
#name = u'imgs/ffr' + str(dt.now())[:10]
#output_file(name + '.html')
#show(chart_NGDP_ser(df,.02,.0225, name))







driver.close()






