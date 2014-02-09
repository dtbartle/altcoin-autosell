# An exception that any methods in exchange may raise.
class ExchangeException(Exception):

    def __init__(self, exception):
        message = '[%s] %s' % (type(exception).__name__, exception)
        Exception.__init__(self, message)

# An order.
class Order(object):
    def __init__(self, market, order_id, bid_order, amount, price):
        self._market = market
        self._order_id = order_id
        self._bid_order = bid_order
        self._amount = amount
        self._price = price

    def GetMarket(self):
        return self._market

    def GetOrderId(self):
        return self._order_id

    def IsBidOrder(self):
        return self._bid_order

    def GetAmount(self):
        return self._amount

    def GetPrice(self):
        return self._price

# An available market.
class Market(object):
    def __init__(self, exchange):
        self._exchange = exchange

    def GetExchange(self):
        return self._exchange

    # Returns the currency that will be sold.
    def GetSourceCurrency(self):
        raise NotImplementedError

    # Returns the currency that will be bought.
    def GetTargetCurrency(self):
        raise NotImplementedError

    # Get the minimum amount of source currency that must be traded.
    def GetTradeMinimum(self):
        raise NotImplementedError

    # Returns a tuple of buy and sell Orders.
    def GetPublicOrders(self):
        raise NotImplementedError

    # Creates an order.
    # If 'bid_order' is True, this is a bid/buy order, otherwise an ask/sell order.
    # Returns an Order.
    def CreateOrder(self, bid_order, amount, price):
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
