# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 16:26:34 2020

@author: XiangyuWang 
"""

import tkinter as tk
import numpy as np

class bdfValueFrame(tk.LabelFrame):
    def __init__(self,master = None, engine = None):
        tk.LabelFrame.__init__(self, master,text = '标债远期估值试算',font=('微软雅黑',12,'bold'))
        self.columnconfigure(0,weight = 1)
        
        self.pe = engine
        
        self.priceSource = tk.StringVar()
        self.priceSource_value = ('Wind最新价','标债报价-买价','标债报价-均值','标债报价-卖价')
        
#        self.irrbond = tk.StringVar()
#        self.irrbond_value = ('','','','','')

        # 记录了self.pe中的合约按照交割日近远排序的ID
        # 该表格上第一行的合约信息为self.pe.cm.bdfCode[self.bdfId[0]]
        self.bdfId = np.argsort([item[-5:-3] for item in self.pe.cm.bdfCode])
        self.bdfnum = len(self.bdfId)
        
        # 表格中变量
        self.bdfCode = []
        self.bdfPrice = []
        self.bond1Name = []
        self.bond2Name = []
        self.bond1w = []
        self.bond2w = []
        self.bond1ytm = []
        self.bond2ytm = []
        self.ytm_shch = []
        self.price_shch = []
        self.irr_shch = []
        self.bond1r = []
        self.bond2r = []
        self.ytm_cfets = []
        self.price_cfets = []
        self.irr_cfets = []
        
        # 期限策略的组合价值,空头可交割金额
        self.portToday = []
        self.portFuture = []
        self.delAmount = []
        
        for i in range(len(self.pe.cm.contractList)):
            self.bdfCode.append(tk.StringVar())
            self.bdfPrice.append(tk.DoubleVar())
            self.bond1Name.append(tk.StringVar())
            self.bond2Name.append(tk.StringVar())
            self.bond1w.append(tk.DoubleVar())
            self.bond2w.append(tk.DoubleVar())
            self.bond1ytm.append(tk.DoubleVar())
            self.bond2ytm.append(tk.DoubleVar())
            self.ytm_shch.append(tk.DoubleVar())
            self.price_shch.append(tk.DoubleVar())
            self.irr_shch.append(tk.DoubleVar())
            self.bond1r.append(tk.DoubleVar())
            self.bond2r.append(tk.DoubleVar())
            self.ytm_cfets.append(tk.DoubleVar())
            self.price_cfets.append(tk.DoubleVar())
            self.irr_cfets.append(tk.DoubleVar())
            self.portToday.append(tk.DoubleVar())
            self.portFuture.append(tk.DoubleVar())
            self.delAmount.append(tk.DoubleVar())
            
        # 资金成本，用于对比期限策略IRR是否超过期限策略资金成本
        self.capitalCost = tk.DoubleVar()
        
        # 国开债今天和交割日的估值，通过本界面的YTM得到
        self.bond_today = np.zeros([len(self.pe.cm.contractList),2])
        self.bond_future = np.zeros([len(self.pe.cm.contractList),2])
        
        
        self.initData()
#        self.setVariable()
        
        self.createTable()
        
    def createTable(self):
        ############################################# 参数选择 #############################################
        frm1 = tk.Frame(self)
        frm1.columnconfigure(8,weight = 1)
        rowId = 0
        tk.Label(frm1,text = '标债最新价来源').grid(column = 0,row = 0,pady = 10,padx = 5)
        cmb_priceSource = tk.ttk.Combobox(frm1,textvariable = self.priceSource,state = 'readonly',width = 12)
        cmb_priceSource['values'] = self.priceSource_value
        cmb_priceSource.bind("<<ComboboxSelected>>", self.resetPrice)
        cmb_priceSource.grid(column = 1, row = 0,pady = 10,padx = 1)

        btn_resetPrice = tk.Button(frm1,text = '价格更新',width = 9,command = self.resetPrice)
        btn_resetPrice.grid(column = 2, columnspan = 2, row = rowId,padx = 5)
        
        btn_resetYTM = tk.Button(frm1,text = '收益率重置',width = 9,command = self.resetYield)
        btn_resetYTM.grid(column = 4, columnspan = 2, row = rowId,padx = 5)
        
        btn_resetWeight = tk.Button(frm1,text = '权重重置',width = 9,command = self.resetWeight)
        btn_resetWeight.grid(column = 6, columnspan = 2, row = rowId,padx = 5)
        
        tk.Label(frm1,text = '期现策略：买入交割券+做空标债远期').grid(column = 8,row = rowId,padx = 5,sticky = 'e')
        tk.Label(frm1,text = '参考资金成本').grid(column = 9,row = rowId,padx = 5,sticky = 'e')
        tk.Entry(frm1,textvariable = self.capitalCost,width = 9).grid(column = 10,row = rowId,padx = 5,sticky = 'e')

        # 暂仅支持 现券为两只交割券组合的形式计算IRR
        # tk.Label(frm1,text = 'IRR现券选择').grid(column = 8,row = 0,padx = 5)
        # cmb_IrrBond = tk.ttk.Combobox(frm1,textvariable = self.irrbond,state = 'readonly',width = 12)
        
        frm1.grid(row = 0,column = 0,sticky = 'we')

        ############################################# 国开债表格 #############################################
        frm2 = tk.Frame(self)        
        columnName = ('合约代码','合约最新价','券1简称','券2简称',\
                      '券1远期YTM','券2远期YTM','虚拟券YTM','标债估值',\
                          '券1权重','券2权重','券1YTM',\
                      '券2YTM','现券现值','组合未来估值','隐含IRR')
        for i in range(len(columnName)):
            frm2.columnconfigure(i,weight = 1)
            
        rowId = 1
        tk.Label(frm2,text = '合约信息',bg = '#BDB76B').grid(column = 0, row = rowId, columnspan = 4,sticky = 'we')
        tk.Label(frm2,text = '远期收益率估值',bg = '#708090').grid(column = 4, row = rowId, columnspan = 4,sticky = 'we')
        tk.Label(frm2,text = '期限套利IRR',bg = '#EEE8AA').grid(column = 8, row = rowId, columnspan = 7,sticky = 'we')

        rowId = rowId + 1
        for i in range(len(columnName)):
            # if i <= 3:
            #     colorCode = '#BDB76B'
            # elif i >=4 and i <= 7:
            #     colorCode = '#708090'
            # elif i >=8 and i <= 14:
            #     colorCode = '#EEE8AA'
            tk.Label(frm2,text = columnName[i]).grid(column = i,row = rowId,padx = 1,pady = 5)
        
        # 组件列表，供修改背景色用
        self.lbl_ShchPrice = []
        self.lbl_irr = []
        
        rowId = rowId + 1  
        width = 8
        ety_w1 = [] # weight函数
        ety_w2 = []
        for i in range(len(self.bdfCode)):
            tk.Label(frm2,textvariable = self.bdfCode[i]).grid(column = 0,row = i + rowId)
            tk.Entry(frm2,textvariable = self.bdfPrice[i],width = width).grid(column = 1,row = i+rowId)
            tk.Label(frm2,textvariable = self.bond1Name[i]).grid(column = 2,row = i+rowId)
            tk.Label(frm2,textvariable = self.bond2Name[i]).grid(column = 3,row = i+rowId)
            
            # 远期收益率估值
            tk.Entry(frm2,textvariable = self.bond1ytm[i],width = width).grid(column = 4,row = i+rowId)
            tk.Entry(frm2,textvariable = self.bond2ytm[i],width = width).grid(column = 5,row = i+rowId)
            tk.Label(frm2,textvariable = self.ytm_shch[i]).grid(column = 6,row = i+rowId)
            self.lbl_ShchPrice.append(tk.Label(frm2,textvariable = self.price_shch[i]))
            self.lbl_ShchPrice[i].grid(column = 7,row = i+rowId)
            
            # 可交割券1 2 的权重
            ety_w1.append(tk.Entry(frm2,textvariable = self.bond1w[i],width = 6))
            ety_w1[i].grid(column = 8,row = i +rowId)
            ety_w2.append(tk.Entry(frm2,textvariable = self.bond2w[i],width = 6))
            ety_w2[i].grid(column = 9,row = i +rowId)
            # 绑定事件，债券1权重与债券2权重和为1    
            # lambda 函数  parameter来自于surrounding时  为指针，需通过此方式进行改进
            def functionFactory(i):
                return([lambda event:self.linkw2(i,event),lambda event:self.linkw1(i,event)])
            ety_w1[i].bind("<Return>", functionFactory(i)[0])
            ety_w2[i].bind("<Return>", functionFactory(i)[1])
            
            # 可交割券1 2 的估值日收益率
            tk.Entry(frm2,textvariable = self.bond1r[i],width = 6).grid(column = 10,row = i+rowId)
            tk.Entry(frm2,textvariable = self.bond2r[i],width = 6).grid(column = 11,row = i+rowId)

            # 组合现值与未来价值、IRR
            tk.Label(frm2,textvariable = self.portToday[i]).grid(column = 12,row = i+rowId)
            tk.Label(frm2,textvariable = self.portFuture[i]).grid(column = 13,row = i+rowId)
            self.lbl_irr.append(tk.Label(frm2,textvariable = self.irr_shch[i]))
            self.lbl_irr[i].grid(column = 14,row = i+rowId)
            
        # 记录原有背景色
        self.oriBgColor = self.lbl_ShchPrice[0].cget("bg")
        self.oriFgColor = self.lbl_ShchPrice[0].cget('fg')
        
        # 估值试算按钮
        rowId = rowId + len(self.bdfCode)
        btn_tryValue = tk.Button(frm2,text = "估值试算",width = 14,command = self.calcBdfValue)
        btn_tryValue.grid(row = rowId,column = 0,columnspan = 3,sticky = 'w', padx = 5,pady = 10)
        frm2.grid(row = 1,column = 0,sticky = 'we')

    #----------------------------------------------------------------------
    # 初始化数据  
    def initData(self):
#        self.priceSource.set(self.priceSource_value[1])
        for i,item in enumerate(self.bdfId):
            self.bdfCode[i].set(self.pe.cm.bdfCode[item])
            self.bond1Name[i].set((self.pe.cm.contractList[item].cInfo['deliveryBond'][0]).bondInfo['name'])
            self.bond2Name[i].set((self.pe.cm.contractList[item].cInfo['deliveryBond'][1]).bondInfo['name'])
        self.resetWeight()
        self.resetPrice()
        self.resetYield()
        self.capitalCost.set(0.0)
        return
        
    #----------------------------------------------------------------------
    # 重置权重
    def resetWeight(self):
        print('权重更新')
        for i in range(self.bdfnum):
            self.bond1w[i].set(0.5)
            self.bond2w[i].set(0.5)
        return
    
    def linkw1(self,i,event):
        self.bond1w[i].set(round(1 - self.bond2w[i].get(),2))
        return
    
    def linkw2(self,i,event):
        self.bond2w[i].set(round(1 - self.bond1w[i].get(),2))
        return
        
    #----------------------------------------------------------------------
    # 重置收益率
    def resetYield(self):
        print('收益率更新')
        for i,item in enumerate(self.bdfId):
            bid1 = self.pe.bondName[item].index(self.bond1Name[i].get())
            bid2 = self.pe.bondName[item].index(self.bond2Name[i].get())
            self.bond1ytm[i].set(self.pe.bondFutureYTM[item][bid1])
            self.bond2ytm[i].set(self.pe.bondFutureYTM[item][bid2])
            self.bond1r[i].set(self.pe.bondTodayYTM[item][bid1])
            self.bond2r[i].set(self.pe.bondTodayYTM[item][bid2])
        return
    
    
    #----------------------------------------------------------------------
    # 重置价格
    def resetPrice(self,*args):
        print('价格更新')
        if self.priceSource.get() == self.priceSource_value[2]:
            for i,item in enumerate(self.bdfId):
                self.bdfPrice[i].set(round(0.5 * self.pe.cm.contractList[item].cInfo['bidPrice'] + \
                             0.5 * self.pe.cm.contractList[item].cInfo['askPrice'],4))        
            return
        
        if self.priceSource.get() == self.priceSource_value[0]:
            dictName = 'lastPrice'
        elif self.priceSource.get() == self.priceSource_value[1]:
            dictName = 'bidPrice'
        elif self.priceSource.get() == self.priceSource_value[3]:
            dictName = 'askPrice'
        else:
            return
        for i,item in enumerate(self.bdfId):
            self.bdfPrice[i].set(round(self.pe.cm.contractList[item].cInfo[dictName],4))
        pass    
    
    #----------------------------------------------------------------------
    # 估值试算按钮
    def calcBdfValue(self):
         #repo = self.pe.getFr007()
        changeBackFunc = []
        for i in range(self.bdfnum):
            # 合约剩余期限
            delDate = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryDate']
            curDate = self.pe.priceDate
            deliveryTenor = (delDate - curDate).days / 365
            # 交割券期限
            bondTenor = int(self.bdfCode[i].get()[:-8][3:])
            # 最新估值
            p = self.bdfPrice[i].get()
            
            # 可交割券的权重
            w1 = self.bond1w[i].get()
            w2 = self.bond2w[i].get()
            
            # 债券今天估值和交割日估值
            today_r1 = self.bond1r[i].get() / 100
            today_r2 = self.bond2r[i].get() /100
            future_r1 = self.bond1ytm[i].get() / 100
            future_r2 = self.bond2ytm[i].get() / 100
            binfo1 = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0].bondInfo
            binfo2 = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1].bondInfo
            self.bond_today[i,0] = self.pe.getDpFromYtm(curDate,binfo1['paymentDate'],today_r1,binfo1['coupon'])
            self.bond_today[i,1] = self.pe.getDpFromYtm(curDate,binfo2['paymentDate'],today_r2,binfo2['coupon'])
            self.bond_future[i,0] = self.pe.getDpFromYtm(delDate,binfo1['paymentDate'],future_r1,binfo1['coupon']) + \
                self.pe.getInterestFutureValue(curDate,binfo1,delDate)
            self.bond_future[i,1] = self.pe.getDpFromYtm(delDate,binfo2['paymentDate'],future_r2,binfo2['coupon']) + \
                self.pe.getInterestFutureValue(curDate,binfo2,delDate)
            btoday = w1 * self.bond_today[i,0] + w2 * self.bond_today[i,1]
            bfuture = w1 * self.bond_future[i,0] + w2 * self.bond_future[i,1]
            self.portToday[i].set(round(btoday,4))
            
            # # step1 交易中心估值（不做运算）
            # r = 0.5 * today_r1 + 0.5 * today_r2
            # futurePrice = self.pe.bdfValuationCfets(self.bond1r[i].get()/100,self.bond2r[i].get()/100,\
            #                                         repo,deliveryTenor,bondTenor)
            # irr = self.pe.getIRR(futurePrice,p,deliveryTenor,btoday,bfuture)
            # self.ytm_cfets[i].set(round(r,4))
            # self.price_cfets[i].set(round(futurePrice,4))
            # self.irr_cfets[i].set(round(irr*100,4))
            
            # step2 远期收益率估值
            # futureYtm = self.bond1w[i].get() * future_r1 + self.bond2w[i].get() * future_r2 修改如下
            futureYtm = 0.5 * future_r1 + 0.5 * future_r2
            fp_shch = self.pe.bdfValuationFair(futureYtm,deliveryTenor,bondTenor)
            portfolioFutureValue = bfuture + p - fp_shch
            irr_shch = self.pe.getIRR(btoday,portfolioFutureValue,deliveryTenor)
            self.ytm_shch[i].set(round(futureYtm*100,4))
            self.price_shch[i].set(round(fp_shch,4))
            self.irr_shch[i].set(round(irr_shch*100,4))
            self.portFuture[i].set(round(portfolioFutureValue,4))
            if i ==0:
                print(btoday)
                print(portfolioFutureValue)
        
            # step3 标债估值结果高亮显示，IRR与资金成本对比，IRR大于资金成本字体为红色，IRR小于资金成本字体为绿色
            def functionFactory(i):
                return([lambda:self.changeBackPrice(i),lambda:self.changeBackIrr(i)])
            
            self.lbl_ShchPrice[i].configure(bg='red')
            self.lbl_ShchPrice[i].configure(fg='white')
            self.lbl_ShchPrice[i].after(800,functionFactory(i)[0])
            self.lbl_irr[i].configure(bg='red')
            self.lbl_irr[i].configure(fg='white')
            self.lbl_irr[i].after(800,functionFactory(i)[1])
        return
    
    def changeBackPrice(self,i):
        self.lbl_ShchPrice[i].configure(bg=self.oriBgColor)
        self.lbl_ShchPrice[i].configure(fg=self.oriFgColor) 
    def changeBackIrr(self,i):
        self.lbl_irr[i].configure(bg = self.oriBgColor)
        if self.irr_shch[i].get() < self.capitalCost.get():
            self.lbl_irr[i].configure(fg = 'green')
        else:
            self.lbl_irr[i].configure(fg = 'red')
    
    
    