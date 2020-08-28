# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 15:34:00 2020

@author: Xiangyu Wang
"""

import tkinter as tk
from tkinter import ttk
from datetime import date
import numpy as np

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk

class curveFrame(tk.LabelFrame):
    def __init__(self,master = None,engine = None):
        tk.LabelFrame.__init__(self, master,text = '融资利率曲线构建',font=('微软雅黑',12,'bold'))
        
        self.pe = engine
        
        # 利率曲线变量
        self.curveSource = tk.StringVar()
        self.interpMethod = tk.StringVar()
        
        self.curveSource.set('手动输入互换曲线')
        self.cmb_curve_source_value = ('FR007互换曲线','手动输入互换曲线','手动输入即期曲线')
        self.interpMethod.set('平行插值')
        self.cmb_interp_method_value = ('平行插值','线性插值','自然三次样条插值')
        
        self.swapRate = []
        self.spotRate = []
        self.spread = []
        self.startDate = []
        self.endDate = []
        self.days = []
        
        for i in range(7):
            self.swapRate.append(tk.DoubleVar())
            self.spotRate.append(tk.DoubleVar())
            self.spread.append(tk.DoubleVar())
            self.startDate.append(tk.StringVar())
            self.endDate.append(tk.StringVar())
            self.days.append(tk.DoubleVar())
        
        self.tenorName = ('ON','7D','1M','3M','6M','9M','1Y')
        
        self.allCurve = [] # 最终曲线构建结果
        self.buildTimes = tk.IntVar()
        self.buildTimes.set(0)
        
        self.setVariable()
        
        # 设置子框架可变动大小
        for i in range(2):
            self.columnconfigure(i, weight=1)
            
        self.createCurveFrm()
        self.createCanvasFrm()
    
    def createCurveFrm(self):
        self.master1 = tk.Frame(self)
        self.master1.grid(column = 0,row = 0,sticky = 'nswe',ipadx = 10,padx = 10)
        for i in range(1):
            self.master1.columnconfigure(i, weight=1)
#        for i in range(2):
#            self.master1.rowconfigure(i, weight=1)
        
        frm1 = tk.Frame(self.master1)
        frm1.grid(column = 0,row = 0,sticky = 'nswe')
        for i in range(4):
            frm1.columnconfigure(i, weight=1)
#        for i in range(1):
#            frm1.rowconfigure(i, weight=1)
        frm2 = tk.Frame(self.master1)
        frm2.grid(column = 0,row = 1,sticky = 'nswe')
#        frm3 = tk.Frame(top).grid(column = 0,row = 0)
        for i in range(7):
            frm2.columnconfigure(i, weight=1)
#        for i in range(9):
#            frm2.rowconfigure(i, weight=1)
        
        tk.Label(frm1,text = '融资利率曲线来源').grid(column = 0,row = 0,padx = 1,pady = 1)
        cmb_sorce = tk.ttk.Combobox(frm1,state = 'readonly',textvariable = self.curveSource)
        cmb_sorce['values'] = self.cmb_curve_source_value
        cmb_sorce.grid(column = 1, row = 0, padx = 1,pady = 1)
        cmb_sorce.bind("<<ComboboxSelected>>", self.cmb_sorce_func)
        
        tk.Label(frm1,text = '利率曲线插值方法').grid(column = 2,row = 0,padx = 1,pady = 1,sticky = 'e')
        cmb_interpMethod = tk.ttk.Combobox(frm1,state = 'readonly',textvariable = self.interpMethod)
        cmb_interpMethod['values'] = self.cmb_interp_method_value
        cmb_interpMethod.grid(column = 3, row = 0, padx = 1,pady = 1,sticky = 'e')
               
        # +-BP按钮
        def addBp_spread():
            for item in self.spread:
                item.set(item.get()+10)
        def minBp_spread():
            for item in self.spread:
                item.set(item.get()-10)
                
        def addBp_swap():
            for item in self.swapRate:
                item.set(item.get()+0.1)
        def minBp_swap():
            for item in self.swapRate:
                item.set(item.get()-0.1)
            
        tk.Label(frm2,text = '互换利率平移(+/-)').grid(column = 0,row = 0,columnspan = 2,pady = 5) 
        tk.Button(frm2,text = '+10BP',command = addBp_swap).grid(column = 2,row = 0,sticky = 'e',pady = 5)
        tk.Button(frm2,text = '-10BP',command = minBp_swap).grid(column = 3,row = 0,sticky = 'w',pady = 5)    
            
        tk.Label(frm2,text = '额外资金成本(+/-)').grid(column = 4,row = 0,columnspan = 2,pady = 5) 
        tk.Button(frm2,text = '+10BP',command = addBp_spread).grid(column = 6,row = 0,sticky = 'e',pady = 5)
        tk.Button(frm2,text = '-10BP',command = minBp_spread).grid(column = 7,row = 0,sticky = 'w',pady = 5)
        
        
        # 利率曲线设置
        rowid = 1
        colName = ('期限','起息日','到期日','剩余天数','互换利率','即期利率',\
                   '额外资金成本(BP)')
        for j in range(len(colName)-1):
            tk.Label(frm2,text = colName[j]).grid(column = j,row = rowid)
        tk.Label(frm2,text = colName[j+1]).grid(column = j+1,row = rowid,columnspan = 2)
        for i in range(len(self.tenorName)):
            tk.Label(frm2,text = self.tenorName[i],width = 9).grid(column = 0,row = i + 1+rowid)
            tk.Label(frm2,textvariable = self.startDate[i],width = 9).grid(column = 1,row = i + 1+rowid)
            tk.Label(frm2,textvariable = self.endDate[i],width = 9).grid(column = 2,row = i + 1+rowid)
            tk.Label(frm2,textvariable = self.days[i],width = 9).grid(column = 3,row = i + 1+rowid)
            tk.Entry(frm2,textvariable = self.swapRate[i],width = 12).grid(column = 4,row = i + 1+rowid,padx = 5,sticky = 'we')
            tk.Entry(frm2,textvariable = self.spotRate[i],width = 12).grid(column = 5,row = i + 1+rowid,padx =5,sticky = 'we')
            tk.Entry(frm2,textvariable = self.spread[i],width = 12).grid(column = 6,row = i +1+ rowid,columnspan = 2,padx = 5,sticky = 'wew')

        # 构建按钮
#        tk.Button(frm2,text = '同步试算参数').grid(column = 0,row = 9,columnspan = 2)
        self.btn_build = tk.Button(frm2,text = '融资利率曲线构建',relief = 'raised',command = self.buildCurve)
#        self.btn_build.bind("<Button-1>", self.buildCurve)
        self.btn_build.grid(column = 5,row = i +2+ rowid,columnspan = 3,pady = 3,sticky = 'e')
        return
        
    
    def createCanvasFrm(self):
        self.master2 = tk.Frame(self)
        self.master2.grid(column = 1,row = 0,sticky = 'nswe',ipadx = 10,padx = 10)
        
        # 设置grid可变大小
        for i in range(1):
            self.master2.rowconfigure(i, weight=1, minsize=30)
        for i in range(1):
            self.master2.columnconfigure(i, weight=1, minsize=30)


        self.f = plt.figure(figsize = [6,1])
        self.ax = self.f.add_subplot(111)
        self.canvas=FigureCanvasTkAgg(self.f,self.master2)
        self.canvas.get_tk_widget().grid(column=0, row = 0,sticky = 'nswe')
        self.ax.set_title("融资利率曲线")
        self.canvas.draw()
        return
        

    #----------------------------------------------------------------------
    #### 从引擎载入数据
    def setVariable(self):
        c = self.pe.curve
#        spot = c.getKeySpotRate()
#        print(c.inputRate)
        for i in range(len(self.tenorName)):
            self.swapRate[i].set(3)
#            self.spotRate[i].set(spot[i])
            self.startDate[i].set(c.tenor_start[i])
            self.endDate[i].set(c.tenor_end[i])
            self.days[i].set(c.tenor[i])
            
        pass
        
    #----------------------------------------------------------------------
    #### 向引擎传入数据
    def updateVariable(self):
        pass
        
    #----------------------------------------------------------------------
    #### 曲线构建按钮函数
    def buildCurve(self):
        # spread
        spread = np.zeros(7)
        for i in range(len(self.tenorName)):
            spread[i] = self.spread[i].get()
        
        # curvesetting
        if self.interpMethod.get() == '平行插值':
            interp = 0
        elif self.interpMethod.get() == '线性插值':
            interp = 1
        elif self.interpMethod.get() == '自然三次样条插值':
            interp = 2
        setting = {'interpSpace':0, # 0 - continuous rate 1 - simple rate  2 - 'instantF' 
           'innerInterpMethod':interp,# 0 - constant Forward 1 - Linear 2-natural Cubic spline
           'outterInterpMethod':1}
        self.pe.curve.loadSetting(setting)

         # 若输入参数为互换利率，需要先通过拔靴求解即期利率
        if self.curveSource.get() in ('手动输入互换曲线','FR007互换曲线'):   
            swapRate = np.zeros(len(self.tenorName))
            for i in range(len(self.tenorName)):
                swapRate[i] = self.swapRate[i].get()   
                
                curveInfo = {'curveDate':date.today(),  
                            'startDate' : [0,1,1,1,1,1,1],    
                            'tenor':['ON','7D','1M','3M','6M','9M','1Y'],     
                            'rate':swapRate / 100,               
                            'rateType':[1,1,1,2,2,2,2],           
                            'basis':np.array([365,365,365,365,365,365,365])}
                self.pe.curve.loadData(curveInfo)
                self.pe.curve.buildCurve()
            bootstrap_spot = self.pe.curve.getKeySpotRate()
#            print(bootstrap_spot)
            for i in range(len(self.tenorName)):
                self.spotRate[i].set(bootstrap_spot[i] * 100)
        
        # 通过即期利率曲线+spread构建贴现利率曲线
        spot = np.zeros(len(self.tenorName))
        for i in range(len(self.tenorName)):
            spot[i] = self.spotRate[i].get() / 100 + self.spread[i].get() / 10000
#        print(spot)
        curveInfo = {'curveDate':date.today(),  
                    'startDate' : [0] * 7,    
                    'tenor':self.pe.curve.tenor.tolist(),     
                    'rate':spot,               
                    'rateType':np.ones(7),           
                    'basis':np.array([360,360,360,360,360,360,360])}
        self.pe.curve.loadData(curveInfo)
        self.pe.curve.buildCurve()
        self.allCurve = self.pe.curve.getContCurve()

        self.ax.clear()
        self.ax.scatter(self.pe.curve.tenor, self.pe.curve.getKeySpotRate(rateType = 0), c = 'g', marker='x',s = 10)
        self.ax.plot(range(1,len(self.allCurve)+1),self.allCurve)
        self.ax.set_title("融资利率曲线")
        self.canvas.draw()
        self.buildTimes.set(self.buildTimes.get() + 1)

    def cmb_sorce_func(self,*args):
        if self.curveSource.get() == self.cmb_curve_source_value[0]:
            swap = self.pe.getSwapCurveFromWind()
            for i in range(len(self.tenorName)):
                self.swapRate[i].set(swap[i])
        return
        
        
        
        
        
        #        # 曲线结果查询区域
#        tk.Label(self.master2,text = '曲线结果查询:').grid(column = 0,row = 0,padx = 1)
#        tk.Label(self.master2,text = '期限天数').grid(column = 0,row = 1,padx = 1)
#        tk.Label(self.master2,text = '即期利率(单利)').grid(column = 1,row = 1,padx = 1)
#        tk.Label(self.master2,text = '即期利率(连续复利)').grid(column = 2,row = 1,padx = 1)
#        tk.Label(self.master2,text = '贴现因子').grid(column = 3,row = 1,padx = 1)
#        
#        tk.Entry(self.master2,width = 9).grid(column = 0,row = 2,padx = 1)
#        tk.Label(self.master2,width = 9).grid(column = 1,row = 2,padx = 1)
#        tk.Label(self.master2,width = 9).grid(column = 2,row = 2,padx = 1)
#        tk.Label(self.master2,width = 9).grid(column = 3,row = 2,padx = 1)
        
        
        