altcoin-autosell
================

Script that continuously autosells altcoins for BTC. Supported exchanges:
* CoinEx (https://gist.github.com/erundook/8377222)

Exchanges that could be supported:
* BTC-e (https://btc-e.com/api/documentation)
* BTER (http://bter.com/api)
* Cryptsy (https://www.cryptsy.com/pages/api)
* Vircurex (https://vircurex.com/welcome/api)

Configuration file should go in ~/.altcoin-autosell.config, e.g.:

    [General]
    target_currency = BTC  // optional, currency to convert to
    sleep_seconds = 60  // optional, number of seconds to sleep between polls
    
    [CoinEx]
    api_key = abc123
    api_secret = 456def
