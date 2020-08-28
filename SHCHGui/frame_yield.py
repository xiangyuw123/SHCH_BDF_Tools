# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 10:45:07 2020

@author: Xiangyu Wang
"""

import tkinter as tk
from tkinter import ttk

from .CalendarUI import calendarWidget
from SHCHPriceEngine.GkzBond import gkzBond
from SHCHPriceEngine.otherFunc import str2date,sim2cont


import numpy as np
import datetime

class yieldFrame(tk.LabelFrame):
    def __init__(self,master = None,engine = None):
        tk.LabelFrame.__init__(self, master,text = '可交割券收益率试算',font=('微软雅黑',12,'bold'))
        self.columnconfigure(0,weight = 1)
        
        self.pe = engine
        
        self.valueInstitute = tk.StringVar()
        self.valueInstitute.set('上清所估值')
        self.valueInstituteValue = ('手动录入净价','手动录入全价','手动录入收益率',\
                     '上清所估值','中债估值','中证估值','CFETS估值','Wind最新价格')
        
        self.date_str = tk.StringVar() # 估值日期

        # 记录了self.pe中的合约按照交割日近远排序的ID
        self.bdfId = np.argsort([item[-5:-3] for item in self.pe.cm.bdfCode])
        self.bdfnum = len(self.bdfId)

        # 表中变量
        self.bdfCode = []
        self.bondName = []
        # 债券估值变量 2 * len(bdf contract)
        self.today_cp = []
        self.today_dp = []
        self.today_ytm = []
        self.deliveryDay = [tk.StringVar(),tk.StringVar()]
        self.spotRate = [tk.DoubleVar(),tk.DoubleVar()]
        self.spread = []
        self.future_cp = []
        self.future_dp = []
        self.future_ytm = []
        
        # 初始化变量
        for i in range(len(self.pe.cm.contractList) * 2):
            self.bdfCode.append(tk.StringVar())
            self.bondName.append(tk.StringVar())
            self.today_cp.append(tk.DoubleVar())
            self.today_dp.append(tk.DoubleVar())
            self.today_ytm.append(tk.DoubleVar())
            self.spread.append(tk.DoubleVar())
            self.future_cp.append(tk.DoubleVar())
            self.future_dp.append(tk.DoubleVar())
            self.future_ytm.append(tk.DoubleVar())
            
            
            
        # 载入引擎变量
        self.setVariable()
        
        # 创建表格
        self.createTable()
        return

    def createTable(self):
        ############################################# 参数选择 #############################################
        frm1 = tk.Frame(self)
        for i in range(11):
            frm1.columnconfigure(i,weight = 1)
            
        tk.Label(frm1,text = '债券估值来源').grid(column = 0,row = 0,pady = 10,padx = 1)
        cmb_gkzSource = tk.ttk.Combobox(frm1,textvariable = self.valueInstitute,state = 'readonly',width = 12)
        cmb_gkzSource['values'] = self.valueInstituteValue
        cmb_gkzSource.bind("<<ComboboxSelected>>", self.cmb_valueSource_select)
        cmb_gkzSource.grid(column = 1, row = 0,pady = 10,padx = 1)
        
        tk.Label(frm1, text = '估值日期').grid(column = 2,row = 0,padx = 1,pady = 10)
        valueDate = tk.ttk.Combobox(frm1,textvariable = self.date_str,width = 12)
        valueDate.bind("<Button-1>", self.date_str_gain)
        valueDate.grid(column = 3, row = 0, padx = 0,pady = 10)
        
        tk.Label(frm1, text = '当季交割日期').grid(column = 4,row = 0,padx = 1,pady = 10)
        tk.Label(frm1, textvariable = self.deliveryDay[0]).grid(column = 5,row = 0,padx = 1,pady = 10)
        tk.Label(frm1, text = '当季交割日贴现率').grid(column = 6,row = 0,padx = 1,pady = 10)
        tk.Entry(frm1, textvariable = self.spotRate[0],width = 9).grid(column = 7,row = 0,padx = 1,pady = 10)

        
        tk.Label(frm1, text = '次季交割日期').grid(column = 8,row = 0,padx = 1,pady = 10)
        tk.Label(frm1, textvariable = self.deliveryDay[1]).grid(column = 9,row = 0,padx = 1,pady = 10)
        tk.Label(frm1, text = '次季交割日贴现率').grid(column = 10,row = 0,padx = 1,pady = 10)
        tk.Entry(frm1, textvariable = self.spotRate[1],width = 9).grid(column = 11,row = 0,padx = 1,pady = 10)
        frm1.grid(row = 0,column = 0,sticky = 'we')
        
        ############################################# 国开债表格 #############################################
        frm2 = tk.Frame(self)
        columnName = ('合约代码','交割券简称','估值日净价','估值日全价','估值日YTM','合约交割日',\
                      '交割日贴现率','额外借券成本','交割日净价','交割日全价','交割日YTM')
        for i in range(len(columnName)):
            frm2.columnconfigure(i,weight = 1)
        
        for i in range(len(columnName)):
            tk.Label(frm2,text = columnName[i]).grid(column = i,row = 0,padx = 1,pady = 5)
        
        width = 11
        rowId = 1
        for i in range(self.bdfnum):
            tk.Label(frm2,textvariable = self.bdfCode[i]).grid(column = 0,row = i + rowId)
            tk.Label(frm2,textvariable = self.bondName[i]).grid(column = 1,row = i+rowId)
            tk.Entry(frm2,textvariable = self.today_cp[i],width = width).grid(column = 2,row = i+rowId)
            tk.Entry(frm2,textvariable = self.today_dp[i],width = width).grid(column = 3,row = i+rowId)
            tk.Entry(frm2,textvariable = self.today_ytm[i],width = width).grid(column = 4,row = i +rowId)
            tk.Label(frm2,textvariable = self.deliveryDay[0]).grid(column = 5,row = i +rowId)
            tk.Label(frm2,textvariable = self.spotRate[0]).grid(column = 6,row = i+rowId)
            tk.Entry(frm2,textvariable = self.spread[i],width = width).grid(column = 7,row = i+rowId)
            tk.Label(frm2,textvariable = self.future_cp[i]).grid(column = 8,row = i+rowId)
            tk.Label(frm2,textvariable = self.future_dp[i]).grid(column = 9,row = i+rowId)
            tk.Label(frm2,textvariable = self.future_ytm[i]).grid(column = 10,row = i+rowId)

        for i in range(self.bdfnum,2*self.bdfnum):
            tk.Label(frm2,textvariable = self.bdfCode[i]).grid(column = 0,row = i + rowId)
            tk.Label(frm2,textvariable = self.bondName[i]).grid(column = 1,row = i+rowId)
            tk.Entry(frm2,textvariable = self.today_cp[i],width = width).grid(column = 2,row = i+rowId)
            tk.Entry(frm2,textvariable = self.today_dp[i],width = width).grid(column = 3,row = i+rowId)
            tk.Entry(frm2,textvariable = self.today_ytm[i],width = width).grid(column = 4,row = i +rowId)
            tk.Label(frm2,textvariable = self.deliveryDay[1]).grid(column = 5,row = i +rowId)
            tk.Label(frm2,textvariable = self.spotRate[1]).grid(column = 6,row = i+rowId)
            tk.Entry(frm2,textvariable = self.spread[i],width = width).grid(column = 7,row = i+rowId)
            tk.Label(frm2,textvariable = self.future_cp[i]).grid(column = 8,row = i+rowId)
            tk.Label(frm2,textvariable = self.future_dp[i]).grid(column = 9,row = i+rowId)
            tk.Label(frm2,textvariable = self.future_ytm[i]).grid(column = 10,row = i+rowId)
            
        ############################################# 试算按钮 #############################################
        rowId = rowId + 2 * len(self.pe.cm.contractList)
        tk.Button(frm2,text = "债券信息查询",command = self.queryBond).grid(column = 0,row = rowId+1, pady = 5,padx = 1,columnspan = 2)
        tk.Button(frm2,text = "估值日YTM试算",command = self.btn_calcTodayPrice).grid(column = 2,row = rowId+1, pady = 5,padx = 1,columnspan = 3,sticky = 'e')
        frmTmp = tk.Frame(frm2)
        tk.Label(frmTmp,text = "额外借券成本(+/-)").grid(column = 0,row = 0,sticky = 'e')
        tk.Button(frmTmp,text = "+10BP",command = self.addBps).grid(column = 1,row = 0,sticky = 'e')
        tk.Button(frmTmp,text = "-10BP",command = self.minusBps).grid(column = 2,row = 0,sticky = 'e')
        frmTmp.grid(column = 5, row = rowId+1,pady = 5,padx = 1,columnspan = 3,sticky = 'e')
        tk.Button(frm2,text = "交割日YTM试算",command = self.btn_calcDelPrice).\
        grid(column = len(columnName) - 3,row = rowId+1, pady = 5,padx = 1,columnspan = 3,sticky = 'e')
        frm2.grid(column = 0,row = 1,sticky = 'we')
        pass
        
        
    #----------------------------------------------------------------------
    #### 生成日历组件
    def date_str_gain(self,*args):
#        width, height = self.winfo_reqwidth() + 50, 50 #窗口大小
#        x, y = (self.winfo_screenwidth()  - width )/2, (self.winfo_screenheight() - height)/2
#        frm_gkz1.geometry('%dx%d+%d+%d' % (width, height, x, y )) #窗口位置居中
        [self.date_str.set(date)
        for date in [calendarWidget((500, 400), 'll').selection()] 
        if date]
        return
    
    #----------------------------------------------------------------------
    #### 读取引擎里数据，并更新UI数据
    def setVariable(self):
        # 估值日设定
        self.date_str.set(self.pe.cm.bondValueDate)
        
        # 交割日信息
        self.deliveryDay[0].set(self.pe.cm.contractList[self.bdfId[0]].cInfo['deliveryDate'].strftime('%Y-%m-%d'))
        self.deliveryDay[1].set(self.pe.cm.contractList[self.bdfId[-1]].cInfo['deliveryDate'].strftime('%Y-%m-%d'))
        
#        # 标债合约信息
        id = 0
        for item in self.bdfId:
            self.bdfCode[id].set(self.pe.cm.bdfCode[item])
            self.bdfCode[id+1].set(self.pe.cm.bdfCode[item])
            self.bondName[id].set((self.pe.cm.contractList[item].cInfo['deliveryBond'][0]).bondInfo['name'])
            self.bondName[id+1].set((self.pe.cm.contractList[item].cInfo['deliveryBond'][1]).bondInfo['name'])
            id = id + 2
        
        for item in self.spread:
            item.set(0)
        
        pass

    #----------------------------------------------------------------------
    #### 借券成本加减按钮函数
    def addBps(self):
        for item in self.spread:
            item.set(float(item.get()) + 10)
        return
    
    def minusBps(self):
        for item in self.spread:
            item.set(float(item.get()) - 10)
        return
    
    #----------------------------------------------------------------------
    #### 获取债券估值选择按钮
    def cmb_valueSource_select(self,*args):
        # 如果选择了从Wind上获取估值
        if self.valueInstitute.get() in self.valueInstituteValue[3:]:
            self.pe.cm.updateBondValue(self.valueInstitute.get(),\
                                       datetime.datetime.strptime(self.date_str.get(),"%Y-%m-%d"))
            # 更新估值信息
            for i in range(self.bdfnum):
                # 可交割券1
                b1 = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0]
                self.today_cp[2*i].set(b1.priceInfo['valueCleanPrice'])
                self.today_dp[2*i].set(b1.priceInfo['valueDirtyPrice'])
                self.today_ytm[2*i].set(b1.priceInfo['valueYield'])
                
                # 可交割券2
                b2 = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1]
                self.today_cp[2*i + 1].set(b2.priceInfo['valueCleanPrice'])
                self.today_dp[2*i + 1].set(b2.priceInfo['valueDirtyPrice'])
                self.today_ytm[2*i + 1].set(b2.priceInfo['valueYield'])            
                
            # 将估值信息上传至pe
            todayYtmList = []
            bdfcode = []
            bondname = []
            for i in range(self.bdfnum):
                bdfcode.append(self.bdfCode[2*i].get())
                bondname.append([self.bondName[2*i].get(),self.bondName[2*i+1].get()])
                todayYtmList.append([self.today_ytm[2*i].get(),self.today_ytm[2*i+1].get()])
            self.pe.updateBondResult(bdfcode,bondname,todayYtmList)
                
            if b1.priceInfo['valueCleanPrice'] == None:
                tk.messagebox.showwarning('提示','获取数据失败，请确认数据权限')
        return
    
    #----------------------------------------------------------------------
    #### 估值日YTM试算按钮
    def btn_calcTodayPrice(self):
        self.cmb_valueSource_select()
        valueDate = str2date(self.date_str.get())
        if self.valueInstituteValue.index(self.valueInstitute.get()) >=3:
            return
        if self.valueInstitute.get() == self.valueInstituteValue[0]:
            # 通过净价计算全价与YTM
            for i in range(self.bdfnum):
                # 可交割券1
                bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0].bondInfo
                cp = self.today_cp[2*i].get()
                # 计算全价
                dp = self.pe.getDpFromCp(valueDate, bondInfo['paymentDate'],cp,bondInfo['coupon'])
                self.today_dp[2 * i].set(dp)
                # 计算YTM
                ytm = self.pe.getYtmFromDp(valueDate,bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_ytm[2 * i].set(ytm*100)
                
                # 可交割券2
                bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1].bondInfo
                cp = self.today_cp[2*i + 1].get()
                # 计算全价
                dp = self.pe.getDpFromCp(valueDate, bondInfo['paymentDate'],cp,bondInfo['coupon'])
                self.today_dp[2*i + 1].set(dp)
                # 计算YTM
                ytm = self.pe.getYtmFromDp(valueDate,bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_ytm[2*i + 1].set(ytm*100)     
                
        elif self.valueInstitute.get() == self.valueInstituteValue[1]:
            # 通过全价计算净价与YTM
            for i in range(self.bdfnum):
                # 可交割券1
                bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0].bondInfo
                dp = self.today_dp[2*i].get()
                # 计算全价
                cp = self.pe.getCpFromDp(valueDate, bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_cp[2 * i].set(cp)
                # 计算YTM
                ytm = self.pe.getYtmFromDp(valueDate,bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_ytm[2 * i].set(ytm*100)

                # 可交割券2
                bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1].bondInfo
                dp = self.today_dp[2*i + 1].get()
                # 计算全价
                cp = self.pe.getCpFromDp(valueDate, bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_cp[2*i + 1].set(cp)
                # 计算YTM
                ytm = self.pe.getYtmFromDp(valueDate,bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_ytm[2*i + 1].set(ytm*100)   
            
        elif self.valueInstitute.get() == self.valueInstituteValue[2]:
            # 通过YTM计算净价与全价
            for i in range(self.bdfnum):
                # 可交割券1
                bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0].bondInfo
                ytm = self.today_ytm[2*i].get() / 100
                # 计算全价
                dp = self.pe.getDpFromYtm(valueDate,bondInfo['paymentDate'],ytm,bondInfo['coupon'])
                self.today_dp[2*i].set(dp)
                #计算净价
                cp = self.pe.getCpFromDp(valueDate, bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_cp[2 * i].set(cp)
                
                # 可交割券2
                bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1].bondInfo
                ytm = self.today_ytm[2*i+1].get() / 100

                # 计算全价
                dp = self.pe.getDpFromYtm(valueDate,bondInfo['paymentDate'],ytm,bondInfo['coupon'])
                self.today_dp[2*i+1].set(dp)

                # 计算净价
                cp = self.pe.getCpFromDp(valueDate, bondInfo['paymentDate'],dp,bondInfo['coupon'])
                self.today_cp[2*i + 1].set(cp)
                
        # 将估值信息上传至pe
        todayYtmList = []
        bdfcode = []
        bondname = []
        for i in range(self.bdfnum):
            bdfcode.append(self.bdfCode[2*i].get())
            bondname.append([self.bondName[2*i].get(),self.bondName[2*i+1].get()])
            todayYtmList.append([self.today_ytm[2*i].get(),self.today_ytm[2*i+1].get()])
        self.pe.updateBondResult(bdfcode,bondname,todayYtmList)
        return
    
    #----------------------------------------------------------------------
    #### 交割日YTM试算按钮
    def btn_calcDelPrice(self):
        valueDate = self.pe.priceDate # 今日 非估值日！
        for i in range(self.bdfnum):
            if i < self.bdfnum / 2:
                delD = str2date(self.deliveryDay[0].get())
                tenor = (delD - self.pe.priceDate).days
                r1 = self.spotRate[0].get() / 100 - self.spread[2 * i].get() / 10000
                r2 = self.spotRate[0].get() / 100 - self.spread[2 * i + 1].get() / 10000
            else:
                delD = str2date(self.deliveryDay[1].get())
                tenor = (delD - self.pe.priceDate).days
                r1 = self.spotRate[1].get() / 100 - self.spread[2 * i].get() / 10000
                r2 = self.spotRate[1].get() / 100 - self.spread[2 * i + 1].get() / 10000

            # 可交割券1
            bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0].bondInfo
            # step1 计算交割日净价
            tytm = self.today_ytm[2*i].get() / 100 # 通过YTM计算得到今日的全价（非估值日），再从全价计算得到今日净价，假设收益率不变
            tdp = self.pe.getDpFromYtm(valueDate,bondInfo['paymentDate'],tytm,bondInfo['coupon'])
            #tcp = self.pe.getCpFromDp(valueDate, bondInfo['paymentDate'],tdp,bondInfo['coupon'])
            fdp = self.pe.getFuturePrice(valueDate,tdp,bondInfo,delD,r1)
            self.future_dp[2 * i].set(round(fdp,4))

            # step2 计算交割日净价
            #全价转净价
            fcp = self.pe.getCpFromDp(delD,bondInfo['paymentDate'],fdp,bondInfo['coupon'],N = 100)
            self.future_cp[2 * i].set(round(fcp,4))
            # step3 计算交割日远期YTM
            fytm = self.pe.getYtmFromDp(delD,bondInfo['paymentDate'],fdp,bondInfo['coupon'])
            self.future_ytm[2 * i].set(round(fytm*100,4))
        
            # 可交割券2
            bondInfo = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1].bondInfo
            # step1 计算交割日净价
            tytm = self.today_ytm[2*i+1].get() / 100 # 通过YTM计算得到今日的全价（非估值日），再从全价计算得到今日净价，假设收益率不变
            tdp = self.pe.getDpFromYtm(valueDate,bondInfo['paymentDate'],tytm,bondInfo['coupon'])
            #tcp = self.pe.getCpFromDp(valueDate, bondInfo['paymentDate'],tdp,bondInfo['coupon'])
            fdp = self.pe.getFuturePrice(valueDate,tdp,bondInfo,delD,r2)
            self.future_dp[2*i + 1].set(round(fdp,4))

            # step2 计算交割日全价
            #全价转净价
            fcp = self.pe.getCpFromDp(delD,bondInfo['paymentDate'],fdp,bondInfo['coupon'],N = 100)
            self.future_cp[2 * i + 1].set(round(fcp,4))
            # step3 计算交割日远期YTM
            fytm = self.pe.getYtmFromDp(delD,bondInfo['paymentDate'],fdp,bondInfo['coupon'])
            self.future_ytm[2 * i + 1].set(round(fytm*100,4))
            
            
        # 将估值信息上传至pe
        todayYtmList = []
        futureYtmList = []
        bdfcode = []
        bondname = []
        for i in range(self.bdfnum):
            bdfcode.append(self.bdfCode[2*i].get())
            bondname.append([self.bondName[2*i].get(),self.bondName[2*i+1].get()])
            futureYtmList.append([self.future_ytm[2*i].get(),self.future_ytm[2*i+1].get()])
            todayYtmList.append([self.today_ytm[2*i].get(),self.today_ytm[2*i+1].get()])
        self.pe.updateBondResult(bdfcode,bondname,todayYtmList = todayYtmList,futureYtmList = futureYtmList)
        return
    
    
    #----------------------------------------------------------------------
    #### 查询债券信息
    def queryBond(self):
        top = tk.Toplevel()
        top.title('债券信息查询')
        
        column = ('code','name','startDate','tenor','coupon','pmtDate')
        tree = ttk.Treeview(top,show = 'headings',columns = column,height = 8)      # #创建表格对象        
        
        columnName = ('债券代码','债券简称','起息日','期限(年)','票面利率','利息支付日')
        for i in range(len(tree['columns'])):
            tree.heading(i, text = columnName[i])
            tree.column(i,width=100,minwidth = 70)        
        tree.column(i,width=600,minwidth = 500)        
        for i in range(len(self.pe.cm.bondCode)):
            binfo = self.pe.cm.deliveryBondList[i].bondInfo
            coupon = round(binfo['coupon']*100,4)
            startDate = binfo['paymentDate'][0].strftime("%Y-%m-%d")
            tenor = len(binfo['paymentDate']) - 1
            pmtDate = ''
            for item in binfo['paymentDate'][1:]:
                pmtDate = pmtDate + item.strftime("%Y%m%d") + ','     
            tree.insert('',i,values = (binfo['windCode'],binfo['name'],startDate,tenor,coupon,pmtDate))
            
        tree.pack()
        pass
        
    
    
    
    
    
    
    