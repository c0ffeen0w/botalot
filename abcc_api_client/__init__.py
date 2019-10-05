import json
import config
import httplib2
import hmac
import hashlib
import datetime
from prettytable import PrettyTable
from decimal import *
import time

from config import BID_SIDE, ASK_SIDE

h = httplib2.Http()
server = "https://api.abcc.com"

tick_size = Decimal(config.tick_size)

ORDER_TYPE_LIMIT = "limit"
ORDER_TYPE_MARKET = "market"


def sign_sha256(key, message):
    return hmac.new(key, msg=message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().lower()


def get_unix_timestamp(utc_correction):
    time.sleep(1)
    utc = utc_correction + int(datetime.datetime.utcnow().timestamp())
    return utc


def calibrate_time_with_server():
    request_method = "GET"
    request_endpoint = "/api/v1/common/timestamp"
    tonce = get_unix_timestamp(0)
    params = "access_key={}&tonce={}".format(config.abcc_key, tonce)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    print(data)
    if 'error' in data:
        error = data['error']
        if int(error['code']) == 11004:
            msg = error['message']
            tokens = msg.split(' ')
            our_utc = tokens[2].split('.')[0]
            their_utc = tokens[8].split('.')[0]
            print("\nplease put in config.py: utc_correction = ", int(their_utc) - int(our_utc))
        else:
            print("unexpected error:", error)
    else:
        print("time seems in sync")


def show_open_orders():
    request_method = "GET"
    request_endpoint = "/api/v1/exchange/orders"
    tonce = get_unix_timestamp(config.utc_correction)
    params = "access_key={}&tonce={}".format(config.abcc_key, tonce)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    print("open orders:", data['meta']['total_count'])
    print(data['orders'])


def clear_open_orders():
    request_method = "POST"
    request_endpoint = "/api/v1/exchange/orders/clear"
    tonce = get_unix_timestamp(config.utc_correction)
    params = "access_key={}&market_code={}&tonce={}".format(config.abcc_key, config.market, tonce)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    print("deleted orders: ", data)


def clear_all_markets_open_orders():
    request_method = "POST"
    request_endpoint = "/api/v1/exchange/orders/clear"
    tonce = get_unix_timestamp(config.utc_correction)
    params = "access_key={}&tonce={}".format(config.abcc_key, tonce)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    print(data)


def show_markets():
    request_method = "GET"
    request_endpoint = "/api/v1/common/markets"
    tonce = get_unix_timestamp(config.utc_correction)
    params = "access_key={}&tonce={}".format(config.abcc_key, tonce)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    print(data)


def get_order_book():
    request_method = "GET"
    request_endpoint = "/api/v1/exchange/order_book"
    tonce = get_unix_timestamp(config.utc_correction)
    params = "access_key={}&market_code={}&tonce={}".format(config.abcc_key, config.market, tonce)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    return data


def get_sorted_book_half(whole_order_book, side):
    # order book is received from abcc with asks and bids sorted descending
    # asks are here reversed to have best order in index 0 for both sides
    if side == BID_SIDE:
        return whole_order_book[BID_SIDE]
    if side == ASK_SIDE:
        return whole_order_book[ASK_SIDE][::-1]
    raise Exception("unknown book side")


def show_order_book():
    book = get_order_book()
    print("market:", config.market, str(datetime.datetime.now()).split(".")[0])
    p = PrettyTable(['bid_size', 'price', 'ask_size'])
    p.align['price'] = "l"
    for ask in book['asks']:
        p.add_row(['', ask['price'], ask['remaining_volume']])
    p.add_row(['', '', ''])
    for bid in book['bids']:
        p.add_row([bid['remaining_volume'], bid['price'], ''])
    print(p)


def get_best_price(sorted_half_book):
    if len(sorted_half_book) < 1:
        raise Exception("book side empty")
    return sorted_half_book[0]['price']


def get_best_size(sorted_half_book):
    if len(sorted_half_book) < 1:
        raise Exception("book side empty")
    return sorted_half_book[0]['remaining_volume']


def is_best_price(price, side):
    whole_book = get_order_book()
    book_half = get_sorted_book_half(whole_book, side)
    best_price = Decimal(get_best_price(book_half))
    if price == best_price:
        return True
    return False


def get_order_action_from_side(side):
    if side == BID_SIDE:
        return "buy"
    elif side == ASK_SIDE:
        return "sell"
    else:
        raise Exception("unknown order side!")


def send_order(side, size, price, type):
    request_method = "POST"
    request_endpoint = "/api/v1/exchange/orders"
    tonce = get_unix_timestamp(config.utc_correction)
    # body = {}
    order_action = get_order_action_from_side(side)
    params = "access_key={}&market_code={}&ord_type={}&price={}&side={}&tonce={}&volume={}" \
        .format(config.abcc_key, config.market, type, price, order_action, tonce, size)
    payload = "{}|{}|{}".format(request_method, request_endpoint, params)
    sig = sign_sha256(config.abcc_secret, payload)
    req = "{}{}?{}&signature={}".format(server, request_endpoint, params, sig)
    (resp, content) = h.request(req, request_method, headers={'cache-control': 'no-cache'})
    data = json.loads(content)
    if 'error' in data:
        print(data)
        raise Exception(str(data))
    if 'order' not in data:
        raise Exception(str(data))
    return data['order']


def dime(side):
    whole_book = get_order_book()
    bid_side = get_sorted_book_half(whole_book, BID_SIDE)
    ask_side = get_sorted_book_half(whole_book, ASK_SIDE)
    best_bid_price = Decimal(get_best_price(bid_side))
    best_ask_price = Decimal(get_best_price(ask_side))
    if best_ask_price - best_bid_price < tick_size:
        print("order book too tight. diming not possible!")
        return
    price = (best_ask_price + best_bid_price) / 2
    if side == ASK_SIDE:
        price = best_ask_price - tick_size
    elif side == BID_SIDE:
        price = best_bid_price + tick_size
    else:
        raise Exception("unknown side!")

    order_info = send_order(side, config.order_size, price, ORDER_TYPE_LIMIT)
    print("new order:", order_info)
    return order_info
