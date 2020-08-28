# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 18:25:10 2020

@author: Xiangyu Wang
"""

from scipy import interpolate
import datetime
import numpy as np

class curve(object):
    def __init__(self,workCalendar,inputData = None, setting = None):

        self.resetCurve()
        
        self.setting = {'interpSpace':0, # 0 - continuous rate 1 - simple rate  2 - 'instantF' 
                        'innerInterpMethod':1,# 0 - constant Forward 1 - Linear 2-quadratic 3 - natural Cubic spline
                        'outterInterpMethod':1}# 0 - 水平外插 1-线性外插 2-自然外插

        self.cal = workCalendar
        if setting:
            self.loadSetting(setting)
            
        if inputData:
            self.loadData(inputData)
            
        try:
            self.buildCurve()
        except:
            print('曲线未构造')
            
    #----------------------------------------------------------------------
    # 确认起息日
    def getStartDate(self,today,startDate):
        sd = []
        for item in startDate:
            if item == 0:
                sd.append(today)
            else:
                sd.append(self.cal.adjWorkDay(today + datetime.timedelta(item)))
        return(sd)
        
    #----------------------------------------------------------------------
    # 确认期限对应的到期日
    def getEndDate(self,startDate,tenorList):
        endDate = []
        if len(startDate) == 1:
            startDate = [startDate] * len(tenorList)

        if isinstance(tenorList[0],str):
            for i in range(len(tenorList)):
                tmp = tenorList[i]
                if tmp == 'ON':
                    endDate.append(self.cal.adjWorkDay(startDate[i] + datetime.timedelta(1)))
                elif tmp[-1] == 'D':
                    endDate.append(self.cal.adjWorkDay(startDate[i] + datetime.timedelta(int(tmp[:-1]))))
                elif tmp[-1] == 'M':
                    endDate = endDate + self.cal.findPaymentDate(startDate[i],[int(tmp[:-1])])
                elif tmp[-1] == 'Y':
                    endDate = endDate + self.cal.findPaymentDate(startDate[i],[int(tmp[:-1]) * 12])
        else:
            for i in range(len(tenorList)):
                endDate.append(self.cal.adjWorkDay(startDate[i] + datetime.timedelta(tenorList[i])))

        return endDate
            
    #----------------------------------------------------------------------
    # 确认期限据今天日期
    def getTenor(self,today,endDate = None,startDate = None,tenorList = None):
        if not endDate:
            endDate = self.getEndDate(startDate,tenorList)
        tenor = []
#        print(endDate)
        for item in endDate:
            tenor.append((item - today).days)
        return(np.array(tenor))
    
    #----------------------------------------------------------------------
    # 载入插值设置
    def loadSetting(self,setting):
        self.setting.update(setting)
        return
    
    #----------------------------------------------------------------------
    # 载入市场数据
    def loadData(self,data):
        '''
        data = {'curveDate':[],  datetime
        'startDate' : [0,0],     np.array
        'tenor':['ON','3M'],     np.array or str
        'rate':[],               np.array
        'rateType':[0,1,2],           int
        'basis':360 or 365          np.array
        }
        '''
        # 重置曲线
        self.resetCurve()
        
        # 更新曲线日期 datetime.date
        self.curveDate = data['curveDate']
        
        # 确定各个期限的起息日 datetime.date
        if isinstance(data['startDate'][0],int):
            self.tenor_start = self.getStartDate(self.curveDate,data['startDate'])
        else:
            self.tenor_start = data['startDate']
            
        # 确定各个期限的到期日和到期日距今日天数 datetime.date int
        endDate = self.getEndDate(self.tenor_start,data['tenor'])
        self.tenor_end = endDate
        self.tenor = self.getTenor(self.curveDate,endDate)
        
        # 装入曲线
        if len(data['basis']) == 1:
            basis = np.repeat(data['basis'],len(data['tenor']))
        else:
            basis = data['basis']
            
        if len(data['rateType']) == 1:
            self.rateType = np.repeat(data['rateType'],len(data['tenor']))
        else:
            self.rateType = data['rateType'] 
        
        self.inputRate = data['rate'] / basis * self.curveBasis
        return
            
    #----------------------------------------------------------------------
    # 构造曲线 得到各期限点贴现因子  插值整条曲线
    def buildCurve(self):
        self.df = np.ones(len(self.tenor))
            
        # 单利/连续复利得到贴现因子
        for i in [i for i,x in enumerate(self.rateType) if x == 0 or x == 1]:
            t = (self.tenor_end[i] - self.tenor_start[i]).days 
            if self.rateType[i] == 0 :
                df2Start = np.exp(-self.inputRate[i] * t / self.curveBasis)
            else:
                df2Start = 1 / (1 + self.inputRate[i] * t / self.curveBasis)
            startDays = self.tenor[i] - t
            if startDays != 0:
                startId = np.where(self.tenor == startDays)
                self.df[i] = df2Start * self.df[startId]
            else:
                self.df[i] = df2Start
                
        # 互换利率拔靴得到远期利率 注：互换利率最远期限的所有支付日 为所有互换利率对应的EndDate
        idList = [i for i,x in enumerate(self.rateType) if x == 2]
        paymentDate = []
        swapRate = []
        for i in idList:
            paymentDate.append(self.tenor_end[i])
            swapRate.append(self.inputRate[i])
        paymentDate.insert(0,self.tenor_start[i])
        tau = np.array([x.days for x in np.diff(paymentDate)]) / self.curveBasis
        df2Start = self.bootstrap(np.array(swapRate),tau)
        startDays = (paymentDate[0] - self.curveDate).days
        if startDays != 0:
            startId = np.where(self.tenor == startDays)
            self.df[idList] = df2Start * self.df[startId]
        else:
            self.df[idList] = df2Start
            
        # 得到插值点
        if self.setting['interpSpace'] == 0:
            interpRate = np.log(1 / self.df) / (self.tenor / self.curveBasis)
        elif self.setting['interpSpace'] == 1:
            interpRate = (1 / self.df - 1) / (self.tenor / self.curveBasis)
        else:
            print('暂不支持')
        
        # 设置插值函数
#        'innerInterpMethod':1,# 0 - constant Forward 1 - Linear 2 - natural Cubic spline
#        'outterInterpMethod':1
        if self.setting['outterInterpMethod'] == 0:
            extra = (interpRate[0],interpRate[-1])
        else:
            extra = 'extrapolate'

        if self.setting['innerInterpMethod'] == 0:
            interpFunc = interpolate.interp1d(self.tenor,interpRate,'zero',bounds_error = False,fill_value = (interpRate[0],interpRate[-1]))
        elif self.setting['innerInterpMethod'] == 1:
            interpFunc = interpolate.interp1d(self.tenor,interpRate,'linear',fill_value = extra)
        elif self.setting['innerInterpMethod'] == 2:
            def interpFunc(xx):
                yy = np.zeros(len(xx))
                id1 = [i for i,x in enumerate(xx) if x < self.tenor[0]]
                id2 = [i for i,x in enumerate(xx) if x > self.tenor[-1]]
                id3 = [i for i in range(len(xx)) if i not in id1+id2]
                f = interpolate.CubicSpline(self.tenor,interpRate,bc_type = 'natural')
                yy[id3] = f(xx[id3])
                
                if self.setting['outterInterpMethod'] == 0:
                    yy[id1] = self.interpRate[0]
                    yy[id2] = self.interpRate[-1]
                elif self.setting['outterInterpMethod'] == 1:
                    f1 = interpolate.interp1d(self.tenor,interpRate,'linear',fill_value = 'extrapolate')
                    yy[id1+id2] = f1(xx[id1+id2])
                elif self.setting['outterInterpMethod'] == 2:
                    yy[id1+id2] = f(xx[id1+id2])
                return(yy)
        
        # 插值整条曲线
        allT = np.arange(self.tenor[-1]) + 1
        allCurve = interpFunc(allT)
        if self.setting['interpSpace'] == 0:
            self.allCurve_df = np.exp(-allCurve * (allT / self.curveBasis))
        elif self.setting['interpSpace'] == 1:
            self.allCurve_df = 1 / ( 1 + allCurve * allT / self.curveBasis)
        else:
            print('暂不支持')
        return
            
    #----------------------------------------------------------------------
    # 互换利率拔靴
    def bootstrap(self,swapRate,tau):
        df = np.zeros(len(swapRate))
        for i in range(len(swapRate)):
            tmp = 0
            for j in range(i):
                tmp = tmp + swapRate[i] * tau[j] * df[j]
            df[i] = (1 - tmp) / (1 + swapRate[i] * tau[i])
        return(np.array(df))
    
    #----------------------------------------------------------------------
    # 重置曲线
    def resetCurve(self):
        self.curveDate = []
        self.tenor = []             # 每个期限对应的天数
        self.tenor_name = []        # 每个期限名称
        self.tenor_start = []   # 每个期限的起息日 datetime
        self.tenor_end = [] # 每个期限的到期日
        self.inputRate = []  # simple spot rate
        self.rateType = [] # 最后一次载入的曲线类型 0-cont rate 1-simple rate 2- swap rate
        self.df = []       # 关键期限点的贴现因子
        
        self.allCurve_para = []
        self.allCurve_simple = [] # 以天为单位的全期限曲线
        self.allCurve_cont = [] # 以天为单位的全期限曲线
        self.allCurve_df = []
        self.curveBasis = 360
        return

    #----------------------------------------------------------------------
    # 获得曲线上数据函数
    def getDF(self,day):
        if len(self.allCurve_df) == 0:
            self.buildCurve()
        if day > len(self.allCurve_df):
            # 超出曲线外部分  水平外插连续复利得到
            r = np.log(1 / self.allCurve_df[-1]) / len(self.allCurve_df) * self.curveBasis
            return(np.exp(-r * day / self.curveBasis))
        else:
            return(self.allCurve_df[day-1])
    
    def getRate(self,day,type = 0,basis = 365):
        df = self.getDF(day)
        if type == 0:
            # 连续复利
            return(np.log(1 / df) / day * basis)
        elif type == 1:
            # 单利
            return((1 / df - 1) / day * basis)


    def getDiscountCurve(self):
        return(self.allCurve_df)
        
    def getContCurve(self):
        if len(self.allCurve_cont) == 0:
            self.allCurve_cont = np.log(1 / self.allCurve_df) / (np.arange(1,self.tenor[-1]+1) / self.curveBasis)
        return(self.allCurve_cont)
    
    def getSimpleCurve(self):
        if len(self.allCurve_simple) == 0:
            self.allCurve_simple = (1 / self.allCurve_df -1) / (np.arange(1,self.tenor[-1]+1) / self.curveBasis)
        return(self.allCurve_simple)
        
    def getKeySpotRate(self, rateType = 1):
        # rateType 为输出利率形式 0-连续复利 1-单利
        if len(self.df) == 0:
            return(np.zeros(len(self.inputRate)))
            
        if rateType == 0:
            r = np.log(1 / self.df) / (self.tenor / self.curveBasis)
        elif rateType == 1:
            r = (1 / self.df - 1) / (self.tenor / self.curveBasis)
        return(r)
        
    def getForwardRate(self,start,end, basis = 360):
        t1 = (start - self.curveDate).days
        t2 = (end - self.curveDate).days
        d1 = self.getDF(t1)
        d2 = self.getDF(t2)
        f = (d1 / d2 - 1) / (t2 - t1) * basis
        return(f)
    
if __name__ =='__main__':
    pass
    
    
    