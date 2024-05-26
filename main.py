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


def set_qty_btc():
    btc = float(get_balance('BTC'))
    btc = float('{:.6f}'.format(btc))
    if btc > 0.000725:
        _btc = 0.000724
    elif btc < 0.000199:
        _btc = 0.000199
    else:
        _btc = btc
    r.set('qty_btc', _btc)


def set_qty_usdc():
    usdc = float(get_balance('USDC'))
    usdc = float('{:.6f}'.format(usdc))
    if usdc > 50:
        _usdc = 50
    elif usdc < 10.1:
        _usdc = 10.1
    else:
        _usdc = usdc

    r.set('qty_usdc', _usdc)


def buy(qty=10.1):

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


def sell(qty=0.000199):

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
set_qty_btc()
set_qty_usdc()
r.set(name='no_buy', value=0)
r.set(name='no_sell', value=0)
r.set(name='diff', value=50)


while True:

    difference = float(r.get('diff'))
    old_price = float(r.get('old_price'))
    new_price = float(r.get('price'))

    if new_price - old_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'B')
        print(buy(float(r.get('qty_usdc'))))
        print(f'price: {new_price}')
        print()
        set_old_price(new_price)
        set_qty_usdc()
        continue

    if old_price - new_price > difference:

        print(datetime.now().strftime("%H:%M:%S"), 'S')
        print(sell(int(r.get('qty_btc'))))
        print(f'price: {new_price}')
        print()
        set_qty_btc()
        set_old_price(new_price)

    sleep(1)
