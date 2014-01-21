# A base class for Exchanges.
class Exchange(object):

    # Returns the name of the exchange.
    def GetName(self):
        raise NotImplementedError

    # Returns a dict of currency_name to currency_id, e.g.
    # {
    #   'BTC' : 1,
    #   'LTC' : 2,
    #   'DOGE': 12,
    #   '42': 15,
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

    # Returns a dict of (source_currency_id, target_currency_id) -> market_id, e.g.
    # {
    #   (12, 1): 1,
    #   (15, 2): 2,
    #   (2, 1) : 3,
    # }
    def GetMarkets(self):
        raise NotImplementedError

    # Creates an order (market order if price is 0).
    # If 'bid' is True, this is a bid/buy order, otherwise an ask/sell order.
    # Returns an order_id.
    def CreateOrder(self, market_id, amount, bid=True, price=0):
        raise NotImplementedError

# An exception that any methods in Exchange may raise.
class ExchangeException(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
