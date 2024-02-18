import redis
from time import sleep
from datetime import datetime

from pybit.unified_trading import HTTP
from pybit.unified_trading import WebSocket

from config import API_KEY, API_SECRET

r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

ws = WebSocket(
    testnet=False,
    channel_type="spot",
)

session = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)


def set_old_price(_price):
    r.set(name='old_price', value=_price)


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
            qty="15"
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
            qty="0.000308"
        )
    except Exception as e:
        response = e

    return response


set_old_price(r.get('price'))
r.set(name='diff', value=200)


while True:

    difference = float(r.get('diff'))
    old_price = float(r.get('old_price'))
    new_price = float(r.get('price'))

    if new_price - old_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'S', end=' ')
        print(sell())
        set_old_price(new_price)
        continue

    if old_price - new_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'B', end=' ')
        print(buy())
        set_old_price(new_price)

    sleep(1)
