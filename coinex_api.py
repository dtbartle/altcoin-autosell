import exchange_api
import hashlib
import hmac
import json
import urllib2

class CoinEx(exchange_api.Exchange):

    name = 'CoinEx'

    def __init__(self, api_key, api_secret):
        self.api_url = 'https://coinex.pw/api/v2/'
        self.api_headers = {'Content-type' : 'application/json',
                            'Accept' : 'application/json',
                            'User-Agent' : 'autocoin-autosell'}
        self.api_key = api_key
        self.api_secret = api_secret

    def GetName(self):
        return 'CoinEx'

    def _Request(self, method, headers=None, post_data=None):
        if headers is None:
            headers = {}
        headers.update(self.api_headers.items())
        request = urllib2.Request(self.api_url + method, post_data, headers)
        try:
            response = urllib2.urlopen(request)
            try:
                response_json = json.loads(response.read())
                if not method in response_json:
                    raise exchange_api.ExchangeException('Root not in %s.' % method)
                return response_json[method]
            finally:
                response.close()
        except (urllib2.HTTPError, ValueError) as e:
            raise exchange_api.ExchangeException(e)

    def _PrivateRequest(self, method, post_data=None):
        hmac_data = '' if not post_data else post_data
        digest = hmac.new(self.api_secret, hmac_data, hashlib.sha512).hexdigest()
        headers = {'API-Key' : self.api_key,
                   'API-Sign': digest}
        return self._Request(method, headers, post_data)

    def GetCurrencies(self):
        currencies = {}
        try:
            for currency in self._Request('currencies'):
                currencies[currency['name']] = currency['id']
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
        return currencies

    def GetBalances(self):
        balances = {}
        try:
            for balance in self._PrivateRequest('balances'):
                balances[balance['currency_id']] = float(balance['amount']) / pow(10, 8)
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
        return balances

    def GetMarkets(self):
        try:
            return [exchange_api.Market(trade_pair['currency_id'], trade_pair['market_id'],
                                        trade_pair['id']) for
                    trade_pair in self._Request('trade_pairs')]
        except (TypeError, KeyError) as e:
            raise exchange_api.ExchangeException(e)
        return markets

    def CreateOrder(self, market_id, amount, bid=True, price=0):
        order = {'trade_pair_id' : market_id,
                 'amount' : int(amount * pow(10, 8)),
                 'bid' : bid,
                 'rate' : max(1, int(price * pow(10, 8)))}
        post_data = json.dumps({'order' : order})
        order_response = self._PrivateRequest('orders', post_data)
        if not order_response:
            raise exchange_api.ExchangeException('Order response empty.')
        if not 'id' in order_response[0]:
            raise exchange_api.ExchangeException('id not in orders.')
        return order_response[0]['id']
