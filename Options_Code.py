import os
import sys
import time
import yfinance as yf
import pandas as pd

pd.set_option('display.max_columns', 20)
start_time = time.time()

#import csv file of stonk tickers
stockTickers = pd.read_csv('stonktickers.csv')
df = pd.DataFrame({'Ticker':[], 'Stock Price': []})
finaldf = pd.DataFrame({'Ticker':[], 'Stock Price': [], 'Strike': [],'Expiration Date': [], 'Option Cost': [], 'Profit Yield': []})


#prompt user to enter stock $ range
min_stockPrice = float(input("Enter a minimum stock price: "))
max_stockPrice = float(input("Enter a maximum stock price: "))
#prompt user to enter expiration date fro option
oldExpDate = input("Enter an option expiration date (yyyy-mm-dd): ")
newExpDate = ''
#prompt user to enter % for $ swing
pctSwing = float(input("Enter the desired swing %: "))


#download = yf.download(stockTickers, period="1d", threads=4)

#generate stock $ and append to dataframe
for index, row in stockTickers.iterrows():
        try:
            data = yf.Ticker(row[0]).history("1d")
            data2 = data['Close'].tolist()
            data3 = data2.pop()
            if float(data3) >= min_stockPrice and float(data3) <= max_stockPrice:
                df = df.append({'Ticker': row[0],'Stock Price': data3}, ignore_index=True)
        except Exception:
            pass


def callOptions():
    tempdf = pd.DataFrame({'Strike': [],'Expiration Date': [], 'Option Cost': [], 'Profit Yield': []})
    for index, row in df.iterrows():
        try:
            tick = yf.Ticker(df.at[index, 'Ticker']).option_chain(expirationDateCheck(df.at[index, 'Ticker'], oldExpDate)).calls
            for i, r in tick.iterrows():
                if ((tick.at[i, 'strike'] - df.at[index, 'Stock Price']) > 0) and (((tick.at[i, 'strike'] - df.at[index, 'Stock Price']) / df.at[
                    index, 'Stock Price']) * 100) >= pctSwing:
                    profitYield = ((tick.at[i, 'lastPrice'] / df.at[index, 'Stock Price']) * 100)
                    tempdf = tempdf.append({'Strike': tick.at[i, 'strike'], 'Expiration Date': newExpDate,
                                            'Option Cost': tick.at[i, 'lastPrice'], 'Profit Yield': profitYield},
                                           ignore_index=True)
                    print(tick.at[i, 'strike'])
                    break
        except Exception:
            tempdf = tempdf.append({'Strike': 'N/A', 'Expiration Date': 'N/A', 'Option Cost': 'N/A', 'Profit Yield': 'N/A'}, ignore_index=True)
    global finaldf
    finaldf = pd.concat([df, tempdf], axis=1)



def expirationDateCheck(ticker, date):
    try:
        yf.Ticker(ticker).option_chain(date)
        global newExpDate
        newExpDate = oldExpDate
        return newExpDate
    except:
         newExpDate = yf.Ticker(ticker).options[0]
         return newExpDate



callOptions()
finaldf.to_csv(r'/Users/edy/Desktop/Python Code/stonkData.csv')
print("---%s seconds ---" % (time.time() - start_time))





