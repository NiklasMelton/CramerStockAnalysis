import numpy as np
import yfinance as yf
import pickle
def load_ticker_data(TCKRS):
    TCKRS = ' '.join([tckr for tckr in TCKRS if '.' not in tckr])
    print(TCKRS)
    return yf.Tickers(TCKRS)

def load_close_data(tickers):
    ticker_data = load_ticker_data(tickers)
    data = dict()
    for tckr in tickers:
        if '.' not in tckr:
            try:
                tckr_data = getattr(ticker_data.tickers,tckr).history(period='max')
                if not tckr_data.empty:
                    data[tckr] = tckr_data
            except Exception as E:
                print(E)
    data = filter_close_data(data)
    return data

def filter_close_data(data):
    for tckr in data:
        data[tckr].reset_index(inplace = True)
        data[tckr] = {'Date': data[tckr]['Date'].to_numpy(), 'Close': data[tckr]['Close'].to_numpy()}
    return data

def format_date(date):
    parts = date.split('/')
    return '{}-{}-{}'.format(parts[-1].strip(),parts[0].strip(),parts[1].strip())


if __name__ == '__main__':

    cramer_picks = dict()
    cramer_lines = list(open('buyStocksCramerFormatted.txt','r').readlines())[9:]
    cramer_lines.reverse()
    for line in cramer_lines:
        sline = line.split(',')
        if len(sline) > 2:
            ticker = sline[0][1:]
            date = sline[1]
            if ticker not in cramer_picks:
                cramer_picks[ticker] = date

    # close_data = load_close_data(list(cramer_picks.keys()))
    # pickle.dump(close_data,open('CramerData.pckl','wb'))
    close_data = pickle.load(open('CramerData.pckl','rb'))
    average_gain_to_date = 0
    average_gain_to_max = 0
    average_days_to_max = 0
    i = 0

    worst_pick = None
    worst_profit = np.inf

    best_pick = None
    best_profit = -np.inf

    uticks = set()

    for ticker,date in cramer_picks.items():
        if ticker in close_data:
            try:
                ticker_data = close_data[ticker]
                fdate = format_date(date)
                idx_buy = [fdate in str(d) for d in ticker_data['Date']].index(True)
                buy_price = ticker_data['Close'][idx_buy]
                max_idx = np.argmax(ticker_data['Close'][idx_buy:])
                max_price = ticker_data['Close'][max_idx]
                last_price = ticker_data['Close'][-1]

                profit_to_date = (last_price-buy_price)/buy_price
                max_profit = (max_price-buy_price)/buy_price
                days_to_max = max_idx-idx_buy

                if profit_to_date < worst_profit:
                    worst_profit = profit_to_date
                    worst_pick = ticker
                if profit_to_date > best_profit:
                    best_profit = profit_to_date
                    best_pick = ticker

                average_days_to_max += days_to_max
                average_gain_to_date += profit_to_date
                average_gain_to_max += max_profit
                i += 1
                uticks.add(ticker)
            except Exception as E:
                print(E)



    average_days_to_max /= i
    average_gain_to_date /= i
    average_gain_to_max /= i

    print(i,len(uticks))
    print('Average Profit to Date:',average_gain_to_date)
    print('Average Max Profit:',average_gain_to_max)
    print('Average Days to Max Profit:',average_days_to_max)
    print('Worst Pick:',worst_pick,'with profit:',worst_profit)
    print('Best Pick:',best_pick,'with profit:',best_profit)



