import exchange_api
import hashlib
import hmac
import json
import urllib2

class CoinEx(exchange_api.Exchange):

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
        for currency in self._Request('currencies'):
            if 'name' not in currency:
                raise exchange_api.ExchangeException('name not in currencies.')
            if 'id' not in currency:
                raise exchange_api.ExchangeException('id not in currencies.')
            currencies[currency['name']] = currency['id']
        return currencies

    def GetBalances(self):
        balances = {}
        for balance in self._PrivateRequest('balances'):
            if 'currency_id' not in balance:
                raise exchange_api.ExchangeException('currency_id not in balances.')
            if 'amount' not in balance:
                raise exchange_api.ExchangeException('amount not in balances.')
            balances[balance['currency_id']] = float(balance['amount']) / pow(10, 8)
        return balances

    def GetMarkets(self):
        markets = {}
        for trade_pair in self._Request('trade_pairs'):
            if 'currency_id' not in trade_pair:
                raise exchange_api.ExchangeException('currency_id not in trade_pairs.')
            if 'market_id' not in trade_pair:
                raise exchange_api.ExchangeException('market_id not in trade_pairs.')
            if 'id' not in trade_pair:
                raise exchange_api.ExchangeException('id not in trade_pairs.')
            markets[(trade_pair['currency_id'], trade_pair['market_id'])] = trade_pair['id']
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
