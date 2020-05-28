# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 12:10:45 2020

@author: ethan
"""


from datetime import datetime as dt

import pandas as pd

from bokeh.io import export_png,output_file,show
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter, Label, LabelSet, ColumnDataSource
from bokeh.models.tickers import SingleIntervalTicker
from bokeh.layouts import column

from fredData import get_FFR, get_SEP, get_TIPS
from CME_DataNoAPI import get_futures
from SPF_NoAPI import get_SPF

FOMC_MEETINGS = [dt(2020, 1, 29),
         dt(2020, 3, 18),
         dt(2020, 4, 29),
         dt(2020, 6, 10),
         dt(2020, 7, 29),
         dt(2020, 9, 16),
         dt(2020, 11, 5),
         dt(2020, 12, 15),
         dt(2021, 1, 29),
         dt(2021, 3, 18),
         dt(2021, 4, 29),
         dt(2021, 6, 10),
         dt(2021, 7, 29),
         dt(2021, 9, 16),
         dt(2021, 11, 5),
         dt(2021, 12, 15)
         ]

def makeData():
    df = pd.concat([PCE, TIPS])
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
    data = pd.DataFrame({
            'q1': q1.data,
            'q2': q2.data,
            'q3': q3.data,
            'qmin': qmin.data,
            'qmax': qmax.data,
            'upper': upper.data,
            'lower': lower.data
            })
    data = data.append(SEP)
    
    return data, out

def make_x_axis_labels(SEP):
    xdict = []
    for date in SEP.index.tolist():
        xdict.append((str(date), str(date)))
    xdict = xdict + [
            ('',''),
            ('COREPCE2','Nowcast'),
            ('COREPCE3','1 Quarter'),
            ('COREPCE4','2 Quarters'),
            ('COREPCE5','3 Quarters'),
            ('COREPCE6','1 Year'),
            (' ',' '),
            ('TIPS_5','5 Years'),
            ('TIPS_10','10 Years')
            ]
    xdict = dict(xdict)
    return xdict

def set_up(x, y):
    xrng = (dt.now(), x.max())
    if y.min() < 0:
        yrng = (y.min() - .0025, y.max() + .0025)
    else:
        yrng = (0, y.max() + .0025)
        
    x = x.dropna()
    y = y.dropna()
    
    return(x,y,xrng,yrng)
    
def FFR_chart(data, low, up, name):
    xdata, ydata, xrng, yrng = set_up(data['Month'], data['Last'])

    now = dt.now().strftime('%B, %d, %Y')
    
    p = figure(width = 1400, height = int(700*2/3),
               title="CME 30-Day Federal Fund Futures: {}".format(now), 
               x_axis_label = 'Date', x_axis_type = 'datetime',
               y_axis_label = 'Implied Federal Funds Rate', 
               y_range = yrng, x_range = xrng)

    
    p.line(xdata,ydata, color = 'blue')
    p.line(xrng, [low,low], color ='Black', line_dash = 'dashed')
    p.line(xrng, [up,up], color ='Black', line_dash = 'dashed')
    
    xpos = len(xdata) // 2
    ypos = (low + up)/2
    
    lbl = Label(x=xdata[xpos], y=ypos - .0005,
                 text='Current FFR Target Range')
    p.add_layout(lbl)
    
    for date in FOMC_MEETINGS:
        p.line([date,date], yrng, color = 'black', alpha = 0.3)
    for y in range(0, int(yrng[-1]*400)):
        p.line(xrng, y/400, color = 'grey', alpha = 0.3)
    
    ytik = SingleIntervalTicker()
    ytik.interval = .0025
    p.yaxis[0].ticker = ytik
    p.xaxis[0].ticker.desired_num_ticks = len(xdata)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.yaxis.formatter=NumeralTickFormatter(format="0.00%")
    
    export_png(p, filename = name + '.png')
    
    return p

def inf_chart():
    xlab = list(xdict.values())
    data, out = makeData()
    
    
    ymax = float(data['qmax'].max())+ .004
    ymin = float(data['qmin'].min())
    
    # now we draw the chart
    p = figure(width = 1400,
               title="Target👏The👏Forecast👏", 
               y_axis_label = 'Inflation Forecast', 
               y_range = (ymin, ymax), x_range = xlab)
    xlab.pop(4)
    xlab.pop(9)
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
        p.circle(out['x'], out['y'], size=6, color="#F38630", fill_alpha=0.6)
    
    
    # Cosmetic stuff
    p.line(['2019', '10 Years'], [.02,.02], color = 'black', line_dash = 'dashed')
    p.line([' ', ' '], [0,.04], color = 'black')
    p.line(['', ''], [0,.04], color = 'black')
    
    text = ['Summary of Economic Projections',
            'PCE-Core Inflation: December 11, 2019',
            'Survey of Professional Forecasters',
            'PCE-Core Inflation: {}Q{}'.format(PCE.year,PCE.quarter),
            'TIPS Spread: last six weeks']
    df = pd.DataFrame({
            'text':text,
            'y':[ymax - .002, ymax - .004, ymax - .002, ymax - .004, ymax - .002 ],
            'x': ['2019', '2019','Nowcast','Nowcast', '5 Years'],
            'xoff': [-40,-40,-90,-90,-90]
            })
    source = ColumnDataSource(df)
    labels = LabelSet(x = 'x', y = 'y', text = 'text',x_offset = 'xoff', 
                      source = source)
    p.add_layout(labels)
    
    p.xgrid.grid_line_color = None
    p.yaxis.formatter=NumeralTickFormatter(format="0.00%")
    p.yaxis[0].ticker.desired_num_ticks = 10
    name = u'imgs/inf_forecast' + str(dt.now())[:10]
    export_png(p, filename = name + '.png')
    p.xaxis.major_label_overrides = xdict

    return p

name = u'imgs/ffr' + str(dt.now())[:10]
output_file(name + '.html')

futures = get_futures()
FFR = get_FFR()
SEP = get_SEP()
PCE = get_SPF()
TIPS = get_TIPS()
xdict = make_x_axis_labels(SEP)

col = column(FFR_chart(futures,FFR['FFR_lower'],FFR['FFR_upper'], name), inf_chart())
show(col)
#%%







