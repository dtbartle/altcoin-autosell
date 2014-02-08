altcoin-autosell
================

Script that continuously autosells altcoins for BTC. Supported exchanges:
* CoinEx (https://gist.github.com/erundook/8377222)
* Cryptsy (https://www.cryptsy.com/pages/api)

Exchanges that could be supported:
* BTC-e (https://btc-e.com/api/documentation)
* BTER (http://bter.com/api)
* Vircurex (https://vircurex.com/welcome/api)

Configuration file should go in ~/.altcoin-autosell.config, e.g.:

    [General]
    # optional, comma-separated list of currencies to convert to
    #target_currencies = BTC, LTC
    # optional, comma-separated list of currencies to convert from
    #source_currencies = DOGE, TAG, DGC
    # optional, number of seconds to sleep between polls
    #poll_delay = 60
    # optional, number of seconds to sleep between requests
    #request_delay = 1
    
    [CoinEx]
    api_key = abc123
    api_secret = 456def

    [Cryptsy]
    api_public_key = abc123
    api_private_key = 456def
