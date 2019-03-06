from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import *
from ibapi.ticktype import TickType
from ibapi.contract import Contract
import redis
import json
# import random
import time
from threading import Thread
import utils.log as logger
from datetime import datetime, timedelta

try:
    import pandas as pd
except Exception as e:
    print(e)

# 其实还有货币对：'USD.KRW',但是同时也有个"KRW.USD",所以只订阅其中一个交易对
products = ['AUD.CAD', 'AUD.CHF', 'AUD.CNH', 'AUD.HKD', 'AUD.JPY', 'AUD.NZD', 'AUD.SGD', 'AUD.USD', 'AUD.ZAR',
            'CAD.CHF', 'CAD.CNH', 'CAD.JPY', 'CHF.CNH', 'CHF.CZK', 'CHF.DKK', 'CHF.HUF', 'CHF.JPY', 'CHF.NOK',
            'CHF.PLN', 'CHF.SEK', 'CHF.TRY', 'CHF.ZAR', 'CNH.HKD', 'CNH.JPY', 'DKK.JPY', 'DKK.NOK', 'DKK.SEK',
            'EUR.AUD', 'EUR.CAD', 'EUR.CHF', 'EUR.CNH', 'EUR.CZK', 'EUR.DKK', 'EUR.GBP', 'EUR.HKD', 'EUR.HUF',
            'EUR.ILS', 'EUR.JPY', 'EUR.MXN', 'EUR.NOK', 'EUR.NZD', 'EUR.PLN', 'EUR.RUB', 'EUR.SEK', 'EUR.SGD',
            'EUR.TRY', 'EUR.USD', 'EUR.ZAR', 'GBP.AUD', 'GBP.CAD', 'GBP.CHF', 'GBP.CNH', 'GBP.CZK', 'GBP.DKK',
            'GBP.HKD', 'GBP.HUF', 'GBP.JPY', 'GBP.MXN', 'GBP.NOK', 'GBP.NZD', 'GBP.PLN', 'GBP.SEK', 'GBP.SGD',
            'GBP.TRY', 'GBP.USD', 'GBP.ZAR', 'HKD.JPY', 'KRW.AUD', 'KRW.CAD', 'KRW.CHF', 'KRW.EUR', 'KRW.GBP',
            'KRW.HKD', 'KRW.JPY', 'KRW.USD', 'MXN.JPY', 'NOK.JPY', 'NOK.SEK', 'NZD.CAD', 'NZD.CHF', 'NZD.JPY',
            'NZD.USD', 'SEK.JPY', 'SGD.CNH', 'SGD.JPY', 'TRY.JPY', 'USD.CAD', 'USD.CHF', 'USD.CNH', 'USD.CZK',
            'USD.DKK', 'USD.HKD', 'USD.HUF', 'USD.ILS', 'USD.JPY', 'USD.KRW', 'USD.MXN', 'USD.NOK', 'USD.PLN',
            'USD.RUB', 'USD.SEK', 'USD.SGD', 'USD.TRY', 'USD.ZAR', 'ZAR.JPY']
product_index = 0
specific_pair = None

TICKER_TYPE_BID_SIZE = 0
TICKER_TYPE_BID_PRICE = 1
TICKER_TYPE_ASK_PRICE = 2
TICKER_TYPE_ASK_SIZE = 3
redis_client = redis.StrictRedis(charset="utf-8", decode_responses=True)
PLATFORM = 'IB'
thread = None
PORT = 4002
# PORT = 7497


def subscribe_all_contracts_lob(wrapper):
    # while 1:
    for item in products:
        currencies = item.split('.')
        time.sleep(0.03)
        # if client.isConnected():
        wrapper.subscribe_pair(currencies[0], currencies[1])



def save_klines(pair, klines):
    currencies = pair.split('.')
    csv_file_name = "files/%s_%s_D.csv" % (currencies[0], currencies[1])
    try:
        df_new = pd.DataFrame(klines, columns=["date", "high", "open", "low", "close", "volume"])
        df_old = pd.read_csv(csv_file_name, index_col=0)
        df_old["date"] = df_old["date"].astype(str)
        df_new = pd.concat([df_old, df_new], axis=0)
    except Exception as e:
        print(e)
    finally:
        df_new.sort_values(by=['date'], ascending=True)
        df_new.drop_duplicates(['date'])
        df_new.to_csv(csv_file_name)


def subscribe_and_save_kline(wrapper, start="20100101 00:00:00", end="20190101 00:00:00"):
    time.sleep(1)
    time_format = '%Y%m%d %H:%M:%S'
    global product_index, specific_pair
    if product_index >= len(products):
        print("end")
        return
    pair = specific_pair or products[product_index]
    currencies = pair.split('.')

    start_date_time = datetime.strptime(start, time_format)
    mid_end_date_time = start_date_time + timedelta(days=356)
    end_date_time = datetime.strptime(end, time_format)

    if end_date_time > mid_end_date_time:
        mid_end = mid_end_date_time.strftime(time_format)

        def finish_callback(callback_wrapper):
            save_klines(pair, callback_wrapper.klines)
            subscribe_and_save_kline(wrapper, mid_end, end)

        wrapper.subscribe_kline(currencies[0], currencies[1], mid_end, finish=finish_callback)
    else:
        def finish_callback(callback_wrapper):
            save_klines(pair, callback_wrapper.klines)
            global product_index, specific_pair
            if specific_pair:
                return
            product_index += 1
            print("finish " + pair + " next index " + str(product_index))
            subscribe_and_save_kline(wrapper)

        wrapper.subscribe_kline(currencies[0], currencies[1], end, finish=finish_callback)


def check_correlate():
    df_combine = None
    for pair in products:
        currencies = pair.split('.')
        csv_file_name = "files/%s_%s_D.csv" % (currencies[0], currencies[1])
        try:
            df = pd.read_csv(csv_file_name, index_col=0)
            df_sub = df[["date", "close"]]
            df_sub.rename(columns={'close': pair}, inplace=True)

            if type(df_combine) == type(None):
                df_combine = df_sub
            else:
                df_combine = df_combine.merge(df_sub, on="date", how='left')
                df_combine = df_combine.drop_duplicates(["date"])
            print(pair, df_combine.count())
        except Exception as e:
            print(e)
        finally:
            pass
    df_combine.to_csv("files/tmp.csv")
    result = df_combine.corr('pearson')
    print("check", result)
    result.to_csv("files/result.csv")


class IBClient(EWrapper):
    def __init__(self, clientId):
        super().__init__()
        self.req_id_base = 1000
        self.index = 0
        self.cache_data = {}
        # self.products = sorted(products, key=lambda x: random.random(), reverse=False)
        self.products = products
        self.req_id_map = {}
        # self.req_id = 0
        self.callback_map = {}
        self.thread = None
        self.ready = None
        self.clientId = clientId or 1
        # global client
        client = EClient(wrapper=self)
        self.client = client
        self.klines = None

    @staticmethod
    def create_cash_contract(symbol, currency):
        contract = Contract()
        contract.symbol = symbol
        contract.currency = currency
        contract.secType = "CASH"
        contract.exchange = "IDEALPRO"
        return contract

    def publish_data(self, reqId):
        product_name = self.get_symbol_by_req_id(reqId).replace('.', '')
        cache = self.cache_data.get(reqId, None)
        if not cache or not cache.get('askSize') or not cache.get('bidSize'):
            return
        # self.cache_data.pop(reqId, None)
        cache["symbol"] = product_name
        data = {
            "asks": [[cache.get("askPrice",'-1'), cache.get('askSize')]],
            "bids": [[cache.get("bidPrice",'-1'), cache.get("bidSize")]],
            "symbol": product_name
        }
        # logger.error("publish data:" + product_name)
        redis_client.set(product_name + "DEPTH@" + PLATFORM.lower(), json.dumps(data), ex=180)
        redis_client.publish(PLATFORM, json.dumps({"symbol": product_name, "time": time.time()}))

    def start(self):
        # 端口号是在IB gateway 或者TWS里面设置的,模拟账号是4002
        self.client.connect("127.0.0.1", 4002, clientId=self.clientId)
        self.client.run()

    def connectAck(self):
        super().connectAck()
        if not self.thread or not self.thread.is_alive():
            self.thread = Thread(target=lambda: self.ready(self))
            self.thread.setDaemon(True)
            self.thread.start()

    def connectionClosed(self):
        logger.debug("IBClient", "断开重连")
        time.sleep(0.5)
        # self.client = EClient(wrapper=self)
        # self.client.connect("127.0.0.1", PORT, clientId=self.clientId)
        # self.client.run()

    def get_symbol_by_req_id(self, req_id):
        value = self.req_id_map.get(req_id, '')
        return value

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        item = self.get_symbol_by_req_id(reqId)
        logger.error(item + ",errorCode:" + str(errorCode) + ",error:" + errorString)
        finish = self.callback_map.get(str(reqId))
        if finish:
            finish(self)

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        data = self.cache_data.get(reqId, {})
        if tickType == TICKER_TYPE_ASK_PRICE:
            data['askPrice'] = str(price)
            # print("tickPrice", reqId, price)
        elif tickType == TICKER_TYPE_BID_PRICE:
            data['bidPrice'] = str(price)
            # print("tickPrice", reqId, price)

        self.cache_data[reqId] = data

    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        data = self.cache_data.get(reqId, {})
        if tickType == TICKER_TYPE_ASK_SIZE:
            data['askSize'] = str(size)
            # print("tickSize", reqId, size)

        elif tickType == TICKER_TYPE_BID_SIZE:
            data['bidSize'] = str(size)
            # print("tickSize", reqId, size)
        self.cache_data[reqId] = data
        self.publish_data(reqId)


    def create_req_code(self):
        self.req_id_base += 1
        return self.req_id_base

    def tickSnapshotEnd(self, reqId: int):
        super().tickSnapshotEnd(reqId)
        # product_name = self.get_symbol_by_req_id(reqId).replace('.', '')
        # cache = self.cache_data.get(reqId, None)
        # if not cache or not cache.get('askSize') or not cache.get('bidSize'):
        #     return
        # self.cache_data.pop(reqId, None)
        # cache["symbol"] = product_name
        # data = {
        #     "asks": [[cache.get("askPrice"), cache.get('askSize')]],
        #     "bids": [[cache.get("bidPrice"), cache.get("bidSize")]],
        #     "symbol": product_name
        # }
        # logger.error("publish data:" + product_name)
        # redis_client.set(product_name + "DEPTH@" + PLATFORM.lower(), json.dumps(data), ex=180)
        # redis_client.publish(PLATFORM, json.dumps({"symbol": product_name, "time": time.time()}))
        self.publish_data(reqId)


    def subscribe_kline(self, symbol, currency, end_datetime, duration="1 Y", bar_type="1 day", finish=None):
        self.klines = []
        contract = IBClient.create_cash_contract(symbol, currency)
        req_id = self.create_req_code()
        self.req_id_map[req_id] = symbol + "." + currency
        self.client.reqHistoricalData(req_id, contract, end_datetime, duration, bar_type, "MIDPOINT", 1, 1, False, [])
        if finish:
            self.callback_map[str(req_id)] = finish

    def historicalData(self, reqId: int, bar: BarData):
        # print("HistoricalData. ReqId:", reqId, "BarData.", bar)
        self.klines.append([
            bar.date,
            bar.high,
            bar.open,
            bar.low,
            bar.close,
            bar.volume
        ])

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        finish = self.callback_map.get(str(reqId))
        if finish:
            finish(self)

    def subscribe_pair(self, symbol, currency):
        contract = IBClient.create_cash_contract(symbol, currency)
        # if req_id < 0:
        req_id = self.create_req_code()
        # wrapper.req_id = req_id
        self.req_id_map[req_id] = symbol + "." + currency
        # if wrapper.client.isConnected():
        self.client.reqMktData(req_id, contract, "", False, False, [])
        # else:
        #     time.sleep(0.5)
        #     wrapper.client.reqMktData(req_id, contract, "", True, False, [])


ttt = None


def test():
    global ttt
    # ttt = IBClient(1234)
    test2 = IBClient(2345)
    test2.ready = subscribe_all_contracts_lob
    test2.start()
