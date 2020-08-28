# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 14:49:36 2020
构建标债远期价格监控框架UI界面

@author: xiangyu wang
"""

import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from datetime import date


class bdfFrame(tk.LabelFrame):
    def __init__(self,master = None,engine = None):
        tk.LabelFrame.__init__(self, master,text = '标债远期价格监控',font=('微软雅黑',12,'bold'))
        
        ############################ 设置界面变量 ############################
        self.pe = engine
        
        # 国开债估值来源
        self.gkzSourceValue = ['手动录入(双击)','估值机构收益率','Wind最新价格']
        self.gkzSource = tk.StringVar()
        self.gkzSource.set(self.gkzSourceValue[1])

        self.bdfSource = tk.StringVar()
        self.bdfSourceValue = ['Wind最新价','标债报价-买价','标债报价-均值','标债报价-卖价']
        self.bdfSource.set(self.bdfSourceValue[2])
        
        # 融资利率曲线设置
        self.curveSource = tk.StringVar()
        self.curveSourceValue = ['FR007互换曲线','手动输入互换曲线','手动输入即期曲线']
        self.interpMethod = tk.StringVar()
        self.interpMethodValue = ['平行插值','线性插值','自然三次样条插值']
        
        self.tenorName = ('ON','7D','1M','3M','6M','9M','1Y')
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
            self.days.append(tk.StringVar())
        self.allCurve = [] # 最终曲线构建结果
        # 初始化融资利率曲线设置
        self.curveSource.set(self.curveSourceValue[0])
        self.interpMethod.set(self.interpMethodValue[2])
        c = self.pe.curve
        for i in range(len(self.tenorName)):
            self.startDate[i].set(c.tenor_start[i])
            self.endDate[i].set(c.tenor_end[i])
            self.days[i].set(c.tenor[i])
        self.cmb_sorce_func()
        self.buildCurve()

        # 同步利率曲线参数
        self.syncTimes = tk.IntVar()
        self.syncTimes.set(0)
        
        # 可交割券设置窗口参数
        self.bdfcode = []
        self.bdfId = []
        self.bond1name = []
        self.bond2name = []
        self.bond1weight = []
        self.bond2weight = []
        self.bond1spread = []
        self.bond2spread = []
        for i in range(len(self.pe.cm.contractList)):
            self.bdfcode.append(tk.StringVar())
            self.bond1name.append(tk.StringVar())
            self.bond2name.append(tk.StringVar())
            self.bdfcode[i].set(self.pe.bdfCode[i])
            self.bdfId.append(i)
            self.bond1name[i].set(self.pe.bondName[i][0])
            self.bond2name[i].set(self.pe.bondName[i][1])
            self.bond1weight.append(tk.DoubleVar())
            self.bond2weight.append(tk.DoubleVar())
            self.bond1spread.append(tk.DoubleVar())
            self.bond2spread.append(tk.DoubleVar())
            self.bond1weight[i].set(0.5)
            self.bond2weight[i].set(0.5)
            self.bond1spread[i].set(0.0)
            self.bond2spread[i].set(0.0)        
        
        
#        self.curveSetting = {'source':[],
#                             'interpSpace':[],
#                             'interpMethod':[],
#                             'spotRate':[]}
#        self.bondSetting = {}
        
        ############################ 创建界面 ############################
        self.createFrm()

        ############################ 初始化数据 ############################
        self.updateGkzSource()
        self.updateBdfSource()
        
        ############################ 注册回调函数 ############################
        self.pe.register(bdfHandle = self.bdfCallBack)
        return
    
    #----------------------------------------------------------------------
    # 创建界面
    def createFrm(self):
        for i in range(3):
            self.rowconfigure(i, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        ############################ 价格来源选择Frame1 ############################
        frm_bdf1 = tk.Frame(self)
        for i in range(1):
            frm_bdf1.rowconfigure(i, weight=1, minsize=30)
        for i in range(2):
            frm_bdf1.columnconfigure(i, weight=1, minsize=30)
        
        # 国开债来源下拉框
        tk.Label(frm_bdf1,text = '国开债收益率来源').grid(column = 0,row = 0,padx = 1,pady = 1)
        cmb_gkzSource = tk.ttk.Combobox(frm_bdf1,textvariable = self.gkzSource,state = 'readonly')
        cmb_gkzSource['values'] = self.gkzSourceValue
        cmb_gkzSource.bind("<<ComboboxSelected>>", self.updateGkzSource)
        cmb_gkzSource.grid(column = 1, row = 0, padx = 1,pady = 1)
        
        # 标债远期报价格式
        tk.Label(frm_bdf1,text = '标债远期现价来源').grid(column = 2,row = 0,padx = 1,pady = 1)
        cmb_bdfSource = tk.ttk.Combobox(frm_bdf1,textvariable = self.bdfSource,state = 'readonly')
        cmb_bdfSource['values'] = self.bdfSourceValue
        cmb_bdfSource.bind("<<ComboboxSelected>>", self.updateBdfSource)
        cmb_bdfSource.grid(column = 3, row = 0, padx = 1,pady = 1)
        
        frm_bdf1.grid(column = 0,row = 0,pady = 1,sticky = 'w')
        ############################ 标债合约价格监控Frame2 ############################
        frm_bdf2 = tk.Frame(self)
        frm_bdf2.rowconfigure(0, weight=1)
        frm_bdf2.rowconfigure(1, weight=0, minsize=30)
        frm_bdf2.columnconfigure(1, weight=0, minsize=30)
        frm_bdf2.columnconfigure(0, weight=1, minsize=30)

        #----------------------------------------------------------------------
        # 修复tkinter 8.6.9Treeview Tags Bug
        def fixed_map(option):
            # Returns the style map for 'option' with any styles starting with
            # ("!disabled", "!selected", ...) filtered out
        
            # style.map() returns an empty list for missing options, so this should
            # be future-safe
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]
        style = ttk.Style(frm_bdf2)
        style.map("Treeview",
                  foreground=fixed_map("foreground"),
                  background=fixed_map("background"))
        
        columns =  ("bdf", "bond1", "yield1", "bond2",'yield2','bdfPrice','value1','value2','irr','value3','bid_price',\
                    'bid_volumn','ask_price','ask_volumn')
        
#        columns =  ("bdf", "bond1")
        tree = ttk.Treeview(frm_bdf2,show = 'headings',columns = columns,height = 8)      # #创建表格对象
        
        colName = ('标债远期合约','可交割券1','券1收益率','可交割券2','券2收益率','标债远期现价','交易中心估值',\
                   '远期收益率估值','隐含收益率(%)','Wind最新价','标债远期买价','标债远期买量','标债远期卖价','标债远期卖量')

        for i in range(len(tree['columns'])):
            tree.heading(i, text = colName[i])
            tree.column(i,width=100,minwidth = 70)
        
        # 初始化表格
        for i in range(len(self.pe.cm.bdfCode)):
            bdfcode = self.pe.cm.bdfCode[i][:-3]
            cinfo = self.pe.cm.contractList[i].cInfo
            b1name = cinfo['deliveryBond'][0].bondInfo['name']
            yield1 = 0.0
            b2name = cinfo['deliveryBond'][1].bondInfo['name']
            yield2 = 0.0
            bdfPrice = 0.0
            value1 = round(self.pe.bdfCfetPrice[i],2)
            value2 = round(self.pe.bdfShchPrice[i],2)
            value3 = round(cinfo['lastPrice'],2)
            irr = round(self.pe.ShchIrr[i]*100,4)
            bidPrice = round(cinfo['bidPrice'],2)
            bidVolumn = round(cinfo['bidVolumn'],0)
            askPrice = round(cinfo['askPrice'],2)
            askVolumn = round(cinfo['askVolumn'],0)
            item = (bdfcode,b1name,yield1,b2name,yield2,bdfPrice,value1,value2,irr,value3,\
                    bidPrice,bidVolumn,askPrice,askVolumn)
            tree.insert('',i,values = item,tags = i)
        
        vsb = ttk.Scrollbar(frm_bdf2, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frm_bdf2, orient="horizontal", command=tree.xview)
        
        tree.configure(yscrollcommand = vsb.set)
        tree.configure(xscrollcommand = hsb.set)

                        
        # pack everything
        vsb.grid(column = 1,row = 0,sticky = 'ns')
        hsb.grid(column = 0,row = 1,sticky = 'we')
        tree.grid(column = 0,row = 0,sticky = 'nswe')
        self.tree = tree

        frm_bdf2.grid(column = 0,row = 1,pady = 1,sticky = 'nswew')

        ############################ 参数设置Frame3 ############################
        frm_bdf3 = tk.Frame(self)
        for i in range(1):
            frm_bdf3.rowconfigure(i, weight=1, minsize=30)
        for i in range(2):
            frm_bdf3.columnconfigure(i, weight=1, minsize=30)
        frm_bdf3.grid(column = 0,row = 2,sticky = 'w',pady = 1)
        
        btn_curve = tk.Button(frm_bdf3,text = '贴现利率设置',command = self.openCurveSetting)
        btn_bond = tk.Button(frm_bdf3,text = '可交割券设置',command = self.openBondSetting)
        btn_curve.grid(column = 0,row = 0,padx = 10)
        btn_bond.grid(column = 1, row = 0,padx = 10)
        return
    
    
    #----------------------------------------------------------------------
    # 债券估值收益率更新
    def updateGkzSource(self,*args):
        self.updateGkzPrice()
        self.autoPrice()
        return

    #----------------------------------------------------------------------
    # 标债价格下拉框点击按钮
    def updateBdfSource(self,*args):
        self.autoPrice()
        return

    #----------------------------------------------------------------------
    # 国开债价格更新
    def updateGkzPrice(self):
        if self.gkzSourceValue.index(self.gkzSource.get()) == 0:
#            tk.messagebox.showinfo('提示','请双击相关合约直接录入')
            self.tree.bind('<Double-1>',self.treeDoubleClick) #绑定双击事件
        elif self.gkzSourceValue.index(self.gkzSource.get()) == 1:
            for i,cid in enumerate(self.tree.get_children()):
                yield1 = self.pe.cm.contractList[i].cInfo['deliveryBond'][0].priceInfo['valueYield']
                yield2 = self.pe.cm.contractList[i].cInfo['deliveryBond'][1].priceInfo['valueYield']
                self.tree.set(cid,column = 'yield1',value = round(yield1,4))
                self.tree.set(cid,column = 'yield2',value = round(yield2,4))
        elif self.gkzSourceValue.index(self.gkzSource.get()) == 2:
            for i,cid in enumerate(self.tree.get_children()):
                try:
                    yield1 = self.pe.cm.contractList[i].cInfo['deliveryBond'][0].priceInfo['windYield']
                    yield2 = self.pe.cm.contractList[i].cInfo['deliveryBond'][1].priceInfo['windYield']
                except:
                    yield1 = (self.pe.cm.contractList[i].cInfo['deliveryBond'][0].priceInfo['bidYield'] +\
                              self.pe.cm.contractList[i].cInfo['deliveryBond'][0].priceInfo['askYield'])/2
                    yield2 = (self.pe.cm.contractList[i].cInfo['deliveryBond'][1].priceInfo['bidYield'] +\
                              self.pe.cm.contractList[i].cInfo['deliveryBond'][1].priceInfo['askYield'])/2
                self.tree.set(cid,column = 'yield1',value = round(yield1,4))
                self.tree.set(cid,column = 'yield2',value = round(yield2,4))
        return

    def treeDoubleClick(self,event):
        top = tk.Toplevel()
        top.title('融资利率设置')	
        y1 = tk.DoubleVar()
        y2 = tk.DoubleVar()
        item = self.tree.selection()
        
        y1.set(self.tree.item(item)['values'][2])
        y2.set(self.tree.item(item)['values'][4])
        
        tk.Label(top,text = '可交割券1YTM').pack(side = tk.LEFT)
        tk.Entry(top,textvariable = y1,width = 12).pack(side = tk.LEFT)
        tk.Label(top,text = '可交割券2YTM').pack(side = tk.LEFT)
        tk.Entry(top,textvariable = y2,width = 12).pack(side = tk.LEFT)
        def confirm():     		
            self.tree.set(item,column = 'yield1',value = round(y1.get(),4))
            self.tree.set(item,column = 'yield2',value = round(y2.get(),4))
            top.destroy()
        tk.Button(top,text = '应用设置',command = confirm).pack(side = tk.LEFT)
        

        return


    #----------------------------------------------------------------------
    # 标债价格更新
    def updateBdfPrice(self):
        print('更新价格')
        for i,cid in enumerate(self.tree.get_children()):
            cinfo = self.pe.cm.contractList[i].cInfo
            latestPrice = cinfo['lastPrice']
            bidPrice = cinfo['bidPrice']
            bidVolumn = cinfo['bidVolumn']
            askPrice = cinfo['askPrice']
            askVolumn = cinfo['askVolumn']
            self.tree.set(cid,column = 'value3',value = round(latestPrice,2))
            self.tree.set(cid,column = 'bid_price',value = round(bidPrice,2))
            self.tree.set(cid,column = 'bid_volumn',value = round(bidVolumn,0))
            self.tree.set(cid,column = 'ask_price',value = round(askPrice,2))
            self.tree.set(cid,column = 'ask_volumn',value = round(askVolumn,0))
        return
      
    #----------------------------------------------------------------------
    # 回调函数
    def bondCallback(self,data):
        print('收到债券信息')
        if self.gkzSourceValue.index(self.gkzSource.get()) == 0:
            pass
        else:
            # 更新界面上债券信息
            self.updateGkzPrice()
            self.autoPrice()
        return

    def bdfCallBack(self,data):
        # 更新界面上价格信息
        print('收到标债信息')
        self.updateBdfPrice()
        self.autoPrice()
        return
        
    #----------------------------------------------------------------------
    # 估值函数
    def autoPrice(self):
        print('开始计算标债估值')
        # FR007
        repo = self.pe.getFr007()
        print('价格监控')
        # 确定标债远期最新价来源
        pList = np.zeros(len(self.bdfcode))
        if self.bdfSourceValue.index(self.bdfSource.get()) == 0:
            pList = self.pe.getBdfLastPrice()
        elif self.bdfSourceValue.index(self.bdfSource.get()) == 1:
            pList = self.pe.getBdfBidPrice()
        elif self.bdfSourceValue.index(self.bdfSource.get()) == 2:
            pList = self.pe.getBdfMidPrice()
        elif self.bdfSourceValue.index(self.bdfSource.get()) == 3:
            pList = self.pe.getBdfAskPrice()
            
        # 债券估值日    
        valueDate = self.pe.priceDate
        for i,cid in enumerate(self.tree.get_children()):
            # 合约剩余期限
            delD = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryDate']
            deliveryDays = (delD - self.pe.priceDate).days
            deliveryTenor = deliveryDays / 365
            # 交割券期限
            bondTenor = int(self.bdfcode[i].get()[:-8][3:])
            # 标债的最新估值
            p = pList[i]
            # 债券收益率 来源于利率曲线与债券额外成本
            r1 = self.pe.curve.getRate(deliveryDays,1) - self.bond1spread[i].get() / 10000
            r2 = self.pe.curve.getRate(deliveryDays,1) - self.bond2spread[i].get() / 10000
            # step1 计算交易中心估值
            todayYtm1 = float(self.tree.item(cid)['values'][2]) / 100
            todayYtm2 = float(self.tree.item(cid)['values'][4]) / 100
            # if i == 0:
            #     print(todayYtm1)
            #     print(todayYtm2)
            #     print(deliveryTenor)
            #     print(bondTenor)
            futurePrice_cfets = self.pe.bdfValuationCfets(todayYtm1,todayYtm2,repo,deliveryTenor,bondTenor)
            # step2 远期收益率估值
            #2.1 计算债券估值日净价
            # 可交割券1
            bondInfo1 = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][0].bondInfo
            # 计算全价
            dp1 = self.pe.getDpFromYtm(valueDate,bondInfo1['paymentDate'],todayYtm1,bondInfo1['coupon'])
            #计算净价
            cp1 = self.pe.getCpFromDp(valueDate, bondInfo1['paymentDate'],dp1,bondInfo1['coupon'])
            # 可交割券2
            bondInfo2 = self.pe.cm.contractList[self.bdfId[i]].cInfo['deliveryBond'][1].bondInfo
            # 计算全价
            dp2 = self.pe.getDpFromYtm(valueDate,bondInfo2['paymentDate'],todayYtm2,bondInfo2['coupon'])
            # 计算净价
            cp2 = self.pe.getCpFromDp(valueDate, bondInfo2['paymentDate'],dp2,bondInfo2['coupon'])

            #2.2 计算债券远期估值
            fdp1 = self.pe.getFuturePrice(valueDate,dp1,bondInfo1,delD,r1)
            fdp2 = self.pe.getFuturePrice(valueDate,dp2,bondInfo2,delD,r2)
            fcp1 = self.pe.getCpFromDp(delD,bondInfo1['paymentDate'],fdp1,bondInfo1['coupon'],N = 100)
            fcp2 = self.pe.getCpFromDp(delD,bondInfo2['paymentDate'],fdp2,bondInfo2['coupon'],N = 100)
            fytm1 = self.pe.getYtmFromDp(delD,bondInfo1['paymentDate'],fdp1,bondInfo1['coupon'])
            fytm2 = self.pe.getYtmFromDp(delD,bondInfo2['paymentDate'],fdp2,bondInfo2['coupon'])
            interestFutureValue1 = self.pe.getInterestFutureValue(valueDate,bondInfo1,delD,r1)
            interestFutureValue2 = self.pe.getInterestFutureValue(valueDate,bondInfo2,delD,r2)
            
            # 2.3 虚拟券YTM
            bond1w = self.bond1weight[i].get()
            bond2w = self.bond2weight[i].get()
            # futureYtm = bond1w * fytm1 + bond2w * fytm2 修改为
            futureYtm = 0.5 * fytm1 + 0.5 * fytm2
            fp_shch = self.pe.bdfValuationFair(futureYtm,deliveryTenor,bondTenor)

            # 计算期现策略的IRR
            btoday = bond1w * dp1 + bond2w * dp2
            bfuture = bond1w * (fdp1 + interestFutureValue1) + bond2w * (fdp2 + interestFutureValue2)
            portFuture = bfuture + p - fp_shch
            if i == 0:
                print(btoday)
                print(portFuture)

            irr_shch = self.pe.getIRR(btoday,portFuture,deliveryTenor)
            
            # 呈现结果
            self.tree.set(cid,column = 'bdfPrice',value = round(p,4))
            self.tree.set(cid,column = 'value1',value = round(futurePrice_cfets,4))
            self.tree.set(cid,column = 'value2',value = round(fp_shch,4))
            self.tree.set(cid,column = 'irr',value = round(irr_shch*100,4))
            
            # 给表格行上色，远期收益率估值>远期价格则为棕色否则为蓝色，后续考虑优化为自定义设定资金成本，并跟自定义成本进行比较
            if fp_shch > p:
                self.tree.tag_configure(i, background='sandybrown')
            elif fp_shch < p:
                self.tree.tag_configure(i, background='lightblue')
        return
    
    #----------------------------------------------------------------------
    # 生成利率曲线设置界面
    def openCurveSetting(self):
        top = tk.Toplevel()
        top.title('融资利率设置')
        frm1 = tk.Frame(top)
        frm1.grid(column = 0,row = 0)
        frm2 = tk.Frame(top)
        frm2.grid(column = 0,row = 1)
#        frm3 = tk.Frame(top).grid(column = 0,row = 0)
        
        
        tk.Label(frm1,text = '融资利率曲线来源').grid(column = 0,row = 0,padx = 1,pady = 1)
        cmb_sorce = tk.ttk.Combobox(frm1,state = 'readonly',textvariable = self.curveSource)
        cmb_sorce['values'] = self.curveSourceValue
        cmb_sorce.grid(column = 1, row = 0, padx = 1,pady = 1)
        
        tk.Label(frm1,text = '利率曲线插值方法').grid(column = 2,row = 0,padx = 1,pady = 1)
        cmb_interpMethod = tk.ttk.Combobox(frm1,state = 'readonly',textvariable = self.interpMethod)
        cmb_interpMethod['values'] = self.interpMethodValue
        cmb_interpMethod.grid(column = 3, row = 0, padx = 1,pady = 1)
               
        colName = ('期限','起息日','到期日','剩余天数','互换利率','即期利率',\
                   '额外资金成本(BP)')
        
        for j in range(len(colName)-1):
            tk.Label(frm2,text = colName[j]).grid(column = j,row = 0)
        tk.Label(frm2,text = colName[j+1]).grid(column = j+1,row = 0,columnspan = 2)
        for i in range(len(self.tenorName)):
            tk.Label(frm2,text = self.tenorName[i],width = 9).grid(column = 0,row = i + 1)
            tk.Label(frm2,textvariable = self.startDate[i],width = 9).grid(column = 1,row = i + 1)
            tk.Label(frm2,textvariable = self.endDate[i],width = 9).grid(column = 2,row = i + 1)
            tk.Label(frm2,textvariable = self.days[i],width = 9).grid(column = 3,row = i + 1)
            tk.Entry(frm2,textvariable = self.swapRate[i],width = 9).grid(column = 4,row = i + 1,ipadx = 5)
            tk.Entry(frm2,textvariable = self.spotRate[i],width = 9).grid(column = 5,row = i + 1,ipadx = 5)
            tk.Entry(frm2,textvariable = self.spread[i],width = 12).grid(column = 6,row = i + 1,columnspan = 2,ipadx = 5,sticky = 'w')

        def addBp():
            for item in self.spread:
                item.set(item.get()+10)
        
        def minBp():
            for item in self.spread:
                item.set(item.get()-10)
            
        tk.Label(frm2,text = '额外资金成本(+/-)').grid(column = 4,row = 8,sticky = 'w',columnspan = 2) 
        tk.Button(frm2,text = '+10BP',command = addBp).grid(column = 6,row = 8,sticky = 'w')
        tk.Button(frm2,text = '-10BP',command = minBp).grid(column = 7,row = 8,sticky = 'w')
        def syncCurve():
            self.syncTimes.set(self.syncTimes.get() + 1)
        tk.Button(frm2,text = '同步试算参数',command = syncCurve).grid(column = 0,row = 9,columnspan = 2)

        def applySetting():
            self.buildCurve()
            top.destroy()
        tk.Button(frm2,text = '应用参数设置',command = applySetting).grid(column = 2,row = 9,columnspan = 2)
        return
    
    #----------------------------------------------------------------------
    # 曲线来源选择界面
    def cmb_sorce_func(self,*args):
        if self.curveSource.get() == self.curveSourceValue[0]:
            swap = self.pe.getSwapCurveFromWind()
            for i in range(len(self.tenorName)):
                self.swapRate[i].set(swap[i])
        return
    
    #----------------------------------------------------------------------
    # 构造曲线函数
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
        return
    
    #----------------------------------------------------------------------
    # 生成债券设置界面
    def openBondSetting(self):
        top = tk.Toplevel()
        top.title('可交割券设置')
        rowId = 0
        tk.Label(top,text = '可交割券设置(用于远期收益率估值、IRR计算)').grid(column = 0,row = rowId,columnspan = 7,sticky = 'we')
        
        rowId = rowId + 1
        colname = ('合约代码','券1简称','券2简称','组合券1权重','组合券2权重','券1额外借贷成本','券2额外借贷成本')
        for i in range(len(colname)):
            tk.Label(top,text = colname[i]).grid(column = i, row = rowId, padx = 2)
        rowId = rowId + 1
        for i in range(len(self.bdfcode)):
            tk.Label(top,textvariable = self.bdfcode[i]).grid(column = 0, row = rowId+i, padx = 2)
            tk.Label(top,textvariable = self.bond1name[i]).grid(column = 1, row = rowId+i, padx = 2)
            tk.Label(top,textvariable = self.bond2name[i]).grid(column = 2, row = rowId+i, padx = 2)
            tk.Entry(top,textvariable = self.bond1weight[i],width = 7).grid(column = 3, row = rowId+i, padx = 2)
            tk.Entry(top,textvariable = self.bond2weight[i],width = 7).grid(column = 4, row = rowId+i, padx = 2)
            tk.Entry(top,textvariable = self.bond1spread[i],width = 10).grid(column = 5, row = rowId+i, padx = 2)
            tk.Entry(top,textvariable = self.bond2spread[i],width = 10).grid(column = 6, row = rowId+i, padx = 2)
        
        rowId = rowId + len(self.bdfcode)
        tk.Button(top,text = '应用参数设置').grid(row = rowId,column = 0, columnspan = 7 ,sticky = 'e',pady = 5,padx = 2)
        return
    

    
    
if __name__ =='__main__':
    root = tk.Tk()
    root.title('this is right')
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)

    app1 = bdfFrame(root)
    app1.pack(fill = 'both',expand = 1)
    root.mainloop()


