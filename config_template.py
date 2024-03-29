# copy this template file to 'config.py' and make changes there

# values defined in api of abcc.com
BID_SIDE = "bids"
ASK_SIDE = "asks"

# your api key and secret from abcc
abcc_key = ""
abcc_secret = b""

# find your utc_correction with calibrate_time.py
utc_correction = 0
previous_utc = 0  # don't touch this

# find market code to trade with show_markets.py
market = ""

# smallest change of a price in the given market
# a bot dimes another order by this amount to be in front of it
# the minimum of this setting is market specific, see show_markets.py
tick_size = "0.00000001"

# size of the diming order
order_size = 1500

# side of the diming order. BID_SIDE = buy orders are send, ASK_SIDE = sell orders are send
dime_side = BID_SIDE

# interval in seconds to check for diming possibility
dime_check_sec = 15

# interval to wash. in seconds. yes, hygiene is important to bots!
wash_check_sec = 40

# random upper time limit for sending wash order
wash_check_upperlimit_sec = 20

# min order size to wash. actual order size will be random between this and dime order size
min_order_size = 1500

