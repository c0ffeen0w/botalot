import abcc_api_client as api
import config
import time
import sys
import random
from decimal import *

active_order = []
nextWashTime = config.wash_check_sec + api.get_unix_timestamp(0)



def get_washing_order_side():
    if config.dime_side == config.BID_SIDE:
        return config.ASK_SIDE
    elif config.dime_side == config.ASK_SIDE:
        return config.BID_SIDE
    else:
        raise Exception("unknown side!")


api.calibrate_time_with_server()

api.clear_open_orders()
api.show_order_book()
active_order = api.dime(config.dime_side)

while True:
    try:
        api.calibrate_time_with_server()
        api.show_order_book()
        time.sleep(config.dime_check_sec)
        if 'id' in active_order:
            price = Decimal(active_order['price'])
            size = active_order['remaining_volume']

            if (not api.is_best_price(price, config.dime_side)) or \
                    (not api.is_best_size(size, config.dime_side)):
                api.clear_open_orders()
                active_order = []
                active_order = api.dime(config.dime_side)
            elif api.get_unix_timestamp(0) > nextWashTime:
                print("wash_order:")
                max_size = int(float(size))
                wash_size = random.randrange(config.min_order_size, max_size)
                wash_order = api.send_order(get_washing_order_side(), wash_size, price, api.ORDER_TYPE_LIMIT)
                print(wash_order)
                nextWashTime = config.wash_check_sec + api.get_unix_timestamp(0)

    except KeyboardInterrupt:
        print("Ctrl-C detected. deleting open orders...")
        api.clear_open_orders()
        sys.exit()
