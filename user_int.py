# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 14:20:42 2020

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

print('Last 30 days available: ')
df = pd.read_csv('data/cme_database.csv')
days = d[]
#%%