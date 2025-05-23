"""
点名器4
抽取一位同学的姓名，显示出来并朗读
常驻窗口
具有名单编辑器功能

"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, SERIF, BOLD
import nameselector4.Speak as speak
import win32.win32api as win32api
import win32.win32gui as win32gui


import win32con
import time
import os
from random import choice
import pathlib
import asyncio
import threading

#hwnd = win32gui.FindWindow(None, windowName)


def windowNoBorder(hwnd):
    """
    无边框窗口
    """
    if hwnd:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style &= ~win32con.WS_BORDER
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
def setWindowPos(hwnd,percentY):
    """
    设置窗口位置
    (X一定为0，Y为屏幕高度的百分比)
    """
    if hwnd:
        x, y, cx, cy = win32gui.GetWindowRect(hwnd)
        screenHeight = win32api.GetSystemMetrics(1)
        y = int(screenHeight*percentY)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, y, cx, cy, 0)
def setWindowSize(hwnd,width,height):
    """
    设置窗口大小
    """
    width=int(width)
    height=int(height)
    if hwnd:
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, width, height, 0)
def setWindowTransparancy(hwnd,alpha):
    """
    设置窗口透明度
    alpha为0~255
    """
    alpha=int(alpha)
    if hwnd:
        extendedStyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extendedStyle | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), alpha, win32con.LWA_ALPHA)
def tweenTransparency(hwnd,startAlpha,endAlpha,split=10,duration=1):
    """
    窗口透明度渐变
    duration为渐变时间
    alpha为0~255
    """
    split=int(split)

    if hwnd:
        increment=(endAlpha-startAlpha)/(duration*split)
        for i in range(int(duration*split)):
            alpha=startAlpha+i*increment
            setWindowTransparancy(hwnd,alpha)
            time.sleep(duration/split)
            
            
        setWindowTransparancy(hwnd,endAlpha)

class windowStatus:


    windowSize=(15,15)
    windowContent=None
    currentStatus=0
    #三种状态
    # 0：未开始 点击按钮进入点名阶段
    # 1：点名阶段 点击按钮点名，或点击返回按钮返回到0，或点击编辑按钮进入编辑阶段
    # 2：编辑阶段 点击按钮保存，或点击返回按钮返回到1
    windowSizeList=[(15,15),(100,100),(400,300)]
    windowContentList=[None,None,None] #late

speakList=[]
speakThreadShouldClose=False
def speakThread():
    while not speakThreadShouldClose:
        
        if speakList:
            speak.speak(speakList.pop(0))
        else:
            time.sleep(.01)
    return 123456756897
threading.Thread(target=speakThread).start()


class NameSelector4(toga.App):
    ws=windowStatus()
    nameList=[]
    nameListpop=[]
    HomophonesDict={}

    if not pathlib.Path('namelist.txt').exists():
        with open('namelist.txt','w',encoding='utf-8') as f:
            f.write('在这里添加名单\n每行一个名字')
    if not pathlib.Path('HomophonesDict.txt').exists():
        with open('HomophonesDict.txt','w',encoding='utf-8') as f:
            f.write('在这里添加同音字:如\n覃:秦')
    with open('namelist.txt','r',encoding='utf-8') as f:
        for line in f:
            nameList.append(line.strip())
    with open('HomophonesDict.txt','r',encoding='utf-8') as f:
        for line in f:
            key,value=line.strip().split(':')
            HomophonesDict[key]=value
    
    def startup(self):
        self._impl.create_menus = lambda *x, **y: None # 禁用菜单栏
        self.hwnd=None
        self.defaultFont=toga.Font(family='微软雅黑',size=20)
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        def getWindowStatus(self,num):
            self.ws.windowSize=self.ws.windowSizeList[num]
            self.ws.windowContent=self.ws.windowContentList[num]
            self.ws.currentStatus=num
            return self.ws
        def switchTo(self):
            tweenTransparency(self.hwnd,255,0,20,.3)
            self.main_window.content=self.ws.windowContent  
            self.main_window.size=self.ws.windowSize
            tweenTransparency(self.hwnd,0,255,20,.3)

        def startButton_Click(widget):
            getWindowStatus(self,1)
            switchTo(self)
            selectButton_Click(widget)
        def backButton_Click(widget):
            getWindowStatus(self,self.ws.currentStatus-1)
            switchTo(self)
        def selectButton_Click(widget):
            global speakList
            if self.nameListpop==[]:
                self.nameListpop=self.nameList.copy()
            selectedName=choice(self.nameListpop)
            self.nameListpop.remove(selectedName)
           
            self.nameLabel.text=selectedName
            for key,value in self.HomophonesDict.items():
                selectedName=selectedName.replace(key,value)         
            speakList.append(selectedName)
        def editButton_Click(widget):
            getWindowStatus(self,2)
            switchTo(self)
        async def nameInput_Change(widget):
            try:
                self.nameList=widget.value.split('\n')
                with open('namelist.txt','w',encoding='utf-8') as f:
                    f.write('\n'.join(self.nameList))

            except Exception as e:
                await self.main_window.dialog(toga.ErrorDialog('错误',str(e)))
            self.nameListpop=self.nameList.copy()
        async def HomophonesInput_Change(widget):
            try:
                self.HomophonesDict={}
                for line in widget.value.split('\n'):
                    key,value=line.strip().split(':')
                    self.HomophonesDict[key]=value
                with open('HomophonesDict.txt','w',encoding='utf-8') as f:
                    f.write('\n'.join([f'{key}:{value}' for key,value in self.HomophonesDict.items()]))
            except ValueError:
                pass
            except Exception as e:
                await self.main_window.dialog(toga.ErrorDialog('错误',str(e)))
        def exitNameSelector4(widget):
            global speakThreadShouldClose
            tweenTransparency(self.hwnd,255,0,20,.3)
            speakThreadShouldClose=True
            self.exit()
            
        Launch=toga.Box(style=Pack(direction=COLUMN))
        self.startButton=toga.Button('>',on_press=startButton_Click,style=Pack(padding=5,font_size=30))
        #self.startButton=toga.Image('resources/start.png',on_press=startButton_Click,style=Pack(padding=5,font_size=30))
        Launch.add(self.startButton)
        

        NameSelector=toga.Box(style=Pack(direction=COLUMN))
        self.nameLabel=toga.Label('',style=Pack(padding=5,font_size=40))
        self.backButton=toga.Button('返回',on_press=backButton_Click,style=Pack(padding=5,font_size=10))
        self.selectButton=toga.Button('点名',on_press=selectButton_Click,style=Pack(padding=5,font_size=20))
        self.editButton=toga.Button('编辑',on_press=editButton_Click,style=Pack(padding=5,font_size=10))

        EditBox=toga.Box(style=Pack(direction=COLUMN))
        buttonBox2=toga.Box(style=Pack(direction=ROW))
        buttonBox2.add(toga.Button('返回',on_press=backButton_Click,style=Pack(padding=5,font_size=10)))
        buttonBox2.add(toga.Button('退出点名器',on_press=exitNameSelector4,style=Pack(padding=5,font_size=10)))
        EditBox.add(buttonBox2)
        EditorBox=toga.Box(style=Pack(direction=ROW))
        nameEditorBox=toga.Box(style=Pack(direction=COLUMN))
        nameEditorBox.add(toga.Label('名单编辑器',style=Pack(padding=5,font_size=15)))
        nameInput=toga.MultilineTextInput(value='\n'.join(self.nameList),style=Pack(padding=5,font_size=15,width=200,height=200),on_change=nameInput_Change)
        nameEditorBox.add(nameInput)
        HomophonesBox=toga.Box(style=Pack(direction=COLUMN))
        HomophonesBox.add(toga.Label('同音字编辑器',style=Pack(padding=5,font_size=15)))
        HomophonesInput=toga.MultilineTextInput(value='\n'.join([f'{key}:{value}' for key,value in self.HomophonesDict.items()]),on_change=HomophonesInput_Change,style=Pack(padding=5,font_size=15,width=200,height=200))
        HomophonesBox.add(HomophonesInput)
        
        EditorBox.add(nameEditorBox)
        EditorBox.add(HomophonesBox)
        

        
        
        


        buttonBox=toga.Box(style=Pack(direction=ROW,padding=10))
        buttonBox.add(self.backButton)
        buttonBox.add(self.selectButton)
        buttonBox.add(self.editButton)
       

        NameSelector.add(buttonBox)
        NameSelector.add(self.nameLabel)

        EditBox.add(EditorBox)
        
        self.ws.windowContentList[0]=Launch
        self.ws.windowContentList[1]=NameSelector
        self.ws.windowContentList[2]=EditBox
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.title='com.example.nameselector4.main'
        self.main_window.content = Launch
       
        self.main_window.size = (20,20)
        self.main_window.show()
        
        self.hwnd = win32gui.FindWindow(None, self.main_window.title)
        
        #设置窗口大小
        setWindowSize(self.hwnd,15,15)
        self.main_window.size = (5,5)
        #设置窗口位置
        setWindowPos(self.hwnd,0.6)
        #设置窗口无边框
        windowNoBorder(self.hwnd)



def main():
    return NameSelector4()
