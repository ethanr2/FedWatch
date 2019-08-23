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
from bokeh.models import NumeralTickFormatter, Label,ColumnDataSource
from bokeh.models.tickers import FixedTicker, SingleIntervalTicker
from bokeh.layouts import row, column

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

import os 

def makedf():
    df1 = pd.read_excel('data/2019-08-20/spf.xlsx', sheet_name = 'PCE')
    df1 = df1.loc[(df1['YEAR'] == 2019) & (df1['QUARTER'] == 3), ['PCE2', 'PCE6']].dropna()/100
    df2 = pd.read_csv('data/2019-08-20/T5YIE.csv')
    df2['DATE'] = pd.DatetimeIndex(df2['DATE'])
    recent = df2['DATE'].max()
    first = recent - timedelta(days = 42)
    df2 = df2.loc[df2['DATE'] > dt.now() - timedelta(days = 42),:]
    
    data = list(df2['T5YIE'].astype(float)/100)
    types = ['T5YIE']*len(df2) 
    dates = list(df2['DATE'])
    
    for col in df1:
        data.extend(list(df1[col]))
        types.extend([col]*len(df1[col]))
        dates.extend([pd.NaT]*len(df1[col]))
    out = pd.DataFrame(data = {
            'type': types,
            'data': data,
            'date': dates
            })

    return out, recent.strftime('%Y-%m-%d'), first.strftime('%Y-%m-%d')


df, recent, first = makedf()
print(df)
xlab = {
        'PCE2':'SPF - PCE Inflation Nowcast: 2019Q3', 
        'PCE6':'SPF - PCE Inflation 1 Year: 2019Q3',
        'T5YIE':'TIPS Spread - 5 Years: {} to {}'.format(first, recent)
        }
df['type'] = df['type'].apply(lambda x: xlab[x]) 
xlab = list(xlab.values())
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
p = figure(width = 1400,
           title="Target👏The👏Forecast👏", 
           y_axis_label = 'Inflation Forecast', 
           y_range = (0,.03), x_range = xlab)
# if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
qmin = groups.quantile(q=0.00)
qmax = groups.quantile(q=1.00)
upper.data = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,'data']),upper.data)]
lower.data = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'data']),lower.data)]

# stems
p.segment(xlab, upper.data, xlab, q3.data, line_color="black")
p.segment(xlab, lower.data, xlab, q1.data, line_color="black")

# boxes
p.vbar(xlab, 0.7, q2.data, q3.data, 
       fill_color='orange', line_color="black", alpha = .90)
p.vbar(xlab, 0.7, q1.data, q2.data, 
       fill_color='blue', line_color="black", alpha = .90)

# whiskers (almost-0 height rects simpler than segments)
p.rect(xlab, lower.data, 0.2, 0.0001, line_color="black")
p.rect(xlab, upper.data, 0.2, 0.0001, line_color="black")

# outliers

if not out.empty:
    print(out.empty)
p.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)

p.xgrid.grid_line_color = None
p.yaxis.formatter=NumeralTickFormatter(format="0.00%")
p.yaxis[0].ticker.desired_num_ticks = 20
name = u'imgs/inf_corecast' + str(dt.now())[:10]
export_png(p,name + '.png')

show(p)