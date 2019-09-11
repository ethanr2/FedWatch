# -*- coding: utf-8 -*--
"""
Created on Tue Aug 20 04:18:14 2019

@author: ethan
"""

from datetime import date, timedelta
from datetime import datetime as dt
from time import time

import numpy as np
import pandas as pd
from scipy import stats

from bokeh.io import export_png,output_file,show
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter, LabelSet,ColumnDataSource
from bokeh.models.tickers import FixedTicker, SingleIntervalTicker
from bokeh.layouts import row, column

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

import os 

def makedf():
    df1 = pd.read_excel('data/2019-08-20/spf.xlsx', sheet_name = 'COREPCE')
    df1 = df1.loc[(df1['YEAR'] == 2019) & (df1['QUARTER'] == 3), ['COREPCE2', 'COREPCE3', 'COREPCE4', 'COREPCE5', 'COREPCE6']].dropna()/100
    df2 = pd.read_excel('data/2019-08-20/fedwatch.xls', sheet_name = 1)
    df2['DATE'] = pd.DatetimeIndex(df2['DATE'])
    recent = df2['DATE'].max()
    first = recent - timedelta(days = 42)
    df2 = df2.loc[df2['DATE'] > dt.now() - timedelta(days = 42),:]
    
    data = list(df2['T5YIE'].astype(float)/100)
    types = ['T5YIE']*len(df2['T5YIE']) 
    dates = list(df2['DATE'])
    
    data.extend( list(df2['T10YIE'].astype(float)/100))
    types.extend(['T10YIE']*len(df2['T10YIE']))
    dates.extend( list(df2['DATE']))
    for col in df1:
        data.extend(list(df1[col]))
        types.extend([col]*len(df1[col]))
        dates.extend([pd.NaT]*len(df1[col]))
    out = pd.DataFrame(data = {
            'type': types,
            'data': data,
            'date': dates
            })
    out = out.loc[out['data'] != 0,:]
    return out, recent.strftime('%Y-%m-%d'), first.strftime('%Y-%m-%d')

def makeData():
    df, recent, first = makedf()
    print(df)

    df['type'] = df['type'].apply(lambda x: xdict[x])
    # find the quartiles and IQR for each category
    groups = df.groupby('type')
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr
    
    # find the outliers for each category
    def outliers(group):
        gName = group.name
        return group[(group.data > upper.loc[gName]['data']) | (group.data < lower.loc[gName]['data'])]['data']
    out = groups.apply(outliers).dropna()
    
    # prepare outlier data for plotting, we need coordinates for every outlier.
    if not out.empty:
        outx = []
        outy = []
        for keys in out.index:
            outx.append(keys[0])
            outy.append(out.loc[keys[0]].loc[keys[1]])
    out = pd.DataFrame({
            'x': outx,
            'y': outy
            })
    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper.data = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'data']),upper.data)]
    lower.data = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'data']),lower.data)]
    def SEP():
        sep = pd.DataFrame({
                'qmax': [2.1,2.2,2.2], 
                'q3' : [1.9,2.1,2.1],
                'q2' : [1.8,2.0,2.0],
                'q1' : [1.8,2.0,2.0],
                'qmin' : [1.6, 1.9, 2.0]
                }, index = ['2019','2020','2021'])
        iqr = sep['q3'] - sep['q1']
        sep['upper'] = sep['q3'] + 1.5*iqr
        sep['lower'] = sep['q1'] - 1.5*iqr
        
        return sep/100
    data = pd.DataFrame({
            'q1': q1.data,
            'q2': q2.data,
            'q3': q3.data,
            'qmin': qmin.data,
            'qmax': qmax.data,
            'upper': upper.data,
            'lower': lower.data
            })
    data = data.append(SEP())
    
    return data, out


xdict = {
        '2019':'2019',
        '2020':'2020',
        '2021':'2021',
        '':'',
        'COREPCE2':'Nowcast', 
        'COREPCE3':'1 Quarter', 
        'COREPCE4':'2 Quarters', 
        'COREPCE5':'3 Quarters', 
        'COREPCE6':'1 Year', 
        ' ':' ',
        'T5YIE':'5 Years',
        'T10YIE':'10 Years'
        }
xlab = list(xdict.values())
#data, out = makeData()

ymax = float(data['qmax'].max())+ .004
ymin = float(data['qmin'].min())

# now we draw the chart
p = figure(width = 1400,
           title="Target👏The👏Forecast👏", 
           y_axis_label = 'Inflation Forecast', 
           y_range = (ymin, ymax), x_range = xlab)
xlab.pop(3)
xlab.pop(8)
# the order is slightly messed up
data = data.loc[xlab,:]

# stems
p.segment(xlab, data['upper'], xlab, data['q3'], line_color="black")
p.segment(xlab, data['lower'], xlab, data['q1'], line_color="black")

# boxes
p.vbar(xlab, 0.7, data['q2'], data['q3'], 
       fill_color='orange', line_color="black", alpha = .90)
p.vbar(xlab, 0.7, data['q1'], data['q2'], 
       fill_color='blue', line_color="black", alpha = .90)

# whiskers (almost-0 height rects simpler than segments)
p.rect(xlab, data['lower'], 0.2, 0.0001, line_color="black")
p.rect(xlab, data['upper'], 0.2, 0.0001, line_color="black")

# outliers

if not out.empty:
    print(out.empty)
    p.circle(out['x'], out['y'], size=6, color="#F38630", fill_alpha=0.6)


# Cosmetic stuff
p.line(['2019', '10 Years'], [.02,.02], color = 'black', line_dash = 'dashed')
p.line([' ', ' '], [0,.04], color = 'black')
p.line(['', ''], [0,.04], color = 'black')

text = ['Summary of Economic Projections',
        'PCE Inflation: March 20, 2019',
        'Survey of Professional Forecasters - PCE-Core Inflation:',
        ' 2019Q3, August 9, 2019',
        'TIPS Spread: last six weeks']
df = pd.DataFrame({
        'text':text,
        'y':[ymax - .002, ymax - .004, ymax - .002, ymax - .004, ymax - .002 ],
        'x': ['2019', '2019','Nowcast','Nowcast', '5 Years'],
        'xoff': [-50,-50,-100,-100,-100]
        })
source = ColumnDataSource(df)
labels = LabelSet(x = 'x', y = 'y', text = 'text',x_offset = 'xoff', 
                  source = source)
p.add_layout(labels)

p.xgrid.grid_line_color = None
p.yaxis.formatter=NumeralTickFormatter(format="0.00%")
p.yaxis[0].ticker.desired_num_ticks = 10
name = u'imgs/inf_corecast' + str(dt.now())[:10]
export_png(p,name + '.png')
p.xaxis.major_label_overrides = xdict

show(p)