import ccxt
import config
from datetime import datetime
import pandas as pd  


exchange = ccxt.binanceus({
    'apiKey': config.API_KEY,
    'secret': config.API_SECRET,
    'enableRateLimit': True,
    'timeout': 30000
})


portfolio = {}


deposits = exchange.fetch_deposits()
deposits_df = pd.DataFrame.from_dict(deposits)[['datetime', 'currency', 'amount']]
# print(deposits_df)
# currencies = deposits_df.currency.unique()

# total_deposit = {}
# for currency in currencies:
#     total_deposit.update({currency: {'deposits': sum(deposits_df.amount[deposits_df.currency == currency])}})
# total_deposit_df = pd.DataFrame.from_dict(total_deposit).transpose()
# print(total_deposit_df)




orders = exchange.fetch_orders()
orders_df = pd.DataFrame.from_dict(orders)[['datetime', 'side', 'symbol', 'type', 'amount', 'price', 'cost', 'fee']]
# print(orders_df.fee[1]['cost'])
symbols = orders_df.symbol.unique()
# print(orders_df[orders_df.symbol=='BTC/USD'].fee[0]['cost'])
total_costs = {}
for symbol in symbols:
    buys = orders_df[orders_df.side == 'buy']
    sells = orders_df[orders_df.side == 'sell']
    # print(buys)
    cost = sum(buys.cost[buys.symbol == symbol]) - sum(sells.cost[sells.symbol == symbol])
    # fees = sum(orders_df[orders_df.symbol==symbol].fee['cost'])
    fees=0
    for f in orders_df.fee[orders_df.symbol == symbol]:
        fees += f['cost']
        
        
    total_costs.update({symbol: {"costs": cost, "fees": fees}})

total_costs_df = pd.DataFrame.from_dict(total_costs).transpose()
# print(total_costs_df)


balances = exchange.fetch_balance()['info']
total_value = 0
total_cost = 0
total_fees = 0
for balance in balances:
    bal = float(balance['balance'])
    sym = balance['currency']
    deposits = sum(deposits_df.amount[deposits_df.currency == sym])
    if bal > 0:
        
        if not sym =='USD':
            
            price = float(exchange.fetch_ticker(symbol=sym + '/USD')['info']['price'])
            value = price * bal
            
            cost = total_costs[sym+'/USD']['costs']
            fees = total_costs[sym+'/USD']['fees']
            
            avg_purchase_price = cost / bal
            break_even_price = (cost+fees) / bal
            gains = value - cost
            percent_gains = gains / cost * 100
            
            

            portfolio.update({sym: {"Balance": bal, 
                                    "Deposits": deposits,
                                    "Price": price,
                                    "Avg. Price": avg_purchase_price,
                                    "Break-Even Price": break_even_price,
                                    "Value": value, 
                                    "Cost": cost,  
                                    "Fees Paid": fees,                                  
                                    "Gains/Losses": gains,
                                    "% Gains": percent_gains}})
            total_cost += float(portfolio[sym]['Cost'])
            total_fees += float(portfolio[sym]['Fees Paid'])
            total_value += portfolio[sym]['Value']
        else:
            price = ''
            purchase_price = ''
            value = bal
            cost = ''
            fees = ''
            gains = ''
            percent_gains = ''
            portfolio.update({sym: {"Balance": bal, 
                                    "Deposits": deposits,
                                    "Price": price,
                                    "Avg. Price": '',
                                    "Break-Even Price": '', 
                                    "Value": value, 
                                    "Cost": cost,
                                    "Fees Paid": fees,                                    
                                    "Gains/Losses": gains,
                                    "% Gains": percent_gains}})

        
total_deposit_usd = sum(deposits_df.amount[deposits_df.currency == 'USD'])  
total_gains = (total_value + portfolio['USD']['Value']) - total_deposit_usd
total_percent_gains = total_gains / total_deposit_usd * 100

portfolio.update({'Total (USD)': {"Balance": '', 
                            "Deposits": total_deposit_usd,
                            "Price": '', 
                            "Value": total_value + portfolio['USD']['Value'], 
                            "Cost": total_cost,
                            "Fees Paid": total_fees,
                            "Break-Even Price": '',
                            "Avg. Price": '',
                            "Gains/Losses": total_gains,
                            "% Gains": total_percent_gains}})
portfolio_df = pd.DataFrame.from_dict(portfolio).transpose()
# print(portfolio_df[portfolio_df.index == 'LTC'])
print(portfolio_df)


# portfolio = pd.DataFrame(balances_df['Balance'], total_deposit_df['Total Deposits'])
# print(portfolio)



