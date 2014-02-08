#!/usr/bin/python

import argparse
import coinex_api
try:
    import configparser
except ImportError:
    # Python 2.7 compatbility
    import ConfigParser
    configparser = ConfigParser
import cryptsy_api
import exchange_api
import os
import sys
import time

def _Log(message, *args):
    print('%s: %s' % (time.strftime('%c'), message % args))

def _LoadExchangeConfig(config, target_currencies, exchange_class, *keys):
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
        target_currency_ids = []
        for target_currency in target_currencies:
            currency_ids = [currency_id for currency_id, currency_name in
                            currencies.items() if currency_name == target_currency]
            if currency_ids:
                target_currency_ids += currency_ids
            else:
                _Log('%s does not list %s, ignoring.', exchange.name, target_currency)
        if not target_currency_ids:
            return None
    except exchange_api.ExchangeException as e:
        _Log('Failed to get %s currencies, disabling: %s', exchange.name, e)
        return None

    try:
        markets = exchange.GetMarkets()
        target_markets = [(target_currency_id, {market.source_currency_id : market for
                                                market in markets if
                                                market.target_currency_id == target_currency_id}) for
                          target_currency_id in target_currency_ids]
    except exchange_api.ExchangeException as e:
        _Log('Failed to get %s markets, disabling: %s', exchange_name, e)
        return None

    _Log('Monitoring %s.', exchange.name)
    return (exchange, currencies, target_markets)


parser = argparse.ArgumentParser(description='Script to auto-sell altcoins.')
parser.add_argument('-c', '--config', dest='config_path', default='~/.altcoin-autosell.config',
                    help='path to the configuration file')
args = parser.parse_args()

config = configparser.RawConfigParser()
config_path = os.path.expanduser(args.config_path)
_Log('Using config from "%s".', config_path)
config.read(config_path)

target_currencies = ([target_currency.strip() for target_currency in
                      config.get('General', 'target_currencies').split(',')] if
                     config.has_option('General', 'target_currencies') else
                     ['BTC', 'LTC'])
_Log('Selling to %s.', target_currencies)
poll_delay = (config.getint('General', 'poll_delay') if
              config.has_option('General', 'poll_delay') else 60)
request_delay = (config.getint('General', 'request_delay') if
                 config.has_option('General', 'request_delay') else 1)

exchanges = [_LoadExchangeConfig(config, target_currencies, coinex_api.CoinEx,
                                 'api_key', 'api_secret'),
             _LoadExchangeConfig(config, target_currencies, cryptsy_api.Cryptsy,
                                 'api_private_key', 'api_public_key')]
exchanges = [exchange for exchange in exchanges if exchange is not None]
if not exchanges:
    _Log('No exchange sections defined!')
    sys.exit(1)

while True:
    for (exchange, currencies, target_markets) in exchanges:
        try:
            balances = exchange.GetBalances()
        except exchange_api.ExchangeException as e:
            _Log('Failed to get %s balances: %s', exchange.name, e)
            continue

        for (currency_id, balance) in balances.items():
            for target_currency_id, markets in target_markets:
                if currency_id not in markets:
                    continue
                elif balance < markets[currency_id].trade_minimum:
                    currency_id = None  # don't try other markets
                    continue

                currency_name = (currencies[currency_id] if
                                 currency_id in currencies else currency_id)
                target_currency_name = (currencies[target_currency_id] if
                                        target_currency_id in currencies else target_currency_id)
                try:
                    time.sleep(request_delay)
                    order_id = exchange.CreateOrder(markets[currency_id].market_id,
                                                    balance, bid=False)
                except exchange_api.ExchangeException as e:
                    _Log('Failed to create sell order of %s %s for %s on %s: %s',
                         balance, currency_name, target_currency_name, exchange.name, e)
                else:
                    _Log('Created sell order %s of %s %s for %s on %s.',
                         order_id, balance, currency_name, target_currency_name, exchange.name)
                finally:
                    currency_id = None  # don't try other markets
    time.sleep(poll_delay)
