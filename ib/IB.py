from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import *
from ibapi.ticktype import TickType
from ibapi.contract import Contract
import redis
import json

import time

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

TICKER_TYPE_BID_SIZE = 0
TICKER_TYPE_BID_PRICE = 1
TICKER_TYPE_ASK_PRICE = 2
TICKER_TYPE_ASK_SIZE = 3
redis_client = redis.StrictRedis(charset="utf-8", decode_responses=True)
PLATFORM = 'IB'


class IBClient(EWrapper):
    def __init__(self):
        super().__init__()
        self.req_id_base = 1000
        self.index = 0
        self.cash_data = {}
        self.client = EClient(wrapper=self)
        # 端口号是在IB gateway 或者TWS里面设置的,模拟账号是4002
        self.client.connect("127.0.0.1", 4002, clientId=1234)
        self.client.run()

    def subscribe_all_contracts(self):
        for item in products:
            currencies = item.split('.')
            self.subscribe_pair(currencies[0], currencies[1])
        # self.subscribe_pair('CHF','JPY')

    def subscribe_contract_at_index(self):
        i = self.index % len(products)
        item = products[i]
        currencies = item.split('.')
        req_id = self.create_req_code('', '', i)
        self.subscribe_pair(currencies[0], currencies[1], req_id)

    def create_cash_contract(self, symbol, currency):
        contract = Contract()
        contract.symbol = symbol
        contract.currency = currency
        contract.secType = "CASH"
        contract.exchange = "IDEALPRO"
        return contract

    def create_req_code(self, symbol, currency, index=-1):
        if 0 <= index < len(products):
            return self.req_id_base + index
        item = symbol + '.' + currency
        i = products.index(item)
        if i < 0:
            raise Exception('找不到对应货币对')
        return self.req_id_base + i

    def connectAck(self):
        super().connectAck()
        self.subscribe_contract_at_index()

    def connectionClosed(self):
        print('断开重连')
        self.client.connect("127.0.0.1", 4002, clientId=1234)
        self.client.run()

    def subscribe_pair(self, symbol, currency, req_id=-1):
        contract = self.create_cash_contract(symbol, currency)
        if req_id < 0:
            req_id = self.create_req_code(symbol, currency)
        self.client.reqMktData(req_id, contract, "", True, False, [])
        # self.client.reqTickByTickData(req_id, contract, 'BidAsk', 0, False)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        if reqId - self.req_id_base >= 0:
            item = products[reqId - self.req_id_base]
            print(item + ",errorCode:" + str(errorCode) + ",error:" + errorString)
        else:
            print("requestId:" + str(reqId) + "errorCode:" + str(errorCode) + ",error:" + errorString)

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("tickPrice:" + str(price) + ",tickType:" + str(tickType))
        if tickType == TICKER_TYPE_ASK_PRICE:
            self.cash_data['askPrice'] = str(price)
        elif tickType == TICKER_TYPE_BID_PRICE:
            self.cash_data['bidPrice'] = str(price)

    def tickSize(self, reqId: TickerId, tickType: TickType, size: int):
        super().tickSize(reqId, tickType, size)
        print("tickerSize:" + str(size) + ",tickType:" + str(tickType))
        if tickType == TICKER_TYPE_ASK_SIZE:
            self.cash_data['askSize'] = str(size)
        elif tickType == TICKER_TYPE_BID_SIZE:
            self.cash_data['bidSize'] = str(size)

    def tickSnapshotEnd(self, reqId: int):
        super().tickSnapshotEnd(reqId)
        print("TickSnapshotEnd. TickerId:", reqId)
        product_name = products[reqId - self.req_id_base]
        self.cash_data["symbol"] = product_name
        redis_client.set(product_name + "@" + PLATFORM, json.dumps(self.cash_data), ex=20)
        redis_client.publish(PLATFORM, json.dumps({"symbol": product_name, "time": time.time()}))
        self.cash_data = {}

        time.sleep(0.015)
        self.index += 1
        self.subscribe_contract_at_index()

    # def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float,
    #                      bidSize: int, askSize: int, tickAttribBidAsk: TickAttribBidAsk):
    #     print(str(reqId) + ":tick by tick,bidPrice:" + str(bidPrice) + '，bidSize:' + str(bidSize) + ",askPrice:" + str(
    #         askPrice)
    #           + ",askSize:" + str(askSize))

    # def mktDepthExchanges(self, depthMktDataDescriptions: ListOfDepthExchanges):
    #     super().mktDepthExchanges(depthMktDataDescriptions)
    #     print("MktDepthExchanges:")
    #     for desc in depthMktDataDescriptions:
    #         print("DepthMktDataDescription.", desc)
    #
    # def updateMktDepth(self, reqId: TickerId, position: int, operation: int,
    #                    side: int, price: float, size: int):
    #     # super().updateMktDepth(reqId, position, operation, side, price, size)
    #     print("UpdateMarketDepth. ReqId:", reqId, "Position:", position, "Operation:",
    #           operation, "Side:", side, "Price:", price, "Size:", size)


ttt = None


def test():
    global ttt
    ttt = IBClient()
