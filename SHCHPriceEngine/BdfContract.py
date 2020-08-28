# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 14:20:36 2020

@author: Xiangyu Wang
"""


class bdfContract(object):
    def __init__(self,code,contractInfo = None):
        
        self.cInfo = {'windCode':[],
                      'name':[],           # 合约代码
                      'issueDate':[],     # 上市日
                      'lastTradeDate':[],  # 最后交易日
                      'deliveryDate':[],   # 交割日
                      'basicPrice':[],     # 挂牌基准价
                      'deliveryBond':[],   # 可供交割的债券，为未来实物交割留下接口
                      'ctdBond':[],        # 最廉价交割券
                      'priceTime':[],
                      'lastPrice':0.0,# 合约最新价 
                      'bidPrice':0.0,
                      'bidVolumn':0.0,
                      'askPrice':0.0,
                      'askVolumn':0.0,
                      'value1':0.0,
                      'value2':0.0}# 最新价时间 
        if contractInfo:
            self.cInfo.update(contractInfo)
        return

        
    def getContractInfo(self):
        pass
    
    def updateCtdBond(self):
        pass

    def updateInfo(self,cinfo):
        self.cInfo.update(cinfo)
        return


    

