# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 10:00:11 2020

@author: Xiangyu Wang
"""


# try to change version
# try to modify2
import os,sys
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
from fileExplorer import DirList

# 载入Wind API
# 首次运行程序需配置Wind所在目录
try:
    from WindPy import w
except:
    sitepath=".";
    for x in sys.path:
        ix=x.find('site-packages')
        if( ix>=0 and x[ix:]=='site-packages'):
          sitepath=x;
          break;
    d = DirList('.')
    d.top.mainloop()
    os.chdir(basedir)
    print(os.getcwd())
    windPath = sitepath + '\\WindPy.pth'
    # 创建路径文件 并写入Wind路劲
    fp = open(windPath,'w') #直接打开一个文件，如果文件不存在则创建文件
    endId = d.WindDir.find('WindNET')
    windDir = d.WindDir[:endId+7] + '\\x64'
    fp.write(windDir)
    fp.close()
    from WindPy import w

# 载入其他包
from SHCHPriceEngine import priceEngine
from SHCHGui import mainWindow
from SHCHPriceEngine.WorkCalendar import SHCH_workCalendar
from SHCHPriceEngine.ContractMgr import BdfContractMgr

w.start()
calen = SHCH_workCalendar()
CM = BdfContractMgr(calen)
CM.subscribeBond()
CM.subscribeBdf()
pe1 = priceEngine(calen,CM)
pe2 = priceEngine(calen,CM)
root = mainWindow(pe1,pe2)
root.mainloop()
CM.cancelSubscribe()



