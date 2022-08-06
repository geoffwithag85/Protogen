# This code is an exercise in creating a websocket connection to stream data, 
# and then to manipulate the data accordingly.

import numpy as np 
import pprint, websocket, json, time
import dateutil.parser
import plotly.graph_objects as go 
import pandas as pd 
import config


minutes_processed = {}
minute_candlesticks = []
current_tick = None 
previous_tick = None

def on_open(ws):
    print("Connection Open")
    time.sleep(1)
    ws.send(json.dumps(ws.sub_msg))
    ws.msg_count = 0
    
def on_close(ws):
    print("Connection Closed")
    print(ws.msg_count, " messages received")

def on_message(ws, message):
    global current_tick, previous_tick
    
    json_message = json.loads(message)
    previous_tick = current_tick
    current_tick = json_message

    print("=== Recieved Tick ===")
    print("{} @ {}".format(current_tick['time'], current_tick['price']))

    tick_datetime_object = dateutil.parser.parse(current_tick['time'])
    tick_dt = tick_datetime_object.strftime("%m/%d/%Y %H:%M")
    print(tick_dt)

    if not tick_dt in minutes_processed:
        print("starting new candlestick")
        minutes_processed[tick_dt] = True 
        print(minutes_processed) 

        if len(minute_candlesticks) > 0:
            minute_candlesticks[-1]['close'] = previous_tick['price']

        if len(minute_candlesticks) > 1:
            df = pd.DataFrame.from_dict(minute_candlesticks)
            candlestick = go.Candlestick(x=df['minute'],
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'])
            figure = go.Figure(data=[candlestick])
            #figure.show()
            figure.update_layout(
                title = '1m candles real time coinbase websocket stream',
                yaxis_title = 'BTC-USD Price ($USD)'
                )
            figure.write_html('candles.html', auto_open=False)

                    
        minute_candlesticks.append({
            "minute": tick_dt,
            "open": current_tick['price'],
            "high": current_tick['price'],
            "low": current_tick['price']
        })

    if len(minute_candlesticks) > 0:
        current_candlestick = minute_candlesticks[-1]
        if current_tick['price'] > current_candlestick['high']:
            current_candlestick['high'] = current_tick['price']
            
        if current_tick['price'] < current_candlestick['low']:
            current_candlestick['low'] = current_tick['price']
            

        print("=== Candlesticks ===")
        for candlestick in minute_candlesticks:
            print(candlestick)

    #print("Message Recieved")
    #pprint.pprint(json_message)
    
    ws.msg_count += 1


def on_error(ws, error):
    print(error)



websocket.enableTrace = True
ws = websocket.WebSocketApp(config.SOCKET, on_open=on_open, 
                                    on_close=on_close, 
                                    on_message=on_message, 
                                    on_error=on_error)

ws.sub_msg = {
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channels": ["matches"]
        }

ws.run_forever(ping_interval=30)





    #    if flag==1 & (len(minute_candlesticks) > 1):
    #         minss = current_candlestick['minute']
    #         mins.append(minss)
    #         oss = current_candlestick['open']
    #         os.append(float(oss))
    #         hss = current_candlestick['high']
    #         hs.append(float(hss))
    #         lss = current_candlestick['low']
    #         ls.append(float(lss))
    #         css = current_candlestick['close']
    #         cs.append(float(css))
    #         fig = go.Figure(data=[go.Candlestick(x=mins,
    #                         open=os,
    #                         high=hs,
    #                         low=ls,
    #                         close=cs)])

    #         fig.show()
    #         flag=0