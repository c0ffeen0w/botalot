import abcc_api_client as api
import config
import time
import sys
from decimal import *

active_order = []

api.calibrate_time_with_server()
api.clear_open_orders()
api.show_order_book()
active_order = api.dime(config.dime_side, config.order_size)

while True:
    try:
        api.calibrate_time_with_server()
        api.show_order_book()
        time.sleep(config.dime_check_sec)
        if 'id' in active_order:
            price = Decimal(active_order['price'])
            if not api.is_best_price(price, config.dime_side):
                api.clear_open_orders()
                active_order = []
                active_order = api.dime(config.dime_side, config.order_size)

    except KeyboardInterrupt:
        print("Ctrl-C detected. deleting open orders...")
        api.clear_open_orders()
        sys.exit()
