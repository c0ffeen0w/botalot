import abcc_api_client as api
import config

active_order = []

api.clear_open_orders()
api.show_order_book()
active_order = api.dime(config.ASK_SIDE)
api.show_order_book()

