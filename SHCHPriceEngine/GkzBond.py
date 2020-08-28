# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:44:25 2020

@author: Xiangyu Wang
"""
from WindPy import w
import numpy as np

class gkzBond(object):
    def __init__(self,code = None,bondInfo = None, priceInfo = None,\
                 ):
        self.code = code
        # 获得债券信息
        if not bondInfo:
            self.getBondInfo()
        else:
            self.bondInfo = bondInfo

        # 获得价格信息  
        if not priceInfo:
            self.priceInfo = {'last':0.0, # 前收盘价
                              'priceTime':[],
                              'windCleanPrice':0.0,    # wind净价
                              'windDirtyPrice':0.0,    # wind全价
                              'windYield':0.0,
                              'bidPrice':0.0,
                              'bidYield':0.0,
                              'bidVolumn':0.0,
                              'askPrice':0.0,
                              'askVolumn':0.0,
                              'askYield':0.0,
                              'maclayDuration':0.0,
                              'valueInstitute':[],    # 估值机构名称
                              'valueDate':[],
                              'valueCleanPrice':0.0 ,        # 机构估值净价
                              'valueDirtyPrice':0.0,  
                              'valueYield' : 0.0}
        else:
            self.priceInfo = priceInfo

        self.histPrice = None
        self.histDate = None
        return
    
    
    def getBondInfo(self):
        d1 = w.wss(self.code,'sec_name,couponrate,carrydate,actualbenchmark,interestfrequency','N=0')
        d2 = w.wset('cashflow','windcode='+self.code+';field=cash_flows_date')
        dt = [d1.Data[2][i]] + [datetime.datetime.strptime(x,"%Y-%m-%d") for x in d2.Data[0]]
        self.bondInfo = {'windCode':self.code,
                 'name':d1.Data[0],
                 'coupon':d1.Data[1] / 100,
                 'paymentDate':[datetime.date(x.year,x.month,x.day) for x in dt],
                  'basis':d1.Data[3][i],
                 'interestfrequency':d1.Data[4][i]}
        return
    
    def updatePrice(self,newPriceDict):
        self.priceInfo.update(newPriceDict)
        return
    
#    def calcBondPrice(self,source = 1, price,calcDate,paymentDate,coupon = 0.03,N = 100):
#        # 计算债券 净价、全价、YTM,三者中有任意一个即可计算出另外两个
#        # source为计算的来源  1-净价  2-全价 3-YTM
#        
#        if not cp:
#            pass
#        elif not dp:
#            pass
#        elif not r:
#            pass
#        else:
#            print('missing parameter')
#        return{'valueCleanPrice':cp,'valueDirtyPrice':dp,'valueYield':r}
        




