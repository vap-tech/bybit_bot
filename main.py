import redis
from time import sleep
from datetime import datetime

from pybit.unified_trading import HTTP
from pybit.unified_trading import WebSocket

from config import API_KEY, API_SECRET

ws = WebSocket(
    testnet=False,
    channel_type="spot",
)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

session = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)


def handle_message(message):
    r.set(name='price', value=message['data']['lastPrice'])


ws.ticker_stream(
    symbol="BTCUSDC",
    callback=handle_message
)


def buy():
    try:
        response = session.place_order(
            category="spot",
            symbol="BTCUSDC",
            side="Buy",
            orderType="Market",
            qty="10"
        )
    except Exception as e:
        response = e

    return response


def sell():
    try:
        response = session.place_order(
            category="spot",
            symbol="BTCUSDC",
            side="Sell",
            orderType="Market",
            qty="0.000208"
        )
    except Exception as e:
        response = e

    return response


old_price = float(r.get('price'))


difference = 230
stop_loss = 40

while 1:

    sleep(1)

    new_price = float(r.get('price'))
    if new_price > old_price:

        if new_price - old_price > difference:
            stop_price = new_price
            while 1:
                price = float(r.get('price'))
                if price > stop_price:
                    stop_price = price
                    continue
                if price < stop_price:
                    if stop_price - price >= stop_loss:
                        old_price = price
                        break

            print(datetime.now().strftime("%H:%M:%S"), end=' ')
            print(sell())
            continue

    elif new_price < old_price:

        if old_price - new_price > difference:

            stop_price = new_price
            while 1:
                price = float(r.get('price'))
                if price < stop_price:
                    stop_price = price
                    continue
                if price > stop_price:
                    if price - stop_price >= stop_loss:
                        old_price = price
                        break

            print(datetime.now().strftime("%H:%M:%S"), end=' ')
            print(buy())
            continue
