# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 09:57:46 2020

@author: Xiangyu Wang
"""
# 计算标债估值引擎

from SHCHPriceEngine.WorkCalendar import SHCH_workCalendar
from SHCHPriceEngine.ContractMgr import BdfContractMgr
from SHCHPriceEngine.InterestRateCurve import curve

from WindPy import w

from datetime import date
import numpy as np
from scipy.optimize import fsolve


class priceEngine(object):
    def __init__(self,workCalendar = None,contractMgr = None):
        if not workCalendar:
            self.cal = SHCH_workCalendar()
        else:
            self.cal = workCalendar

        if not contractMgr:
            print('初始化Contract Manager')
            self.cm = BdfContractMgr(self.cal)
        else:
            self.cm = contractMgr

        self.curve = self.initCurve()
        self.tenor_start = self.curve.tenor_start
        self.tenor_end = self.curve.tenor_end
        
        self.priceDate = date.today()
        self.bondValuePara = {}
        self.curveBuildPara = {}
        self.bdfValuePara = {}

        # 估值数据信息
        self.bdfCode = self.cm.bdfCode
        self.bdfnum = len(self.bdfCode)

        self.bdfTodayPrice = np.zeros(self.bdfnum)
        self.bdfCfetPrice = np.zeros(self.bdfnum)
        self.bdfShchPrice = np.zeros(self.bdfnum)
        self.CfetIrr = np.zeros(self.bdfnum)
        self.ShchIrr = np.zeros(self.bdfnum)

        self.bondCode = [[item.cInfo['deliveryBond'][0].bondInfo['windCode'],\
                        item.cInfo['deliveryBond'][1].bondInfo['windCode']] for item in self.cm.contractList]
        self.bondName = [[item.cInfo['deliveryBond'][0].bondInfo['name'],\
                        item.cInfo['deliveryBond'][1].bondInfo['name']] for item in self.cm.contractList]            
        self.bondFutureYTM = np.zeros((self.bdfnum,2))
        self.bondTodayYTM = np.zeros((self.bdfnum,2))

        # 保存FR007数据
        #swap = self.getSwapCurveFromWind()
        #swap = self.curve.get
        #self.fr007 = self.getFr007()
        
    def getParameterFromUI(self):
        pass
        
    def outputDataToUI(self):
        pass

    
    #----------------------------------------------------------------------
    # 初始化利率曲线
    def initCurve(self):
        c = curve(self.cal)
        # 初始化利率曲线
        curveInfo = {'curveDate':date.today(),  
        'startDate' : [0,1,1,1,1,1,1],    
        'tenor':['ON','7D','1M','3M','6M','9M','1Y'],     
        'rate':np.ones(7) * 3 / 100,               
        'rateType':[1,1,1,2,2,2,2],           
        'basis':np.array([365,365,365,365,365,365,365])}

        setting = {'interpSpace':0, # 0 - continuous rate 1 - simple rate  2 - 'instantF' 
                   'innerInterpMethod':1,# 0 - constant Forward 1 - Linear 2-quadratic 3 - natural Cubic spline
                   'outterInterpMethod':1}
        c.loadSetting(setting)
        c.loadData(curveInfo)
        return(c)
    
    #----------------------------------------------------------------------
    # 获取Wind FR007互换利率曲线
    def getSwapCurveFromWind(self):
        today = self.priceDate.strftime("%Y-%m-%d")
        data = w.edb('M1001845,M1001846,M1004122,M1004123,M1004124,M1004125,M1004126',\
                     today,today,'Fill=Previous')
        swapRate = np.zeros(7)
        if len(data.Times) == 1:
            for i in range(len(swapRate)):
                swapRate[i] = data.Data[0][i]
        else:
            for i in range(len(swapRate)):
                swapRate[i] = data.Data[i][-1]
#        idTmp = np.where(np.array(data.Times) == date(today.year,today.month,today.day))
        return(swapRate)

    #----------------------------------------------------------------------
    # 从曲线获取FR007利率
    def getFr007(self):
        f_start = self.tenor_start[1]
        f_end = self.tenor_end[1]
        repo = self.curve.getForwardRate(f_start,f_end,365)
        return(repo)

    #----------------------------------------------------------------------
    # 注册回调函数
    def register(self,bondHandle = None, bdfHandle = None):
        if bondHandle:
            self.cm.registerBondCallback(bondHandle)
            
        if bdfHandle:
            self.cm.registerBdfCallback(bdfHandle)
        return
    
    #----------------------------------------------------------------------
    # 订阅Wind数据
    def subscribe(self):
        print('开始订阅...................................')
        self.cm.subscribeBdf()
        self.cm.subscribeBond()
        return

    #----------------------------------------------------------------------
    # 取消订阅
    def cancelSubscribe(self):
        self.cm.cancelSubscribe()
        print('取消订阅成功！！！！！！！！！！！！')
    
#    def loadCurve(self):
#        self.curve.
        
    #----------------------------------------------------------------------
    # 国开债价格计算公式
    def getCpFromDp(self,curDate,paymentDate,dp,coupon = 0.03,N = 100):
        nextId = next(i + 1 for i,d in enumerate(paymentDate[1:]) if d >= curDate)
        preId = nextId - 1
        period1 = (curDate - paymentDate[preId]).days
        # basis 距离结算日最近一次付息日与上一付息日之间的天数
        basis = (paymentDate[nextId] - paymentDate[preId]).days
        accuredInterest = coupon * N * period1 / basis
        return(dp - accuredInterest)
    
    
    def getDpFromYtm(self,curDate,paymentDate,r,coupon = 0.03, N= 100):
        # 尚待支付的支付周期
        nextId = next(i+1 for i,d in enumerate(paymentDate[1:]) if d >= curDate)
        outstandingPaymentDate = paymentDate[nextId:]

        # 贴现时间
        df_t = np.zeros(len(outstandingPaymentDate))
        basis0 = (paymentDate[nextId] - paymentDate[nextId - 1]).days
        df_t[0] =  (outstandingPaymentDate[0] - curDate).days / basis0
        for i in range(1,len(df_t)):
            df_t[i] = df_t[i-1] + 1

#        tau = np.array([item.days for item in np.diff(paymentDate[nextId - 1 :])]) / 365
#        tau = np.ones(len(tau))
        # 假设国开债票息计息基准均为A/A,计息基准为其他国开债用此公式可能出现错误
        cashflow = coupon * N 
        pv = sum(cashflow / ((1 + r) ** df_t)) + N / ((1 + r) ** df_t[-1])
        return(pv)
        
    
    def getDpFromCp(self,curDate,paymentDate,cp,coupon = 0.03,N = 100):
        nextId = next(i+1 for i,d in enumerate(paymentDate[1:]) if d >= curDate)
        preId = nextId - 1
        basis = (paymentDate[nextId] - paymentDate[preId]).days
        period1 = (curDate - paymentDate[preId]).days
        accuredInterest = coupon * N * period1 / basis  
        return(cp + accuredInterest)

    def getYtmFromDp(self,curDate,paymentDate,dp,coupon = 0.03,N = 100):
        def objFunc(ytm):
            f = self.getDpFromYtm(curDate,paymentDate,ytm,coupon, N) - dp
            return(f)
        rs = fsolve(objFunc,0.03)
        return(rs[0])
    
    #def getFuturePrice(self,today_cp,tenor,r = 0.03):
        # 根据债券当前净价，计算债券远期净价
        # BT = Bt exp(r(T-t))  tenor - T-t
    #    return(today_cp * (1 + r * tenor))

    def getFuturePrice(self,today,today_dp,bondInfo,deliveryDay,r = None,interestCurve = None,includeInterest = False):
        # 根据债券当前全价，计算债券远期全价
        # 注:估值日为T的全价，包含了当日需要支付的利息
        # BT = Bt exp(r(T-t)) - AI * (1+f*t)  tenor - T-t
        # 当参数includeInterest为TRUE时，计算结果包含了持有至交割日期间支付的利息
        # bondInfo['coupon']  bondInfo['paymentDate']
        if not interestCurve:
            interestCurve = self.curve
        # 确定今天至交割日期间的利息支付
        coupon = bondInfo['coupon']
        pmtDate = bondInfo['paymentDate'][1:]
        pmtId = np.where((np.array(pmtDate) <= deliveryDay) & (np.array(pmtDate) >= today))[0]
        if len(pmtId) == 0:
            interest_delDate = 0
        else:
            #pmtId = np.insert(pmtId,0,pmtId[0]-1)
            #print(pmtId)
            interest_delDate = np.zeros(len(pmtId))
            for i in range(len(pmtId)):
                pmtD = pmtDate[pmtId[i] + 1]
                startD = pmtDate[pmtId[i]]
                pmtTenor = (deliveryDay - pmtD).days / 365
                # 这里默认利息支付计息基准为A/A
                interestPaid = 100 * coupon 
                f = interestCurve.getForwardRate(pmtD,deliveryDay,365)
                interest_delDate[i] = interestPaid * (1 + f * (pmtTenor))
        int_total = np.sum(interest_delDate)
        # 今日到交割日剩余期限
        tenor = (deliveryDay - today).days / 365
        if not r:
            r = interestCurve.getRate(tenor,type = 1,basis = 365)
        future_dp = today_dp * (1 + r * tenor) - int_total
        if includeInterest:
            return(future_dp+int_total)
        return(future_dp)

    def getInterestFutureValue(self,today,bondInfo,deliveryDay,r = None,interestCurve = None):
        # 确定今天至交割日期间的利息支付在未来的价值
        if not interestCurve:
            interestCurve = self.curve
        # 确定今天至交割日期间的利息支付
        coupon = bondInfo['coupon']
        pmtDate = bondInfo['paymentDate'][1:]
        pmtId = np.where((np.array(pmtDate) <= deliveryDay) & (np.array(pmtDate) >= today))[0]
        if len(pmtId) == 0:
            interest_delDate = 0
        else:
            #pmtId = np.insert(pmtId,0,pmtId[0]-1)
            #print(pmtId)
            interest_delDate = np.zeros(len(pmtId))
            for i in range(len(pmtId)):
                pmtD = pmtDate[pmtId[i] + 1]
                startD = pmtDate[pmtId[i]]
                pmtTenor = (deliveryDay - pmtD).days / 365
                # 这里默认利息支付计息基准为A/A
                interestPaid = 100 * coupon 
                f = interestCurve.getForwardRate(pmtD,deliveryDay,365)
                interest_delDate[i] = interestPaid * (1 + f * (pmtTenor))
        int_total = np.sum(interest_delDate)
        return(int_total)
        
    #----------------------------------------------------------------------
    # 标债远期价格计算公式
    def bdfValuationCfets(self,y1,y2,repo,deliveryTenor,bondTenor,coupon = 0.03,N = 100):
        # 交易中心估值法
        r = (y1 + y2) / 2
        p = sum(N * coupon / (1 + r) ** np.arange(1,bondTenor + 1)) + N / (1 + r) ** bondTenor
        f = p * (1 + (repo - r) * deliveryTenor)
        return(f)
    
    def bdfValuationFair(self,futrueYtm,delieryTenor,bondTenor,coupon = 0.03,N = 100):
        # 远期收益率估值法
        f = sum(N * coupon / (1 + futrueYtm) ** np.arange(1,bondTenor + 1)) + N / (1 + futrueYtm) ** bondTenor
        return(f)

    # def getIRR(self,p,f,t,bond_today,bond_future):
    #     irr = (bond_future+(f-p)-bond_today)/bond_today	/t
    #     return(irr)
    def getIRR(self,p,f,t):
        return((f / p - 1) / t)
    #----------------------------------------------------------------------
    # 从UI更新债券估值
    def updateBondResult(self,bdfCode,bondName,todayYtmList = None,futureYtmList = None):
        for i in range(len(bdfCode)):
            bdfId = self.bdfCode.index(bdfCode[i])
            bid1 = self.bondName[bdfId].index(bondName[i][0])
            bid2 = self.bondName[bdfId].index(bondName[i][1])
            if todayYtmList:
                self.bondTodayYTM[bdfId][bid1] = todayYtmList[i][0]
                self.bondTodayYTM[bdfId][bid2] = todayYtmList[i][1]

            if futureYtmList:
                self.bondFutureYTM[bdfId][bid1] = futureYtmList[i][0]
                self.bondFutureYTM[bdfId][bid2] = futureYtmList[i][1]
        return

    #----------------------------------------------------------------------
    # 读取标债远期最新价格
    def getBdfLastPrice(self):
        pList = np.zeros(self.bdfnum)
        for i in range(self.bdfnum):
            cinfo = self.cm.contractList[i].cInfo
            pList[i] = cinfo['lastPrice']
        return(pList)

    def getBdfBidPrice(self):
        pList = np.zeros(self.bdfnum)
        for i in range(self.bdfnum):
            cinfo = self.cm.contractList[i].cInfo
            pList[i] = cinfo['bidPrice']
        return(pList)

    def getBdfAskPrice(self):
        pList = np.zeros(self.bdfnum)
        for i in range(self.bdfnum):
            cinfo = self.cm.contractList[i].cInfo
            pList[i] = cinfo['askPrice']
        return(pList)

    def getBdfMidPrice(self):
        pList = np.zeros(self.bdfnum)
        for i in range(self.bdfnum):
            cinfo = self.cm.contractList[i].cInfo
            pList[i] = (cinfo['bidPrice'] + cinfo['askPrice']) / 2
        return(pList)

if __name__ =='__main__':
    pe = priceEngine()

    
    
    
    
    