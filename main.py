import time
from datetime import datetime

from pybit.unified_trading import HTTP

from config import API_KEY, API_SECRET


session = HTTP(
    testnet=False,
    api_key=API_KEY,
    api_secret=API_SECRET,
)


def buy():
    try:
        response = session.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="Buy",
            orderType="Market",
            qty="5"
        )
    except Exception as e:
        response = e

    return response


def sell():
    try:
        response = session.place_order(
            category="spot",
            symbol="BTCUSDT",
            side="Sell",
            orderType="Market",
            qty="0.0001"
        )
    except Exception as e:
        response = e

    return response


def get_balance():
    response = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="RVN",
    )

    return response


def get_tickers():
    response = session.get_tickers(
        category="spot",
        symbol="BTCUSDT",
    )

    return response


old_price = float(get_tickers()['result']['list'][0]['lastPrice'])

percent = 0.5
i = 2 * 60 * 24

while i:
    time.sleep(30)

    difference = old_price / 100 * percent
    new_price = float(get_tickers()['result']['list'][0]['lastPrice'])
    if new_price > old_price:

        if new_price - old_price > difference:
            old_price = new_price
            print(datetime.now().strftime("%H:%M:%S"), end=' ')
            print(sell())
            continue

    elif new_price < old_price:

        if old_price - new_price > difference:
            old_price = new_price
            print(datetime.now().strftime("%H:%M:%S"), end=' ')
            print(buy())
            continue

    i -= 1


print()
print('завершено корректно')
