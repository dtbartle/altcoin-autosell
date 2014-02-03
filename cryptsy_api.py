import exchange_api
import hashlib
import hmac
import json
import time
try:
    import http.client
    import urllib.request
    import urllib.error
    import urllib.parse
except ImportError:
    # Python 2.7 compatbility
    import httplib
    class http: client = httplib
    import urllib
    import urllib2
    class urllib: request = urllib2; error = urllib2; parse = urllib

class Cryptsy(exchange_api.Exchange):

    name = 'Cryptsy'

    def __init__(self, api_public_key, api_private_key):
        self.api_auth_url = 'https://api.cryptsy.com/api'
        self.api_headers = {'Content-type' : 'application/x-www-form-urlencoded',
                            'Accept' : 'application/json',
                            'User-Agent' : 'autocoin-autosell'}
        self.api_public_key = api_public_key
        self.api_private_key = api_private_key.encode('utf-8')

    def _GetTradeMinimum(self, market):
        trade_minimums = {('Points', 'BTC') : 0.1}
        try:
            trade_pair = (market['primary_currency_code'], market['secondary_currency_code'])
            return trade_minimums.get(trade_pair, 0.0000001)
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)

    def _Request(self, method, post_dict=None):
        if post_dict is None:
            post_dict = {}
        post_dict['method'] = method
        post_dict['nonce'] = int(time.time())
        post_data = urllib.parse.urlencode(post_dict).encode('utf-8')
        digest = hmac.new(self.api_private_key, post_data, hashlib.sha512).hexdigest()
        headers = {'Key' : self.api_public_key,
                   'Sign': digest}
        headers.update(self.api_headers.items())

        try:
            request = urllib.request.Request(self.api_auth_url, post_data, headers)
            response = urllib.request.urlopen(request)
            try:
                response_json = json.loads(response.read().decode('utf-8'))
                if 'error' in response_json and response_json['error']:
                    raise exchange_api.ExchangeException(response_json['error'])
                return response_json
            finally:
                response.close()
        except (urllib.error.URLError, urllib.error.HTTPError, http.client.HTTPException,
                ValueError) as e:
            raise exchange_api.ExchangeException(e)

    def GetCurrencies(self):
        currencies = {}
        try:
            for market in self._Request('getmarkets')['return']:
                currencies[market['primary_currency_code']] = market['primary_currency_code']
                currencies[market['secondary_currency_code']] = market['secondary_currency_code']
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
        return currencies

    def GetBalances(self):
        try:
            return {currency: float(balance) for currency, balance in
                    self._Request('getinfo')['return']['balances_available'].items()}
        except (TypeError, KeyError, ValueError) as e:
            raise exchange_api.ExchangeException(e)

    def GetMarkets(self):
        try:
            return [exchange_api.Market(market['primary_currency_code'],
                                        market['secondary_currency_code'],
                                        market['marketid'],
                                        self._GetTradeMinimum(market)) for
                    market in self._Request('getmarkets')['return']]
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
        return markets

    def CreateOrder(self, market_id, amount, bid=True, price=0):
        post_dict = {'marketid' : market_id,
                     'ordertype' : 'Buy' if bid else 'Sell',
                     'quantity' : amount,
                     'price' : max(0.0000001, price)}
        try:
            return self._Request('createorder', post_dict)['orderid']
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
