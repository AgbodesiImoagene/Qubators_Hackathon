# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 13:57:07 2021

@author: agbod
"""

try:
    import pyi_splash
    pyi_splash.update_text('Loading complete...')
    pyi_splash.close()
except:
    pass

from aiohttp.client_exceptions import ClientConnectorError
from asyncio import new_event_loop, set_event_loop, Queue, LifoQueue, create_task, gather, sleep
# from asyncio import run as arun
from asyncio.exceptions import TimeoutError, CancelledError
from pandas import Series, DataFrame
from numpy import array, vectorize # , reshape
from numpy import double as npdouble
from matplotlib import rcParams
from matplotlib.pyplot import Figure, gcf
from matplotlib.dates import DateFormatter, MinuteLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import time, strftime, localtime, daylight, timezone, altzone
from time import sleep as tsleep
import websockets.legacy.client
from threading import Thread
import sys
import os
from os.path import abspath, join
from sys import exit as sysexit
from queue import Queue as qQueue
from datetime import datetime
from nest_asyncio import apply
from tkinter import X, BOTH, TOP, BOTTOM, LEFT, END, HORIZONTAL, WORD, Y, RIGHT, SINGLE, VERTICAL # , NONE, INSERT
from PIL import ImageTk, Image
from binance import Client, AsyncClient, BinanceSocketManager
from binance.helpers import round_step_size
from binance.enums import KLINE_INTERVAL_1MINUTE
from binance.exceptions import BinanceRequestException, BinanceAPIException
from tkinter.ttk import Combobox
from tkinter import StringVar, IntVar, Canvas, Text, Tk, Entry, Button, Frame, Label, Listbox, Scale, Scrollbar, scrolledtext, Radiobutton, messagebox
from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW, Popen, PIPE

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)

FILE_NAME = resource_path('TradeRecords.txt')
logoImg = resource_path('Logo.ico')
nameImg = resource_path('NameCropped.png')
welcomeImg = resource_path('Welcome.png')

rcParams['font.size'] = 10

myFmt = DateFormatter('%H:%M')
mns = MinuteLocator()

if len(sys.argv) == 1:
    useTestnet = ''
    API_KEY = ''
    SECRET_KEY = ''
    base = 'BTC'
    quote = 'USDT'
    sl = 0.2
    tp = 0.4
    trade_allocation = ''
    useClosingTime = False
    startTime = ''
    closingTime = ''
    strategy = ''
else:
    useTestnet = sys.argv[1]
    API_KEY = sys.argv[2]
    SECRET_KEY = sys.argv[3]
    base = sys.argv[4]
    quote = sys.argv[5]
    sl = sys.argv[6]
    tp = sys.argv[7]
    trade_allocation = sys.argv[8]
    useClosingTime = sys.argv[9]
    startTime = sys.argv[10]
    closingTime = sys.argv[11]
    strategy = sys.argv[12]

pair = base + quote
client = ''
filters = ''
init_price = ''
hourBoxEntry = "00"
minBoxEntry = "00"
offset = ''
startBaseBalance = ''
startQuoteBalance = ''
currentBaseBalance = ''
currentQuoteBalance = ''
close = False
min_trade_allocation = ''
curr_open_positions = []


class TheWindow:
    def __init__(self):
        self.root = Tk()
        self.root.title("AutoTrader")
        self.root.iconbitmap(logoImg)
        
        self.root.geometry("800x400")
        self.root.configure(bg = "#80D5FF")
    
        self.imgs = [0, 0]
        i = Image.open(nameImg)
        j = i.resize((round(i.size[0] * 0.4), round(i.size[1] * 0.4)))
        self.imgs[0] = ImageTk.PhotoImage(j)
        i = Image.open(welcomeImg)
        j = i.resize((round(i.size[0] * 0.8), round(i.size[1] * 0.8)))
        self.imgs[1] = ImageTk.PhotoImage(j)
        
        self.root.resizable(False, False)

        self.run()

    def run(self):
        if len(sys.argv) == 1:
            self.initGUI()
        else:
            self.initGUI2()
        
    def initGUI(self):
        introFrame = Frame(
            self.root,
            bg = "#80D5FF",
            height = 400,
            width = 800,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        introFrame.place(x = 0, y = 0)
        
        label1 = Label(introFrame,
                       image=self.imgs[1],
                       height = 400,
                       width = 400,
                       bg="#80D5FF"
        )
        label1.place(
            x=200,
            y=0
        )
        
        next_button = Button(
            introFrame,
            text="next",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.destroyWelcomeFrame([introFrame]),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        next_button.place(
            x=700,
            y=320
        )
    
    def initGUI2(self):
        introFrame = Frame(
            self.root,
            bg = "#80D5FF",
            height = 400,
            width = 800,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        introFrame.place(x = 0, y = 0)
        
        label1 = Label(introFrame,
                       image=self.imgs[1],
                       height = 400,
                       width = 400,
                       bg="#80D5FF"
        )
        label1.place(
            x=200,
            y=0
        )
        
        next_button = Button(
            introFrame,
            text="next",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.destroyWelcomeFrame2([introFrame]),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        next_button.place(
            x=700,
            y=320
        )
    
    def destroyWelcomeFrame(self, prevFrames):
        for frame in prevFrames:
            frame.destroy()
        self.testnet()
        
    def destroyWelcomeFrame2(self, prevFrames):
        global client
        global filters
        global init_price
        global offset
        global startBaseBalance
        global startQuoteBalance
        global currentBaseBalance
        global currentQuoteBalance
        global min_trade_allocation
        global curr_open_positions

        try:
            client = Client(API_KEY, SECRET_KEY, testnet=useTestnet)
            client.get_account()
        except ClientConnectorError:
            messagebox.showerror(
                title="Could not create client.",
                message="Please check connection. ")
            return
        except TimeoutError:
            messagebox.showerror(
                title="Could not create client.",
                message="Connection timeout. ")
            return
        except Exception as e:
            messagebox.showerror(
                title="Could not create client.",
                message=str(e))
            return
        
        if useClosingTime:
            if localtime().tm_isdst and daylight:
                offset = -altzone
            else:
                offset = -timezone

        startBaseBalance = client.get_asset_balance(asset=base)
        startBaseBalance = float(startBaseBalance['free'])
        startQuoteBalance = client.get_asset_balance(asset=quote)
        startQuoteBalance = float(startQuoteBalance['free'])
        currentBaseBalance = startBaseBalance
        currentQuoteBalance = startQuoteBalance
        
        data = client.get_symbol_info(pair)
        filters = {}
        filters['maxPrecision'] = 10 ** -(data['baseAssetPrecision'])
        all_filters = data['filters']
        for dictionary in all_filters:
            if dictionary['filterType'] == 'LOT_SIZE':
                filters['lotStepSize'] = float(dictionary['stepSize'])
            if dictionary['filterType'] == 'MARKET_LOT_SIZE':
                filters['minQty'] = float(dictionary['minQty'])
                filters['maxQty'] = float(dictionary['maxQty'])
                filters['stepSize'] = float(dictionary['stepSize'])
            if dictionary['filterType'] == 'MIN_NOTIONAL':
                filters['minNotional'] = float(dictionary['minNotional'])
            if dictionary['filterType'] == 'PRICE_FILTER':
                filters['tickSize'] = float(dictionary['tickSize'])
                
        init_price = client.get_ticker(symbol=pair)
        init_price = float(init_price["lastPrice"])
        min_trade_allocation = filters['minNotional'] * (100 / (99 - sl))
        
        curr_open_positions = sys.argv[13]

        for frame in prevFrames:
            frame.destroy()
        self.root.geometry("1000x500")
        self.root.configure(bg='#C4C4C4')
        self.mainWindow()

    def testnet(self):
        infoFrame = Frame(
            self.root,
            bg = "#80D5FF",
            height = 400,
            width = 200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        infoFrame.place(x = 0, y = 0)
        
        useTestnetFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        useTestnetFrame.place(x = 200, y = 0)
        prevFrames = [infoFrame, useTestnetFrame]
        
        button_1 = Button(
            useTestnetFrame,
            text="Yes",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.clientKeys(True, prevFrames),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_1.place(
            x=150.0,
            y=150,
            width=100.0,
            height=60.0
        )
        
        button_2 = Button(
            useTestnetFrame,
            text="No",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.clientKeys(False, prevFrames),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_2.place(
            x=350.0,
            y=150,
            width=100.0,
            height=60.0
        )
        
        name = Label(
            infoFrame,
            image=self.imgs[0],
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=1,
            y=30
        )
        
        info = Label(
            infoFrame,
            text="The testnet is a test environment \n"
            "for the Binance network that allows \n"
            "you trial this program with simulated \n"
            "funds although the prices are not \n"
            "always an accurate reflection of \n"
            "real-time prices. \n\n",        
            justify=LEFT,
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(8))
        )
        info.place(
            x=4,
            y=90
        )
    
        
        useTestnetQuestion = Label(
            useTestnetFrame,
            text="Do you want to use a Testnet?",
            bg="white",
            fg="black",
            font=("Roboto", int(20))
        )
        useTestnetQuestion.place(
            x=100,
            y=50
        )
    
    def clientKeys(self, val, prevFrames):
        global useTestnet
        useTestnet = val
        
        infoFrame = Frame(
            self.root,
            bg = "#80D5FF",
            height = 400,
            width = 200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        infoFrame.place(x = 0, y = 0)
        
        prevFrames[0].destroy()
        prevFrames[1].destroy()
        
        clientDetailsFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        clientDetailsFrame.place(x = 200, y = 0)
            
        name = Label(
            infoFrame,
            image=self.imgs[0],
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=1,
            y=30
        )
    
        if val:
            text1 = "Binance Testnet API key"
            text2 = "Binance Testnet secret key"
            info = Label(
                infoFrame,
                text="If you don't already have Testnet API \n"
                "keys, head to testnet.binance.vision, \n"
                "login with Github credentials and \n"
                "click on generate HMAC_SHA256 Key, \n"
                "then copy the keys into the spaces \n"
                "provided. \n\n"
                "Be sure to save the keys to a secure \n"
                "location for future ease of access. \n\n"
                "Please check that your internet \n"
                "connection is working properly. ",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        else:
            text1 = "Binance API key"
            text2 = "Binance secret key"
            info = Label(
                infoFrame,
                text="If you don't already have Binance API \n"
                "keys, register an account with \n"
                "Binance or login to your existing \n"
                "one, then click 'API Management' \n"
                "from the user center icon. Enter \n"
                "a label for your API and click \n"
                "'Create API'. Ensure the 'Enable \n"
                "Reading' and 'Enable Spot and \n"
                "Margin Trading' restrictions are \n"
                "selected. \n\n"
                "Be sure to save the keys to a secure \n"
                "location for future ease of access. \n\n"
                "Please check that your internet \n"
                "connection is working properly. ",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        
        label1 = Label(
            clientDetailsFrame, 
            text=text1,
            bg="white",
            fg="black",
            font=("Roboto", int(18))
        )
        label1.place(x=30, y=70)
        API_KEY_entry = Entry(
            clientDetailsFrame, 
            bd=4, 
            bg="#DADADA", 
            highlightthickness=0,
            font=("Roboto", int(15))
        )
        API_KEY_entry.place(x=30, y=120, width=500, height=40)
        API_KEY_entry.focus()
        
        label2 = Label(
            clientDetailsFrame, 
            text=text2,
            bg="white",
            fg="black",
            font=("Roboto", int(18))
        )
        label2.place(x=30, y=170)
        SECRET_KEY_entry = Entry(
            clientDetailsFrame, 
            bd=4, 
            bg="#DADADA", 
            highlightthickness=0, 
            font=("Roboto", int(15)),
            show="*"
        )
        SECRET_KEY_entry.place(x=30, y=220, width=500, height=40)
        
        prevFrames = [infoFrame, clientDetailsFrame]
        keys = [API_KEY_entry, SECRET_KEY_entry]
        
        button_1 = Button(
            clientDetailsFrame,
            text="Create client",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.validateClient(prevFrames, keys),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_1.place(
            x=380,
            y=300
        )
    
        button_2 = Button(
            clientDetailsFrame,
            text="prev",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.destroyWelcomeFrame(prevFrames),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_2.place(
            x=30,
            y=300
        )
    
    def validateClient(self, prevFrames, keys):
        global client
        global API_KEY
        global SECRET_KEY
    
        API_KEY = keys[0].get()
        SECRET_KEY = keys[1].get()
    
        try:
            client = Client(API_KEY, SECRET_KEY, testnet=useTestnet)
            client.get_account()
        except ClientConnectorError:
            messagebox.showerror(
                title="Could not create client.",
                message="Please check connection. ")
            return
        except BinanceRequestException or BinanceAPIException as e:
            messagebox.showerror(
                title="Could not create client.",
                message=str(e) + "\nPlease enter valid keys. ")
            return
        except TimeoutError:
            messagebox.showerror(
                title="Could not create client.",
                message="Connection timeout. ")
            return
        except Exception as e:
            messagebox.showerror(
                title="Could not create client.",
                message=str(e))
            return
        else:
            self.destroyClientKeysFrame(prevFrames)
    
    def destroyClientKeysFrame(self, prevFrames):
        for frame in prevFrames:
            frame.destroy()
        self.settings()
        
    def settings(self):
        infoFrame = Frame(
            self.root,
            bg = "#80D5FF",
            height = 400,
            width = 200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        infoFrame.place(x = 0, y = 0)
        
        settingsFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        settingsFrame.place(x = 200, y = 0)
        
        name = Label(
            infoFrame,
            image=self.imgs[0],
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=1,
            y=30
        )
    
        info = Label(
            infoFrame,
            text="Enter or select a base symbol or \n"
            "quote symbol that forms a valid \n"
            "Binance pair. \n\n"
            "Lot size is a fixed amount of the \n"
            "quote currency to be entered into \n"
            "each trade. \n\n"
            "Closing time is the time of day the \n"
            "application automatically closes all \n"
            "its trades and exits within 24 hours. ",
            justify=LEFT,
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(8))
        )
        info.place(
            x=4,
            y=90
        )
    
        quote_label = Label(
            settingsFrame, 
            text="Quote symbol: ",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        quote_label.place(x=300, y=50)
    
        quoteChoice = StringVar(settingsFrame)            
        quoteDropdown = Combobox(settingsFrame, textvariable=quoteChoice, width=6)
        if useTestnet:
            quoteDropdown["values"] = ("USDT", "BUSD", "BTC", "BNB")
        else:
            quoteDropdown["values"] = ("USDT", "USDC", "BUSD", "TUSD", "PAX", "BTC", "ETH", "BNB")
    
        quoteDropdown.place(x=385, y=50)
        quoteDropdown.set(quote)
        
        base_label = Label(
            settingsFrame, 
            text="Base symbol: ",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        base_label.place(x=20, y=50)
    
        baseChoice = StringVar(settingsFrame)            
        baseDropdown = Combobox(settingsFrame, textvariable=baseChoice, width=6)
        if useTestnet:
            baseDropdown["values"] = ("BTC", "ETH", "BNB", "LTC", "TRX", "XRP")
        else:
            baseDropdown["values"] = ("BTC", "ETH", "BNB", "LTC", "TRX", "XRP",
                                      "NEO", "QTUM", "EOS", "SNT", "BNT", "BCC", 
                                      "GAS", "HSR", "OAX", "DNT", "MCO", "ICN", 
                                      "WTC", "LRC", "YOYO", "OMG", "ZRX", "STRAT", 
                                      "SNGLS", "BQX", "KNC", "FUN", "SNM", "IOTA", 
                                      "LINK", "XVG", "SALT", "MDA", "MTL", "SUB", 
                                      "ETC", "MTH", "ENG", "DNT", "ZEC", "AST", "DOGE", 
                                      "DASH", "BTG", "EVX", "REQ", "VIB", "HSR", 
                                      "POWR", "ARK", "MANA", "DGD", "ADA", "MATIC")
    
        baseDropdown.place(x=100, y=50)
        baseDropdown.set(base)
        
        sl_label = Label(
            settingsFrame, 
            text="Stop-loss percentage",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        sl_label.place(x=20, y=120)
        
        slScale = Scale(
            settingsFrame, 
            from_=0.02, 
            to=2.00, 
            resolution=0.02, 
            orient=HORIZONTAL, 
            length=200
        )
        slScale.set(sl)
        slScale.place(x=20, y=150)
    
        tp_label = Label(
            settingsFrame, 
            text="Take-profit percentage",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        tp_label.place(x=300, y=120)
        
        tpScale = Scale(
            settingsFrame, 
            from_=0.02, 
            to=2.00, 
            resolution=0.02, 
            orient=HORIZONTAL, 
            length=200
        )
        tpScale.set(tp)
        tpScale.place(x=300, y=150)
        
        lotSizeLabel = Label(
            settingsFrame, 
            text="Lot Size (quote currency)",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        lotSizeLabel.place(x=20, y=220)
        
        LotSizeEntry = Entry(
            settingsFrame, 
            bd=2, 
            width=16
        )
        LotSizeEntry.place(x=20, y=250)
        LotSizeEntry.insert(0, str(trade_allocation))
        LotSizeEntry.focus()
        
        closingTimeLabel = Label(
            settingsFrame, 
            text="Closing Time [HH:MM]",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        closingTimeLabel.place(x=300, y=220)
        
        HourChoice = StringVar(settingsFrame)
        HourBox = Combobox(settingsFrame, textvariable=HourChoice, state="readonly", width=4)
        HourBox["values"] = tuple([f"{i:02d}" for i in range(0, 24)])
        HourBox.place(x=300, y=250)
        HourBox.set(hourBoxEntry)
        MinChoice = StringVar(settingsFrame)
        MinBox = Combobox(settingsFrame, textvariable=MinChoice, state="readonly", width=4)
        MinBox["values"] = tuple([f"{i:02d}" for i in range(0, 60)])
        MinBox.place(x=350, y=250)
        MinBox.set(minBoxEntry)
        enableButton = Button(
            settingsFrame,
            text="Enable" if not useClosingTime else "Disable",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=1,
            highlightthickness=0,
            command=lambda: self.enableClosingTime(HourBox, MinBox, enableButton),
            font=("Roboto", int(8)),
            relief="ridge"
        )
        enableButton.place(
            x=400,
            y=250
        )
        if not useClosingTime:
            HourBox.configure(state='disabled')
            MinBox.configure(state='disabled')
        
        prevFrames = [infoFrame, settingsFrame]
        setting_vars = [baseChoice, quoteChoice, slScale, tpScale, LotSizeEntry, HourChoice, MinChoice]
        
        button_1 = Button(
            settingsFrame,
            text="next",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.validateSettings(prevFrames, setting_vars),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_1.place(
            x=440,
            y=300
        )
        
    def enableClosingTime(self, HourBox, MinBox, enableButton):
        global useClosingTime
        useClosingTime = not useClosingTime
        
        if useClosingTime:
            HourBox.configure(state='normal')
            MinBox.configure(state='normal')
            enableButton.configure(text="Disable")
        else:
            HourBox.configure(state='disabled')
            MinBox.configure(state='disabled')
            enableButton.configure(text="Enable")
        
    def validateSettings(self, prevFrames, setting_vars):
        global base
        global quote
        global pair
        global filters
        global init_price
        global sl
        global tp
        global hourBoxEntry
        global minBoxEntry
        global trade_allocation
        global startTime
        global closingTime
        global offset
        global startBaseBalance
        global startQuoteBalance
        global currentBaseBalance
        global currentQuoteBalance
        global min_trade_allocation
        
        base = setting_vars[0].get()
        quote = setting_vars[1].get()
        pair = base + quote
        sl = setting_vars[2].get()
        tp = setting_vars[3].get()
        hourBoxEntry = setting_vars[5].get()
        minBoxEntry = setting_vars[6].get()
        try:
            trade_allocation = float(setting_vars[4].get())
        except ValueError:
            messagebox.showerror(
                title="Error",
                message="Enter a number for Lot Size. ")
            return
        except Exception as e:
            messagebox.showerror(
                title="Error",
                message=e)
            return
        
        if useClosingTime:
            if localtime().tm_isdst and daylight:
                offset = -altzone
            else:
                offset = -timezone
                
            startTime = ((time() % 86400) + offset) % 86400
            closingTime = hourBoxEntry + ":" + minBoxEntry
            closingTime = datetime.strptime(closingTime, '%H:%M')
            closingTime = (closingTime - datetime(1900, 1, 1)).total_seconds()
            
            if ((time() % 86400) + offset) % 86400 < closingTime:
                closingTime = closingTime - startTime
            else:
                closingTime = 86400 - startTime + closingTime

        data = client.get_symbol_info(pair)
        if data == None:
            messagebox.showerror(
                title="Error",
                message=pair + "is not a valid symbol pair. ")
            return
        
        startBaseBalance = client.get_asset_balance(asset=base)
        startBaseBalance = float(startBaseBalance['free'])
        startQuoteBalance = client.get_asset_balance(asset=quote)
        startQuoteBalance = float(startQuoteBalance['free'])
        currentBaseBalance = startBaseBalance
        currentQuoteBalance = startQuoteBalance
        
        filters = {}
        filters['maxPrecision'] = 10 ** -(data['baseAssetPrecision'])
        all_filters = data['filters']
        for dictionary in all_filters:
            if dictionary['filterType'] == 'LOT_SIZE':
                filters['lotStepSize'] = float(dictionary['stepSize'])
            if dictionary['filterType'] == 'MARKET_LOT_SIZE':
                filters['minQty'] = float(dictionary['minQty'])
                filters['maxQty'] = float(dictionary['maxQty'])
                filters['stepSize'] = float(dictionary['stepSize'])
            if dictionary['filterType'] == 'MIN_NOTIONAL':
                filters['minNotional'] = float(dictionary['minNotional'])
            if dictionary['filterType'] == 'PRICE_FILTER':
                filters['tickSize'] = float(dictionary['tickSize'])
                
        init_price = client.get_ticker(symbol=pair)
        init_price = float(init_price["lastPrice"])
        maxQuote = init_price * filters['maxQty']
        min_trade_allocation = filters['minNotional'] * (100 / (99 - sl))
        
        if (trade_allocation * (100 - sl) / 100) < filters['minNotional']:
            messagebox.showerror(
                title="Error",
                message="Trade allocation is too small. \n"
                "minimum value is " + str(min_trade_allocation))
            return
        elif trade_allocation > startQuoteBalance:
            messagebox.showerror(
                title="Error",
                message="Trade allocation is too large. \n"
                "You do not have enough " + quote)
            return
        elif trade_allocation > maxQuote:
            messagebox.showerror(
                title="Error",
                message="Trade allocation is too large. \n"
                "Maximum value is" + maxQuote)
            return
        
        self.destroySettingsFrame(prevFrames)
    
    def destroySettingsFrame(self, prevFrames):
        for frame in prevFrames:
            frame.destroy()
        self.chooseStrategy()
    
    def chooseStrategy(self):    
        infoFrame = Frame(
            self.root,
            bg = "#80D5FF",
            height = 400,
            width = 200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        infoFrame.place(x = 0, y = 0)
        
        strategyFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        strategyFrame.place(x = 200, y = 0)
        
        name = Label(
            infoFrame,
            image=self.imgs[0],
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=1,
            y=30
        )
            
        strategyChoice = IntVar(strategyFrame)            
        info = Label(
            infoFrame,
            text="Enter and exit trades \n"
            "manually. \n\n",
            justify=LEFT,
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(8))
        )
        info.place(
            x=4,
            y=90
        )
        option0 = Radiobutton(
            strategyFrame, 
            text="Manual Trading", 
            variable=strategyChoice, 
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=0, 
            width=60, 
            anchor="w"
        )
        option0.place(x=50, y=60)
        option1 = Radiobutton(
            strategyFrame, 
            text="Simple Moving Average Strategy", 
            variable=strategyChoice, 
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=1, 
            width=60, 
            anchor="w"
        )
        option1.place(x=50, y=90)
        option2 = Radiobutton(
            strategyFrame, 
            text="Exponential Moving Average Strategy", 
            variable=strategyChoice, 
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=2, 
            width=60, 
            anchor="w"
        )
        option2.place(x=50, y=120)
        option3 = Radiobutton(
            strategyFrame, 
            text="MACD Strategy", 
            variable=strategyChoice,
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=3, 
            width=60, 
            anchor="w"
        )
        option3.place(x=50, y=150)
        option4 = Radiobutton(
            strategyFrame, 
            text="MACD + RSI Strategy", 
            variable=strategyChoice,
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=4, 
            width=60, 
            anchor="w"
        )
        option4.place(x=50, y=180)
        option5 = Radiobutton(
            strategyFrame, 
            text="MACD + RSI + Stochastic Strategy", 
            variable=strategyChoice,
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=5, 
            width=60, 
            anchor="w"
        )
        option5.place(x=50, y=210)
        option6 = Radiobutton(
            strategyFrame, 
            text="Moving Average + MACD + RSI Strategy", 
            variable=strategyChoice,
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=6, 
            width=60, 
            anchor="w"
        )
        option6.place(x=50, y=240)
        option0.select()

        prevFrames = [infoFrame, strategyFrame]
        button_1 = Button(
            strategyFrame,
            text="Finish",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.clearWindow(strategyChoice),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_1.place(
            x=420,
            y=300
        )
    
        button_2 = Button(
            strategyFrame,
            text="prev",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.destroyClientKeysFrame(prevFrames),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_2.place(
            x=30,
            y=300
        )
    
    def strategyLabels(self, choice, infoFrame):
        for w in infoFrame.winfo_children():
            w.destroy()

        name = Label(
            infoFrame,
            text="AutoTrader",
            bg="#80D5FF",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=12,
            y=30
        )

        if choice.get() == 0:
            info = Label(
                infoFrame,
                text="Enter and exit trades \n"
                "manually. \n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        elif choice.get() == 1:
            info = Label(
                infoFrame,
                text="This strategy places a buy \n"
                "order when the current 20 MA \n"
                "crosses the 50 MA upwards or if \n"
                "the price dips below the 20 MA \n"
                "during a perfect uptrend. \n"
                "20 MA > 50 MA > 100 MA > 200 MA \n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        elif choice.get() == 2:
            info = Label(
                infoFrame,
                text="This strategy places a buy \n"
                "order when the current 12 EMA \n"
                "crossesthe  26 EMA upwards or if \n"
                "the price dips below the 12 EMA \n"
                "in a perfect uptrend. \n"
                "12 EMA > 26 EMA > 50 EMA > 100 EMA\n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        elif choice.get() == 3:
            info = Label(
                infoFrame,
                text="This strategy places a buy \n"
                "order when the MACD line \n"
                "crosses the Signal line upwards \n"
                "if the price is above the 100 \n"
                "EMA \n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        elif choice.get() == 4:
            info = Label(
                infoFrame,
                text="This strategy places a buy \n"
                "order when the MACD line \n"
                "crosses the signal line upwards \n"
                "if the RSI is below 60. \n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        elif choice.get() == 5:
            info = Label(
                infoFrame,
                text="This strategy places a buy \n"
                "order when the RSI crosses 50 \n"
                "upwards if the MACD is greater \n"
                "than the signal line and the \n"
                "stochastic indicator is less than \n"
                "80. \n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
        elif choice.get() == 6:
            info = Label(
                infoFrame,
                text="This strategy places a buy \n"
                "order when the MACD line \n"
                "crosses the signal line upwards \n"
                "if the RSI is below 60 and the \n"
                "20 MA is greater than the 50 MA. \n\n",
                justify=LEFT,
                bg="#80D5FF",
                fg="black",
                font=("Roboto", int(8))
            )
            info.place(
                x=4,
                y=90
            )
    
    def clearWindow(self, choice):
        global strategy

        strategy = choice.get()
        
        for widgets in self.root.winfo_children():
            widgets.destroy()
        self.root.geometry("1000x500")
        self.root.configure(bg='#C4C4C4')
        self.mainWindow()
    
    def mainWindow(self):
        balanceFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 180,
            width = 180,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        balanceFrame.pack_propagate(False)
        balanceFrame.place(x = 10, y = 10)    
        balanceLabel = Label(balanceFrame, text='Available Balance', bd=0, font=('Roboto', int(10)))
        balanceLabel.pack(fill=X, side=TOP)
        balanceText = Text(balanceFrame, bd=0, font=('Roboto', int(9)), cursor='arrow')
        balanceText.insert('end', f'Starting Quote Balance: \n{startQuoteBalance} \n'
                           f'Starting Base Balance: \n{startBaseBalance} ')
        balanceText.pack(fill=BOTH, side=BOTTOM)
        balanceText.configure(state='disabled')
        
        slidersFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 280,
            width = 180,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        slidersFrame.place(x = 10, y = 210)
        slidersFrame.pack_propagate(False)
        slidersLabel = Label(slidersFrame, text='Settings', bd=0, font=('Roboto', int(10)))
        slidersLabel.pack(fill=X, side=TOP)
        slScale = Scale(
            slidersFrame, 
            from_=0.02, 
            to=2.00, 
            resolution=0.02, 
            orient=HORIZONTAL, 
            length=150, 
            label="Stop-loss percentage"
        )
        slScale.set(sl)
        slScale.place(x=10, y=20)    
        tpScale = Scale(
            slidersFrame, 
            from_=0.02, 
            to=2.00, 
            resolution=0.02, 
            orient=HORIZONTAL, 
            length=150, 
            label="Take-profit percentage"
        )
        tpScale.set(tp)
        tpScale.place(x=10, y=100)
        
        lotSizeLabel = Label(
            slidersFrame, 
            text=f"Lot Size ({quote})",
            bg="white",
            fg="black",
            font=("Roboto", int(9))
        )
        lotSizeLabel.place(x=10, y=180)
        LotSizeEntry = Entry(
            slidersFrame, 
            bd=1, 
            width=16
        )
        LotSizeEntry.place(x=10, y=210)
        LotSizeEntry.insert(0, str(trade_allocation))
        LotSizeButton = Button(
            slidersFrame,
            text="set",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.validateAllocation(LotSizeEntry),
            relief="ridge"
        )
        LotSizeButton.place(
            x=125,
            y=210, 
            width=40,
            height=20
        )
        
        chartFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 230,
            width = 580,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        chartFrame.pack_propagate(False)
        chartFrame.place(x = 210, y = 10)
        chartLabel = Label(chartFrame, text='Chart', font=('Roboto', int(10)), bd=0)
        chartLabel.pack(fill=X, side=TOP)
        chartScrollable = V_ScrollableFrame(chartFrame)
        gcf().autofmt_xdate()
        
        tradesFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 230,
            width = 380,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        tradesFrame.pack_propagate(False)
        tradesFrame.place(x = 210, y = 260)
        tradesLabel = Label(tradesFrame, text='Trade Records', font=('Roboto', int(10)), bd=0)
        tradesLabel.pack(fill=X, side=TOP)
        tradesText = scrolledtext.ScrolledText(tradesFrame, bd=0, cursor='arrow', wrap=WORD)
        tradesText.pack(fill=BOTH, side=BOTTOM)
        tradesText.configure(state='disabled')
        
        openTradesFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 230,
            width = 180,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        openTradesFrame.pack_propagate(False)
        openTradesFrame.place(x = 610, y = 260)
        openTradesLabel = Label(openTradesFrame, text='Open Positions', font=('Roboto', int(10)), bd=0)
        openTradesLabel.pack(fill=X, side=TOP)
        openTradesScrollbar = Scrollbar(openTradesFrame)
        openTradesScrollbar.pack(fill=Y, side=RIGHT)
        self.openTradesListbox = Listbox(openTradesFrame, yscrollcommand=openTradesScrollbar.set, bd=0, selectmode=SINGLE)
        self.openTradesListbox.pack(fill=BOTH, expand=True)
        openTradesScrollbar.config(command=self.openTradesListbox.yview)

        pricesFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 280,
            width = 180,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        pricesFrame.pack_propagate(False)
        pricesFrame.place(x = 810, y = 10)
        pricesLabel = Label(pricesFrame, text='Live Prices', font=('Roboto', int(10)), bd=0)
        pricesLabel.pack(fill=X, side=TOP)
        pricesText = scrolledtext.ScrolledText(pricesFrame, bd=0, cursor='arrow')
        pricesText.pack(fill=BOTH, side=BOTTOM)
        pricesText.configure(state='disabled')
        
        buyButton = Button(
            self.root,
            text="Buy",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.thread.manualBuy(),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        buyButton.place(
            x=850,
            y=310, 
            width=80,
            height=40
        )

        sellButton = Button(
            self.root,
            text="Sell",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.manualSellHandler(),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        sellButton.place(
            x=850,
            y=370, 
            width=80,
            height=40
        )
        sellButton.configure(state='disabled')
        
        quitButton = Button(
            self.root,
            text="Quit",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.on_closing(),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        quitButton.place(
            x=850,
            y=430, 
            width=80,
            height=40
        )

        frames = {'prices': pricesText, 
                  'balances': balanceText, 
                  'trades': tradesText, 
                  'chart': chartScrollable.frame, 
                  'sliders': slidersFrame, 
                  'positions': self.openTradesListbox, 
                  'sell': sellButton}
        sliders = {'tp': tpScale, 'sl': slScale}
        self.startAsync(frames, sliders)
    
    def validateAllocation(self, entry):
        global trade_allocation
        
        try:
            allocation = float(entry.get())
        except ValueError:
            entry.delete(0, END)
            entry.insert(0, str(trade_allocation))
            messagebox.showerror(
                title="Error",
                message="Enter a number for Lot Size. ")
            return
        except Exception as e:
            entry.delete(0, END)
            entry.insert(0, str(trade_allocation))
            messagebox.showerror(
                title="Error",
                message=e)
            return
        
        maxQuote = init_price * filters['maxQty']
        if (allocation * (100 - sl) / 100) < filters['minNotional']:
            entry.delete(0, END)
            entry.insert(0, str(trade_allocation))
            messagebox.showerror(
                title="Error",
                message="Trade allocation is too small. \n"
                "minimum value is " + str(min_trade_allocation))
            return
        elif allocation > currentQuoteBalance:
            entry.delete(0, END)
            entry.insert(0, str(trade_allocation))
            messagebox.showerror(
                title="Error",
                message="Trade allocation is too large. \n"
                "You do not have enough " + quote)
            return
        elif allocation > maxQuote:
            entry.delete(0, END)
            entry.insert(0, str(trade_allocation))
            messagebox.showerror(
                title="Error",
                message="Trade allocation is too large. \n"
                "Maximum value is" + maxQuote)
            return
        else:
            trade_allocation = allocation
            return

    def startAsync(self, frames, sliders):
        self.thread = AsyncioThread(self)
        self.thread.start()
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.on_closing())
        try:
            self.root.after(100, lambda: self.refresh_frames(frames, sliders))
        except Exception as e:
            messagebox.showerror(
                title="Error",
                message=str(e) + "\nAutoTrader will now restart.")
            restartQ.put_nowait(1)
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? "):
            stopQ.put_nowait(1)
            
    def manualSellHandler(self):
        sellQ.put_nowait(self.openTradesListbox.curselection()[0])
        
    def refresh_frames(self, frames, sliders):
        global tp
        global sl
        
        while True:
            if not self.thread.price.empty():
                frames['prices'].configure(state='normal')
                frames['prices'].insert("end", str(self.thread.price.get_nowait()) + '\n')
                frames['prices'].see("end")
                frames['prices'].yview("end")
                frames['prices'].configure(state='disabled')
            if not self.thread.trades.empty():
                frames['balances'].configure(state='normal')
                frames['balances'].delete(1.0, END)
                frames['balances'].insert('end', 
                                              f'Starting {quote} Balance: \n{startQuoteBalance} \n'
                                              f'Starting {base} Balance: \n{startBaseBalance} \n\n'
                                              f'Current {quote} Balance: \n{currentQuoteBalance} \n'
                                              f'Current {base} Balance: \n{currentBaseBalance} '
                                              )
                frames['balances'].configure(state='disabled')
                frames['trades'].configure(state='normal')
                frames['trades'].insert("end", self.thread.trades.get_nowait())
                frames['trades'].see("end")
                frames['trades'].yview("end")
                frames['trades'].configure(state='disabled')
            if not self.thread.charts.empty():
                for w in frames['chart'].winfo_children():
                    w.destroy()
                figs = self.thread.charts.get_nowait()
                for fig in figs:
                    frm = Frame(frames['chart'], 
                                bg = "#FFFFFF", 
                                width = 550, 
                                height = 200, 
                                bd=0
                                )
                    frm.pack(side=TOP)
                    frm.pack_propagate(False)
                    line = FigureCanvasTkAgg(fig, frm)
                    line.get_tk_widget().pack(fill=BOTH)
            if not self.thread.open_positions_display.empty():
                pos = self.thread.open_positions_display.get_nowait()
                if pos[0] == 'add':
                    frames['positions'].insert("end", f"[{pos[2]}] {pos[1]} {base}")
                elif pos[0] == 'del':
                    frames['positions'].delete(pos[1])
            if not self.thread.errors.empty():
                e = self.thread.errors.get_nowait()
                messagebox.showerror(
                    title="Error",
                    message=str(e) + "\nAutoTrader will now restart.")
                restartQ.put_nowait(1)
            if not close and not frames['positions'].curselection() == ():
                frames['sell'].configure(state='normal')
            else:
                frames['sell'].configure(state='disabled')
            if not close:
                tp = sliders['tp'].get()
                sl = sliders['sl'].get()
            self.root.update()
            tsleep(0.5)

class AsyncioThread(Thread):
    def __init__(self, theWindow):
        self.asyncio_loop = new_event_loop()
        set_event_loop(self.asyncio_loop)
        
        self.theWindow = theWindow
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        self.asyncio_loop.run_until_complete(self.trader())
        
    async def trader(self):
        global client
        global model
        global scaler

        self.open_positions = Queue()
        self.price = LifoQueue()
        self.price_buy = LifoQueue()
        self.price_sell = LifoQueue()
        self.price_manual_sell = LifoQueue()
        self.data = Queue()
        self.data_frame = Queue()
        self.data_frame_figure = Queue()
        self.charts = Queue()
        self.signals = Queue()
        self.sell_price = Queue()
        self.trades = Queue()
        self.errors = Queue()
        self.open_positions_display = Queue()
                
        client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=useTestnet)

        await self.open_positions.put(curr_open_positions)
        for i in curr_open_positions:
            self.asyncio_loop.call_soon_threadsafe(self.open_positions_display.put_nowait, 
                                                   ['add', i['qty'], i['time']])

        self.save_to_records(startQuoteBalance, 'open')
        self.tasks = [create_task(self.check_closing_time()),
                      create_task(self.kline_data()), 
                      create_task(self.update_data()),
                      create_task(self.lineplots()), 
                      create_task(self.generate_signals()), 
                      create_task(self.place_buy_order()),
                      create_task(self.place_sell_order()), 
                      create_task(self.manualSell())]

        try:
            await gather(*self.tasks, create_task(self.checkQuit()), create_task(self.checkRestart()))
        except CancelledError:
            pass
        
        return

    async def checkQuit(self):
        while stopQ.empty() and not close:
            await sleep(2)
        await self.closeProgram()

    async def checkRestart(self):
        while restartQ.empty() and not close:
            await sleep(2)
        await self.restartProgram()

    async def check_closing_time(self):
        global close
        if useClosingTime:
            while time_diff() < closingTime and time_diff() < 86400:
                await sleep(10)
            close = True

    async def kline_data(self):
        bm = BinanceSocketManager(client)
        ks = bm.kline_socket(pair, interval=KLINE_INTERVAL_1MINUTE)
        myKeys = ['t', 'o', 'h', 'l', 'c', 'v', 'T', 'q', 'n', 'V', 'Q']
        async with ks as kscm:
            while not close:
                try:
                    a = await kscm.recv()
                except Exception as e:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
                else:
                    res = a['k']
                    self.asyncio_loop.call_soon_threadsafe(self.price.put_nowait, float(res['c']))
                    self.asyncio_loop.call_soon_threadsafe(self.price_buy.put_nowait, float(res['c']))
                    self.asyncio_loop.call_soon_threadsafe(self.price_sell.put_nowait, float(res['c']))
                    self.asyncio_loop.call_soon_threadsafe(self.price_manual_sell.put_nowait, float(res['c']))
                    if res['x']:
                        candle = [res[x] for x in myKeys]
                        self.asyncio_loop.call_soon_threadsafe(self.data.put_nowait, candle)
        return

    async def update_data(self):
        df = await self.get_historical_data()
        self.asyncio_loop.call_soon_threadsafe(self.data_frame_figure.put_nowait, df)
        while not close:
            new_row = await self.data.get()
            if strategy == 1:
                new_row = new_row + [0, 0, 0, 0]
            elif strategy == 2:
                new_row = new_row + [0, 0, 0, 0]
            elif strategy == 3:
                new_row = new_row + [0, 0, 0, 0, 0]
            elif strategy == 4:
                new_row = new_row + [0, 0, 0, 0, 0]
            elif strategy == 5:
                new_row = new_row + [0, 0, 0, 0, 0, 0, 0]
            elif strategy == 6:
                new_row = new_row + [0, 0, 0, 0, 0, 0, 0]
            new_row = array(new_row).astype(npdouble)
            df = self.update_df(df, new_row)
            self.asyncio_loop.call_soon_threadsafe(self.data_frame.put_nowait, df)
            self.asyncio_loop.call_soon_threadsafe(self.data_frame_figure.put_nowait, df)
        return

    async def get_historical_data(self):
        headings = ['Open Time', 'Open', 'High', 'Low', 'Close',
                    'Volume', 'Close Time', 'Quote Asset Volume',
                    'Number of Trades', 'Taker buy Base Asset Volume',
                    'Taker buy Quote Asset Volume', 'Ignore']
        klines = array(await client.get_historical_klines(pair, AsyncClient.KLINE_INTERVAL_1MINUTE, '1 day ago UTC')).astype(npdouble)
        df = DataFrame.from_records(klines, columns=headings)
        df.drop(['Ignore'], axis=1, inplace=True)
        df.dropna(inplace=True)
        if strategy == 1:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_100'] = df['Close'].rolling(window=100).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
        elif strategy == 2:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
        elif strategy == 3:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        elif strategy == 4:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))
        elif strategy == 5:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))
            high_14 = df['High'].rolling(14).max()
            low_14 = df['Low'].rolling(14).min()
            df['%K'] = (df['Close'] - low_14) * 100 / (high_14 - low_14)
            df['%D'] = df['%K'].rolling(3).mean()
        elif strategy == 6:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))
        return df

    def update_df(self, df, new_row):
        new_row = Series(new_row, index=df.columns)
        if new_row[0] != df.iloc[-1, 0]:
            df = df.append(new_row, ignore_index=True)
        else:
            df.iloc[-1, :] = new_row
        if strategy == 1:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_100'] = df['Close'].rolling(window=100).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
        elif strategy == 2:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
            df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
        elif strategy == 3:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        elif strategy == 4:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))
        elif strategy == 5:
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))
            high_14 = df['High'].rolling(14).max()
            low_14 = df['Low'].rolling(14).min()
            df['%K'] = (df['Close'] - low_14) * 100 / (high_14 - low_14)
            df['%D'] = df['%K'].rolling(3).mean()
        elif strategy == 6:
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            delta = df['Close'].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'] = 100 - (100 / (1 + rs))
        return df

    async def generate_signals(self):
        while not close:
            df = await self.data_frame.get()
            if strategy == 0:
                pass
            elif strategy == 1:
                if self.strat1(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
            elif strategy == 2:
                if self.strat2(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
            elif strategy == 3:
                if self.strat3(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
            elif strategy == 4:
                if self.strat4(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
            elif strategy == 5:
                if self.strat5(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
            elif strategy == 6:
                if self.strat6(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
        return
    
    def strat1(self, df):
        price = df['Close']
        ma_20 = df['SMA_20']
        ma_50 = df['SMA_50']
        ma_100 = df['SMA_100']
        ma_200 = df['SMA_200']
        if ma_20.iloc[-1] > ma_50.iloc[-1] and ma_20.iloc[-2] < ma_50.iloc[-2]:
            return True
        if ma_20.iloc[-1] > ma_50.iloc[-1] and ma_50.iloc[-1] > ma_100.iloc[-1] and ma_100.iloc[-1] > ma_200.iloc[-1]:
            if price.iloc[-1] < ma_20.iloc[-1] and price.iloc[-1] > ma_50.iloc[-1] and (ma_20.iloc[-1] - price.iloc[-1]) / price.iloc[-1] > tp * 100:
                return True
        return False
    
    def strat2(self, df):
        price = df['Close']
        ma_12 = df['EMA_12']
        ma_26 = df['EMA_26']
        ma_50 = df['EMA_50']
        ma_100 = df['EMA_100']
        if ma_12.iloc[-1] > ma_26.iloc[-1] and ma_12.iloc[-2] < ma_26.iloc[-2]:
            return True
        if ma_12.iloc[-1] > ma_26.iloc[-1] and ma_26.iloc[-1] > ma_50.iloc[-1] and ma_50.iloc[-1] > ma_100.iloc[-1]:
            if price.iloc[-1] < ma_12.iloc[-1] and price.iloc[-1] > ma_26.iloc[-1] and (ma_12.iloc[-1] - price.iloc[-1]) / price.iloc[-1] > tp * 100:
                return True
        return False
     
    def strat3(self, df):
        price = df['Close']
        macd = df['MACD']
        signalLine = df['Signal Line']
        ma_100 = df['EMA_100']
        dif = (price.iloc[-10:] - ma_100.iloc[-10:]) >= 0
        if macd.iloc[-1] > signalLine.iloc[-1] and macd.iloc[-2] < signalLine.iloc[-2] and dif.all():
            return True
        return False

    def strat4(self, df):
        macd = df['MACD']
        signalLine = df['Signal Line']
        rsi = df['RSI']
        if macd.iloc[-1] > signalLine.iloc[-1] and macd.iloc[-2] < signalLine.iloc[-2] and rsi.iloc[-1] < 60:
            return True
        return False

    def strat5(self, df):
        macd = df['MACD']
        signalLine = df['Signal Line']
        rsi = df['RSI']
        k = df['%K']
        d = df['%D']
        if macd.iloc[-1] > signalLine.iloc[-1] and rsi.iloc[-2] < 50 and rsi.iloc[-1] > 50 and k.iloc[-1] < 80 and d.iloc[-1] < 80:
            return True
        return False

    def strat6(self, df):
        ma_20 = df['SMA_20']
        ma_50 = df['SMA_50']
        macd = df['MACD']
        signalLine = df['Signal Line']
        rsi = df['RSI']
        if macd.iloc[-1] > signalLine.iloc[-1] and macd.iloc[-2] < signalLine.iloc[-2] and rsi.iloc[-1] < 60:
            if ma_20.iloc[-1] > ma_50.iloc[-1]:
                return True
        return False

    def manualBuy(self):
        self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)

    async def manualSell(self):
        global curr_open_positions
        
        while not close:
            if not sellQ.empty():
                i = sellQ.get_nowait()
                current_price = await self.price_manual_sell.get()
                pos = await self.open_positions.get()
                await self.open_positions.put(pos)
                try:
                    s = pos[i]
                except IndexError:
                    pass
                else:
                    done = await self.sell(s['qty'], current_price, s['id'], i)
                    if done:
                        pos.remove(s)
                        curr_open_positions = pos
                        await self.open_positions.get()
                        await self.open_positions.put(pos)
            await sleep(0.5)
        
    async def place_buy_order(self):
        count = 1
        while not close:
            s = await self.signals.get()
            if s == 1:                
                try:
                    balance = await client.get_asset_balance(asset=quote)
                except Exception as e:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
                else:
                    current_price = await self.price_buy.get()
                    balance = float(balance['free'])
                    allocation = trade_allocation
                    quantity =  allocation / current_price
                    if balance < min_trade_allocation:
                        pass
                    elif balance < trade_allocation:
                        pass
                    else:
                        if allocation >= filters['minNotional']:
                            quantity =  allocation / current_price
                        else:
                            quantity =  (filters['minNotional'] * 1.001) / current_price
                        if quantity > filters['maxQty']:
                            quantity = filters['maxQty']
                        res = await self.buy(quantity, current_price, count)
                        if res:
                            count += 1
        return
    
    async def buy(self, qty, current_price, count):
        if filters['stepSize'] == 0:
            qty = round_step_size(qty, filters['lotStepSize'])
        else:
            qty = round_step_size(qty, filters['stepSize'])
            
        try:
            order = await client.order_market_buy(
                symbol=pair,
                quantity=qty)
        except Exception as e:
            self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
            return False
        else:
            while True:
                await sleep(0.2)
                try:
                    trade_status = await client.get_order(symbol=pair, orderId=order['orderId'])
                except Exception as ex:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(ex))
                    return False
                else:
                    if float(trade_status['executedQty']) == qty:
                        await self.save_trades('buy', qty, current_price, count)
                        await self.sell_price.put({'stop-loss': (1 - (sl / 100)) * current_price, 
                                                   'take-profit': (1 + (tp / 100)) * current_price, 
                                                   'qty': qty, 
                                                   'id': count, 
                                                   'time': strftime('%H:%M')
                                                   })
                        self.asyncio_loop.call_soon_threadsafe(self.open_positions_display.put_nowait, 
                                                               ['add', qty, strftime('%H:%M')])
                        return True
    
    async def place_sell_order(self):
        global curr_open_positions
        
        sell_list = []
        while not close:
            current_price = await self.price_sell.get()
            if not self.sell_price.empty():
                position = await self.sell_price.get()
                sell_list = await self.open_positions.get()
                sell_list.append(position)
                await self.open_positions.put(sell_list)
                curr_open_positions = sell_list
            for s in sell_list:
                if current_price < s['stop-loss'] or current_price > s['take-profit']:
                    done = await self.sell(s['qty'], current_price, s['id'], sell_list.index(s))
                    if done:
                        sell_list.remove(s)
                        curr_open_positions = sell_list
                        await self.open_positions.get()
                        await self.open_positions.put(sell_list)
        return
    
    async def sell(self, qty, current_price, count, idx):
        try:
            order = await client.order_market_sell(
                symbol=pair,
                quantity=qty)
        except Exception as e:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
                return False
        else:
            await sleep(0.6)
            try:
                await client.get_order(symbol=pair, orderId=order['orderId'])
            except Exception as ex:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(ex))
                return False
            else:
                self.asyncio_loop.call_soon_threadsafe(self.open_positions_display.put_nowait, 
                                       ['del', idx])
                await self.save_trades('sell', qty, current_price, count)
                return True
        
    async def close_positions(self):
        res = await self.open_positions.get()
        self.open_positions.put_nowait(res)
        if not res == []:
            self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 'Closing positions. \n\n')
        positions = await self.open_positions.get()
        data = await client.get_symbol_ticker(symbol=pair)
        price = float(data['price'])
        for i in positions:
            await self.sell(i['qty'], price, i['id'], positions.index(i))
            
        closing_balance = await client.get_asset_balance(asset=quote)
        closing_balance = float(closing_balance['free'])
        self.save_to_records(closing_balance, 'close')

    def save_to_records(self, balance, trade_period):
        try:
            file = open(FILE_NAME, 'a')
            self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, strftime('%c') + '\n\n')
            if useTestnet:
                file.write('Testnet \n')
            if trade_period == 'open':
                file.write(strftime('%c') + '\n')
                file.write(f'Opening balance: {balance} {quote}. \n')
            elif trade_period == 'close':
                file.write(f'Closing balance: {balance} {quote}. \n\n')
        finally:
            file.close()
        
    async def save_trades(self, trade_type, qty, price, count):
        global currentBaseBalance
        global currentQuoteBalance
        
        currentBaseBalance = await client.get_asset_balance(asset=base)
        currentBaseBalance = float(currentBaseBalance['free'])
        currentQuoteBalance = await client.get_asset_balance(asset=quote)
        currentQuoteBalance = float(currentQuoteBalance['free'])

        try:
            file = open(FILE_NAME, 'a')
            file.write(strftime('%H:%M') + '\n')
            if trade_type == 'buy':
                file.write(f'Trade {count} \n')
                file.write(f'Bought {qty} {base} at {price} {quote} per {base} ({qty * price} {quote}). \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, strftime("%H:%M") + '\n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Trade {count} \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 
                                                       f'Bought {qty} {base} at {price} {quote} per {base} ({round(qty * price, 4)} {quote}) \n\n')
            elif trade_type == 'sell':
                file.write(f'Closed trade {count} \n')
                file.write(f'Sold {qty} {base} at {price} {quote} per {base} ({qty * price} {quote}). \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, strftime("%H:%M") + '\n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Closed trade {count} \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 
                                                       f'Sold {qty} {base} at {price} {quote} per {base} ({round(qty * price, 4)} {quote}) \n\n')
        finally:
            file.close()
            
    async def lineplots(self):
        while not close:
            df = await self.data_frame_figure.get()
            x = df['Close Time'].to_numpy()
            x = x[-60:]
            func = lambda i: datetime.fromtimestamp(int(i) / 1000)
            vecfunc = vectorize(func)
            x = vecfunc(x)
    
            fig1 = Figure()
            plot1 = self.plotPrice(df, x, fig1)
            if strategy == 0:
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1])
            elif strategy == 1:
                y1 = df['SMA_20'].to_numpy()
                y2 = df['SMA_50'].to_numpy()
                plot1.plot(x, y1[-60:], "-b", label="20 S.M.A.")
                plot1.plot(x, y2[-60:], "-r", label="50 S.M.A.")
                plot1.legend(loc="upper right", fontsize="x-small")
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1])
            elif strategy == 2:
                y1 = df['EMA_12'].to_numpy()
                y2 = df['EMA_26'].to_numpy()
                plot1.plot(x, y1[-60:], "-b", label="12 E.M.A.")
                plot1.plot(x, y2[-60:], "-r", label="26 E.M.A.")
                plot1.legend(loc="upper right", fontsize="x-small")
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1])
            elif strategy == 3:
                y1 = df['EMA_100'].to_numpy()
                plot1.plot(x, y1[-60:], "-b", label="100 E.M.A.")
                plot1.legend(loc="upper right", fontsize="x-small")
                fig2 = Figure()
                self.plotMACD(df, x, fig2)
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1, fig2])
            elif strategy == 4:
                plot1.legend(loc="upper right", fontsize="x-small")
                fig2 = Figure()
                self.plotMACD(df, x, fig2)
                fig3 = Figure()
                self.plotRSI(df, x, fig3)
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1, fig2, fig3])
            elif strategy == 5:
                plot1.legend(loc="upper right", fontsize="x-small")
                fig2 = Figure()
                self.plotMACD(df, x, fig2)
                fig3 = Figure()
                self.plotRSI(df, x, fig3)
                fig4 = Figure()
                self.plotStochastic(df, x, fig4)
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1, fig2, fig3, fig4])
            elif strategy == 6:
                y1 = df['SMA_20'].to_numpy()
                y2 = df['SMA_50'].to_numpy()
                plot1.plot(x, y1[-60:], "-b", label="20 S.M.A.")
                plot1.plot(x, y2[-60:], "-r", label="50 S.M.A.")
                plot1.legend(loc="upper right", fontsize="x-small")
                fig2 = Figure()
                self.plotMACD(df, x, fig2)
                fig3 = Figure()
                self.plotRSI(df, x, fig3)
                self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, [fig1, fig2, fig3])
            
    def plotPrice(self, df, x, figure):
        ax = figure.add_subplot(111)
        y = df['Close'].to_numpy()
        ax.plot(x, y[-60:], "-g", label="Price")
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.set_minor_locator(mns)
        ax.set_title(pair)
        return ax
    
    def plotMACD(self, df, x, figure):
        ax = figure.add_subplot(111)
        y1 = df['MACD'].to_numpy()
        y2 = df['Signal Line'].to_numpy()
        ax.plot(x, y1[-60:], "-b", label="MACD")
        ax.plot(x, y2[-60:], "-r", label="Signal Line")
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.set_minor_locator(mns)
        ax.legend(loc="upper right", fontsize="x-small")
        ax.set_title("MACD")
        return ax

    def plotRSI(self, df, x, figure):
        ax = figure.add_subplot(111)
        y = df['RSI'].to_numpy()
        ax.plot(x, y[-60:], "-b", label="RSI")
        ax.plot(x, [30]*len(x), color='k', linestyle='--')
        ax.plot(x, [70]*len(x), color='k', linestyle='--')
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.set_minor_locator(mns)
        ax.legend(loc="upper right", fontsize="x-small")
        ax.set_title("RSI")
        return ax

    def plotStochastic(self, df, x, figure):
        ax = figure.add_subplot(111)
        y1 = df['%K'].to_numpy()
        y2 = df['%D'].to_numpy()
        ax.plot(x, y1[-60:], "-b", label="%K")
        ax.plot(x, y2[-60:], "-r", label="%D")
        ax.plot(x, [20]*len(x), color='k', linestyle='--')
        ax.plot(x, [80]*len(x), color='k', linestyle='--')
        ax.xaxis.set_major_formatter(myFmt)
        ax.xaxis.set_minor_locator(mns)
        ax.legend(loc="upper right", fontsize="x-small")
        ax.set_title("Stochastic Indicator")
        return ax
    
    async def closeProgram(self):
        global client
        global close

        close = True
        try:
            await self.close_positions()
        except:
            pass
            
        await sleep(2)
        try:
            await client.close_connection()
        except:
            pass
        try:
            self.asyncio_loop.stop()
        except:
            pass
        try:
            self.asyncio_loop.close()
        except:
            pass
        self.theWindow.root.destroy()
        sysexit()

    async def restartProgram(self):
        global client
        global close

        close = True
        try:
            await self.close_positions()
        except:
            pass
            
        await sleep(2)
        try:
            await client.close_connection()
        except:
            pass
        try:
            self.asyncio_loop.stop()
        except:
            pass
        try:
            self.asyncio_loop.close()
        except:
            pass
        self.theWindow.root.destroy()
        os.system('AutoTrader.exe '
                  f'{useTestnet}, '
                  f'{API_KEY} '
                  f'{SECRET_KEY} '
                  f'{base} '
                  f'{quote} '
                  f'{sl} '
                  f'{tp} '
                  f'{trade_allocation} '
                  f'{useClosingTime} '
                  f'{startTime} '
                  f'{closingTime} '
                  f'{strategy} '
                  f'{curr_open_positions}')
        sysexit()
        
class V_ScrollableFrame:
    def __init__(self, container):
        canvas = Canvas(container, width=550, height=230)
        scrollbar=Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        self.frame = Frame(canvas, 
                           bg = "#FFFFFF",
                           bd=0
                           )
        self.frame.bind('<Configure>', 
                        lambda e: canvas.configure(scrollregion=canvas.bbox('all')
                                                 )
                        )
        canvas.create_window((0, 0), window=self.frame, anchor='nw', width=550)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT)
        scrollbar.pack(side=RIGHT, fill=Y)

def time_diff():
    currTime = ((time() % 86400) + offset) % 86400
    if currTime > startTime:
        return currTime - startTime
    else:
        return 86400 - startTime + currTime

def popen(cmd: str) -> str:
    """For pyinstaller -w"""
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
    process = Popen(cmd,startupinfo=startupinfo, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    return process.stdout.read()

if __name__ == '__main__':
    apply()
    stopQ = qQueue()
    sellQ = qQueue()
    restartQ = qQueue()
    window = TheWindow()
    window.root.mainloop()
