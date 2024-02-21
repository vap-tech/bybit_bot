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
        return

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
        return

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


def get_balance(coin='BTC'):

    count = 10

    while True:

        try:
            response = session.get_wallet_balance(
                accountType="UNIFIED",
                coin=coin,
            )
            if response['retMsg'] == 'OK' or count <= 0:
                break

        except Exception as e:
            print(e)
            sleep(1)
            count -= 1
            if count <= 0:
                return '0'

    return response['result']['list'][0]['coin'][0]['equity']


def get_qty_to_trade() -> dict:
    btc = float(get_balance('BTC'))
    usdc = float(get_balance('USDC'))
    return {'BTC': btc, 'USDC': usdc}


def set_qty_to_trade(qty_to_trade: dict) -> None:

    btc = qty_to_trade['BTC'] / 5
    if btc < 0.000199:
        btc = 0.000199
    r.set('qty_btc', btc)

    usdc = qty_to_trade['USDC'] / 5
    if usdc < 10.1:
        usdc = 10.1
    r.set('qty_usdc', usdc)


set_old_price(r.get('price'))
r.set(name='diff', value=500)
set_qty_to_trade(get_qty_to_trade())

while True:

    difference = float(r.get('diff'))
    old_price = float(r.get('old_price'))
    new_price = float(r.get('price'))
    qty_btc = float(r.get('qty_btc'))
    qty_usdc = float(r.get('qty_usdc'))

    if new_price - old_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'S', end=' ')
        sell(qty_btc)
        print(f'qty_btc: {qty_btc}, price: {new_price}')
        set_old_price(new_price)
        continue

    if old_price - new_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'B', end=' ')
        buy(qty_usdc)
        print(f'qty_usdc: {qty_usdc}, price: {new_price}')
        set_old_price(new_price)

    set_qty_to_trade(get_qty_to_trade())
    sleep(1)
