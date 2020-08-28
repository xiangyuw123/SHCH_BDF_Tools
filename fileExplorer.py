# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:15:14 2020

@author: 123
"""
# this master modify
import os
from time import sleep
import tkinter as tk 

class DirList(object):
    def __init__(self, initdir=None):
        self.WindDir = ''
        '''构造函数，说明版本信息'''
        self.top = tk.Tk()
        self.label = tk.Label(self.top, 
            text = '首次使用本软件，请设置Wind终端所在目录',font=('仿宋', 14, 'bold'))
        self.label.pack()

        self.cwd = tk.StringVar(self.top)

        self.frm1 = tk.Frame(self.top)
        self.frm1.pack(fill = tk.X)
        self.dir1Text = tk.Label(self.frm1, text = '当前目录:',\
            font=('仿宋', 11, 'bold'))
        self.dir1Text.pack(side = tk.LEFT)
        
        self.dir1 = tk.Label(self.frm1, 
            fg='blue', font=('Helvetica', 10, 'bold'))
        self.dir1.pack(side = tk.LEFT)

        self.dirfm = tk.Frame(self.top)
        self.dirsb = tk.Scrollbar(self.dirfm)
        self.dirsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.dirs = tk.Listbox(self.dirfm, height=15,
            width=50, yscrollcommand=self.dirsb.set)
            
        self.dirs.bind('<Double-1>', self.setDirAndGo)
        self.dirsb.config(command=self.dirs.yview)
        self.dirs.pack(side=tk.LEFT, fill=tk.BOTH)
        self.dirfm.pack()

        self.dirn = tk.Entry(self.top, width=50,
            textvariable=self.cwd)
        self.dirn.bind('<Return>', self.doLS)
        self.dirn.pack()

        self.bfm = tk.Frame(self.top)
#        self.clr = tk.Button(self.bfm, text='Clear',
#            command = self.clrDir,
#            activeforeground = 'white',
#            activebackground = 'blue')
        self.ls = tk.Button(self.bfm, 
            text = '确认当前文件夹',
            command = self.selectFolder,
            activeforeground = 'white',
            activebackground = 'green')
        self.quit = tk.Button(self.bfm, text='Quit',
            command=self.top.quit,
            activeforeground='white',
            activebackground='red')
#        self.clr.pack(side=tk.LEFT)
        self.ls.pack(side=tk.LEFT)
#        self.quit.pack(side=tk.LEFT)
        self.bfm.pack()

        if initdir:
            self.cwd.set(os.curdir)
            self.doLS()

#    def clrDir(self, ev=None):
#        self.cwd.set('')

    def setDirAndGo(self, ev=None):
        self.last = self.cwd.get()
        self.dirs.config(selectbackground='red')
        check = self.dirs.get(self.dirs.curselection())
        if not check:
            check = os.curdir
        self.cwd.set(check)
        self.doLS()

    def doLS(self, ev=None):
        error = ''
        tdir = self.cwd.get()
        if not tdir: tdir = os.curdir

        if not os.path.exists(tdir):
            error = tdir + ': no such file'
        elif not os.path.isdir(tdir):
            error = tdir + ': not a directory'

        if error:
            self.cwd.set(error)
            self.top.update()
            sleep(2)
            if not (hasattr(self, 'last') \
                and self.last):
                self.last = os.curdir
                self.cwd.set(self.last)
                self.dirs.config(\
                    selectbackground='LightSkyBlue')
                self.top.update()
                return

        self.cwd.set(\
            'FETCHING DIRECTORY CONTENTS...')
        self.top.update()
        dirlist = os.listdir(tdir)
        dirlist.sort()
        os.chdir(tdir)
        self.dir1.config(text=os.getcwd())
        self.dirs.delete(0, tk.END)
        self.dirs.insert(tk.END, os.curdir)
        self.dirs.insert(tk.END, os.pardir)
        for eachFile in dirlist:
            self.dirs.insert(tk.END, eachFile)
        self.cwd.set(os.curdir)
        self.dirs.config(\
            selectbackground='LightSkyBlue')
    
    def selectFolder(self):
        self.WindDir = os.getcwd()
        self.top.destroy()

def main():
    d = DirList(os.curdir)
    tk.mainloop()
    
if __name__ == '__main__':
    main()