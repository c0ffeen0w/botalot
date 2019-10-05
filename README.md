# botalot

This is a partial implementation of the abcc.com API with examples of bots using this interface.

## requirements
- API keys from abcc.com
- Python 3.7
- packages: json httplib2 hmac hashlib datetime prettytable decimal time

## configuration
- copy config_template.py config.py
- edit config.py and add your API keys
- run `python calibrate_time.py` to find your utc_timestamp correction and set it in config.py
- run `python show_markets.py` to find the market code you want to trade. Use multiple installations for multiple markets, if you dare. 
- edit bot parameters to your liking

## running the bots

### dimelot
- run with `python dimealot.py`
- depending on the config.py settings an order is kept in front of the market. the best order found in the market is dimed with the given tick size. being dimed by others leads to a new dime attempt. 
- there is no tracking of position size! the bot will only stop when it runs out of assets to trade. even then it might keep trying..

### washalot
- run with `python washalot.py`
- this bot allows to dime automatically like dimealot but additionally has a timer that triggers a second order to trade against the diming order. this behaviour can be useful to study and improve the management of trades and positions within the bot. or simply to donate some fees to the exchange. use wisely.
- the bots can be stopped with Ctrl-C and should try to cancel all active orders in their respective markets

## disclaimer
- well, you know it: USE AT YOUR OWN RISK! this software comes as is, without any guarantees or warranty! 
- be sure to read the license!
- if you trade with this software with real, digital, virtual or other money, tokens, coins or other, it is on your own risk and you will lose at least some of them! so much for a guarantee!   
- if you make some money, against all odds, consider donating some. good luck!
 

