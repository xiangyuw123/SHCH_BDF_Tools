# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 17:04:56 2020

@author: Xiangyu Wang 
"""
from WindPy import w
import requests
import pandas as pd
import datetime
from .GkzBond import gkzBond
from .BdfContract import bdfContract
from .WorkCalendar import SHCH_workCalendar
import numpy as np

# 负责标债合约信息初始化
# 储存标债合约信息
# 储存并更新可交割国开债信息

class BdfContractMgr(object):
    def __init__(self,ShchCalendar,valueInst = None):
        self.calendar = ShchCalendar
        self.bdfCode = []
        self.contractList = []    # 所有标债远期合约列表
        self.bondCode = []              
        self.deliveryBondList = []  # 所有标债远期可交割债券信息
        self.initDate = datetime.date.today()  # 记录初始化日期
        
        self.instName = ['手动输入','上清所估值','中债估值','中证估值','CFETS估值','Wind最新价格']
        # 估值机构，0为手动收入，1上清所估值，2中债估值，3wind最新收益率
        if not valueInst:
            self.bondValueInst = 4
        else:
            self.bondValueInst = self.instName.index(valueInst)
            
        # 估值机构在wind中对应代码
        self.windValueCodeMap = ['net_shc,dirty_shc,yield_shc',# 上清所估值代码
                                 'net_cnbd,dirty_cnbd,yield_cnbd',  # 中债估值代码
                                 'net_csi1,dirty_csi1,yield_csi1', # 中证估值
                                 'net_cfets,dirty_cfets,yield_cfets']    # 交易中心估值
        # 债券估值日期
        self.bondValueDate = self.calendar.findLastDay(self.initDate)
        
        # 从网站爬虫获取信息
        self.__getDataFromUrl()
        print('网站爬虫成功')
        self.requestId = []     # 订阅行情记录
        
        # 从Wind读取债券信息
        self.updateBondValue()
        
        # 回调函数列表
        self.subBondHandle = []
        self.subBdfHandle = []
        return
    
    #----------------------------------------------------------------------
    def addContract(self,bdf):
        self.contractList.append(bdf)
        return
    
    #----------------------------------------------------------------------
    def updateBondList(self):
        pass
    
    #----------------------------------------------------------------------
    def __getDataFromUrl(self):
        url="https://www.shclearing.com/bdf/cpxm/hyxxb/"
        r = requests.get(url,headers={'User-Agent': 'Custom'})    #发送请求
        r.encoding = r.apparent_encoding
        df = pd.read_html(r.text)
        
        # 可交割债券信息
        bondCode = []
        for item in df[0][4][1:]:
            bondCode.append(item+'.IB')
        bondCode = list(set(bondCode))  
        
        # 从Wind获取债券信息
        d1 = w.wss(bondCode,'sec_name,couponrate,carrydate,actualbenchmark,interestfrequency','N=0') # 证券简称，票息
        for i in range(len(bondCode)):
            print(bondCode[i])
            d2 = w.wset('cashflow','windcode='+bondCode[i]+';field=cash_flows_date')
            dt = [d1.Data[2][i]] + [datetime.datetime.strptime(x,"%Y-%m-%d") for x in d2.Data[0]]
            bInfoTmp = {'windCode':bondCode[i],
                 'name':d1.Data[0][i],
                 'coupon':d1.Data[1][i] / 100,
                 'paymentDate':[datetime.date(x.year,x.month,x.day) for x in dt],
                 'basis':d1.Data[3][i],
                 'interestfrequency':d1.Data[4][i]}
            bTmp = gkzBond(bondCode[i],bInfoTmp,{})
            self.deliveryBondList.append(bTmp)
        print('现金流表获取成功')
        
        # 标债合约信息
        bdfCode = []
        for item in df[0][0][1:len(df[0][0]):2]:
            bdfCode.append(item+'.IB')
        
        bdfWindInfo = w.wss(bdfCode,'sec_name,lastdelivery_date','N=0')
        # 将交割日格式由datetime转为date
        date_delivery = [datetime.date(x.year,x.month,x.day) for x in bdfWindInfo.Data[1]]
        for i in range(len(bdfCode)):
            bid1 = bondCode.index(df[0][4][2*i+1] + '.IB')
            bid2 = bondCode.index(df[0][4][2*i+2] + '.IB')
            cInfo = {'windCode':bdfCode[i],
                     'name':bdfWindInfo.Data[0][i],           # 合约代码
                      'issueDate':df[0][1][1+2*i],     # 上市日
                      'lastTradeDate':df[0][2][1+2*i],  # 最后交易日
                      'deliveryDate':date_delivery[i],   # 交割日
                      'basicPrice':df[0][3][1+2*i],     # 挂牌基准价
                      'deliveryBond':[self.deliveryBondList[bid1],
                                      self.deliveryBondList[bid2]],   # 可供交割的债券，为未来实物交割留下接口
                      'ctdBond':[self.deliveryBondList[bid1],
                                 self.deliveryBondList[bid2]]   # 可供交割的债券，为未来实物交割留下接口
                      }
            
            bdfTmp = bdfContract(bdfCode[i],cInfo)
            self.contractList.append(bdfTmp)
        self.bondCode = bondCode
        self.bdfCode = bdfCode
        return
    
    #----------------------------------------------------------------------
    # 订阅债券价格回调函数
    def subscribeBond(self):
        fieldsMap = {'rt_last_cp':'windCleanPrice',
                     'rt_last_dp':'windDirtyPrice',
                     'rt_last_ytm':'windYield',
                     'rt_bid1':'bidPrice',
                     'rt_bid_price1ytm':'bidYield',
                     'rt_bsize1':'bidVolumn',
                     'rt_ask1':'askPrice',
                     'rt_ask_price1ytm':'askYield',
                     'rt_asize1':'askVolumn',
                     'rt_mac_duration':'maclayDuration',
                     'rt_pre_close':'last'}

        def windCallBack(data):
            print(data)
            for i,wBondCode in enumerate(data.Codes):
                binfo = {'priceTime':data.Times}
                for j,field in enumerate(data.Fields):
                    bInfoField = fieldsMap[field.lower()]
                    binfo[bInfoField] = data.Data[j][i]
                codeId = self.bondCode.index(wBondCode)
                self.deliveryBondList[codeId].updatePrice(binfo)
            
            for item in self.subBondHandle:
                try:
                    item(data)
                except:
                    print('handle'+item+'错误')

        bsub = w.wsq(self.bondCode,"rt_last_cp,rt_last_dp,rt_last_ytm,\
                     rt_bid1,rt_bid_price1ytm,rt_bsize1,rt_ask1,rt_ask_price1ytm,rt_asize1,\
                     rt_mac_duration,rt_pre_close",func=windCallBack)
        self.requestId.append(bsub.RequestID)
        return
    #                'windCleanPrice':data.Data[0][i],    # wind净价
#                          'windDirtyPrice':data.Data[1][i],    # wind全价
#                          'windYield':data.Data[2][i],
#                          'bidPrice':data.Data[3][i],
#                          'bidYield':data.Data[4][i],
#                          'bidVolumn':data.Data[5][i],
#                          'askPrice':data.Data[6][i],
#                          'askYield':data.Data[7][i],
#                          'askVolumn':data.Data[8][i],
#                          'maclayDuration':data.Data[9][i],
#                          'last':data.Data[10][i]
    #----------------------------------------------------------------------
    # 订阅标债远期价格回调函数
    def subscribeBdf(self):
        fieldsMap = {'rt_latest':'lastPrice',
                    'rt_bid1':'bidPrice',
                    'rt_bsize1':'bidVolumn',
                    'rt_ask1':'askPrice',
                    'rt_asize1':'askVolumn'}
        def windCallBack(data):
            print(data)
            for i,wBdfCode in enumerate(data.Codes):
                cinfo = {'priceTime':data.Times[0]}
                for j,field in enumerate(data.Fields):
                    # 确定更新的信息
                    cInfoField = fieldsMap[field.lower()]
                    cinfo[cInfoField] = data.Data[j][i]
#                        'midPrice':data.Data[0][i],# 合约最新价 
#                          'bidPrice':data.Data[1][i],
#                          'bidVolumn':data.Data[2][i],
#                          'askPrice':data.Data[3][i],
#                          'askVolumn':data.Data[4][i]
                # 确定获取标债代码
                codeId = self.bdfCode.index(wBdfCode)
                self.contractList[codeId].updateInfo(cinfo)
                
            for item in self.subBdfHandle:
                try:
                    item(data)
                except:
                    print('handle'+item+'错误')
                    
        bsub = w.wsq(self.bdfCode,"rt_latest,rt_bid1,rt_bsize1,rt_ask1,rt_asize1",\
                     func=windCallBack)
        self.requestId.append(bsub.RequestID)
        return
            
    #----------------------------------------------------------------------
    # 向回调函数中加入函数
    def registerBondCallback(self,handle):
        self.subBondHandle.append(handle)
        
    def registerBdfCallback(self,handle):
        self.subBdfHandle.append(handle)
    
    #----------------------------------------------------------------------
    # 取消订阅
    def cancelSubscribe(self):
        w.cancelRequest(0)  
        self.subBondHandle.clear()
        self.subBdfHandle.clear()
        self.requestId.clear()
        return
    
    #----------------------------------------------------------------------
    # 更新债券估值信息
    def updateBondValue(self,valueInst = None,valueDay = None,bInfoList = {}):
        # 如果直接输入债券信息bInfo，则忽略ValueInst和ValueDay直接根据bInfo 更新债券信息
        # bInfoList格式为{bondcode:bInfo}
        if len(bInfoList) > 0:
            for key in bInfoList:
                id = self.bondCode.index(key)
                self.deliveryBondList[id].updatePrice(bInfoList[key])
            return
        
        # 如果未输入bInfo，则根据参数更新债券价格
        if not valueInst:
            valueInst = self.bondValueInst
        else:
            valueInst = self.instName.index(valueInst)
        
        if not valueDay:
            valueDay = self.bondValueDate
            
        if valueInst == 0:
            # 如果是估值机构为手动输入
            pass
        elif not valueInst == len(self.instName):
            # 如果估值机构是上清估值、中债估值、CFETS估值
            windCode = self.windValueCodeMap[valueInst-1]
            windInfo = w.wss(self.bondCode,windCode,'tradeDate='+valueDay.strftime('%Y%m%d')+';date='+valueDay.strftime('%Y%m%d'),'credibility=1')
#            print(windInfo)
            for i in range(len(self.deliveryBondList)):
                bInfo = {'valueInstitute':valueInst,    # 估值机构名称
                              'valueDate':valueDay,
                              'valueCleanPrice':windInfo.Data[0][i],        # 机构估值净价
                              'valueDirtyPrice': windInfo.Data[1][i],  
                              'valueYield' : windInfo.Data[2][i]}
                self.deliveryBondList[i].updatePrice(bInfo)
        else:
            # 如果估值机构是Wind最新估值
            for i in range(len(self.deliveryBondList)):
                bInfo = {'valueInstitute':valueInst,    # 估值机构名称
                              'valueDate':valueDay,
                              'valueCleanPrice':self.deliveryBondList[i].priceInfo['windCleanPrice'] ,        # 机构估值净价
                              'valueDirtyPrice': self.deliveryBondList[i].priceInfo['windDirtyPrice'],  
                              'valueYield' : self.deliveryBondList[i].priceInfo['windYield']}
                self.deliveryBondList[i].updatePrice(bInfo)


        self.bondValueInst = valueInst
        self.valueDay = valueDay
        return
                    
if __name__ =='__main__': 
    cal = SHCH_workCalendar()
    test = BdfContractMgr(cal)
    def subBond(data):
        print(data)
        
    def subBdf(data):
        print(data)
        
    test.subscribeBond(subBond)
    test.subscribeBdf(subBdf)
    test.cancelSubscribe()
    
        
        
         
        
         
        
        