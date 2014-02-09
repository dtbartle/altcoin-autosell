import collections
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

class Market(exchange_api.Market):
    _TRADE_MINIMUMS = {('Points', 'BTC') : 0.1}

    def __init__(self, exchange, source_currency, target_currency, market_id, reverse_market):
        self._exchange = exchange
        self._source_currency = source_currency
        self._target_currency = target_currency
        self._market_id = market_id
        self._reverse_market = reverse_market

    def GetSourceCurrency(self):
        return self._source_currency

    def GetTargetCurrency(self):
        return self._target_currency

    def GetTradeMinimum(self):
        return self._TRADE_MINIMUMS.get((self._source_currency, self._target_currency), 0.0000001)

    def CreateOrder(self, amount, bid=True, price=None):
        if self._reverse_market:
            bid = not bid
        if price is None:
            if not bid:
                raise exchange_api.ExchangeException('Market sell orders are not supported.')
            price = 0
        post_dict = {'marketid' : self._market_id,
                     'ordertype' : 'Buy' if bid else 'Sell',
                     'quantity' : amount,
                     'price' : max(0.0000001, price)}
        try:
            return self._exchange._Request('createorder', post_dict)['orderid']
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)

class Cryptsy(exchange_api.Exchange):
    @staticmethod
    def GetName():
        return 'Cryptsy'

    def __init__(self, api_public_key, api_private_key):
        self.api_auth_url = 'https://api.cryptsy.com/api'
        self.api_headers = {'Content-type' : 'application/x-www-form-urlencoded',
                            'Accept' : 'application/json',
                            'User-Agent' : 'autocoin-autosell'}
        self.api_public_key = api_public_key
        self.api_private_key = api_private_key.encode('utf-8')

        self._markets = collections.defaultdict(dict)
        try:
            for market in self._Request('getmarkets')['return']:
                market1 = Market(self, market['primary_currency_code'],
                                 market['secondary_currency_code'], market['marketid'], False)
                self._markets[market1.GetSourceCurrency()][market1.GetTargetCurrency()] = market1
                market2 = Market(self, market['secondary_currency_code'],
                                 market['primary_currency_code'], market['marketid'], True)
                self._markets[market2.GetSourceCurrency()][market2.GetTargetCurrency()] = market2
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
        return self._markets.keys()

    def GetMarkets(self):
        return self._markets

    def GetBalances(self):
        try:
            return {currency: float(balance) for currency, balance in
                    self._Request('getinfo')['return']['balances_available'].items()}
        except (TypeError, KeyError, ValueError) as e:
            raise exchange_api.ExchangeException(e)
