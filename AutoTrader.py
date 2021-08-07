import asyncio
# import nest_asyncio
import pandas as pd
import numpy as np
import binance
# import ta
import time
import joblib
from datetime import datetime
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from binance import AsyncClient, BinanceSocketManager
from binance.helpers import round_step_size
from userVariables import *
from binance.enums import *
from binance.exceptions import *

FILE_NAME = 'TradeRecords.txt'

pair = base + quote
close_time = datetime.strptime(close_time, '%H:%M:%S')
close_time = (close_time - datetime(1900, 1, 1)).total_seconds()
    
async def create_clients(): # Initialise clients
    try:
        client = await AsyncClient.create(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    except BinanceAPIException or BinanceRequestException as e:
        print(e.message)
        return False
    else:
        if use_testnet:
            try:
                test_client = await AsyncClient.create(TESTNET_API_KEY, TESTNET_SECRET_KEY, testnet=True)
            except BinanceRequestException as e:
                print(e.message)
                return False
            else:
                clients = [client, test_client]
        else:
            clients = [client]
        start_balance = await clients[use_testnet].get_asset_balance(asset=quote)
        start_balance = start_balance['free']
        print(f'Opening balance = {start_balance}. ') # Save start balance
        save_to_records(start_balance, 'open')
        return clients

async def close_clients(clients): # Close clients
    for i in clients:
        await i.close_connection()
    
async def check_symbol(clients): # Check if specified pair is valid
    if clients == False:
        return False
    try:
        await clients[use_testnet].get_symbol_info(pair)
    except BinanceRequestException:
        print(pair + ' is an ivalid pair. ')
        return False
    return True

async def get_symbol_filters(clients): # Symbol info
    data = await clients[use_testnet].get_symbol_info(pair)
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
    return(my_filters)

async def get_historical_data(client):
    headings = ['Open Time', 'Open', 'High', 'Low', 'Close',
                'Volume', 'Close Time', 'Quote Asset Volume',
                'Number of Trades', 'Taker buy Base Asset Volume',
                'Taker buy Quote Asset Volume', 'Ignore']
    
    klines = np.array(await client.get_historical_klines(pair, AsyncClient.KLINE_INTERVAL_1MINUTE, '1 day ago UTC')).astype(np.double)
    df = pd.DataFrame.from_records(klines, columns=headings)
    df.drop(['Ignore'], axis=1, inplace=True)
    return df

def update_df(df, new_row):
    new_row = pd.Series(new_row, index=df.columns)
    if new_row[0] != df.iloc[-1, 0]:
        df = df.append(new_row, ignore_index=True)
    else:
        df.iloc[-1, :] = new_row
    return df

async def update_data(client, live_data, data_frame, finish):
    df = await get_historical_data(client)
    while finish.empty():
        new_row = await live_data.get()
        new_row = np.array(new_row).astype(np.double)
        df = update_df(df, new_row)
        await data_frame.put(df)
    return
    
async def my_signals(model, scaler, data_frame, signals, finish): # Sample strategy
    while finish.empty():
        df = await data_frame.get()
        last_price = df.iloc[-1, 4]
        if pair == 'BTCUSDT':
            input_data = df.iloc[-10:, :].to_numpy()
            predicted_price = model.predict(np.reshape(scaler.transform(input_data), (1, 10, 11))).squeeze()
            print(f'Predicton: {predicted_price}')
            print(f'Last price: {last_price}')
            if predicted_price >= (last_price * (1 + tp)):
                await signals.put(1)
            else:
                await signals.put(0)
        else:
            avg = df.iloc[-60:, 4].mean()
            if (avg - last_price) / last_price > (tp / 10):
                await signals.put(1)
            else:
                await signals.put(0)
    return
 
async def custom_signals(data_frame, signals, finish):
    while finish.empty():
        pass # Code a trading strategy in this function and pass the results into the signals queue
        # You can get data from data_frame with 'await data_frame.get()'
        # This will return a pandas dataframe with candle data from the past day
        # You can calculate indicators manually or use a library like ta
        # New data is passed every minute
        # After getting the data and determining whether to buy or sell you can
        # pass a 1 to signals to buy or a 0 to hold with 'await signals.put(0)'
    return

async def place_buy_order(clients, signals, price, sell_price, filters, finish):
    while finish.empty():
        s = await signals.get()
        if s == 1:                
            try:
                balance = await clients[use_testnet].get_asset_balance(asset=quote)
            except BinanceAPIException as e:
                print(e)
            else:
                current_price = await price.get()
                await price.put(current_price)
                balance = float(balance['free'])
                allocation = balance * trade_allocation
                quantity =  allocation / current_price
                if balance < filters['minNotional']:
                    print(f'Insufficient funds. ')
                else:
                    if allocation >= filters['minNotional']:
                        quantity =  allocation / current_price
                    else:
                        print(f'Minimum trade size is {filters["minNotional"]} {quote}. ')
                        quantity =  filters['minNotional'] / current_price
                    if quantity > filters['maxQty']:
                        quantity = filters['maxQty']
                    await buy(clients[use_testnet], quantity, filters, current_price, sell_price)
    return

async def buy(client, qty, filters, price, sell_price):
    if filters['stepSize'] == 0:
        qty = round_step_size(qty, filters['lotStepSize'])
    else:
        qty = round_step_size(qty, filters['stepSize'])
        
    try:
        order = await client.order_market_buy(
            symbol=pair,
            quantity=qty)
    except BinanceAPIException as e:
        print(e)
    else:
        await asyncio.sleep(0.2)
        try:
            trade_status = await client.get_order(symbol=pair, orderId=order['orderId'])
        except BinanceAPIException as ex:
            print(ex)
        else:
            if float(trade_status['executedQty']) == qty:
                save_trades('buy', qty, price)
                await sell_price.put({'stop-loss': (1 - sl) * price,
                                      'take-profit': (1 + tp) * price,
                                      'qty': qty})

async def place_sell_order(clients, open_positions, price, sell_price, filters, finish):
    sell_list = []
    while finish.empty():
        current_price = await price.get()
        if not sell_price.empty():
            position = await sell_price.get()
            sell_list = await open_positions.get()
            sell_list.append(position)
            await open_positions.put(sell_list)
        for s in sell_list:
            if current_price < s['stop-loss'] or current_price > s['take-profit']:
                await sell(clients[use_testnet], s['qty'], current_price)
                sell_list.remove(s)
                temp = await open_positions.get()
                await open_positions.put(sell_list)
    return

async def sell(client, qty, price):
    try:
        order = await client.order_market_sell(
            symbol=pair,
            quantity=qty)
    except BinanceAPIException as e:
        print(e)
    else:
        await asyncio.sleep(0.2)
        try:
            trade_status = await client.get_order(symbol=pair, orderId=order['orderId'])
        except BinanceAPIException as ex:
            print(ex)
        else:
            save_trades('sell', qty, price)

async def kline_data(client, data, price, finish): # Get live data
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
                print(res['c'])
    return

async def check_closing_time(finish):
    while time.time() % 86400 < close_time:
        await asyncio.sleep(60)
    await finish.put(True)

async def close_positions(clients, filters, open_positions):
    print('Closing positions. ')
    positions = await open_positions.get()
    data = await clients[use_testnet].get_symbol_ticker(symbol=pair)
    price = data['price']
    for i in positions:
        await sell(clients[use_testnet], i['qty'], price)
        
    try:
        closing_balance = await clients[use_testnet].get_asset_balance(asset=quote)
    except BinanceAPIException as e:
        print(e)
    else:
        closing_balance = float(closing_balance['free'])
        print(f'Closing balance = {closing_balance}. ')
        save_to_records(closing_balance, 'close')

def save_to_records(balance, trade_period):
    try:
        file = open(FILE_NAME, 'a')
        file.write(time.strftime('%c') + '\n')
        if trade_period == 'open':
            file.write(f'Opening balance: {balance}. \n')
        elif trade_period == 'close':
            file.write(f'Closing balance: {balance}. \n\n')
    finally:
        file.close()
    
def save_trades(trade_type, qty, price):
    try:
        file = open(FILE_NAME, 'a')
        file.write(time.strftime('%c') + '\n')
        if trade_type == 'buy':
            file.write(f'Bought {qty} {base} at {price} {quote} per {base}. \n')
            print(f'Bought {qty} {base} at {price} {quote} per {base}. ')
        elif trade_type == 'sell':
            file.write(f'Sold {qty} {base} at {price} {quote} per {base}. \n')
            print(f'Sold {qty} {base} at {price} {quote} per {base}. ')
    finally:
        file.close()
    
async def trader(clients, filters, open_positions):
    scaler = joblib.load('X_scaler.pkl')
    model = tf.keras.models.load_model('Checkpoints/cp-40+58-160.5325-18-21-08-06-08-2021.hdf5') # AI model

    print(time.asctime())
    
    price = asyncio.LifoQueue()
    data = asyncio.Queue()
    data_frame = asyncio.Queue()
    signals = asyncio.Queue()
    sell_price = asyncio.Queue()
    finish = asyncio.Queue()
    await open_positions.put([])

    await asyncio.gather(check_closing_time(finish),
                         kline_data(clients[0], data, price, finish),
                         update_data(clients[0], data, data_frame, finish),
                         # custom_signals(data_frame, signals, finish), # Remove the hash at the start of the line to implement your strategy
                         my_signals(model, scaler, data_frame, signals, finish), # Comment out this line
                         place_buy_order(clients, signals, price, sell_price, filters, finish),
                         place_sell_order(clients, open_positions, price, sell_price, filters, finish))
    return

if __name__ == '__main__':
    # nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    clients = loop.run_until_complete(create_clients())
    
    loop = asyncio.get_event_loop()
    if loop.run_until_complete(check_symbol(clients)):
        try:
            loop = asyncio.get_event_loop()
            filters = loop.run_until_complete(get_symbol_filters(clients))

            open_positions = asyncio.Queue()
            
            loop = asyncio.get_event_loop()
            loop.run_until_complete(trader(clients, filters, open_positions))
        except KeyboardInterrupt: # Use (ctrl + c) to end the program early
            pass
    loop = asyncio.get_event_loop()
    loop.run_until_complete(close_positions(clients, filters, open_positions))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(close_clients(clients))
        
