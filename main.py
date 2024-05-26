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


def buy(qty=100.8384):

    r.set(name='no_sell', value=0)

    if r.get(name='no_buy') == '1':
        return 'no_buy'

    if qty < 10.1:
        qty = 10.1

    response = 'error 3'
    count = 2

    while count:

        try:
            response = session.place_order(
                category="spot",
                symbol="BTCUSDC",
                side="Buy",
                orderType="Market",
                qty=qty
            )
            if response['retMsg'] == 'OK':
                break

        except Exception as e:
            response = e
            sleep(1)
            count -= 1
            if count <= 0:
                break

    if 'Insufficient balance' in str(response):
        r.set(name='no_buy', value=1)

    return response


def sell(qty=0.001460):

    r.set(name='no_buy', value=0)

    if r.get(name='no_sell') == '1':
        return 'no_sell'

    if qty < 0.000199:
        qty = 0.000199

    response = 'error 3'
    count = 2

    while count:

        try:
            response = session.place_order(
                category="spot",
                symbol="BTCUSDC",
                side="Sell",
                orderType="Market",
                qty=qty
            )
            if response['retMsg'] == 'OK':
                break

        except Exception as e:
            response = e
            sleep(1)
            count -= 1
            if count <= 0:
                break

    if 'Insufficient balance' in str(response):
        r.set(name='no_sell', value=1)

    return response


set_old_price(r.get('price'))
r.set(name='no_buy', value=0)
r.set(name='no_sell', value=0)
r.set(name='diff', value=50)


while True:

    difference = float(r.get('diff'))
    old_price = float(r.get('old_price'))
    new_price = float(r.get('price'))

    if new_price - old_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'B')
        print(buy())
        print(f'price: {new_price}')
        print()
        set_old_price(new_price)
        continue

    if old_price - new_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'S')
        print(sell())
        print(f'price: {new_price}')
        print()
        set_old_price(new_price)

    sleep(1)
