import collections
import exchange_api
import hashlib
import hmac
import json
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
    def __init__(self, exchange, source_currency_id, target_currency_id, trade_pair_id,
                 reverse_market):
        exchange_api.Market.__init__(self, exchange)
        self._source_currency_id = source_currency_id
        self._source_currency = exchange._GetCurrencyName(source_currency_id)
        self._target_currency_id = target_currency_id
        self._target_currency = exchange._GetCurrencyName(target_currency_id)
        self._trade_pair_id = trade_pair_id
        self._reverse_market = reverse_market

    def GetSourceCurrency(self):
        return self._source_currency

    def GetTargetCurrency(self):
        return self._target_currency

    def GetTradeMinimum(self):
        return 0.01

    def GetPublicOrders(self):
        try:
            request_vars = {'tradePair' : self._trade_pair_id}
            orders = self._exchange._Request('orders', request_vars=request_vars)
            return ([exchange_api.Order(self, order['id'], True,
                                        float(order['amount']) / pow(10, 8),
                                        float(order['rate']) / pow(10, 8)) for
                     order in orders if order['bid']],
                    [exchange_api.Order(self, order['id'], False,
                                        float(order['amount']) / pow(10, 8),
                                        float(order['rate']) / pow(10, 8)) for
                     order in orders if not order['bid']])
        except (TypeError, LookupError) as e:
            raise exchange_api.ExchangeException(e)

    def CreateOrder(self, bid_order, amount, price):
        if self._reverse_market:
            bid_order = not bid_order
        order = {'trade_pair_id' : self._trade_pair_id,
                 'amount' : int(amount * pow(10, 8)),
                 'bid' : bid_order,
                 'rate' : max(1, int(price * pow(10, 8)))}
        post_data = json.dumps({'order' : order}).encode('utf-8')
        try:
            order_id = self._exchange._PrivateRequest('orders', post_data, 'order')['id']
            return exchange_api.Order(self, order_id, bid_order, amount, price)
        except (TypeError, LookupError) as e:
            raise exchange_api.ExchangeException(e)

class CoinEx(exchange_api.Exchange):
    @staticmethod
    def GetName():
        return 'CoinEx'

    def __init__(self, api_key, api_secret):
        self.api_url = 'https://coinex.pw/api/v2/'
        self.api_headers = {'Content-type' : 'application/json',
                            'Accept' : 'application/json',
                            'User-Agent' : 'autocoin-autosell'}
        self.api_key = api_key
        self.api_secret = api_secret.encode('utf-8')

        try:
            self._currency_names = {currency['id'] : currency['name'] for
                                    currency in self._Request('currencies')}
            self._markets = collections.defaultdict(dict)
            for trade_pair in self._Request('trade_pairs'):
                market1 = Market(self, trade_pair['currency_id'], trade_pair['market_id'],
                                 trade_pair['id'], False)
                self._markets[market1.GetSourceCurrency()][market1.GetTargetCurrency()] = market1
                market2 = Market(self, trade_pair['market_id'], trade_pair['currency_id'],
                                 trade_pair['id'], True)
                self._markets[market2.GetSourceCurrency()][market2.GetTargetCurrency()] = market2
        except (TypeError, LookupError) as e:
            raise exchange_api.ExchangeException(e)

    def _GetCurrencyName(self, currency_id):
        return self._currency_names.get(currency_id, '#%s' % currency_id)

    def _Request(self, method, request_vars=None, headers=None, post_data=None, json_root=None):
        request_string = '?' + urllib.parse.urlencode(request_vars) if request_vars else ''
        if headers is None:
            headers = {}
        headers.update(self.api_headers.items())
        try:
            request = urllib.request.Request(self.api_url + method + request_string,
                                             post_data, headers)
            response = urllib.request.urlopen(request)
            try:
                response_json = json.loads(response.read().decode('utf-8'))
                if not json_root:
                    json_root = method
                if not json_root in response_json:
                    raise exchange_api.ExchangeException('JSON root "%s" not in "%s".' %
                                                         (json_root, method))
                return response_json[json_root]
            finally:
                response.close()
        except (urllib.error.URLError, urllib.error.HTTPError, http.client.HTTPException,
                ValueError) as e:
            raise exchange_api.ExchangeException(e)

    def _PrivateRequest(self, method, post_data=None, json_root=None):
        hmac_data = b'' if not post_data else post_data
        digest = hmac.new(self.api_secret, hmac_data, hashlib.sha512).hexdigest()
        headers = {'API-Key' : self.api_key,
                   'API-Sign': digest}
        return self._Request(method, headers=headers, post_data=post_data, json_root=json_root)

    def GetCurrencies(self):
        return self._currency_names.values()

    def GetMarkets(self):
        return self._markets

    def GetBalances(self):
        balances = {}
        try:
            for balance in self._PrivateRequest('balances'):
                balances[self._GetCurrencyName(balance['currency_id'])] = (
                    float(balance['amount']) / pow(10, 8))
        except (TypeError, LookupError) as e:
            raise exchange_api.ExchangeException(e)
        return balances
