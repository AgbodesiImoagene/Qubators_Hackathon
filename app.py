# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 13:49:45 2021

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
from asyncio.exceptions import TimeoutError, CancelledError
from pandas import Series, DataFrame
from numpy import array, vectorize # , reshape
from numpy import double as npdouble
from matplotlib import rcParams
from matplotlib.pyplot import Figure, gcf
from matplotlib.dates import DateFormatter, MinuteLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import time, strftime
import websockets.legacy
import websockets.legacy.client
# from joblib import load
from threading import Thread
# import tensorflow.keras.models as tfmodels
# from tensorflow.keras.models import load_model
from sys import _MEIPASS
from os.path import abspath, join
from sys import exit as sysexit
from queue import Queue as qQueue
from datetime import datetime
from nest_asyncio import apply
from tkinter import X, BOTH, TOP, BOTTOM, LEFT, END, HORIZONTAL # , NONE, VERTICAL, Y, RIGHT, INSERT
from binance import Client, AsyncClient, BinanceSocketManager
from binance.helpers import round_step_size
from binance.enums import KLINE_INTERVAL_1MINUTE
from binance.exceptions import BinanceRequestException, BinanceAPIException
from tkinter.ttk import Combobox
from tkinter import StringVar, IntVar, Text, Tk, Entry, Button, Frame, Label, Scale, scrolledtext, Radiobutton, messagebox
from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW, Popen, PIPE

def resource_path(relative_path):
    try:
        base_path = _MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)

FILE_NAME = resource_path('TradeRecords.txt')
img = resource_path('icon2.ico')

rcParams['font.size'] = 10

myFmt = DateFormatter('%H:%M')
# hrs = mdates.HourLocator()
mns = MinuteLocator()

useTestnet = ''
API_KEY = ''
SECRET_KEY = ''
client = ''
base = 'BTC'
quote = 'USDT'
pair = 'BTCUSDT'
filters = ''
init_price = ''
sl = 0.2
tp = 0.4
trade_allocation = ''
closingTime = 86400
strategy = ''
startBaseBalance = ''
startQuoteBalance = ''
currentBaseBalance = ''
currentQuoteBalance = ''
close = False
min_trade_allocation = ''
model = ''
scaler = ''

class TheWindow:
    def __init__(self):
        self.root = Tk()
        self.root.title("AutoTrader")
        self.root.iconbitmap(img)
        
        self.root.geometry("800x400")
        self.root.configure(bg = "#C4C4C4")
    
        self.run()
        
        self.root.resizable(False, False)

    def run(self):
        self.initGUI()
        
    def initGUI(self):
        introFrame = Frame(
            self.root,
            bg = "#C4C4C4",
            height = 400,
            width = 800,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        introFrame.place(x = 0, y = 0)
        
        label1 = Label(introFrame,
                       text="Welcome to",
                       bg="#C4C4C4",
                       fg="black",
                       font=("Roboto", int(40))
        )
        label1.place(
            x=250,
            y=80
        )
        label2 = Label(
            introFrame,
            text="AutoTrader",
            bg="#C4C4C4",
            fg="black",
            font=("Roboto", int(60), "bold")
        )
        label2.place(
            x=180,
            y=180
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
    
    def destroyWelcomeFrame(self, prevFrames):
        for frame in prevFrames:
            frame.destroy()
        self.testnet()
        
    def testnet(self):
        infoFrame = Frame(
            self.root,
            bg = "#C4C4C4",
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
            text="AutoTrader",
            bg="#C4C4C4",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=12,
            y=30
        )
        
        info = Label(
            infoFrame,
            text="The testnet is a test environment \n"
            "for the Binance network that allows \n"
            "you trial this program with simulated \n"
            "funds although the prices are not always \n"
            "accurate. \n",        
            justify=LEFT,
            bg="#C4C4C4",
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
            bg = "#C4C4C4",
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
            text="AutoTrader",
            bg="#C4C4C4",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=12,
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
                bg="#C4C4C4",
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
                "Margin Trading' restrictions are "
                "selected. \n\n"
                "Be sure to save the keys to a secure \n"
                "location for future ease of access. \n\n"
                "Please check that your internet \n"
                "connection is working properly. ",
                justify=LEFT,
                bg="#C4C4C4",
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
            # command=lambda: destroyClientKeysFrame(prevFrames),
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
            bg = "#C4C4C4",
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
            text="AutoTrader",
            bg="#C4C4C4",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=12,
            y=30
        )
    
        info = Label(
            infoFrame,
            # text="Enter or select a base symbol or quote \n"
            # "symbol that forms a valid Binance \n"
            # "pair. An experimental AI driven \n"
            # "strategy is available only for BTCUSDT. \n\n"
            # "Stop-loss and take-profit percentages \n"
            # "determine the decrease or inrease in \n"
            # "the value of a ticker required to \n"
            # "trigger a sale. \n\n"
            # "Lot size is a fixed amount of the \n"
            # "quote currency to be entered into \n"
            # "each trade. \n\n"
            # "Closing time is the time of day the \n"
            # "application automatically closes all \n"
            # "its trades and exits. ",
            text="Enter or select a base symbol or quote \n"
            "symbol that forms a valid Binance \n"
            "pair. \n\n"
            "Lot size is a fixed amount of the \n"
            "quote currency to be entered into \n"
            "each trade. \n\n"
            "Closing time is the time of day the \n"
            "application automatically closes all \n"
            "its trades and exits. ",
            justify=LEFT,
            bg="#C4C4C4",
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
            text="Closing Time GMT [HH:MM]",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        closingTimeLabel.place(x=300, y=220)
        
        HourChoice = StringVar(settingsFrame)
        HourBox = Combobox(settingsFrame, textvariable=HourChoice, state="readonly", width=4)
        HourBox["values"] = tuple([f"{i:02d}" for i in range(0, 24)])
        HourBox.place(x=300, y=250)
        HourBox.set("00")
        MinChoice = StringVar(settingsFrame)
        MinBox = Combobox(settingsFrame, textvariable=MinChoice, state="readonly", width=4)
        MinBox["values"] = tuple([f"{i:02d}" for i in range(0, 60)])
        MinBox.place(x=350, y=250)
        MinBox.set("00")
        
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
        
    def validateSettings(self, prevFrames, setting_vars):
        global base
        global quote
        global pair
        global filters
        global init_price
        global sl
        global tp
        global trade_allocation
        global closingTime
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
    
        closingTime = setting_vars[5].get() + ":" + setting_vars[6].get() + ":00"
        if closingTime == '00:00:00':
            closingTime = 86400
        else:
            closingTime = datetime.strptime(closingTime, '%H:%M:%S')
            closingTime = (closingTime - datetime(1900, 1, 1)).total_seconds()
        
        if time() % 86400 > closingTime:
            messagebox.showerror(
                title="Error",
                message=
                "Closing time cannot be earlier than current \n"
                "time. If you want the program to run \n"
                "indefinitely set closing time to 00:00. ")
            return

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
            bg = "#C4C4C4",
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
            text="AutoTrader",
            bg="#C4C4C4",
            fg="black",
            font=("Roboto", int(25), "bold")
        )
        name.place(
            x=12,
            y=30
        )
            
        strategyChoice = IntVar(strategyFrame)
        # if pair == "BTCUSDT":
        #  info = Label(
        #      infoFrame,
        #      text="This strategy uses a recurrent \n"
        #      "neural network to attempt to \n"
        #      "predict the next closing price of \n"
        #      "BTCUSDT. It places a buy order if \n"
        #      "the predicted price is significantly \n"
        #      "higher than the last closing price. \n\n"
        #      "This strategy is still experimental \n"
        #      "and was included only to demonstrate \n"
        #      "the applications of machine learning \n"
        #      "in trading. It would not be advisable \n"
        #      "to use this strategy withou a testnet. \n\n",
        #      justify=LEFT,
        #      bg="#C4C4C4",
        #      fg="black",
        #      font=("Roboto", int(8))
        #  )
        #  info.place(
        #      x=4,
        #      y=90
        #  )
        #  option1 = Radiobutton(
        #      strategyFrame, 
        #      text="Custom AI Regression Strategy", 
        #      variable=strategyChoice, 
        #      command=lambda: self.strategyLabels(strategyChoice, infoFrame),
        #      value=0, 
        #      width=60, 
        #      anchor="w"
        #  )
        #  option1.place(x=50, y=100)
        #  option2 = Radiobutton(
        #      strategyFrame, 
        #      text="Moving Average Strategy", 
        #      variable=strategyChoice, 
        #      command=lambda: self.strategyLabels(strategyChoice, infoFrame),
        #      value=1, 
        #      width=60, 
        #      anchor="w"
        #  )
        #  option2.place(x=50, y=150)
        #  option3 = Radiobutton(
        #      strategyFrame, 
        #      text="MACD Strategy", 
        #      variable=strategyChoice, 
        #      command=lambda: self.strategyLabels(strategyChoice, infoFrame),
        #      value=2, 
        #      width=60, 
        #      anchor="w"
        #  )
        #  option3.place(x=50, y=200)
        #  option1.select()
        # else:
        #  info = Label(
        #      infoFrame,
        #      text="This strategy places a buy \n"
        #      "order if the current 20-period \n"
        #      "simple moving average is greater \n"
        #      "than the 50-period simple moving \n"
        #      "average while the price is lower \n"
        #      "than the 20-period moving average. \n\n",
        #      justify=LEFT,
        #      bg="#C4C4C4",
        #      fg="black",
        #      font=("Roboto", int(8))
        #  )
        #  info.place(
        #      x=4,
        #      y=90
        #  )
        #  option1 = Radiobutton(
        #      strategyFrame, 
        #      text="Moving Average Strategy", 
        #      variable=strategyChoice, 
        #      command=lambda: self.strategyLabels(strategyChoice, infoFrame),
        #      value=1, 
        #      width=60, 
        #      anchor="w"
        #  )
        #  option1.place(x=50, y=150)
        #  option2 = Radiobutton(
        #      strategyFrame, 
        #      text="MACD Strategy", 
        #      variable=strategyChoice,
        #      command=lambda: self.strategyLabels(strategyChoice, infoFrame),
        #      value=2, 
        #      width=60, 
        #      anchor="w"
        #  )
        #  option2.place(x=50, y=200)
        #  option1.select()
            
        info = Label(
            infoFrame,
            text="This strategy places a buy \n"
            "order if the current 20-period \n"
            "simple moving average is greater \n"
            "than the 50-period simple moving \n"
            "average while the price is lower \n"
            "than the 20-period moving average. \n\n",
            justify=LEFT,
            bg="#C4C4C4",
            fg="black",
            font=("Roboto", int(8))
        )
        info.place(
            x=4,
            y=90
        )
        option1 = Radiobutton(
            strategyFrame, 
            text="Moving Average Strategy", 
            variable=strategyChoice, 
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=1, 
            width=60, 
            anchor="w"
        )
        option1.place(x=50, y=150)
        option2 = Radiobutton(
            strategyFrame, 
            text="MACD Strategy", 
            variable=strategyChoice,
            command=lambda: self.strategyLabels(strategyChoice, infoFrame),
            value=2, 
            width=60, 
            anchor="w"
        )
        option2.place(x=50, y=200)
        option1.select()

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
            bg="#C4C4C4",
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
                text="This strategy uses a recurrent \n"
                "neural network to attempt to \n"
                "predict the next closing price of \n"
                "BTCUSDT. It places a buy order if \n"
                "the predicted price is significantly \n"
                "higher than the last closing price. \n\n"
                "This strategy is still experimental \n"
                "and was included only to demonstrate \n"
                "the applications of machine learning \n"
                "in trading. It would not be advisable \n"
                "to use this strategy withou a testnet. \n\n",
                justify=LEFT,
                bg="#C4C4C4",
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
                "order if the current 20-period \n"
                "simple moving average is greater \n"
                "than the 50-period simple moving \n"
                "average while the price is lower \n"
                "than the 20-period moving average. \n\n",
                justify=LEFT,
                bg="#C4C4C4",
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
                "order when the current 12-period \n"
                "exponential moving average crosses \n"
                "the the 26-period exponential \n"
                " moving average upwards. \n\n",
                justify=LEFT,
                bg="#C4C4C4",
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
        

        # taScale = Scale(
        #     slidersFrame, 
        #     from_=min_trade_allocation, 
        #     to=startQuoteBalance, 
        #     resolution=filters['tickSize'], 
        #     orient=HORIZONTAL, 
        #     length=150, 
        #     label="Trade allocation"
        # )
        # taScale.set(trade_allocation)
        # taScale.place(x=10, y=180)
    
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
        gcf().autofmt_xdate()
        
        tradesFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 230,
            width = 580,
            bd = 4,
            highlightthickness = 0,
            relief = "ridge"
        )
        tradesFrame.pack_propagate(False)
        tradesFrame.place(x = 210, y = 260)
        tradesLabel = Label(tradesFrame, text='Trades', font=('Roboto', int(10)), bd=0)
        tradesLabel.pack(fill=X, side=TOP)
        tradesText = scrolledtext.ScrolledText(tradesFrame, bd=0, cursor='arrow')
        tradesText.pack(fill=BOTH, side=BOTTOM)
        tradesText.configure(state='disabled')
        
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
            x=845,
            y=320, 
            width=100,
            height=50
        )

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
            x=845,
            y=400, 
            width=100,
            height=50
        )

        frames = {'prices': pricesText, 'balances': balanceText, 'trades': tradesText, 'chart': chartFrame, 'sliders': slidersFrame}
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
        self.root.after(100, lambda: self.refresh_frames(frames, sliders))
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.on_closing())
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? "):
            stopQ.put_nowait(1)
        
    def refresh_frames(self, frames, sliders):
        global tp
        global sl
        # global trade_allocation
        
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
            # sliders['ta'].destroy
            # taScale = Scale(
            #     frames['sliders'], 
            #     from_=min_trade_allocation, 
            #     to=currentQuoteBalance, 
            #     resolution=filters['tickSize'], 
            #     orient=HORIZONTAL, 
            #     length=150, 
            #     label="Trade allocation"
            # )
            # taScale.set(trade_allocation)
            # taScale.place(x=10, y=180)
            # sliders['ta'] = taScale
            frames['trades'].configure(state='normal')
            frames['trades'].insert("end", self.thread.trades.get_nowait())
            frames['trades'].see("end")
            frames['trades'].yview("end")
            frames['trades'].configure(state='disabled')
        if not self.thread.charts.empty():
            for w in frames['chart'].winfo_children():
                w.destroy()
            chartLabel = Label(frames['chart'], text='Chart', font=('Roboto', int(10)), bd=0)
            chartLabel.pack(fill=X, side=TOP)
            fig = self.thread.charts.get_nowait()
            line1 = FigureCanvasTkAgg(fig, frames['chart'])
            line1.get_tk_widget().pack(fill=BOTH)
        if not self.thread.errors.empty():
            e = self.thread.errors.get_nowait()
            messagebox.showerror(
                title="Error",
                message=str(e))
        tp = sliders['tp'].get()
        sl = sliders['sl'].get()
        # trade_allocation = sliders['ta'].get()
        self.root.update()
        self.root.after(500, lambda: self.refresh_frames(frames, sliders))

class AsyncioThread(Thread):
    def __init__(self, theWindow):
        self.asyncio_loop = new_event_loop()
        set_event_loop(self.asyncio_loop)
        
        self.theWindow = theWindow
        
        # self.open_positions = Queue()
        # self.price = LifoQueue()
        # self.price_buy = LifoQueue()
        # self.price_sell = LifoQueue()
        # self.data = Queue()
        # self.data_frame = Queue()
        # self.data_frame_figure = Queue()
        # self.charts = Queue()
        # self.signals = Queue()
        # self.sell_price = Queue()
        # self.trades = Queue()
        
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
        self.data = Queue()
        self.data_frame = Queue()
        self.data_frame_figure = Queue()
        self.charts = Queue()
        self.signals = Queue()
        self.sell_price = Queue()
        self.trades = Queue()
        self.errors = Queue()
        
        # if strategy == 0:
        #     scaler = load('X_scaler.pkl')
        #     model = load_model('cp-40+58-160.5325-18-21-08-06-08-2021.hdf5') # AI model
        
        client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=useTestnet)

        await self.open_positions.put([])
        self.save_to_records(startQuoteBalance, 'open')
        self.tasks = [create_task(self.check_closing_time()),
                      create_task(self.kline_data()), 
                      create_task(self.update_data()),
                      create_task(self.lineplots()), 
                      create_task(self.generate_signals()), 
                      create_task(self.place_buy_order()),
                      create_task(self.place_sell_order())]
        try:
            await gather(*self.tasks, create_task(self.checkQuit()))
        except CancelledError:
            pass
        
        if close:
            self.closeProgram()
        return

    async def checkQuit(self):
        while stopQ.empty() and not close:
            await sleep(2)
        await self.closeProgram()

    async def check_closing_time(self):
        global close
        while time() % 86400 < closingTime and not close:
            await sleep(10)
        close = True

    async def kline_data(self): # Get live data
        bm = BinanceSocketManager(client)
        ks = bm.kline_socket(pair, interval=KLINE_INTERVAL_1MINUTE)
        myKeys = ['t', 'o', 'h', 'l', 'c', 'v', 'T', 'q', 'n', 'V', 'Q']
        async with ks as kscm:
            while not close:
                try:
                    a = await kscm.recv()
                except BinanceAPIException as e:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, e)
                else:
                    res = a['k']
                    self.asyncio_loop.call_soon_threadsafe(self.price.put_nowait, float(res['c']))
                    self.asyncio_loop.call_soon_threadsafe(self.price_buy.put_nowait, float(res['c']))
                    self.asyncio_loop.call_soon_threadsafe(self.price_sell.put_nowait, float(res['c']))
                    if res['x']:
                        candle = [res[x] for x in myKeys]
                        self.asyncio_loop.call_soon_threadsafe(self.data.put_nowait, candle)
        return

    async def update_data(self):
        df = await self.get_historical_data()
        self.asyncio_loop.call_soon_threadsafe(self.data_frame_figure.put_nowait, df)
        while not close:
            new_row = await self.data.get()
            if strategy != 0:
                new_row = new_row + [0, 0, 0, 0]
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
        if strategy != 0:
            df['SMA_20'] = df.loc[:, 'Close'].rolling(window=20).mean()
            df['SMA_50'] = df.loc[:, 'Close'].rolling(window=50).mean()
            df['EMA_12'] = df.loc[:, 'Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df.loc[:, 'Close'].ewm(span=26, adjust=False).mean()
        return df

    def update_df(self, df, new_row):
        new_row = Series(new_row, index=df.columns)
        if new_row[0] != df.iloc[-1, 0]:
            df = df.append(new_row, ignore_index=True)
        else:
            df.iloc[-1, :] = new_row
        if strategy != 0:
            df['SMA_20'] = df.loc[:, 'Close'].rolling(window=20).mean()
            df['SMA_50'] = df.loc[:, 'Close'].rolling(window=50).mean()
            df['EMA_12'] = df.loc[:, 'Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df.loc[:, 'Close'].ewm(span=26, adjust=False).mean()
        return df

    async def generate_signals(self):
        while not close:
            df = await self.data_frame.get()
            last_price = df.iloc[-1, 4]
            if strategy == 0:
                # input_data = df.iloc[-10:, :].to_numpy()
                # predicted_price = model.predict(reshape(scaler.transform(input_data), (1, 10, 11))).squeeze()
                # self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Predicton: {predicted_price} \n\n')
                # self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Last price: {last_price} \n\n')
                # if predicted_price >= (last_price * (1 + tp)):
                #     self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
                pass
            elif strategy == 1:
                if df.iloc[-1, 11] > df.iloc[-1, 12] and (df.iloc[-1, 11] - last_price ) / last_price > tp:
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
            elif strategy == 2:
                if df.iloc[-1, 13] > df.iloc[-1, 14] and df.iloc[-2, 13] < df.iloc[-2, 14]:
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
        return

    def manualBuy(self):
        self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, 1)
        
    async def place_buy_order(self):
        count = 1
        while not close:
            s = await self.signals.get()
            if s == 1:                
                try:
                    balance = await client.get_asset_balance(asset=quote)
                except BinanceAPIException as e:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, e)
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
        except BinanceAPIException as e:
            self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, e)
            return False
        else:
            while True:
                await sleep(0.2)
                try:
                    trade_status = await client.get_order(symbol=pair, orderId=order['orderId'])
                except BinanceAPIException as ex:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, ex)
                    return False
                else:
                    if float(trade_status['executedQty']) == qty:
                        await self.save_trades('buy', qty, current_price, count)
                        await self.sell_price.put({'stop-loss': (1 - sl) * current_price, 
                                                   'take-profit': (1 + tp) * current_price, 
                                                   'qty': qty, 
                                                   'id': count
                                                   })
                        return True
    
    async def place_sell_order(self):
        sell_list = []
        while not close:
            current_price = await self.price_sell.get()
            if not self.sell_price.empty():
                position = await self.sell_price.get()
                sell_list = await self.open_positions.get()
                sell_list.append(position)
                await self.open_positions.put(sell_list)
            for s in sell_list:
                if current_price < s['stop-loss'] or current_price > s['take-profit']:
                    await self.sell(s['qty'], current_price, s['id'])
                    sell_list.remove(s)
                    await self.open_positions.get()
                    await self.open_positions.put(sell_list)
        return
    
    async def sell(self, qty, current_price, count):
        try:
            order = await client.order_market_sell(
                symbol=pair,
                quantity=qty)
        except BinanceAPIException as e:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, e)
        else:
            await sleep(0.2)
            try:
                await client.get_order(symbol=pair, orderId=order['orderId'])
            except BinanceAPIException as ex:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, ex)
            else:
                await self.save_trades('sell', qty, current_price, count)
        
    async def close_positions(self):
        self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 'Closing positions. \n\n')
        positions = await self.open_positions.get()
        data = await client.get_symbol_ticker(symbol=pair)
        price = float(data['price'])
        for i in positions:
            await self.sell(i['qty'], price, i['id'])
            
        try:
            closing_balance = await client.get_asset_balance(asset=quote)
        except BinanceAPIException as e:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, e)
        else:
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
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Bought {qty} {base} at {price} {quote} per {base} ({round(qty * price, 4)} {quote}) \n\n')
            elif trade_type == 'sell':
                file.write(f'Closed trade {count} \n')
                file.write(f'Sold {qty} {base} at {price} {quote} per {base} ({qty * price} {quote}). \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, strftime("%H:%M") + '\n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Closed trade {count} \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Sold {qty} {base} at {price} {quote} per {base} ({round(qty * price, 4)} {quote}) \n\n')
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
    
            fig = Figure()
            plot1 = fig.add_subplot(111)
            y1 = df['Close'].to_numpy()
            plot1.plot(x, y1[-60:], "-g", label="Price")
            if strategy == 1:
                y2 = df['SMA_20'].to_numpy()
                y3 = df['SMA_50'].to_numpy()
                plot1.plot(x, y2[-60:], "-b", label="20 S.M.A.")
                plot1.plot(x, y3[-60:], "-r", label="50 S.M.A.")
            elif strategy == 2:
                y4 = df['EMA_12'].to_numpy()
                y5 = df['EMA_26'].to_numpy()
                plot1.plot(x, y4[-60:], "-b", label="12 E.M.A.")
                plot1.plot(x, y5[-60:], "-r", label="26 E.M.A.")
            plot1.xaxis.set_major_formatter(myFmt)
            plot1.xaxis.set_minor_locator(mns)
            plot1.legend(loc="upper right", fontsize="x-small")
            plot1.set_title(pair)
            self.asyncio_loop.call_soon_threadsafe(self.charts.put_nowait, fig)

    async def closeProgram(self):
        global client
        global close

        # print(1)
        # if not close:
        #     for t in self.tasks:
        #         t.cancel()
        #         with suppress(asyncio.exceptions.CancelledError):
        #             await t
        #             print(t)
            # pending = asyncio.all_tasks()
            # await asyncio.gather(*pending)
        close = True
        await self.close_positions()
        await sleep(2)
        await client.close_connection()
        # self.asyncio_loop.stop()
        # self.asyncio_loop.close()
        self.theWindow.root.destroy()
        sysexit()

def popen(cmd: str) -> str:
    """For pyinstaller -w"""
    startupinfo = STARTUPINFO()
    startupinfo.dwFlags |= STARTF_USESHOWWINDOW
    process = Popen(cmd,startupinfo=startupinfo, stdout=PIPE, stderr=PIPE, stdin=PIPE)
    return process.stdout.read()

if __name__ == '__main__':
    apply()
    stopQ = qQueue()
    window = TheWindow()
    window.root.mainloop()
