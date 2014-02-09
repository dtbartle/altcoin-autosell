# An exception that any methods in exchange may raise.
class ExchangeException(Exception):

    def __init__(self, exception):
        message = '[%s] %s' % (type(exception).__name__, exception)
        Exception.__init__(self, message)

# An available market.
class Market(object):
    # Returns the currency that will be sold.
    def GetSourceCurrency(self):
        raise NotImplementedError

    # Returns the currency that will be bought.
    def GetTargetCurrency(self):
        raise NotImplementedError

    # Get the minimum amount of source currency that must be traded.
    def GetTradeMinimum(self):
        raise NotImplementedError

    # Creates an order (market order if price is None).
    # If 'bid' is True, this is a bid/buy order, otherwise an ask/sell order.
    # Returns an order_id.
    def CreateOrder(self, amount, bid=True, price=None):
        raise NotImplementedError

# A base class for Exchanges.
class Exchange(object):
    # Returns the name of the exchange.
    @staticmethod
    def GetName():
        raise NotImplementedError

    # Returns a list of currencies, e.g. ['BTC', 'LTC', 'DOGE', '42'].
    def GetCurrencies(self):
        raise NotImplementedError

    # Returns an array of Markets.
    def GetMarkets(self):
        raise NotImplementedError

    # Returns a dict of currency to balance, e.g.
    # {
    #   'BTC': 173.23,
    #   'LTC': 19,347,
    # }
    def GetBalances(self):
        raise NotImplementedError
