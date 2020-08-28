# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 10:41:19 2020

@author: Xiangyu Wang
"""


import tkinter as tk
from tkinter import ttk
from .CalendarUI import calendarWidget
from datetime import datetime

class gkzFrame(tk.LabelFrame):
    def __init__(self,master = None,pe = None):
        tk.LabelFrame.__init__(self, master,text = '国开债价格监控',font=('微软雅黑',12,'bold'))
        self.pe = pe
        for i in range(2):
            self.rowconfigure(i, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.gkzSourceValue = ['上清所估值','中债估值','中证估值','CFETS估值']
        self.updateBondValueTimes = tk.IntVar()
        ############################ 价格来源选择Frame1 ############################
        self.frm_gkz1 = tk.Frame(self)
        for i in range(1):
            self.frm_gkz1.rowconfigure(i, weight=1, minsize=30)
        for i in range(4):
            self.frm_gkz1.columnconfigure(i, weight=0, minsize=30)
        self.frm_gkz1.columnconfigure(4, weight=1, minsize=30)
        
        # 国开债来源下拉框
        tk.Label(self.frm_gkz1,text = '估值机构').grid(column = 0,row = 0,padx = 0,pady = 1)
        self.valueInstitute = tk.StringVar()
        self.valueInstitute.set(self.gkzSourceValue[0])
        self.cmb_gkzSource = tk.ttk.Combobox(self.frm_gkz1,textvariable = self.valueInstitute,state = 'readonly')
        self.cmb_gkzSource['values'] = self.gkzSourceValue
        self.cmb_gkzSource.grid(column = 1, row = 0, padx = 0,pady = 1)
        
        # 估值日期选择
        tk.Label(self.frm_gkz1, text = '估值日期').grid(column = 2,row = 0,padx = 0,pady = 1)
        self.date_str = tk.StringVar()
        self.date_str.set(self.pe.cm.bondValueDate)
        self.valueDate = tk.ttk.Combobox(self.frm_gkz1,textvariable = self.date_str)
        self.valueDate.bind("<Button-1>", self.date_str_gain)
        self.valueDate.grid(column = 3, row = 0, padx = 0,pady = 1)
        
        # 更新估值按钮
        tk.Button(self.frm_gkz1, text = '估值更新', command = self.updateBondValue).grid(column = 4,row = 0,padx = 0,pady = 1)
        
        self.frm_gkz1.grid(column = 0,row = 0,pady = 1,sticky = 'we')
        
        ############################ 价格监控Frame ############################
        self.frm2 = tk.Frame(self)
        self.frm2.rowconfigure(0, weight=1)
        self.frm2.rowconfigure(1, weight=0, minsize=30)
        self.frm2.columnconfigure(0, weight=1, minsize=30)
        self.frm2.columnconfigure(1, weight=0, minsize=30)

        columns =  ("code", "name", "last",'newCp','newDp','newYTM','duration','valueCp','valueDp',\
                    'valueYtm','bid_price','bid_volumn','ask_price','ask_volumn')
        
        self.tree = ttk.Treeview(self.frm2,show = 'headings',columns = columns)      #创建表格对象
        
        colName = ('可交割券','简称','前收','Wind净价','Wind全价','Wind收益率',\
                   '久期','估值净价','估值全价','估值收益率','买1价','买1量','卖1价','卖1量')

        for i in range(len(self.tree['columns'])):
            self.tree.heading(i, text = colName[i])
            self.tree.column(i,width=100,minwidth = 70)

        self.insertGkzBond() # 插入国开债信息
        
        vsb = ttk.Scrollbar(self.frm2, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frm2, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand = vsb.set)
        self.tree.configure(xscrollcommand = hsb.set)

                        
        # pack everything
        vsb.grid(column = 1,row = 0,sticky = 'ns')
        hsb.grid(column = 0,row = 1,sticky = 'we')
        self.tree.grid(column = 0,row = 0,sticky = 'nswe')
        self.frm2.grid(column = 0,row = 1,pady = 1,sticky = 'nswew')
        ############################ 加入实时更新回调函数 ############################
        def bondCallBack(data):
            self.updateBondPrice()
            return
        self.pe.register(bondHandle = bondCallBack)
        return
    
    #----------------------------------------------------------------------
    #### 生成日历组件
    def date_str_gain(self,*args):
        width, height = self.frm_gkz1.winfo_reqwidth() + 50, 50 #窗口大小
        x, y = (self.frm_gkz1.winfo_screenwidth()  - width )/2, (self.frm_gkz1.winfo_screenheight() - height)/2
#        frm_gkz1.geometry('%dx%d+%d+%d' % (width, height, x, y )) #窗口位置居中
        [self.date_str.set(date)
        for date in [calendarWidget((x, y), 'll').selection()] 
        if date]
        
    #----------------------------------------------------------------------
    #### 更新国开债最新价格
    def updateBondPrice(self):
        print('债券价格更新')
        for i,cid in enumerate(self.tree.get_children()):
            pInfo = self.pe.cm.deliveryBondList[i].priceInfo
            wcp = pInfo['windCleanPrice']
            wdp  = pInfo['windDirtyPrice']
            wr  = pInfo['windYield']
            duration  = pInfo['maclayDuration']
            bid_price  = pInfo['bidPrice']
            bid_volumn  = pInfo['bidVolumn']
            ask_price  = pInfo['askPrice']
            ask_volumn  = pInfo['askVolumn']
            self.tree.set(cid,column = 'newCp',value = round(wcp,4))
            self.tree.set(cid,column = 'newDp',value = round(wdp,4))
            self.tree.set(cid,column = 'newYTM',value = round(wr,4))
            self.tree.set(cid,column = 'duration',value = round(duration,4))
            self.tree.set(cid,column = 'bid_price',value = round(bid_price,4))
            self.tree.set(cid,column = 'bid_volumn',value = round(bid_volumn,4))
            self.tree.set(cid,column = 'ask_price',value = round(ask_price,4))
            self.tree.set(cid,column = 'ask_volumn',value = round(ask_volumn,4))
        self.updateBondValueTimes.set(self.updateBondValueTimes.get() + 1)
        return
        
    #----------------------------------------------------------------------
    #### 更新国开债估值
    def updateBondValue(self):
        self.pe.cm.updateBondValue(self.valueInstitute.get(),\
                                   datetime.strptime(self.date_str.get(),"%Y-%m-%d"))
        if self.pe.cm.deliveryBondList[0].priceInfo['valueCleanPrice'] == None:
            tk.messagebox.showwarning('提示','获取数据失败，请确认数据权限')
            return
        # 更新估值信息
        for i,cid in enumerate(self.tree.get_children()):
            b1 = self.pe.cm.deliveryBondList[i]
            self.tree.set(cid,column = 'valueCp',value = round(b1.priceInfo['valueCleanPrice'],4))
            self.tree.set(cid,column = 'valueDp',value = round(b1.priceInfo['valueDirtyPrice'],4))
            self.tree.set(cid,column = 'valueYtm',value = round(b1.priceInfo['valueYield'],4))
        return
    
    #----------------------------------------------------------------------
    #### 插入国开债估值信息
    def insertGkzBond(self):
        for item in self.pe.cm.deliveryBondList:
            tmpValue = (item.bondInfo['windCode'],
                        item.bondInfo['name'],
                        round(item.priceInfo['last'],4),
                        round(item.priceInfo['windCleanPrice'],4),
                        round(item.priceInfo['windDirtyPrice'],4),
                        round(item.priceInfo['windYield'],4),
                        round(item.priceInfo['maclayDuration'],4),
                        round(item.priceInfo['valueCleanPrice'],4),
                        round(item.priceInfo['valueDirtyPrice'],4),
                        round(item.priceInfo['valueYield'],4),
                        round(item.priceInfo['bidPrice'],4),
                        item.priceInfo['bidVolumn'],
                        round(item.priceInfo['askPrice'],4),
                        item.priceInfo['askVolumn'])
            self.tree.insert('', 'end', values=tmpValue)
            
    
        
        
        



