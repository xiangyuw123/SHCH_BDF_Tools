# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 14:12:53 2020

@author: xiangyu wang
"""
#from WindPy import w

import tkinter as tk
from tkinter import ttk
from SHCHGui import *
from SHCHPriceEngine import priceEngine
from .frame_curve import curveFrame
from .frame_yield import yieldFrame
from .frame_bdfValue import bdfValueFrame

import datetime

class mainWindow(tk.Tk):
    def __init__(self,priceEngine1 = None,priceEngine2 = None):
        tk.Tk.__init__(self)
        self.title('标准债券远期交易工具')
        self.geometry('1280x768')
        self.pe1 = priceEngine1
        self.pe2 = priceEngine2
        self.initTab()
        
    #----------------------------------------------------------------------
    #### 创建分页
    def initTab(self):
        tab_main= tk.ttk.Notebook(self) #创建分页栏
        tab_main.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        
        #### tab1 页面设计
        tab1=tk.Frame(tab_main)#创建第一页框架
        tab1.place(x=0,y=30)
        tab_main.add(tab1,text='标债远期价格监控')#将第一页插入分页栏中

        self.bdfFrame = bdfFrame(tab1,self.pe1)
        self.bdfFrame.place(relx=0.02,rely=0.02,relwidth=0.96,relheight=0.46)
        self.gkzFrame = gkzFrame(tab1,self.pe1)
        self.gkzFrame.place(relx=0.02,rely=0.52,relwidth=0.46,relheight=0.46)
        self.jgzsFrame = jgzsFrame(tab1,self.pe1)
        self.jgzsFrame.place(relx=0.52,rely=0.52,relwidth=0.46,relheight=0.46)
        
        
        #### tab2 页面设计
        tab2=tk.Frame(tab_main)
        tab2.place(x=100,y=30)
        tab_main.add(tab2,text='定价试算工具')
        
        tk.Button(tab2,text = '同步价格监控参数',command = self.syncParameter,relief = 'raised',takefocus=False).\
        place(relx=0.02,rely=0.02,relwidth=0.1,relheight=0.05)

#        tk.Button(tab2,text = '同步参数设置',command = self.syncParameter,relief = 'raised',takefocus=False).\
#        place(relx=0.15,rely=0.02,relwidth=0.1,relheight=0.05) 
        
#        tk.Button(tab2,text = '从本地导入参数',command = self.inputPara,relief = 'raised',takefocus=False).\
#        place(relx=0.28,rely=0.02,relwidth=0.1,relheight=0.05)
#        
#        tk.Button(tab2,text = '导出参数至本地',command = self.outputPara,relief = 'raised',takefocus=False).\
#        place(relx=0.41,rely=0.02,relwidth=0.1,relheight=0.05)
        
        tk.Button(tab2,text = '标债估值一键试算',command = self.calcAll,relief = 'raised',takefocus=False).\
        place(relx=0.15,rely=0.02,relwidth=0.1,relheight=0.05) 
        
        # canfrm 放入滚动条
        canFrm = tk.Frame(tab2)
        canFrm.place(relx=0.02,rely=0.09,relwidth=0.96,relheight=0.89)
#        print(canFrm.winfo_screenwidth())
        
        canFrm.columnconfigure(0, weight=1)
        canFrm.rowconfigure(0, weight=1)
#        
        # canvas canvas放入试算参数界面
        self.canvas=tk.Canvas(canFrm) #创建canvas
        vsb = tk.Scrollbar(canFrm, orient="vertical", command=self.canvas.yview)


        
        frame = tk.Frame(self.canvas)
        frame.columnconfigure(0,weight = 1)
        # 融资利率设框架
        self.curveFrame = curveFrame(frame,self.pe2)
        self.curveFrame.grid(row = 0,column = 0, sticky = 'we',pady = 5)
        #债券试算框架
        self.yieldFrame = yieldFrame(frame,self.pe2)
        self.yieldFrame.grid(row = 1,column = 0, sticky = 'we',pady = 5)
        #标债试算框架
        self.bdfValueFrame = bdfValueFrame(frame,self.pe2)
        self.bdfValueFrame.grid(row = 2,column = 0, sticky = 'we',pady = 5)
        
        # 在不同框架间建立连接
        self.bdfFrame.syncTimes.trace("w", self.syncCurve)
        self.curveFrame.buildTimes.trace("w", self.linkCurveFrameAndYieldFrame)
        self.gkzFrame.updateBondValueTimes.trace("w", self.linkGkzFrameAndBdfFrame)
        
        
        #标债设置框架
        frame.update_idletasks()
#        print(self.canvas.winfo_width() )
#        print(self.canvas.winfo_reqwidth())

        self.frame_id = self.canvas.create_window(15,5,anchor = 'nw', width = frame.winfo_reqwidth(),\
                             height = frame.winfo_reqheight(),window=frame)
        self.canvas.update_idletasks()
#        
#        # 加入滚动条scrollregion=self.canvas.bbox('all'),
        region = (0,0) + self.canvas.bbox('all')[2:4]
        self.canvas.configure(scrollregion=region,yscrollcommand=vsb.set)
        frame.bind("<Configure>", self.OnFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)
        
        self.canvas.grid(row = 0,column = 0, sticky = 'nswe')
        vsb.grid(row = 0,column = 1, sticky = 'nswe')

        return(tab_main)

    #----------------------------------------------------------------------
    #### 价格监控页面按钮函数
    def syncCurve(self,*args):
        self.bdfFrame.curveSource.set(self.curveFrame.curveSource.get())
        for i in range(len(self.curveFrame.swapRate)):
            self.bdfFrame.swapRate[i].set(self.curveFrame.swapRate[i].get())
            self.bdfFrame.spotRate[i].set(self.curveFrame.spotRate[i].get())
            self.bdfFrame.spread[i].set(self.curveFrame.spread[i].get())
        self.bdfFrame.interpMethod.set(self.curveFrame.interpMethod.get())
        return

    #----------------------------------------------------------------------
    #### 定价试算页面按钮函数
    def syncParameter(self):
        # step1 同步利率曲线
        self.curveFrame.curveSource.set(self.bdfFrame.curveSource.get())
        for i in range(len(self.curveFrame.swapRate)):
            self.curveFrame.swapRate[i].set(self.bdfFrame.swapRate[i].get())
            self.curveFrame.spotRate[i].set(self.bdfFrame.spotRate[i].get())
            self.curveFrame.spread[i].set(self.bdfFrame.spread[i].get())
        self.curveFrame.interpMethod.set(self.bdfFrame.interpMethod.get())
        
        # step2 同步国开债信息
        self.yieldFrame.valueInstitute.set(self.gkzFrame.valueInstitute.get()) # 估值来源
        self.yieldFrame.date_str.set(self.gkzFrame.date_str.get()) # 估值日期
        self.yieldFrame.cmb_valueSource_select()
        for i in range(len(self.bdfValueFrame.bond1w)):
            bdfId = next(j for j,item in enumerate(self.bdfFrame.bdfcode) if item.get() == self.yieldFrame.bdfCode[i].get())
            self.yieldFrame.spread[2 * i].set(self.bdfFrame.bond1spread[bdfId].get())
            self.yieldFrame.spread[2 * i + 1].set(self.bdfFrame.bond2spread[bdfId].get())
            self.bdfValueFrame.bond1w[i].set(self.bdfFrame.bond1weight[bdfId].get())
            self.bdfValueFrame.bond2w[i].set(self.bdfFrame.bond2weight[bdfId].get())
        
        # step3 同步标债估值参数
        self.bdfValueFrame.priceSource.set(self.bdfFrame.bdfSource.get())
        self.bdfValueFrame.resetPrice()
        tk.messagebox.showinfo('提示','试算参数已更新至与价格监控参数相同')
        return
    
    # def syncMarketData(self):
    #     tk.messagebox.showinfo('提示','市场数据已更新')
    #     pass

    # def outputPara(self):
    #     pass
    
    # def inputPara(self):
    #     pass
    
    def calcAll(self):
        # 构建利率曲线
        self.curveFrame.buildCurve()
        # 获取国开债今日估值
        self.yieldFrame.btn_calcTodayPrice()
        # 计算国开债交割日YTM
        self.yieldFrame.btn_calcDelPrice()
        # 计算标债估值
        self.bdfValueFrame.resetYield()
        self.bdfValueFrame.calcBdfValue()
        tk.messagebox.showinfo('提示','试算完成')
        return
    
    #----------------------------------------------------------------------
    # 订阅回调函数
    def subHandleBond(self):
        pass
    
    def subHandleBdf(self):
        pass
    
    #----------------------------------------------------------------------
    # UI界面函数
    def FrameWidth(self, event):
#        print(event.width)
        canvas_width = event.width
        self.canvas.itemconfig(self.frame_id, width = canvas_width * 0.95)

    def OnFrameConfigure(self, event):
#        print('babababa')
        region = (0,0) + self.canvas.bbox('all')[2:4]
        self.canvas.configure(scrollregion=region)

    #----------------------------------------------------------------------
    # 关联curveFrame的利率曲线与yieldFrame的收益率
    def linkCurveFrameAndYieldFrame(self,*args):
#        print('second')
        # 从利率曲线上获取交割日利率
        t1 = (self.str2date(self.yieldFrame.deliveryDay[0].get()) - self.pe2.priceDate).days
        t2 = (self.str2date(self.yieldFrame.deliveryDay[1].get()) - self.pe2.priceDate).days
        spot1 = self.pe2.curve.getRate(t1,1)
        spot2 = self.pe2.curve.getRate(t2,1)
        self.yieldFrame.spotRate[0].set(round(spot1*100,4))
        self.yieldFrame.spotRate[1].set(round(spot2*100,4))
        return

    #----------------------------------------------------------------------
    # 关联“价格监控”分页的机构估值与标债远期价格运算
    def linkGkzFrameAndBdfFrame(self,*args):
        self.bdfFrame.updateGkzSource()
        return

    def str2date(self,dt):
        s = datetime.datetime.strptime(dt,'%Y-%m-%d')
        return(datetime.date(s.year,s.month,s.day))
    
    
    
    
if __name__ =='__main__':
    pe = priceEngine()
    root = mainWindow(pe)
    root.mainloop()
    