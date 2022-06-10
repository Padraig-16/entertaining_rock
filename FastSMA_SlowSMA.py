# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:31:00 2022

@author: Darren
"""
from keys import keys
import argparse
from binance import Client
import pandas as pd

def tech_analysis(df):
    df['FastSMA'] = df.Close.rolling(5).mean()
    df['SlowSMA'] = df.Close.rolling(75).mean()

def main(Investment):
    
    try:
        client = Client(keys[0],keys[1])
    except:
        print("Issue importing binance keys, format should be keys= [key,secret]\
                  in a .py file labels keys")
    try:
        posframe = pd.read_csv('positioncheck')
    except:
        print("Error importing positions csv file")
    def data_retriever(symbol):
        dataframe =  pd.DataFrame(client.get_historical_klines(symbol, '1h','75 hours ago UTC'))
        dataframe.columns = ['Time', 'Close']
        dataframe.Close = dataframe.Close.astype(float)
        dataframe.Time = pd.to_datetime(dataframe.Time, unit ='ms')
        return dataframe
    
    def change_position(coin, order, buy = True):
        if buy:
            posframe.loc[posframe.Currency == coin, 'position']=1
            posframe.loc[posframe.Currency == coin, 'quantity']=float(order['executed'])
        else:
            posframe.loc[posframe.Currency == coin, 'position']=0
            posframe.loc[posframe.Currency == coin, 'quantity']=0
            
    def trading(Investment):
        for coin in posframe[posframe.position ==1].Currency:
            df = data_retriever(coin)
            tech_analysis(df)
            lastrow = df.iloc[-1]
            
            if lastrow.SlowSMA > lastrow.FastSMA:
                order = client.create_order(symbol = coin, 
                                            side = 'SELL', 
                                            type = 'MARKET',quantity = 
                                            posframe[posframe.Currency == coin].quantity.values[0])
                change_position(coin, order,buy=False)
                print(order)
                
        for coin in posframe[posframe.position ==0].Currency:
            df = data_retriever(coin)
            tech_analysis(df)
            lastrow = df.iloc[-1]
            if lastrow.FastSMA > lastrow.SlowSMA:
                order = client.create_order(symbol = coin, 
                                            side = 'BUY', 
                                            type = 'MARKET',
                                            quoteOrderQty = Investment)
                print(order)
                change_position(coin, order, buy=True)
            else:
                print(f'Failed to buy {coin}  an error has occured.')
    while True:
        try:
            trading(Investment)
        except:
            continue
if __name__ == '__main__':
    print("Trading using a Fast and Slow moving average algorithm.")
    parser = argparse.ArgumentParser()
    parser.add_argument('-Investment',type=float, required = False, default = 100,help = 
                        "Investment amount in USDT")

    args = parser.parse_args()
    main(args.Investment)