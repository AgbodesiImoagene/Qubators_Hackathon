from pathlib import Path
import aiohttp
import asyncio
import pandas as pd
import numpy as np
import time
import joblib
import threading
from datetime import datetime
import nest_asyncio
import tkinter as tk
from binance import AsyncClient, BinanceSocketManager
from binance.helpers import round_step_size
import binance.exceptions
from binance.enums import KLINE_INTERVAL_1MINUTE
from binance.exceptions import BinanceRequestException, BinanceAPIException
from tkinter import ttk, Tk, Entry, Button, Frame, Label, Scale, scrolledtext, Radiobutton, messagebox, LEFT, HORIZONTAL


OUTPUT_PATH = Path(__file__).parent

loop = ''
useTestnet = ''
client = ''
base = ''
quote = ''
pair = ''
my_filters = ''
sl = ''
tp = ''
trade_allocation = ''
closingTime = ''
startBaseBalance = ''
startQuoteBalance = ''

# class App(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.start()
        
#     def callback(self):
#         self.root.quit()
        
#     def run(self):
#         self.root = Tk()
#         self.root.protocol("WM_DELETE_WINDOW", self.callback)

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def initGUI():
    introFrame = Frame(
        window,
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
        command=lambda: destroyWelcomeFrame([introFrame]),
        font=("Roboto", int(18)),
        relief="ridge"
    )
    next_button.place(
        x=700,
        y=320
    )

def destroyWelcomeFrame(prevFrames):
    for frame in prevFrames:
        frame.destroy()
    testnet()
    
def testnet():
    infoFrame = Frame(
        window,
        bg = "#C4C4C4",
        height = 400,
        width = 200,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )
    infoFrame.place(x = 0, y = 0)
    
    useTestnetFrame = Frame(
        window,
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
        command=lambda: clientKeys(True, prevFrames),
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
        command=lambda: clientKeys(False, prevFrames),
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
        "funds. ",        
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

def clientKeys(val, prevFrames):
    global useTestnet
    useTestnet = val
    
    infoFrame = Frame(
        window,
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
        window,
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
            "location for future ease of access. ",
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
            "location for future ease of access. ",
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
        command=lambda: validateClientHandler(prevFrames, keys),
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
        command=lambda: destroyWelcomeFrame(prevFrames),
        font=("Roboto", int(18)),
        relief="ridge"
    )
    button_2.place(
        x=30,
        y=300
    )

def validateClientHandler(prevFrames, keys):
    global loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(validateClient(prevFrames, keys))
    return
    
async def validateClient(prevFrames, keys):
    global client

    API_KEY = keys[0].get()
    SECRET_KEY = keys[1].get()

    try:
        session = AsyncClient()._init_session()
        await session.close()
        client = await AsyncClient.create(API_KEY, SECRET_KEY, testnet=useTestnet)
        await client.get_account()
    except aiohttp.client_exceptions.ClientConnectorError:
        messagebox.showerror(
            title="Could not create client.",
            message="Please check connection. ")
        return
    except BinanceRequestException or BinanceAPIException as e:
        messagebox.showerror(
            title="Could not create client.",
            message=str(e) + "\nPlease enter valid keys. ")
        return
    except asyncio.exceptions.TimeoutError:
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
        destroyClientKeysFrame(prevFrames)

def destroyClientKeysFrame(prevFrames):
    for frame in prevFrames:
        frame.destroy()
    settings()
    
def settings():    
    infoFrame = Frame(
        window,
        bg = "#C4C4C4",
        height = 400,
        width = 200,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )
    infoFrame.place(x = 0, y = 0)
    
    settingsFrame = Frame(
        window,
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
        text="Enter or select a base symbol or quote \n"
        "symbol that forms a valid Binance \n"
        "pair. A special AI assisted \n"
        "strategy is available for BTCUSDT \n"
        "only. \n\n"
        "Stop-loss and take-profit percentages \n"
        "determine the decrease or inrease in \n"
        "the value of a ticker required to \n"
        "trigger a sale. \n\n"
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
    quote_label.place(x=250, y=50)

    quoteChoice = tk.StringVar(settingsFrame)            
    quoteDropdown = ttk.Combobox(settingsFrame, textvariable=quoteChoice, width=6)
    if useTestnet:
        quoteDropdown["values"] = ("USDT", "BUSD", "BTC", "BNB")
    else:
        quoteDropdown["values"] = ("USDT", "USDC", "BUSD", "TUSD", "PAX", "BTC", "ETH", "BNB")

    quoteDropdown.place(x=330, y=50)
    quoteDropdown.current(0)
    quoteDropdown.set("USDT")
    
    base_label = Label(
        settingsFrame, 
        text="Base symbol: ",
        bg="white",
        fg="black",
        font=("Roboto", int(10))
    )
    base_label.place(x=20, y=50)

    baseChoice = tk.StringVar(settingsFrame)            
    baseDropdown = ttk.Combobox(settingsFrame, textvariable=baseChoice, width=6)
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
    baseDropdown.current(0)
    
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
        from_=0.1, 
        to=10.00, 
        resolution=0.1, 
        orient=HORIZONTAL, 
        length=200
    )
    slScale.set(0.5)
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
        from_=0.1, 
        to=10.00, 
        resolution=0.1, 
        orient=HORIZONTAL, 
        length=200
    )
    tpScale.set(1.0)
    tpScale.place(x=300, y=150)
    
    lotSizeLabel = Label(
        settingsFrame, 
        text="Lot Size",
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
    
    closingTimeLabel = Label(
        settingsFrame, 
        text="Closing Time (HH MM)",
        bg="white",
        fg="black",
        font=("Roboto", int(10))
    )
    closingTimeLabel.place(x=300, y=220)
    
    HourChoice = tk.StringVar(settingsFrame)
    HourBox = ttk.Combobox(settingsFrame, textvariable=HourChoice, state="readonly", width=4)
    HourBox["values"] = tuple([f"{i:02d}" for i in range(0, 24)])
    HourBox.place(x=300, y=250)
    HourBox.set("20")
    MinChoice = tk.StringVar(settingsFrame)
    MinBox = ttk.Combobox(settingsFrame, textvariable=MinChoice, state="readonly", width=4)
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
        command=lambda: validateSettingsHandler(prevFrames, setting_vars),
        # command=lambda: destroySettingsFrame(prevFrames),
        font=("Roboto", int(18)),
        relief="ridge"
    )
    button_1.place(
        x=380,
        y=300
    )

def validateSettingsHandler(prevFrames, setting_vars):
    # global loop
    # loop = asyncio.get_event_loop()
    loop.run_until_complete(validateSettings(prevFrames, setting_vars))
    return
    
async def validateSettings(prevFrames, setting_vars):
    global client
    global base
    global quote
    global pair
    global my_filters
    global sl
    global tp
    global trade_allocation
    global closingTime
    
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
    closingTime = datetime.strptime(closingTime, '%H:%M:%S')
    closingTime = (closingTime - datetime(1900, 1, 1)).total_seconds()
    
    data = await client.get_symbol_info(pair)
    if data == None:
        messagebox.showerror(
            title="Error",
            message=pair + "is not a valid symbol pair. ")
        return
    
    
    my_filters = {}
    my_filters['maxPrecision'] = 10 ** -(data['baseAssetPrecision'])
    filters = data['filters']
    for dictionary in filters:
        if dictionary['filterType'] == 'LOT_SIZE':
            my_filters['lotStepSize'] = float(dictionary['stepSize'])
        if dictionary['filterType'] == 'MARKET_LOT_SIZE':
            my_filters['minQty'] = float(dictionary['minQty'])
            my_filters['maxQty'] = float(dictionary['maxQty'])
            my_filters['stepSize'] = float(dictionary['stepSize'])
        if dictionary['filterType'] == 'MIN_NOTIONAL':
            my_filters['minNotional'] = float(dictionary['minNotional'])
            
    start_balance = await client.get_asset_balance(asset=quote)
    start_balance = float(start_balance['free'])
    price = await client.get_ticker(symbol=pair)
    price = float(price["lastPrice"])
    maxQuote = price * my_filters['maxQty']
    
    if (trade_allocation * (100 - sl) / 100) < my_filters['minNotional']:
        messagebox.showerror(
            title="Error",
            message="Trade allocation is too small. \n"
            "minimum value is " + str(my_filters['minNotional'] * (100 / (99 - sl))))
        return
    elif trade_allocation > start_balance:
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
    
    destroySettingsFrame(prevFrames)

def destroySettingsFrame(prevFrames):
    for frame in prevFrames:
        frame.destroy()
    chooseStrategy()

def chooseStrategy():    
    infoFrame = Frame(
        window,
        bg = "#C4C4C4",
        height = 400,
        width = 200,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )
    infoFrame.place(x = 0, y = 0)
    
    strategyFrame = Frame(
        window,
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

    info = Label(
        infoFrame,
        text="Enter or select a base symbol or quote \n"
        "symbol that forms a valid Binance \n"
        "pair. A special AI assisted \n"
        "strategy is available for BTCUSDT \n"
        "only. \n\n"
        "Stop-loss and take-profit percentages \n"
        "determine the decrease or inrease in \n"
        "the value of a ticker required to \n"
        "trigger a sale. \n\n"
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
    
    strategyChoice = tk.IntVar(strategyFrame)
    if pair == "BTCUSDT":
        option1 = Radiobutton(
            strategyFrame, 
            text="Custom AI regression strategy", 
            variable=strategyChoice, 
            value=0, 
            width=60, 
            anchor="w"
        )
        option1.place(x=50, y=150)
        option2 = Radiobutton(
            strategyFrame, 
            text="Moving average strategy", 
            variable=strategyChoice, 
            value=1, 
            width=60, 
            anchor="w"
        )
        option2.place(x=50, y=200)
        option1.select()
    else:
        option1 = Radiobutton(
            strategyFrame, 
            text="Moving average strategy", 
            variable=strategyChoice, 
            value=1, 
            width=60, 
            anchor="w"
        )
        option1.place(x=50, y=180)
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
        # command=lambda: validateClientHandler(prevFrames, keys),
        command=lambda: clearWindow(),
        font=("Roboto", int(18)),
        relief="ridge"
    )
    button_1.place(
        x=380,
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
        command=lambda: destroyClientKeysFrame(prevFrames),
        font=("Roboto", int(18)),
        relief="ridge"
    )
    button_2.place(
        x=30,
        y=300
    )

def clearWindow():
    for widgets in window.winfo_children():
        widgets.destroy()
    window.geometry("1000x600")
    mainWindowHandler()

def mainWindowHandler():
    loop.run_until_complete(mainWindow())
    return

async def mainWindow():
    global startBaseBalance
    global startQuoteBalance
    
    balanceFrame = Frame(
        window,
        bg = "#FFFFFF",
        height = 180,
        width = 180,
        bd = 4,
        highlightthickness = 0,
        relief = "ridge"
    )
    balanceFrame.place(x = 10, y = 10)
    
    slidersFrame = Frame(
        window,
        bg = "#FFFFFF",
        height = 280,
        width = 180,
        bd = 4,
        highlightthickness = 0,
        relief = "ridge"
    )
    slidersFrame.place(x = 10, y = 210)

    dfFrame = Frame(
        window,
        bg = "#FFFFFF",
        height = 230,
        width = 580,
        bd = 4,
        highlightthickness = 0,
        relief = "ridge"
    )
    dfFrame.place(x = 210, y = 10)

    tradesFrame = Frame(
        window,
        bg = "#FFFFFF",
        height = 230,
        width = 580,
        bd = 4,
        highlightthickness = 0,
        relief = "ridge"
    )
    tradesFrame.place(x = 210, y = 260)
    
    pricesFrame = Frame(
        window,
        bg = "#FFFFFF",
        height = 280,
        width = 180,
        bd = 4,
        highlightthickness = 0,
        relief = "ridge"
    )
    pricesFrame.place(x = 810, y = 10)
    

    
    
    open_positions = asyncio.Queue()
    startBaseBalance = await client.get_asset_balance(asset=base)
    startBaseBalance = float(startBaseBalance['free'])
    startQuoteBalance = await client.get_asset_balance(asset=quote)
    startQuoteBalance = float(startQuoteBalance['free'])
    frames = {'prices': pricesFrame, 'balances': balanceFrame, 'trades': tradesFrame, 'dataframes': dfFrame, 'sliders': slidersFrame}
    # loop.run_until_complete(updateFrames(frames, open_positions))

async def updateFrames(frames, open_positions):
    price = asyncio.LifoQueue()
    data = asyncio.Queue()
    data_frame = asyncio.Queue()
    signals = asyncio.Queue()
    sell_price = asyncio.Queue()
    finish = asyncio.Queue()
    await open_positions.put([])
    
    await asyncio.gather(updater(), kline_data(frames['prices'], data, price, finish))

async def updater():
    await asyncio.sleep(.999)
    window.after(1, loop.run_until_complete(updater()))


    
# async def create_clients(): # Initialise clients
#     try:
#         client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_SECRET_KEY)
#     except BinanceAPIException or BinanceRequestException as e:
#         print(e.message)
#         return False
#     else:
#         if use_testnet:
#             try:
#                 test_client = await AsyncClient.create(TESTNET_API_KEY, TESTNET_SECRET_KEY, testnet=True)
#             except BinanceRequestException as e:
#                 print(e.message)
#                 return False
#             else:
#                 clients = [client, test_client]
#         else:
#             clients = [client]
#         start_balance = await clients[use_testnet].get_asset_balance(asset=quote)
#         start_balance = start_balance['free']
#         print(f'Opening balance = {start_balance}. ') # Save start balance
#         save_to_records(start_balance, 'open')
#         return clients

# async def close_clients(clients): # Close clients
#     for i in clients:
#         await i.close_connection()
    
# async def check_symbol(clients): # Check if specified pair is valid
#     if clients == False:
#         return False
#     try:
#         await clients[use_testnet].get_symbol_info(pair)
#     except BinanceRequestException:
#         print(pair + ' is an ivalid pair. ')
#         return False
#     return True

# async def get_symbol_filters(clients): # Symbol info
#     data = await clients[use_testnet].get_symbol_info(pair)
#     my_filters = {}
#     my_filters['maxPrecision'] = 10 ** -(data['baseAssetPrecision'])
#     filters = data['filters']
#     for dictionary in filters:
#         if dictionary['filterType'] == 'LOT_SIZE':
#             my_filters['lotStepSize'] = float(dictionary['stepSize'])
#         if dictionary['filterType'] == 'MARKET_LOT_SIZE':
#             my_filters['minQty'] = float(dictionary['minQty'])
#             my_filters['maxQty'] = float(dictionary['maxQty'])
#             my_filters['stepSize'] = float(dictionary['stepSize'])
#         if dictionary['filterType'] == 'MIN_NOTIONAL':
#             my_filters['minNotional'] = float(dictionary['minNotional'])
#     return(my_filters)

# async def get_historical_data(client):
#     headings = ['Open Time', 'Open', 'High', 'Low', 'Close',
#                 'Volume', 'Close Time', 'Quote Asset Volume',
#                 'Number of Trades', 'Taker buy Base Asset Volume',
#                 'Taker buy Quote Asset Volume', 'Ignore']
    
#     klines = np.array(await client.get_historical_klines(pair, AsyncClient.KLINE_INTERVAL_1MINUTE, '1 day ago UTC')).astype(np.double)
#     df = pd.DataFrame.from_records(klines, columns=headings)
#     df.drop(['Ignore'], axis=1, inplace=True)
#     return df

# def update_df(df, new_row):
#     new_row = pd.Series(new_row, index=df.columns)
#     if new_row[0] != df.iloc[-1, 0]:
#         df = df.append(new_row, ignore_index=True)
#     else:
#         df.iloc[-1, :] = new_row
#     return df

# async def update_data(client, live_data, data_frame, finish):
#     df = await get_historical_data(client)
#     while finish.empty():
#         new_row = await live_data.get()
#         new_row = np.array(new_row).astype(np.double)
#         df = update_df(df, new_row)
#         await data_frame.put(df)
#     return
    
# async def my_signals(model, scaler, data_frame, signals, finish): # Sample strategy
#     while finish.empty():
#         df = await data_frame.get()
#         last_price = df.iloc[-1, 4]
#         if pair == 'BTCUSDT':
#             input_data = df.iloc[-10:, :].to_numpy()
#             predicted_price = model.predict(np.reshape(scaler.transform(input_data), (1, 10, 11))).squeeze()
#             print(f'Predicton: {predicted_price}')
#             print(f'Last price: {last_price}')
#             if predicted_price >= (last_price * (1 + tp)):
#                 await signals.put(1)
#             else:
#                 await signals.put(0)
#         else:
#             avg = df.iloc[-60:, 4].mean()
#             if (avg - last_price) / last_price > tp:
#                 await signals.put(1)
#             else:
#                 await signals.put(0)
#     return
 
# async def custom_signals(data_frame, signals, finish):
#     while finish.empty():
#         pass # Code a trading strategy in this function and pass the results into the signals queue
#         # You can get data from data_frame with 'await data_frame.get()'
#         # This will return a pandas dataframe with candle data from the past day
#         # You can calculate indicators manually or use a library like ta
#         # New data is passed every minute
#         # After getting the data and determining whether to buy or sell you can
#         # pass a 1 to signals to buy or a 0 to hold with 'await signals.put(0)'
#     return

# async def place_buy_order(clients, signals, price, sell_price, filters, finish):
#     while finish.empty():
#         s = await signals.get()
#         if s == 1:                
#             try:
#                 balance = await clients[use_testnet].get_asset_balance(asset=quote)
#             except BinanceAPIException as e:
#                 print(e)
#             else:
#                 current_price = await price.get()
#                 await price.put(current_price)
#                 balance = float(balance['free'])
#                 allocation = balance * trade_allocation
#                 quantity =  allocation / current_price
#                 if balance < filters['minNotional']:
#                     print(f'Insufficient funds. ')
#                 else:
#                     if allocation >= filters['minNotional']:
#                         quantity =  allocation / current_price
#                     else:
#                         print(f'Minimum trade size is {filters["minNotional"]} {quote}. ')
#                         quantity =  filters['minNotional'] / current_price
#                     if quantity > filters['maxQty']:
#                         quantity = filters['maxQty']
#                     await buy(clients[use_testnet], quantity, filters, current_price, sell_price)
#     return

# async def buy(client, qty, filters, price, sell_price):
#     if filters['stepSize'] == 0:
#         qty = round_step_size(qty, filters['lotStepSize'])
#     else:
#         qty = round_step_size(qty, filters['stepSize'])
        
#     try:
#         order = await client.order_market_buy(
#             symbol=pair,
#             quantity=qty)
#     except BinanceAPIException as e:
#         print(e)
#     else:
#         await asyncio.sleep(0.2)
#         try:
#             trade_status = await client.get_order(symbol=pair, orderId=order['orderId'])
#         except BinanceAPIException as ex:
#             print(ex)
#         else:
#             if float(trade_status['executedQty']) == qty:
#                 save_trades('buy', qty, price)
#                 await sell_price.put({'stop-loss': (1 - sl) * price,
#                                       'take-profit': (1 + tp) * price,
#                                       'qty': qty})

# async def place_sell_order(clients, open_positions, price, sell_price, filters, finish):
#     sell_list = []
#     while finish.empty():
#         current_price = await price.get()
#         if not sell_price.empty():
#             position = await sell_price.get()
#             sell_list = await open_positions.get()
#             sell_list.append(position)
#             await open_positions.put(sell_list)
#         for s in sell_list:
#             if current_price < s['stop-loss'] or current_price > s['take-profit']:
#                 await sell(clients[use_testnet], s['qty'], current_price)
#                 sell_list.remove(s)
#                 temp = await open_positions.get()
#                 await open_positions.put(sell_list)
#     return

# async def sell(client, qty, price):
#     try:
#         order = await client.order_market_sell(
#             symbol=pair,
#             quantity=qty)
#     except BinanceAPIException as e:
#         print(e)
#     else:
#         await asyncio.sleep(0.2)
#         try:
#             trade_status = await client.get_order(symbol=pair, orderId=order['orderId'])
#         except BinanceAPIException as ex:
#             print(ex)
#         else:
#             save_trades('sell', qty, price)

async def kline_data(frame, data, price, finish): # Get live data
    text = scrolledtext.ScrolledText(frame)
    text.pack(expand=True, fill='both')
    
    bm = BinanceSocketManager(client)
    ks = bm.kline_socket(pair, interval=KLINE_INTERVAL_1MINUTE)
    myKeys = ['t', 'o', 'h', 'l', 'c', 'v', 'T', 'q', 'n', 'V', 'Q']
    async with ks as kscm:
        while finish.empty():
            try:
                a = await kscm.recv()
            except BinanceAPIException as e:
                print(e)
                await finish.put(True)
            else:
                res = a['k']
                await price.put(float(res['c']))
                if res['x']:
                    candle = [res[x] for x in myKeys]
                    await data.put(candle)
                text.insert('insert', str(res['c']))
                text.configure(state="disabled")
                print(res['c'])
    return

async def check_closing_time(finish):
    while time.time() % 86400 < closingTime:
        await asyncio.sleep(60)
    await finish.put(True)

# async def close_positions(clients, filters, open_positions):
#     print('Closing positions. ')
#     positions = await open_positions.get()
#     data = await clients[use_testnet].get_symbol_ticker(symbol=pair)
#     price = data['price']
#     for i in positions:
#         await sell(clients[use_testnet], i['qty'], price)
        
#     try:
#         closing_balance = await clients[use_testnet].get_asset_balance(asset=quote)
#     except BinanceAPIException as e:
#         print(e)
#     else:
#         closing_balance = float(closing_balance['free'])
#         print(f'Closing balance = {closing_balance}. ')
#         save_to_records(closing_balance, 'close')

# def save_to_records(balance, trade_period):
#     try:
#         file = open(FILE_NAME, 'a')
#         file.write(time.strftime('%c') + '\n')
#         if trade_period == 'open':
#             file.write(f'Opening balance: {balance}. \n')
#         elif trade_period == 'close':
#             file.write(f'Closing balance: {balance}. \n\n')
#     finally:
#         file.close()
    
# def save_trades(trade_type, qty, price):
#     try:
#         file = open(FILE_NAME, 'a')
#         file.write(time.strftime('%c') + '\n')
#         if trade_type == 'buy':
#             file.write(f'Bought {qty} {base} at {price} {quote} per {base}. \n')
#             print(f'Bought {qty} {base} at {price} {quote} per {base}. ')
#         elif trade_type == 'sell':
#             file.write(f'Sold {qty} {base} at {price} {quote} per {base}. \n')
#             print(f'Sold {qty} {base} at {price} {quote} per {base}. ')
#     finally:
#         file.close()
    
# async def trader(clients, filters, open_positions):
#     scaler = joblib.load('X_scaler.pkl')
#     model = tf.keras.models.load_model('Checkpoints/cp-40+58-160.5325-18-21-08-06-08-2021.hdf5') # AI model

#     print(time.asctime())
    
#     price = asyncio.LifoQueue()
#     data = asyncio.Queue()
#     data_frame = asyncio.Queue()
#     signals = asyncio.Queue()
#     sell_price = asyncio.Queue()
#     finish = asyncio.Queue()
#     await open_positions.put([])

#     await asyncio.gather(check_closing_time(finish),
#                          kline_data(clients[0], data, price, finish),
#                          update_data(clients[0], data, data_frame, finish),
#                          # custom_signals(data_frame, signals, finish), # Remove the hash at the start of the line to implement your strategy
#                          my_signals(model, scaler, data_frame, signals, finish), # Comment out this line
#                          place_buy_order(clients, signals, price, sell_price, filters, finish),
#                          place_sell_order(clients, open_positions, price, sell_price, filters, finish))
#     return


if __name__ == '__main__':
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    
    window = Tk()
    window.title("AutoTrader")
    
    window.geometry("800x400")
    window.configure(bg = "#C4C4C4")

    initGUI()
    
    window.resizable(False, False)
    tk.mainloop()



