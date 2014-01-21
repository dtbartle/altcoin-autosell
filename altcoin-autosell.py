#!/usr/bin/python

import coinex_api
import ConfigParser
import exchange_api
import os
import sys
import time

def _GetExchangeInfo(exchange, target_currency):
    currencies = exchange.GetCurrencies()
    if target_currency not in currencies:
        print '%s does not list %s, disabling.' % (exchange.GetName(), target_currency)
        return (None, None)
    inverted_currencies = {currency_id : currency_name for
                           currency_name, currency_id in currencies.items()}

    target_currency_id = currencies[target_currency]
    markets = {}
    for ((source_id, target_id), market_id) in exchange.GetMarkets().items():
        if target_id == target_currency_id:
            markets[source_id] = market_id

    print 'Monitoring %s.' % exchange.GetName()
    return (target_currency_id, inverted_currencies, markets)


config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/.altcoin-autosell.config'))

target_currency = (config.get('General', 'target_currency') if
                   config.has_option('General', 'target_currency') else 'BTC')
sleep_seconds = (config.getint('General', 'sleep_seconds') if
                 config.has_option('General', 'sleep_seconds') else 60)

exchanges = []

if config.has_section('CoinEx'):
    if not config.has_option('CoinEx', 'api_key'):
        raise ValueError('Missing CoinEx.api_key')
    if not config.has_option('CoinEx', 'api_secret'):
        raise ValueError('Missing CoinEx.api_secret')
    exchange = coinex_api.CoinEx(config.get('CoinEx', 'api_key'),
                                 config.get('CoinEx', 'api_secret'))

    (target_currency_id, currencies, markets) = _GetExchangeInfo(exchange, target_currency)
    if target_currency_id is not None:
        exchanges.append((exchange, target_currency_id, currencies, markets))

if not exchanges:
    print 'No exchange sections defined!'
    sys.exit(1)

while True:
    for (exchange, target_currency_id, currencies, markets) in exchanges:
        try:
            balances = exchange.GetBalances()
        except exchange_api.ExchangeException as e:
            print 'Failed to get %s balances: %s' % (exchange.GetName(), e)
            continue

        for (currency_id, balance) in balances.items():
            if currency_id == target_currency_id or balance == 0:
                continue
            currency_name = (currencies[currency_id] if
                             currency_id in currencies else currency_id)
            if currency_id not in markets:
                print 'Could not find market for %s on %s.' % (currency_name, exchange.GetName())
                continue

            try:
                order_id = exchange.CreateOrder(markets[currency_id], balance, bid=False)
            except exchange_api.ExchangeException as e:
                print ('Failed to create sell order for %s %s on %s: %s' %
                       (balance, currency_name, exchange.GetName(), e))
            else:
                print ('Created sell order %s for %s %s on %s.' %
                       (order_id, balance, currency_name, exchange.GetName()))
    time.sleep(sleep_seconds)
