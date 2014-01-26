#!/usr/bin/python

import coinex_api
import ConfigParser
import cryptsy_api
import exchange_api
import os
import sys
import time

def _LoadExchangeConfig(config, target_currency, exchange_class, *keys):
    if not config.has_section(exchange_class.name):
        return None

    args = {}
    for key in keys:
        if not config.has_option(exchange_class.name, key):
            raise ValueError('Missing %s.%s.' % (exchange_class.name, key))
        args[key] = config.get(exchange_class.name, key)

    exchange = exchange_class(**args)

    try:
        currencies = exchange.GetCurrencies()
        if target_currency not in currencies:
            print '%s does not list %s, disabling.' % (exchange.name, target_currency)
            return None
        inverted_currencies = {currency_id : currency_name for
                               currency_name, currency_id in currencies.items()}
    except exchange_api.ExchangeException as e:
        print 'Failed to get %s currencies, disabling: %s' % (exchange.name, e)
        return None

    try:
        target_currency_id = currencies[target_currency]
        markets = {}
        for market in exchange.GetMarkets():
            if market.target_currency_id == target_currency_id:
                markets[market.source_currency_id] = market
    except exchange_api.ExchangeException as e:
        print 'Failed to get %s markets, disabling: %s' % (exchange_name, e)
        return None

    print 'Monitoring %s.' % exchange.name
    return (exchange, target_currency_id, inverted_currencies, markets)

config = ConfigParser.RawConfigParser()
config.read(os.path.expanduser('~/.altcoin-autosell.config'))

target_currency = (config.get('General', 'target_currency') if
                   config.has_option('General', 'target_currency') else 'BTC')
poll_delay = (config.getint('General', 'poll_delay') if
              config.has_option('General', 'poll_delay') else 60)
request_delay = (config.getint('General', 'request_delay') if
                 config.has_option('General', 'request_delay') else 1)

exchanges = [_LoadExchangeConfig(config, target_currency, coinex_api.CoinEx,
                                 'api_key', 'api_secret'),
             _LoadExchangeConfig(config, target_currency, cryptsy_api.Cryptsy,
                                 'api_private_key', 'api_public_key')]
exchanges = [exchange for exchange in exchanges if exchange is not None]
if not exchanges:
    print 'No exchange sections defined!'
    sys.exit(1)

while True:
    for (exchange, target_currency_id, currencies, markets) in exchanges:
        try:
            balances = exchange.GetBalances()
        except exchange_api.ExchangeException as e:
            print 'Failed to get %s balances: %s' % (exchange.name, e)
            continue

        for (currency_id, balance) in balances.items():
            if (currency_id == target_currency_id or currency_id not in markets or
                balance < markets[currency_id].trade_minimum):
                continue

            currency_name = (currencies[currency_id] if
                             currency_id in currencies else currency_id)
            try:
                time.sleep(request_delay)
                order_id = exchange.CreateOrder(markets[currency_id].market_id, balance, bid=False)
            except exchange_api.ExchangeException as e:
                print ('Failed to create sell order for %s %s on %s: %s' %
                       (balance, currency_name, exchange.name, e))
            else:
                print ('Created sell order %s for %s %s on %s.' %
                       (order_id, balance, currency_name, exchange.name))
    time.sleep(poll_delay)
