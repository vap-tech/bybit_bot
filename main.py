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


def buy(qty=10.1):

    if qty < 10.1:
        qty = 10.1

    count = 10
    while True:

        try:
            response = session.place_order(
                category="spot",
                symbol="BTCUSDC",
                side="Buy",
                orderType="Market",
                qty=qty
            )
            if response['retMsg'] == 'OK' or count <= 0:
                break

        except Exception as e:
            response = e
            sleep(1)
            count -= 1
            if count <= 0:
                break

    return response


def sell(qty=0.000199):

    if qty < 0.000199:
        qty = 0.000199

    count = 10

    while True:

        try:
            response = session.place_order(
                category="spot",
                symbol="BTCUSDC",
                side="Sell",
                orderType="Market",
                qty=qty
            )
            if response['retMsg'] == 'OK' or count <= 0:
                break

        except Exception as e:
            response = e
            sleep(1)
            count -= 1
            if count <= 0:
                break

    return response


set_old_price(r.get('price'))
r.set(name='diff', value=300)


while True:

    difference = float(r.get('diff'))
    old_price = float(r.get('old_price'))
    new_price = float(r.get('price'))

    if new_price - old_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'S', end=' ')
        print(sell())
        print(f'price: {new_price}')
        set_old_price(new_price)
        continue

    if old_price - new_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'B', end=' ')
        print(buy())
        print(f'price: {new_price}')
        set_old_price(new_price)

    sleep(1)
