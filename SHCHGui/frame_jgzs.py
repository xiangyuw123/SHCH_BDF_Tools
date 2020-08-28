# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 16:13:26 2020
价格走势监控框架

@author: Xiangyu Wang
"""

import tkinter as tk
from tkinter import ttk
from WindPy import w
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#,NavigationToolbar2Tk
import datetime


#### 价格走势查询
class jgzsFrame(tk.LabelFrame):
    def __init__(self,master = None,pe = None):
        tk.LabelFrame.__init__(self, master,text = '价格走势查询',font=('微软雅黑',12,'bold'))
        self.pe = pe

        for i in range(7):
            self.columnconfigure(i, weight=1, minsize=30)
        self.rowconfigure(1, weight=1, minsize=30)
        self.rowconfigure(2, weight=1, minsize=30)

        self.lbl_queryInfo = tk.Label(self,text = '查询信息')
        self.lbl_queryContract = tk.Label(self,text = '合约选取')
        self.btn_query = tk.Button(self,text = '查询',command = self.queryHistPrice,takefocus=False)
        
        self.cmbQueryInfoList = ['标债远期历史价格','可交割券历史价格']
        self.cmb_queryInfo = tk.ttk.Combobox(self,state = 'readonly')
        self.cmb_queryInfo['values'] = self.cmbQueryInfoList
        
        
        # 可查询代码
        self.BondCodeMap = {}
        self.cmbQueryContractList = [[],[]]
        for item in self.pe.bdfCode:
            self.cmbQueryContractList[0].append(item)
        for i,item in enumerate(self.pe.bondName):
            self.cmbQueryContractList[1].append(item[0])
            self.cmbQueryContractList[1].append(item[1])
            self.BondCodeMap[item[0]] = self.pe.bondCode[i][0]
            self.BondCodeMap[item[1]] = self.pe.bondCode[i][1]

        self.cmbQueryContractList[1] = list(set(self.cmbQueryContractList[1]))

        self.cmb_queryContract = tk.ttk.Combobox(self,state = 'readonly')
        self.cmb_queryInfo.bind("<<ComboboxSelected>>", self.cmbQueryInfoCmd)
        
        self.lbl_queryInfo.grid(column = 0,row = 0,pady=1)
        self.cmb_queryInfo.grid(column = 1,row = 0,columnspan=2, pady=1)
        self.lbl_queryContract.grid(column = 3,row = 0,pady=1)
        self.cmb_queryContract.grid(column = 4,row = 0,columnspan=2, pady=1)
        self.btn_query.grid(column = 6,row = 0,columnspan=2,pady=1)
        
        self.f = plt.figure()
        self.ax = self.f.add_subplot(111)
        self.canvas=FigureCanvasTkAgg(self.f,self)
        self.canvas.get_tk_widget().grid(column=0, row = 1,columnspan = 8,pady = 1,sticky = 'nswe')

        
    def queryHistPrice(self):
        if not w.isconnected():
            tk.messagebox.showerror('提示','Wind接口连接失败')
        if self.cmb_queryInfo.current() == 0:
            code = self.cmb_queryContract.get()
        else:
            code = self.BondCodeMap[self.cmb_queryContract.get()]
        if len(code) == 0:
            tk.messagebox.showinfo('提示','请选择查询合约')
        else:
            self.ax.clear()
            period = "ED-1Y"
            tmp = w.wsd(code,"close",period,datetime.date.today().strftime('%Y-%m-%d'))
            
            ts = pd.DataFrame({'time':tmp.Times,'price':tmp.Data[0]}).fillna(method = 'ffill')
            self.ax.plot(ts['time'],ts['price'])
            self.ax.set_title(code)
            self.canvas.draw()
        pass

    def cmbQueryInfoCmd(self,*args):
        queryInfoId = self.cmb_queryInfo.current()
        self.cmb_queryContract['values'] = self.cmbQueryContractList[queryInfoId]
      
            
            
if __name__ =='__main__':
    root = tk.Tk()
    root.title('this is right')
    app1 = jgzsFrame(root)
    app1.pack()
    root.mainloop()