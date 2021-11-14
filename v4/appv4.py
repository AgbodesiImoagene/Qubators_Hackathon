# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 12:05:47 2021

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
from argparse import ArgumentParser
from asyncio.exceptions import TimeoutError
from pandas import Series, DataFrame
from numpy import array, vectorize
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
from queue import Queue as qQueue
from datetime import datetime
from nest_asyncio import apply
from tkinter import X, BOTH, TOP, BOTTOM, LEFT, END, HORIZONTAL, WORD, Y, RIGHT, SINGLE, VERTICAL
from PIL import ImageTk, Image
from binance import Client, AsyncClient, BinanceSocketManager
from binance.helpers import round_step_size
from binance.exceptions import BinanceRequestException, BinanceAPIException
from tkinter.ttk import Combobox
from tkinter import StringVar, IntVar, Canvas, Tk, Entry, Button, Frame, Label
from tkinter import OptionMenu, Listbox, Scale, Scrollbar, scrolledtext, Radiobutton, messagebox
from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW, Popen, PIPE

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath(".")

    return join(base_path, relative_path)

FILE_NAME = 'TradeRecords.txt'
ERROR_LOG = resource_path('log.bin')
logoImg = resource_path('Logo.ico')
nameImg = resource_path('NameCropped.png')
welcomeImg = resource_path('Welcome.png')

parser = ArgumentParser(prog='AutoTrader', add_help=False)
parser.add_argument('-r', '--restart', action='store_true', default=False)
parser.add_argument('-t', '--useTestnet', action='store_true', default=False)
parser.add_argument('-a', '--all', nargs='*')
parser.add_argument('-b', '--bases', nargs='*')
parser.add_argument('-o', '--openPositions', nargs='*', action='append', default=[])
args = parser.parse_args()
rcParams['font.size'] = 10

myFmt = DateFormatter('%H:%M')
mns = MinuteLocator()

# sys.stdout = open(ERROR_LOG, 'w')

if not args.restart:
    useTestnet = ''
    API_KEY = ''
    SECRET_KEY = ''
    sl = 0.8
    tp = 1.0
    trade_allocation = ''
    useClosingTime = 0
    startTime = 0
    closingTime = 0
    strategy = ''
    quote = 'USDT'
    trade_count = qQueue()
    trade_count.put_nowait(1)
    bases = []
    curr_open_positions = qQueue()
    curr_open_positions.put_nowait([])
else:
    useTestnet = args.useTestnet
    API_KEY = args.all[0]
    SECRET_KEY = args.all[1]
    sl = float(args.all[2])
    tp = float(args.all[3])
    trade_allocation = float(args.all[4])
    useClosingTime = int(args.all[5])
    startTime = float(args.all[6])
    closingTime = float(args.all[7])
    strategy = int(args.all[8])
    quote = args.all[9]
    trade_count = qQueue()
    trade_count.put_nowait(int(args.all[10]))
    bases = args.bases
    curr_open_positions = qQueue()
    l = []
    dictionary = {}
    for sublist in args.openPositions:
        dictionary = {'stop-loss': float(sublist[0]), 
                      'take-profit': float(sublist[1]), 
                      'qty': float(sublist[2]), 
                      'id': int(sublist[3]), 
                      'time': sublist[4], 
                      'base': sublist[5]
                      }
        l.append(dictionary)            
    curr_open_positions.put_nowait(l)

base = 'BTC'
quote = 'USDT'
pair = base + quote
client = ''
filters = {}
hourBoxEntry = "00"
minBoxEntry = "00"
offset = ''
startBaseBalance = {}
startQuoteBalance = ''
currentBaseBalance = {}
currentQuoteBalance = ''
chart_num = ''
maxQuote = ''
min_trade_allocation = ''

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
        if not args.restart:
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
        global offset
        global startBaseBalance
        global startQuoteBalance
        global currentBaseBalance
        global currentQuoteBalance
        global chart_num
        global maxQuote
        global min_trade_allocation

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

        for b in bases:
            bal = client.get_asset_balance(asset=b)
            bal = float(bal['free'])
            startBaseBalance[b] = bal
        startQuoteBalance = client.get_asset_balance(asset=quote)
        startQuoteBalance = float(startQuoteBalance['free'])
        currentBaseBalance = startBaseBalance
        currentQuoteBalance = startQuoteBalance
        
        if strategy == 0:
            chart_num = 1
        elif strategy == 1:
            chart_num = 1
        elif strategy == 2:
            chart_num = 1
        elif strategy == 3:
            chart_num = 2
        elif strategy == 4:
            chart_num = 3
        elif strategy == 5:
            chart_num = 4
        elif strategy == 6:
            chart_num = 3
        
        maxQuote = []
        min_trade_allocation = []
        for b in bases:
            p = b + quote
            data = client.get_symbol_info(p)
            f = {}
            f['lotStepSize'] = 1.0
            f['minQty'] = 0.0
            f['maxQty'] = 1000000000000000.0
            f['stepSize'] = 1.0
            f['minNotional'] = 1.0
            f['tickSize'] = 1.0
            f['maxPrecision'] = 10 ** -(data['baseAssetPrecision'])
            all_filters = data['filters']
            for dictionary in all_filters:
                if dictionary['filterType'] == 'LOT_SIZE':
                    try:
                        f['lotStepSize'] = float(dictionary['stepSize'])
                    except Exception:
                        f['lotStepSize'] = 1.0
                if dictionary['filterType'] == 'MARKET_LOT_SIZE':
                    try:
                        f['minQty'] = float(dictionary['minQty'])
                    except Exception:
                        f['minQty'] = 0.0
                    try:
                        f['maxQty'] = float(dictionary['maxQty'])
                    except Exception:
                        f['maxQty'] = 1000000000000000.0
                    try:
                        f['stepSize'] = float(dictionary['stepSize'])
                    except Exception:
                        f['stepSize'] = 1.0
                if dictionary['filterType'] == 'MIN_NOTIONAL':
                    try:
                        f['minNotional'] = float(dictionary['minNotional'])
                    except Exception:
                        f['minNotional'] = 1.0
                if dictionary['filterType'] == 'PRICE_FILTER':
                    try:
                        f['tickSize'] = float(dictionary['tickSize'])
                    except Exception:
                        f['tickSize'] = 1.0
            filters[p] = f
            temp = client.get_ticker(symbol=p)
            temp = float(temp["lastPrice"])
            if temp == 0:
                temp = 1
            maxQuote.append(temp * filters[p]['maxQty'] * (100 / 104))
            min_trade_allocation.append(filters[p]['minNotional'] * (100 / 96))
                
        maxQuote = min(maxQuote)
        min_trade_allocation = max(min_trade_allocation)
        
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
        self.setPairs()
        
    def setPairs(self):
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
        
        pairsFrame = Frame(
            self.root,
            bg = "#FFFFFF",
            height = 400,
            width = 600,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        pairsFrame.place(x = 200, y = 0)
        
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
            text="Enter or select a quote currency \n"
            "and up 10 base currencies that \n"
            "form valid Binance pairs. \n\n",
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
            pairsFrame, 
            text="Quote symbol: ",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        quote_label.place(x=260, y=120)
    
        quoteChoice = StringVar(pairsFrame)            
        quoteDropdown = Combobox(pairsFrame, textvariable=quoteChoice, width=6)
        if useTestnet:
            quoteDropdown["values"] = ("USDT", "BUSD", "BTC", "BNB")
        else:
            quoteDropdown["values"] = ("USDT", "USDC", "BUSD", "TUSD", "PAX", "BTC", "ETH", "BNB")
    
        quoteDropdown.place(x=347, y=120)
        quoteDropdown.set(quote)
        
        base_label = Label(
            pairsFrame, 
            text="Base symbol: ",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        base_label.place(x=265, y=170)
    
        baseChoice = StringVar(pairsFrame)            
        baseDropdown = Combobox(pairsFrame, textvariable=baseChoice, width=6)
        if useTestnet:
            baseDropdown["values"] = ("BTC", "ETH", "BNB", "LTC", "TRX", "XRP")
        else:
            baseDropdown["values"] = ("BTC", "ETH", "BNB", "LTC", "TRX", "XRP",
                                      "NEO", "QTUM", "EOS", "SNT", "BNT", "DOGE", 
                                      "GAS", "HSR", "OAX", "DNT", "ICN", "MANA", 
                                      "WTC", "LRC", "YOYO", "OMG", "ZRX", "MATIC", 
                                      "SNGLS", "BQX", "KNC", "FUN", "SNM", "IOTA", 
                                      "LINK", "XVG", "SALT", "MDA", "MTL", "SUB", 
                                      "ETC", "MTH", "ENG", "DNT", "ZEC", "AST", 
                                      "DASH", "BTG", "EVX", "REQ", "VIB", "HSR", 
                                      "POWR", "ARK", "DGD", "ADA")
    
        baseDropdown.place(x=347, y=170)
        baseDropdown.set(base)
        
        selectButton = Button(
            pairsFrame,
            text="select",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.addPair(baseChoice, quoteChoice, pairsListbox, selectButton, removeButton, quoteDropdown),
            relief="ridge"
        )
        selectButton.place(
            x=420,
            y=170, 
            width=40,
            height=20
        )

        removeButton = Button(
            pairsFrame,
            text="remove",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.removePair(pairsListbox, selectButton, removeButton, quoteDropdown),
            relief="ridge"
        )
        removeButton.place(
            x=270,
            y=250, 
            width=50,
            height=20
        )

        pairsListbox = Listbox(pairsFrame, selectmode=SINGLE, bg='#DADADA', bd=4)
        pairsListbox.place(x=100, y=100, width=100, height=200)
        for b in bases:
            pairsListbox.insert("end", b + quote)
        if bases == []:
            removeButton.configure(state='disabled')
        else:
            quoteDropdown.configure(state='disabled')
        if len(bases) == 10:
            selectButton.configure(state='disabled')
        
        prevFrames = [infoFrame, pairsFrame]
        
        button_1 = Button(
            pairsFrame,
            text="next",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.validatePairs(prevFrames),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        button_1.place(
            x=440,
            y=300
        )

    def addPair(self, baseVar, quoteVar, listBox, addButton, removeButton, quoteBox):
        global base
        global quote
        global bases
        
        base = baseVar.get()
        quote = quoteVar.get()
        pair = base + quote
        
        data = client.get_symbol_info(pair)
        if data == None:
            messagebox.showerror(
                title="Error",
                message=pair + " is not a valid symbol pair. ")
            return
        elif base in bases:
            messagebox.showerror(
                title="Error",
                message="You have already selected " + pair + ". ")
            return
        else:
            listBox.insert("end", pair)
            if len(listBox.curselection()) == 0:
                listBox.activate("end")
                listBox.select_set("end")
            removeButton.configure(state='normal')
            bases.append(base)
            
        if listBox.size() >= 1:
            quoteBox.configure(state='disabled')
        if listBox.size() >= 10:
            addButton.configure(state='disabled')
        
    def removePair(self, listBox, addButton, removeButton, quoteBox):
        global bases
        
        temp = listBox.curselection()
        if len(temp) != 0:
            listBox.delete(temp[0])
            bases.remove(bases[temp[0]])
        if listBox.size() == 0:
            quoteBox.configure(state='normal')
        else:
            listBox.activate("end")
            listBox.select_set("end")

        if listBox.size() < 10:
            addButton.configure(state='normal')
        if len(listBox.curselection()) == 0:
            removeButton.configure(state='disabled')
    
    def validatePairs(self, prevFrames):
        if bases == []:
            messagebox.showerror(
                title="Error",
                message="Please select at least one pair. ")
            return
        self.destroyPairsFrame(prevFrames)

    def destroyPairsFrame(self, prevFrames):
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
            text="Lot size is a fixed amount of the \n"
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
            
        sl_label = Label(
            settingsFrame, 
            text="Stop-loss percentage",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        sl_label.place(x=20, y=70)
        
        slScale = Scale(
            settingsFrame, 
            from_=0.02, 
            to=2.00, 
            resolution=0.02, 
            orient=HORIZONTAL, 
            length=200
        )
        slScale.set(sl)
        slScale.place(x=20, y=100)
    
        tp_label = Label(
            settingsFrame, 
            text="Take-profit percentage",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        tp_label.place(x=300, y=70)
        
        tpScale = Scale(
            settingsFrame, 
            from_=0.02, 
            to=2.00, 
            resolution=0.02, 
            orient=HORIZONTAL, 
            length=200
        )
        tpScale.set(tp)
        tpScale.place(x=300, y=100)
        
        lotSizeLabel = Label(
            settingsFrame, 
            text="Lot Size (quote currency)",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        lotSizeLabel.place(x=20, y=170)
        
        LotSizeEntry = Entry(
            settingsFrame, 
            bd=2, 
            width=16
        )
        LotSizeEntry.place(x=20, y=200)
        LotSizeEntry.insert(0, str(trade_allocation))
        LotSizeEntry.focus()
        
        closingTimeLabel = Label(
            settingsFrame, 
            text="Closing Time [HH:MM]",
            bg="white",
            fg="black",
            font=("Roboto", int(10))
        )
        closingTimeLabel.place(x=300, y=170)
        
        HourChoice = StringVar(settingsFrame)
        HourBox = Combobox(settingsFrame, textvariable=HourChoice, state="readonly", width=4)
        HourBox["values"] = tuple([f"{i:02d}" for i in range(0, 24)])
        HourBox.place(x=300, y=200)
        HourBox.set(hourBoxEntry)
        MinChoice = StringVar(settingsFrame)
        MinBox = Combobox(settingsFrame, textvariable=MinChoice, state="readonly", width=4)
        MinBox["values"] = tuple([f"{i:02d}" for i in range(0, 60)])
        MinBox.place(x=350, y=200)
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
            y=200
        )
        if not useClosingTime:
            HourBox.configure(state='disabled')
            MinBox.configure(state='disabled')
        
        prevFrames = [infoFrame, settingsFrame]
        setting_vars = [slScale, tpScale, LotSizeEntry, HourChoice, MinChoice]
        
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
        
        button_2 = Button(
            settingsFrame,
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

    def enableClosingTime(self, HourBox, MinBox, enableButton):
        global useClosingTime
        useClosingTime = int(not useClosingTime)
        
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
        global filters
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
        global maxQuote
        global min_trade_allocation
        
        sl = setting_vars[0].get()
        tp = setting_vars[1].get()
        hourBoxEntry = setting_vars[3].get()
        minBoxEntry = setting_vars[4].get()
        try:
            trade_allocation = float(setting_vars[2].get())
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

        for b in bases:
            bal = client.get_asset_balance(asset=b)
            bal = float(bal['free'])
            startBaseBalance[b] = bal
        startQuoteBalance = client.get_asset_balance(asset=quote)
        startQuoteBalance = float(startQuoteBalance['free'])
        currentBaseBalance = startBaseBalance
        currentQuoteBalance = startQuoteBalance
        
        maxQuote = []
        min_trade_allocation = []
        for b in bases:
            p = b + quote
            data = client.get_symbol_info(p)
            f = {}
            f['lotStepSize'] = 1.0
            f['minQty'] = 0.0
            f['maxQty'] = 1000000000000000.0
            f['stepSize'] = 1.0
            f['minNotional'] = 1.0
            f['tickSize'] = 1.0
            f['maxPrecision'] = 10 ** -(data['baseAssetPrecision'])
            all_filters = data['filters']
            for dictionary in all_filters:
                if dictionary['filterType'] == 'LOT_SIZE':
                    try:
                        f['lotStepSize'] = float(dictionary['stepSize'])
                    except Exception:
                        f['lotStepSize'] = 1.0
                if dictionary['filterType'] == 'MARKET_LOT_SIZE':
                    try:
                        f['minQty'] = float(dictionary['minQty'])
                    except Exception:
                        f['minQty'] = 0.0
                    try:
                        f['maxQty'] = float(dictionary['maxQty'])
                    except Exception:
                        f['maxQty'] = 1000000000000000.0
                    try:
                        f['stepSize'] = float(dictionary['stepSize'])
                    except Exception:
                        f['stepSize'] = 1.0
                if dictionary['filterType'] == 'MIN_NOTIONAL':
                    try:
                        f['minNotional'] = float(dictionary['minNotional'])
                    except Exception:
                        f['minNotional'] = 1.0
                if dictionary['filterType'] == 'PRICE_FILTER':
                    try:
                        f['tickSize'] = float(dictionary['tickSize'])
                    except Exception:
                        f['tickSize'] = 1.0
            filters[p] = f
            temp = client.get_ticker(symbol=p)
            temp = float(temp["lastPrice"])
            if temp == 0:
                temp = 1
            maxQuote.append(temp * filters[p]['maxQty'] * (100 / 104))
            min_trade_allocation.append(filters[p]['minNotional'] * (100 / 96))

        maxQuote = min(maxQuote)
        min_trade_allocation = max(min_trade_allocation)
                
        if trade_allocation < min_trade_allocation:
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
                "Maximum value is" + str(maxQuote))
            return
        
        base = bases[0]
        
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
            command=lambda: self.destroyPairsFrame(prevFrames),
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
        global chart_num

        strategy = choice.get()
        
        if strategy == 0:
            chart_num = 1
        elif strategy == 1:
            chart_num = 1
        elif strategy == 2:
            chart_num = 1
        elif strategy == 3:
            chart_num = 2
        elif strategy == 4:
            chart_num = 3
        elif strategy == 5:
            chart_num = 4
        elif strategy == 6:
            chart_num = 3

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
        balanceText = scrolledtext.ScrolledText(balanceFrame, bd=0, font=('Roboto', int(9)), cursor='arrow', wrap=WORD)
        balanceText.insert('end', f'Starting {quote} Balance: \n{startQuoteBalance} \n')
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
        chartScrollables = {}
        for b in bases:
            chartScrollables[b] = V_ScrollableFrame(chartFrame)
        chartScrollables[bases[0]].canvas.pack(side=LEFT)
        chartScrollables[bases[0]].scrollbar.pack(side=RIGHT, fill=Y)
        gcf().autofmt_xdate()
        self.createCharts(chartScrollables)
        
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
        openTradesListbox = Listbox(openTradesFrame, yscrollcommand=openTradesScrollbar.set, bd=0, selectmode=SINGLE)
        openTradesListbox.pack(fill=BOTH, expand=True)
        openTradesScrollbar.config(command=openTradesListbox.yview)

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
        pricesTexts = {}
        for b in bases:
            pricesTexts[b] = scrolledtext.ScrolledText(pricesFrame, bd=0, cursor='arrow')
            pricesTexts[b].configure(state='disabled')
            
        pricesTexts[bases[0]].pack(fill=BOTH, side=BOTTOM)

        baseChoice = StringVar(self.root)
        baseChoice.set(bases[0])
        baseMenu = OptionMenu(self.root, 
                              baseChoice,
                              *bases, 
                              command=lambda _: self.displaySelected(baseChoice, chartScrollables, pricesTexts)
        )
        baseMenu.configure(bg="#C4C4C4")
        baseMenu.configure(fg="black")
        baseMenu.configure(borderwidth=2)
        baseMenu.configure(highlightthickness=0)
        baseMenu.configure(font=("Roboto", int(10)))
        baseMenu.configure(relief="ridge")
        baseMenu.place(
            x=850,
            y=300,
            width=80,
            height=20
        )
        
        buyButton = Button(
            self.root,
            text="Buy",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.thread.manualBuy(baseChoice.get()),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        buyButton.place(
            x=850,
            y=330, 
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
            command=lambda: self.manualSellHandler(sellButton, openTradesListbox),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        sellButton.place(
            x=850,
            y=390, 
            width=80,
            height=40
        )
        sellButton.configure(state='disabled')
        
        reloadButton = Button(
            self.root,
            text="Reload",
            bg="#C4C4C4",
            fg="black",
            activebackground="#969696",
            borderwidth=2,
            highlightthickness=0,
            command=lambda: self.reload(reloadButton, openTradesListbox),
            font=("Roboto", int(18)),
            relief="ridge"
        )
        reloadButton.place(
            x=850,
            y=450, 
            width=80,
            height=40
        )

        frames = {'prices': pricesTexts, 
                  'balances': balanceText, 
                  'trades': tradesText, 
                  'chart': chartScrollables, 
                  'sliders': slidersFrame, 
                  'positions': openTradesListbox, 
                  'sell': sellButton, 
                  'reload': reloadButton}
        sliders = {'tp': tpScale, 'sl': slScale}
        self.startAsync(frames, sliders)
    
    def displaySelected(self, var, chartScrollables, pricesTexts):
        global base
        
        new = var.get()
        chartScrollables[base].canvas.pack_forget()
        chartScrollables[base].scrollbar.pack_forget()
        pricesTexts[base].pack_forget()
        chartScrollables[new].canvas.pack(side=LEFT)
        chartScrollables[new].scrollbar.pack(side=RIGHT, fill=Y)
        pricesTexts[new].pack(side=BOTTOM, fill=BOTH)
        base = new
    
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
        
        if allocation < min_trade_allocation:
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
                "Maximum value is" + str(maxQuote))
            return
        else:
            trade_allocation = allocation
            return

    def startAsync(self, frames, sliders):
        self.thread = AsyncioThread(self, 0)
        self.thread.start()
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.on_closing())
        try:
            self.root.after(200, lambda: self.refresh_frames(frames, sliders))
        except Exception as e:
            self.root.protocol('WM_DELETE_WINDOW', lambda: sys.exit())
            messagebox.showerror(
                title="Error",
                message=str(e) + "\nAutoTrader will now restart.")
            restartProgram()

        
    def reload(self, button, tradesListbox):
        button.configure(state='disabled')
        temp = self.thread
        self.thread = AsyncioThread(self, 1)
        while tradesListbox.size() != 0:
            tradesListbox.delete("end")
        self.thread.start()
        temp.kill()
        temp.join()
        del(temp)
        button.configure(state='normal')
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? "):
            closeProgram()
                
    def manualSellHandler(self, button, tradesListbox):
        button.configure(state='disabled')
        self.thread.sellQ.put_nowait(tradesListbox.curselection()[0])
        tsleep(1)
        if not tradesListbox.curselection() == ():
            button.configure(state='normal')
        else:
            button.configure(state='disabled')
        
    def createCharts(self, frames):
        func = lambda i: datetime.fromtimestamp(int(i) / 1000)
        self.vecfunc = vectorize(func)
        
        self.axis = {}
        self.canvas = {}
        for b in bases:
            fig = Figure()
            fig.set_figheight(1.8 * chart_num)
            fig.suptitle(b + quote)
            self.axis[b] = fig.subplots(chart_num, 1, squeeze=False)
            self.canvas[b] = FigureCanvasTkAgg(fig, frames[b].frame)
            self.canvas[b].get_tk_widget().pack(fill=X)
            fig.tight_layout(pad=1.0, w_pad=1.5, h_pad=1.2)
            self.canvas[b].draw()
            
    def updateChart(self, df, b):   
        x = df['Close Time'].to_numpy()
        x = x[-60:]
        x = self.vecfunc(x)
        
        self.axis[b][0, 0] = plotPrice(df, x, self.axis[b][0, 0])
        if strategy == 1:
            y1 = df['SMA_20'].to_numpy()
            y2 = df['SMA_50'].to_numpy()
            self.axis[b][0, 0].plot(x, y1[-60:], "-b", label="20 S.M.A.")
            self.axis[b][0, 0].plot(x, y2[-60:], "-r", label="50 S.M.A.")
            self.axis[b][0, 0].legend(loc="upper right", fontsize="x-small")
        elif strategy == 2:
            y1 = df['EMA_12'].to_numpy()
            y2 = df['EMA_26'].to_numpy()
            self.axis[b][0, 0].plot(x, y1[-60:], "-b", label="12 E.M.A.")
            self.axis[b][0, 0].plot(x, y2[-60:], "-r", label="26 E.M.A.")
            self.axis[b][0, 0].legend(loc="upper right", fontsize="x-small")
        elif strategy == 3:
            y1 = df['EMA_100'].to_numpy()
            self.axis[b][0, 0].plot(x, y1[-60:], "-b", label="100 E.M.A.")
            self.axis[b][0, 0].legend(loc="upper right", fontsize="x-small")
            self.axis[b][1, 0] = plotMACD(df, x, self.axis[b][1, 0])
        elif strategy == 4:
            self.axis[b][0, 0].legend(loc="upper right", fontsize="x-small")
            self.axis[b][1, 0] = plotMACD(df, x, self.axis[b][1, 0])
            self.axis[b][2, 0] = plotRSI(df, x, self.axis[b][2, 0])
        elif strategy == 5:
            self.axis[b][0, 0].legend(loc="upper right", fontsize="x-small")
            self.axis[b][1, 0] = plotMACD(df, x, self.axis[b][1, 0])
            self.axis[b][2, 0] = plotRSI(df, x, self.axis[b][2, 0])
            self.axis[b][3, 0] = plotStochastic(df, x, self.axis[b][3, 0])
        elif strategy == 6:
            y1 = df['SMA_20'].to_numpy()
            y2 = df['SMA_50'].to_numpy()
            self.axis[b][0, 0].plot(x, y1[-60:], "-b", label="20 S.M.A.")
            self.axis[b][0, 0].plot(x, y2[-60:], "-r", label="50 S.M.A.")
            self.axis[b][0, 0].legend(loc="upper right", fontsize="x-small")
            self.axis[b][1, 0] = plotMACD(df, x, self.axis[b][1, 0])
            self.axis[b][2, 0] = plotRSI(df, x, self.axis[b][2, 0])
        self.canvas[b].draw()
        self.root.update()
        tsleep(0.1)
        fun = lambda x: x.clear()
        vectorize(fun)(self.axis[b])
    
    def refresh_frames(self, frames, sliders):
        global tp
        global sl
        
        while True:
            while not self.thread.price.empty():
                [price, p] = self.thread.price.get_nowait()
                b = p.removesuffix(quote)
                frames['prices'][b].configure(state='normal')
                frames['prices'][b].insert("end", str(price) + '\n')
                frames['prices'][b].see("end")
                frames['prices'][b].yview("end")
                frames['prices'][b].configure(state='disabled')
            if not self.thread.trades.empty():
                frames['balances'].configure(state='normal')
                frames['balances'].delete(1.0, END)
                frames['balances'].insert('end', 
                                          f'Starting {quote} Balance: \n{startQuoteBalance} \n\n'
                                          f'Current {quote} Balance: \n{currentQuoteBalance} \n'
                                          )
                for b in bases:
                    frames['balances'].insert('end', 
                                              f'Current {b} Balance: \n{currentBaseBalance[b]} \n'
                                              )
                frames['balances'].configure(state='disabled')
                frames['trades'].configure(state='normal')
                frames['trades'].insert("end", self.thread.trades.get_nowait())
                frames['trades'].see("end")
                frames['trades'].yview("end")
                frames['trades'].configure(state='disabled')
            while not self.thread.data_frame_figure.empty():
                [data, p] = self.thread.data_frame_figure.get_nowait()
                b = p.removesuffix(quote)
                self.updateChart(data, b)
            if not self.thread.open_positions_display.empty():
                pos = self.thread.open_positions_display.get_nowait()
                if pos[0] == 'add':
                    frames['positions'].insert("end", f"[{pos[2]}] {pos[1]} {pos[3]}")
                elif pos[0] == 'del':
                    frames['positions'].delete(pos[1])
            if not self.thread.errors.empty():
                self.thread.errors.get_nowait()
                self.reload(frames['reload'], frames['positions'])
            if not frames['positions'].curselection() == ():
                frames['sell'].configure(state='normal')
            else:
                frames['sell'].configure(state='disabled')
            if not self.thread.closeQ.empty():
                closeProgram()
            tp = sliders['tp'].get()
            sl = sliders['sl'].get()
            self.root.update()
            tsleep(0.1)

class AsyncioThread(Thread):
    def __init__(self, theWindow, stat):
        self.asyncio_loop = new_event_loop()
        set_event_loop(self.asyncio_loop)
        
        self.theWindow = theWindow
        self.stat = stat
        Thread.__init__(self)
        self.daemon = True
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        Thread.start(self)
    
    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
        
    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None
        
    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace
    
    def kill(self):
        while self.open_positions.empty():
            tsleep(0.1)
        if not self.open_positions.empty():
            self.open_positions.get_nowait()
        self.open_positions.put_nowait([])
        try:
            self.asyncio_loop.stop()
        except:
            pass
        try:
            self.asyncio_loop.close()
        except:
            pass
        self.killed = True
        
    def run(self):
        self.asyncio_loop.run_until_complete(self.trader()) #, self.asyncio_loop)
                
    async def trader(self):
        self.open_positions = Queue()
        self.price = LifoQueue()
        self.price_sell = LifoQueue()
        self.data = Queue()
        self.data_frame = Queue()
        self.data_frame_figure = Queue()
        self.signals = Queue()
        self.trades = Queue()
        self.errors = Queue()
        self.open_positions_display = Queue()
        self.sellQ = Queue()
        self.close_positionsQ = qQueue()
        self.doneQ = qQueue()
        self.closeQ = Queue()
                
        try:
            self.client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=useTestnet)
        except Exception as e:
            self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))

        temp = curr_open_positions.get()
        curr_open_positions.put_nowait(temp)
        
        await self.open_positions.put(temp)
        for t in temp:
            self.asyncio_loop.call_soon_threadsafe(self.open_positions_display.put_nowait, 
                                                   ['add', t['qty'], t['time'], t['base']])

        try:
            self.bm = BinanceSocketManager(self.client)
        except Exception as e:
            self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
        
        if not self.stat:
            self.save_to_records(startQuoteBalance, 'open')
        self.tasks = [create_task(self.check_closing_time()),
                      create_task(self.kline_data()),  
                      create_task(self.update_data()),
                      create_task(self.generate_signals()), 
                      create_task(self.place_buy_order()),
                      create_task(self.place_sell_order()), 
                      create_task(self.manualSell()), 
                      create_task(self.close_positions())]

        try:
            await gather(*self.tasks)
        except Exception:
            self.theWindow.root.protocol('WM_DELETE_WINDOW', lambda: sys.exit())

        
        return

    async def check_closing_time(self):
        if useClosingTime:
            while time_diff() < closingTime and time_diff() < 86400:
                await sleep(10)
            self.closeQ.put_nowait(1)

    async def kline_data(self):
        streams = []
        for b in bases:
            s = b + quote + '@kline_1m'
            streams.append(s.lower())
        
        ms = self.bm.multiplex_socket(streams)
        myKeys = ['s', 't', 'o', 'h', 'l', 'c', 'v', 'T', 'q', 'n', 'V', 'Q']
        async with ms as mscm:
            while True:
                try:
                    a = await mscm.recv()
                except Exception as e:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
                else:
                    a = a['data']
                    res = a['k']
                    self.asyncio_loop.call_soon_threadsafe(self.price.put_nowait, [float(res['c']), res['s']])
                    self.asyncio_loop.call_soon_threadsafe(self.price_sell.put_nowait, [float(res['c']), res['s']])
                    if res['x']:
                        candle = [res[x] for x in myKeys]
                        self.asyncio_loop.call_soon_threadsafe(self.data.put_nowait, candle)

    async def update_data(self):
        dfs = await self.get_historical_data()
        for b in bases:
            p = b + quote
            df = dfs[p]
            self.data_frame_figure.put_nowait([df, p])
        while True:
            new_row = await self.data.get()
            p = new_row[0]
            new_row.remove(p)
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
            dfs = self.update_df(p, dfs, new_row)
            df = dfs[p]
            self.data_frame.put_nowait([df, p])
            self.data_frame_figure.put_nowait([df, p])
        return

    async def get_historical_data(self):
        headings = ['Open Time', 'Open', 'High', 'Low', 'Close',
                    'Volume', 'Close Time', 'Quote Asset Volume',
                    'Number of Trades', 'Taker buy Base Asset Volume',
                    'Taker buy Quote Asset Volume', 'Ignore']
        dfs = {}
        for b in bases:
            p = b + quote
            klines = array(await self.client.get_historical_klines(p, AsyncClient.KLINE_INTERVAL_1MINUTE, '1 day ago UTC', limit=1000)).astype(npdouble)
            df = DataFrame.from_records(klines, columns=headings)
            try:
                df.drop(['Ignore'], axis=1, inplace=True)
            except Exception:
                pass
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
            dfs[p] = df
        return dfs

    def update_df(self, p, dfs, new_row):
        df = dfs[p]
        new_row = Series(new_row, index=df.columns)
        if new_row[0] != df.iloc[-1, 0]:
            df = df.append(new_row, ignore_index=True)
        else:
            df.iloc[-1, :] = new_row
        if strategy == 1:
            df['SMA_20'][-80:] = df['Close'][-80].rolling(window=20).mean()
            df['SMA_50'][-110:] = df['Close'][-110:].rolling(window=50).mean()
            df['SMA_100'][-160:] = df['Close'][-160:].rolling(window=100).mean()
            df['SMA_200'][-260:] = df['Close'][-260:].rolling(window=200).mean()
        elif strategy == 2:
            df['EMA_12'][-200:] = df['Close'][-200:].ewm(span=12, adjust=False).mean()
            df['EMA_26'][-200:] = df['Close'][-200:].ewm(span=26, adjust=False).mean()
            df['EMA_50'][-200:] = df['Close'][-200:].ewm(span=50, adjust=False).mean()
            df['EMA_100'][-200:] = df['Close'][-200:].ewm(span=100, adjust=False).mean()
        elif strategy == 3:
            df['EMA_12'][-200:] = df['Close'][-200:].ewm(span=12, adjust=False).mean()
            df['EMA_26'][-200:] = df['Close'][-200:].ewm(span=26, adjust=False).mean()
            df['EMA_100'][-200:] = df['Close'][-200:].ewm(span=100, adjust=False).mean()
            df['MACD'].iloc[-1] = df['EMA_12'].iloc[-1] - df['EMA_26'].iloc[-1]
            df['Signal Line'][-80:] = df['MACD'][-80:].ewm(span=9, adjust=False).mean()
        elif strategy == 4:
            df['EMA_12'][-100:] = df['Close'][-100:].ewm(span=12, adjust=False).mean()
            df['EMA_26'][-100:] = df['Close'][-100:].ewm(span=26, adjust=False).mean()
            df['MACD'].iloc[-1] = df['EMA_12'].iloc[-1] - df['EMA_26'].iloc[-1]
            df['Signal Line'][-80:] = df['MACD'][-80:].ewm(span=9, adjust=False).mean()
            delta = df['Close'][-80:].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'][-80:] = 100 - (100 / (1 + rs))
        elif strategy == 5:
            df['EMA_12'][-100:] = df['Close'][-100:].ewm(span=12, adjust=False).mean()
            df['EMA_26'][-100:] = df['Close'][-100:].ewm(span=26, adjust=False).mean()
            df['MACD'].iloc[-1] = df['EMA_12'].iloc[-1] - df['EMA_26'].iloc[-1]
            df['Signal Line'][-80:] = df['MACD'][-80:].ewm(span=9, adjust=False).mean()
            delta = df['Close'][-80:].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'][-80:] = 100 - (100 / (1 + rs))
            high_14 = df['High'][-80:].rolling(14).max()
            low_14 = df['Low'][-80:].rolling(14).min()
            df['%K'][-80:] = (df['Close'][-80:] - low_14) * 100 / (high_14 - low_14)
            df['%D'][-80:] = df['%K'][-80:].rolling(3).mean()
        elif strategy == 6:
            df['SMA_20'][-80:] = df['Close'][-80:].rolling(window=20).mean()
            df['SMA_50'][-110:] = df['Close'][-110:].rolling(window=50).mean()
            df['EMA_12'][-100:] = df['Close'][-100:].ewm(span=12, adjust=False).mean()
            df['EMA_26'][-100:] = df['Close'][-100:].ewm(span=26, adjust=False).mean()
            df['MACD'].iloc[-1] = df['EMA_12'].iloc[-1] - df['EMA_26'].iloc[-1]
            df['Signal Line'][-80:] = df['MACD'][-80:].ewm(span=9, adjust=False).mean()
            delta = df['Close'][-80:].diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=13, adjust=False).mean()
            ema_down = down.ewm(com=13, adjust=False).mean()
            rs = ema_up / ema_down
            df['RSI'][-80:] = 100 - (100 / (1 + rs))
        dfs[p] = df
        return dfs

    async def generate_signals(self):
        while self.close_positionsQ.empty():
            [df, p] = await self.data_frame.get()
            if strategy == 0:
                pass
            elif strategy == 1:
                if self.strat1(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, p)
            elif strategy == 2:
                if self.strat2(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, p)
            elif strategy == 3:
                if self.strat3(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, p)
            elif strategy == 4:
                if self.strat4(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, p)
            elif strategy == 5:
                if self.strat5(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, p)
            elif strategy == 6:
                if self.strat6(df):
                    self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, p)
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

    def manualBuy(self, b):
        self.asyncio_loop.call_soon_threadsafe(self.signals.put_nowait, b + quote)

    async def manualSell(self):
        while self.close_positionsQ.empty():
            if not self.sellQ.empty():
                i = self.sellQ.get_nowait()
                sell_list = await self.open_positions.get()
                await self.open_positions.put(sell_list)
                try:
                    s = sell_list[i]
                except IndexError:
                    pass
                else:
                    try:
                        data = await self.client.get_symbol_ticker(symbol=s['base'] + quote)
                    except Exception as e:
                        self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
                    else:
                        current_price = float(data['price'])
                        await self.sell(s['qty'], current_price, s['id'], s['base'] + quote, i)
            await sleep(0.5)
        
    async def place_buy_order(self):
        while self.close_positionsQ.empty():
            p = await self.signals.get()
            try:
                balance = await self.client.get_asset_balance(asset=quote)
                data = await self.client.get_symbol_ticker(symbol=p)
            except Exception as e:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
            else:
                current_price = float(data['price'])
                balance = float(balance['free'])
                quantity =  trade_allocation / current_price
                if balance < min_trade_allocation:
                    pass
                elif balance < trade_allocation:
                    pass
                else:
                    if trade_allocation >= filters[p]['minNotional']:
                        quantity =  trade_allocation / current_price
                    else:
                        quantity =  (filters[p]['minNotional'] * 1.001) / current_price
                    if quantity > filters[p]['maxQty']:
                        quantity = filters[p]['maxQty'] * 0.97
                    count = trade_count.get()
                    trade_count.put_nowait(count)
                    res = await self.buy(quantity, current_price, count, p)
                    if res:
                        count = trade_count.get()
                        count += 1
                        trade_count.put_nowait(count)
        return
    
    async def buy(self, qty, current_price, count, p):
        if filters[p]['stepSize'] == 0:
            qty = round_step_size(qty, filters[p]['lotStepSize'])
        else:
            qty = round_step_size(qty, filters[p]['stepSize'])
            
        try:
            order = await self.client.order_market_buy(
                symbol=p,
                quantity=qty)
        except Exception:
            return False
        else:
            while True:
                await sleep(0.5)
                try:
                    trade_status = await self.client.get_order(symbol=p, orderId=order['orderId'])
                except Exception as ex:
                    self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(ex))
                    return False
                else:
                    if float(trade_status['executedQty']) == qty:
                        await self.save_trades('buy', qty, current_price, count, p.removesuffix(quote))
                        data = {'stop-loss': (1 - (sl / 100)) * current_price, 
                                'take-profit': (1 + (tp / 100)) * current_price, 
                                'qty': qty, 
                                'id': count, 
                                'time': strftime('%H:%M'), 
                                'base': p.removesuffix(quote)
                                }
                        sell_list = await self.open_positions.get()
                        sell_list.append(data)
                        await self.open_positions.put(sell_list)
                        curr_open_positions.get()
                        curr_open_positions.put_nowait(sell_list)
                        self.asyncio_loop.call_soon_threadsafe(self.open_positions_display.put_nowait, 
                                                               ['add', qty, strftime('%H:%M'), p.removesuffix(quote)])
                        return True
    
    async def place_sell_order(self):        
        while self.close_positionsQ.empty():
            [current_price, p] = await self.price_sell.get()
            sell_list = await self.open_positions.get()
            await self.open_positions.put(sell_list)
            
            for s in sell_list:
                if p == s['base'] + quote and (current_price < s['stop-loss'] or current_price > s['take-profit']):
                    await self.sell(s['qty'], current_price, s['id'], p, sell_list.index(s))
        return
    
    async def sell(self, qty, current_price, count, p, idx):
        temp = curr_open_positions.get()
        
        try:
            order = await self.client.order_market_sell(
                symbol=p,
                quantity=qty)
        except Exception as e:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(e))
                return False
        else:
            await sleep(0.5)
            try:
                await self.client.get_order(symbol=p, orderId=order['orderId'])
            except Exception as ex:
                self.asyncio_loop.call_soon_threadsafe(self.errors.put_nowait, str(ex))
                return False
            else:
                temp.remove(temp[idx])
                curr_open_positions.put_nowait(temp)
                self.asyncio_loop.call_soon_threadsafe(self.open_positions_display.put_nowait, 
                                       ['del', idx])
                await self.open_positions.get()
                await self.open_positions.put(temp)
                await self.save_trades('sell', qty, current_price, count, p.removesuffix(quote))
                return True
        
    async def close_positions(self):
        while self.close_positionsQ.empty():
            await sleep(0.5)
        self.close_positionsQ.get()
        temp = await self.open_positions.get()
        res = temp.copy()
        self.open_positions.put_nowait(res)
        if not res == []:
            try:
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 'Closing positions. \n\n')
                prices = {}
                for b in bases:
                    data = await self.client.get_symbol_ticker(symbol=b + quote)
                    price = float(data['price'])
                    prices[b] = price
                    
                for i in res:
                    await self.sell(i['qty'], prices[i['base']], i['id'], i['base'] + quote, 0)

                closing_balance = await self.client.get_asset_balance(asset=quote)
                closing_balance = float(closing_balance['free'])
                self.save_to_records(closing_balance, 'close')
            except Exception as e:
                self.save_to_records(currentQuoteBalance, 'close')
        else:            
            self.save_to_records(currentQuoteBalance, 'close')
        self.doneQ.put(1)

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
        
    async def save_trades(self, trade_type, qty, price, count, b):
        global currentBaseBalance
        global currentQuoteBalance
        
        temp = await self.client.get_asset_balance(asset=b)
        currentBaseBalance[b] = float(temp['free'])        
        currentQuoteBalance = await self.client.get_asset_balance(asset=quote)
        currentQuoteBalance = float(currentQuoteBalance['free'])

        try:
            file = open(FILE_NAME, 'a')
            file.write(strftime('%H:%M') + '\n')
            if trade_type == 'buy':
                file.write(f'Trade {count} \n')
                file.write(f'Bought {qty} {b} at {price} {quote} per {b} ({qty * price} {quote}). \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, strftime("%H:%M") + '\n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Trade {count} \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 
                                                       f'Bought {qty} {b} at {price} {quote} per {b} ({round(qty * price, 4)} {quote}) \n\n')
            elif trade_type == 'sell':
                file.write(f'Closed trade {count} \n')
                file.write(f'Sold {qty} {b} at {price} {quote} per {b} ({qty * price} {quote}). \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, strftime("%H:%M") + '\n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, f'Closed trade {count} \n')
                self.asyncio_loop.call_soon_threadsafe(self.trades.put_nowait, 
                                                       f'Sold {qty} {b} at {price} {quote} per {b} ({round(qty * price, 4)} {quote}) \n\n')
        finally:
            file.close()
                        
def plotPrice(df, x, ax):
    y = df['Close'].to_numpy()
    ax.plot(x, y[-60:], "-g", label="Price")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_minor_locator(mns)
    ax.set_title("Price")
    return ax

def plotMACD(df, x, ax):
    y1 = df['MACD'].to_numpy()
    y2 = df['Signal Line'].to_numpy()
    ax.plot(x, y1[-60:], "-b", label="MACD")
    ax.plot(x, y2[-60:], "-r", label="Signal Line")
    ax.plot(x, [0]*len(x), color='k', linestyle='--')
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_minor_locator(mns)
    ax.legend(loc="upper right", fontsize="x-small")
    ax.set_title("MACD")
    return ax

def plotRSI(df, x, ax):
    y = df['RSI'].to_numpy()
    ax.plot(x, y[-60:], "-b", label="RSI")
    ax.plot(x, [30]*len(x), color='k', linestyle='--')
    ax.plot(x, [70]*len(x), color='k', linestyle='--')
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_minor_locator(mns)
    ax.legend(loc="upper right", fontsize="x-small")
    ax.set_title("RSI")
    return ax

def plotStochastic(df, x, ax):
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
    
def closeProgram():
    window.thread.close_positionsQ.put(1)
    window.thread.doneQ.get()
    try:
        window.thread.asyncio_loop.stop()
    except:
        pass
    try:
        window.thread.asyncio_loop.close()
    except:
        pass
    window.root.quit()
    window.root.destroy()
    try:
        sys.exit()
    except SystemExit:
        pass

def restartProgram():
    temp = trade_count.get()
    command = 'AutoTrader -r '
    if useTestnet:
        command = command + '-t '
    command = command + f'-a {API_KEY} {SECRET_KEY} {sl} {tp} {trade_allocation} {useClosingTime} {startTime} {closingTime} {strategy} {quote} {temp} '
    command = command + '-b '
    for b in bases:
        command = command + f'{b} '
    temp = curr_open_positions.get()
    for t in temp:
        command = command + '-o '
        for i in t.values():
            command = command + f'{i} '
            
    try:
        window.thread.asyncio_loop.stop()
    except:
        pass
    try:
        window.thread.asyncio_loop.close()
    except:
        pass

    window.root.quit()
    window.root.destroy()
    os.system(command)
    os.system('exit')
    try:
        sys.exit()
    except SystemExit:
        pass
        
class V_ScrollableFrame:
    def __init__(self, container):
        self.canvas = Canvas(container, width=550, height=230)
        self.scrollbar=Scrollbar(container, orient=VERTICAL, command=self.canvas.yview)
        self.frame = Frame(self.canvas, 
                           bg = "#FFFFFF",
                           bd=0
                           )
        self.frame.bind('<Configure>', 
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')
                                                 )
                        )
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw', width=550)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

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
    window = TheWindow()
    window.root.mainloop()
    try:
        sys.exit()
    except SystemExit:
        pass
