# An exception that any methods in exchange may raise.
class ExchangeException(Exception):

    def __init__(self, exception):
        message = '[%s] %s' % (type(exception).__name__, exception)
        Exception.__init__(self, message)

# An available market.
class Market(object):
    source_currency_id = None
    target_currency_id = None
    market_id = None
    trade_minimum = 0.00000001

    def __init__(self, source_currency_id, target_currency_id, market_id,
                 trade_minimum=0.0000001):
        self.source_currency_id = source_currency_id
        self.target_currency_id = target_currency_id
        self.market_id = market_id
        self.trade_minimum = trade_minimum

# A base class for Exchanges.
class Exchange(object):

    # The name of the exchange.
    name = ''

    # Returns a dict of currency_id to currency_name, e.g.
    # {
    #   1: 'BTC',
    #   2: 'LTC',
    #   12: 'DOGE',
    #   15: '42',
    # }
    def GetCurrencies(self):
        raise NotImplementedError

    # Returns a dict of currency_id to balance, e.g.
    # {
    #   12: 173.23,
    #   13: 19,347,
    # }
    def GetBalances(self):
        raise NotImplementedError

    # Returns an array of Markets.
    def GetMarkets(self):
        raise NotImplementedError

    # Creates an order (market order if price is 0).
    # If 'bid' is True, this is a bid/buy order, otherwise an ask/sell order.
    # Returns an order_id.
    def CreateOrder(self, market_id, amount, bid=True, price=0):
        raise NotImplementedError
