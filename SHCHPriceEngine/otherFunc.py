# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 11:25:56 2020

@author: Xiangyu Wang
"""

from datetime import date,datetime
import numpy as np

def str2date(datestr):
    dt = datetime.strptime(datestr,"%Y-%m-%d")
    return(date(dt.year,dt.month,dt.day))
    
def sim2cont(s,t):
    return( np.log(1 + s * t) / t)

