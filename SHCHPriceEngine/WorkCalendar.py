# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 10:50:01 2020

@author: Xiangyu Wang 
"""

from datetime import date
from datetime import timedelta
from WindPy import w
#from workalendar.asia import China
import calendar

class SHCH_workCalendar(object):
    def __init__(self,workday = None,source = 'Wind',\
                 startDate = date.today() - timedelta(days = 5*365),\
                 endDate = date.today() + timedelta(days = 10*366)):
        self.start = startDate
        self.end = endDate
        if not workday:
            if source == 'Wind':
                if not w.isconnected():
                    w.start()
                self.workDay = self.getCalendarFromWind(startDate,endDate)
                if max(self.workDay) < endDate:
                    self.workDay = self.workDay + self.generateCalendar(start = max(self.workDay),end = endDate)
                    
            if source == 'Manual':
                pass
        else:
            self.workDay = workday
        return
    
    def getCalendarFromWind(self,startDate,endDate):
        wc = w.tdays(startDate,endDate,"TradingCalendar=NIB")
        print('日历载入成功')
        return([x.date() for x in wc.Data[0]])
        
        
    #----------------------------------------------------------------------
    # 生成日历
    def generateCalendar(self,Workday=[],Holiday=[],fixHoliday = [],\
                         start=date(2000,1,1),\
                         end=date(2050,1,1)):
        workDay = []
        for i in range((end - start).days):
            tmpDate = start + timedelta(i)
            # 如果是调整后工作日，则一定为工作日
            if tmpDate in Workday:
                workDay.append(tmpDate)
            # 如果是调整后节假日，则一定为节假日
            elif tmpDate in Holiday:
                next
            # 如果是固定节假日，则一定为节假日
            elif (tmpDate.month,tmpDate.day) in fixHoliday:
                next
            # 如果不是调整后工作日/节假日/固定节假日 则根据周末确定
            elif tmpDate.weekday() <= 4:
                workDay.append(tmpDate) 
        return(workDay)
        
    #----------------------------------------------------------------------
    def adjWorkDay(self,curD,option = False):
        adjDay = next(x for x in self.workDay if x >= curD)
        if not option:
            # 营业日调整，True时则为经调整的营业日准则
            return(adjDay)
        else:
            if adjDay.month != curD.month:
                return(self.findLastDay(curD))
            else:
                return(adjDay)
    
    def findLastDay(self,curD):
        adjDay = max(x for x in self.workDay if x < curD)
        return(adjDay)
    
    def findPaymentDate(self,curD,pmt,adjOption = None,endMonthOption = None):
        # pmt为月份 必须为list形式
        # 营业日调整规则
        if not adjOption:
            adjOption = [True] * len(pmt)
            
        # 月末规则    
        if not endMonthOption:
            endMonthOption = [True] * len(pmt)
        
        # 判断是否为月末
        todayMonDays =  calendar.monthrange(curD.year,curD.month)[1]
        if curD.day == todayMonDays:
            endFlag = True
        else:
            endFlag = False
            
        paymentDate = []

        for i in range(len(pmt)):
            y = (curD.month + pmt[i]) // 12
            m = (curD.month + pmt[i]) % 12
            monDays = calendar.monthrange(curD.year + y,m)[1]
            if curD.day > monDays:
                pdayTmp = date(curD.year + y,m,monDays)
                pday = self.adjWorkDay(pdayTmp,True)
            else:
                if endFlag and endMonthOption[i]:
                    pdayTmp = date(curD.year + y,m,monDays)
                    pday = self.adjWorkDay(pdayTmp,adjOption[i])
                else:
                    pdayTmp = date(curD.year + y,m,curD.day)
                    print(adjOption[i])
                    pday = self.adjWorkDay(pdayTmp,adjOption[i])      
            paymentDate.append(pday)
        return(paymentDate)

    #----------------------------------------------------------------------
    # 手动设定节假日
    def setCalSetting(self,Workday=None,Holiday=None,fixHoliday = None,\
                         start=None,\
                         end=None):
        if Workday:
            self.Workday = Workday
        else:
            self.Workday = []
        if Holiday:
            self.Holiday = Holiday
        else:
            self.Holiday = []
        if fixHoliday:
            self.fixHoliday = fixHoliday
        else:
            self.fixHoliday = []
        if start:
            self.start = start
        if end:
            self.end = end
        self.workDay = self.generateCalendar(self.Workday,self.Holiday,self.fixHoliday,self.start,self.end)
        return
        

if __name__ =='__main__':
    cal = SHCH_workCalendar()
    print(cal.adjWorkDay(date(2020,7,5)))
    print(cal.findLastDay(date(2020,7,5)))
    print(cal.findPaymentDate(date(2020,7,5),[2,6]))